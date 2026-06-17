"""ID-Token-Verifier fuer OIDC-Federation.

Story: PQC-38 (BRK-3) AC-2, AC-3, AC-4.

**Aufgabe:**

Verifiziert ein OIDC ID-Token (JWS Compact, signiert von einem externen
IdP wie Google oder Microsoft). Validiert:

- **Signature** (via Provider-JWKS, algorithm-pinned RS256/ES256).
- **Issuer** (``iss`` muss exact zu Provider-Erwartung passen).
- **Audience** (``aud`` muss unsere ``client_id`` enthalten).
- **Expiry** (``exp`` mit konfigurierbarem Leeway gegen Clock-Skew).
- **Not-Before** (``nbf`` wenn gesetzt).

**Designprinzipien (RFC 9700 BCP 2026, OIDC Core 1.0 Section 3.1.3.7):**

- **Algorithm-Pinning:** ``allowed_algs`` wird explizit uebergeben, NICHT
  aus dem Token-Header gelesen. Schutz gegen alg-confusion-attacks.
- **kid-Lookup:** Header-``kid`` muss in den JWKS-Keys vorhanden sein.
  Wenn nicht (z.B. nach Key-Rotation), triggern wir EINEN Force-Refresh
  und probieren nochmal; danach Fail.
- **Plugin-Layer wraps Verifier:** Diese Klasse ist provider-agnostic.
  Provider-spezifische Logik (Microsoft-tid-Claim) lebt im Plugin.

**Fehlerverhalten:**

- ``IdTokenVerifyError`` mit ``reason`` ("invalid_signature", "expired",
  "invalid_issuer", "invalid_audience", "unknown_kid", "malformed_token").
  Router mapped auf HTTP 401.
"""

from __future__ import annotations

import logging
from typing import Any

import jwt
from jwt import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    InvalidTokenError,
    PyJWKError,
    algorithms,
    get_unverified_header,
)

from services.oidc_jwks_service import JwksFetchError, OidcJwksService

logger = logging.getLogger(__name__)


class IdTokenVerifyError(Exception):
    """Wird geworfen, wenn ID-Token-Verifikation failed.

    Attributes:
        reason: Maschinenlesbarer Code (siehe Modul-Docstring).
    """

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


def _find_signing_key(jwks: dict[str, Any], kid: str | None) -> Any:
    """Liefert den Signing-Key aus dem JWKS, der zum ``kid`` passt.

    Args:
        jwks: JSON-Web-Key-Set (Dict mit ``keys``-Field).
        kid: Key-ID aus dem JWS-Header. None falls Header kein kid hat
            (selten, nur bei Single-Key-Setups).

    Raises:
        IdTokenVerifyError: wenn kein passender Key gefunden.
    """
    keys = jwks.get("keys", [])
    if not isinstance(keys, list):
        msg = "JWKS 'keys' is not a list"
        raise IdTokenVerifyError(msg, reason="malformed_jwks")

    if kid is None:
        # Edge-Case: Token ohne kid. RFC erlaubt das wenn JWKS nur einen Key hat.
        if len(keys) == 1:
            return algorithms.RSAAlgorithm.from_jwk(keys[0])  # type: ignore[no-untyped-call]
        msg = "Token has no 'kid' and JWKS has multiple keys"
        raise IdTokenVerifyError(msg, reason="unknown_kid")

    for key in keys:
        if isinstance(key, dict) and key.get("kid") == kid:
            kty = key.get("kty")
            try:
                if kty == "RSA":
                    return algorithms.RSAAlgorithm.from_jwk(key)  # type: ignore[no-untyped-call]
                if kty == "EC":
                    return algorithms.ECAlgorithm.from_jwk(key)  # type: ignore[no-untyped-call]
            except (PyJWKError, ValueError, KeyError) as exc:
                msg = f"Failed to parse JWK with kid={kid!r}: {exc}"
                raise IdTokenVerifyError(msg, reason="malformed_jwk") from exc
            msg = f"Unsupported JWK kty={kty!r}"
            raise IdTokenVerifyError(msg, reason="unsupported_kty")

    msg = f"No JWK matches kid={kid!r}"
    raise IdTokenVerifyError(msg, reason="unknown_kid")


class IdTokenVerifier:
    """Provider-agnostic ID-Token-Verifier.

    Story-Bezug: PQC-38 BRK-3 AC-2..AC-4.
    """

    def __init__(
        self,
        jwks_service: OidcJwksService,
        exp_leeway_seconds: int,
    ) -> None:
        if exp_leeway_seconds < 0:
            msg = f"exp_leeway_seconds must be >= 0, got {exp_leeway_seconds}"
            raise ValueError(msg)
        self._jwks_service = jwks_service
        self._leeway = exp_leeway_seconds

    async def verify(
        self,
        *,
        token: str,
        jwks_uri: str,
        issuer: str,
        audience: str,
        allowed_algs: list[str],
    ) -> dict[str, Any]:
        """Verifiziert ``token`` gegen das Provider-JWKS.

        Args:
            token: JWS-Compact-encoded ID-Token.
            jwks_uri: URL zum Provider-JWKS-Endpoint.
            issuer: erwarteter ``iss``-Claim (exact-match).
            audience: erwarteter ``aud``-Claim (unsere ``client_id``).
            allowed_algs: Liste der akzeptierten Sig-Algorithmen
                (pinned, NICHT aus Header gelesen).

        Returns:
            Dict mit den verifizierten Token-Claims.

        Raises:
            IdTokenVerifyError mit ``reason`` Code.
        """
        try:
            header = get_unverified_header(token)
        except InvalidTokenError as exc:
            msg = f"Cannot parse token header: {exc}"
            raise IdTokenVerifyError(msg, reason="malformed_token") from exc

        # Algorithm-Pinning: Header-alg MUSS in allowed_algs sein.
        header_alg = header.get("alg")
        if header_alg not in allowed_algs:
            msg = (
                f"Token alg={header_alg!r} not in allowed algorithms "
                f"{allowed_algs}"
            )
            raise IdTokenVerifyError(msg, reason="disallowed_alg")

        kid = header.get("kid")

        # Versuch 1: cached JWKS. Bei unknown_kid Force-Refresh und retry.
        try:
            jwks = await self._jwks_service.get_jwks(jwks_uri)
        except JwksFetchError as exc:
            msg = f"JWKS fetch failed: {exc}"
            raise IdTokenVerifyError(msg, reason="jwks_fetch_failed") from exc

        try:
            signing_key = _find_signing_key(jwks, kid)
        except IdTokenVerifyError as first_attempt:
            if first_attempt.reason != "unknown_kid":
                raise
            # Key-Rotation-Race? Force-Refresh + retry.
            logger.info(
                "id_token_verify.kid_miss_refresh",
                extra={"kid": kid, "jwks_uri": jwks_uri},
            )
            try:
                jwks = await self._jwks_service.get_jwks(jwks_uri, force_refresh=True)
            except JwksFetchError as exc:
                msg = f"JWKS force-refresh failed: {exc}"
                raise IdTokenVerifyError(
                    msg,
                    reason="jwks_fetch_failed",
                ) from exc
            signing_key = _find_signing_key(jwks, kid)

        # Signature + Claims-Verify via pyjwt. exp wird hier mit Leeway gegen
        # Clock-Skew gegen Provider geprueft.
        try:
            payload = jwt.decode(
                token,
                key=signing_key,
                algorithms=allowed_algs,
                issuer=issuer,
                audience=audience,
                leeway=self._leeway,
                options={
                    "require": ["exp", "iat", "iss", "aud", "sub"],
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
            )
        except ExpiredSignatureError as exc:
            msg = "ID token has expired"
            raise IdTokenVerifyError(msg, reason="expired") from exc
        except InvalidSignatureError as exc:
            msg = "ID token signature is invalid"
            raise IdTokenVerifyError(msg, reason="invalid_signature") from exc
        except InvalidIssuerError as exc:
            msg = "ID token issuer mismatch"
            raise IdTokenVerifyError(msg, reason="invalid_issuer") from exc
        except InvalidAudienceError as exc:
            msg = "ID token audience mismatch"
            raise IdTokenVerifyError(msg, reason="invalid_audience") from exc
        except InvalidTokenError as exc:
            # Fallback fuer alle anderen pyjwt-Errors (z.B. MissingRequiredClaimError)
            msg = f"ID token invalid: {exc}"
            raise IdTokenVerifyError(msg, reason="invalid_token") from exc

        if not isinstance(payload, dict):
            msg = "Decoded payload is not a dict"
            raise IdTokenVerifyError(msg, reason="malformed_payload")

        logger.info(
            "id_token_verify.success",
            extra={
                "issuer": payload.get("iss"),
                "sub": payload.get("sub"),
                # email NICHT loggen (PII)
            },
        )
        return payload
