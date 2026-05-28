"""Broker-Token-Ausstellung und -Verifikation im JWS-Compact-Format mit ML-DSA-65.

Stories: PQC-32 (TOK-1, issue), PQC-33 (TOK-2, verify).
Architektur-Bezug: docs/07_design.md Abschnitt 5.1.
RFCs: 7515 (JWS Compact Serialization), 7519 (JWT Claims), 8725 (JWT BCP).

**Token-Struktur:**

    base64url(header) . base64url(payload) . base64url(signature)

mit:
- **Header:** ``{"alg": "ML-DSA-65", "typ": "JWT", "kid": <kid>}``
- **Payload:** ``{"sub", "iss", "iat", "exp", "auth_method", "external_sub"}``
- **Signature:** ML-DSA-65 ueber die ASCII-Bytes von ``header_b64.payload_b64``

**Base64url-Encoding:** ohne Padding (`=` entfernt), per RFC 7515 Anhang C.

**Security (PQC-33, RFC 8725 BCP):**

- alg-Allowlist case-insensitive gegen ``settings.token.allowed_algs``.
- ``alg=none`` wird explizit abgelehnt (auch "None", "NONE" etc.).
- Granulare Exception-Hierarchie: ``InvalidTokenFormatError``,
  ``InvalidSignatureError``, ``InvalidClaimError``, ``ExpiredTokenError`` -
  alle erben von ``TokenServiceError``.
- Clock-Skew-Tolerance auf ``exp`` (default 30s, configurable), NIE auf ``iat``.
"""

from __future__ import annotations

import base64
import binascii
import json
import time
from typing import TYPE_CHECKING, Any, Literal

from crypto.facade import UnknownKidError
from crypto.registry import AlgorithmNotFoundError
from logging_config import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from crypto.facade import CryptoFacade


AuthMethod = Literal["local", "google", "microsoft"]


# ---------------------------------------------------------------------------
# Exception-Hierarchie (PQC-33 Senior-Decision: 4 granulare Sub-Klassen)
# ---------------------------------------------------------------------------


class TokenServiceError(Exception):
    """Basis-Fehler fuer TokenService-Probleme."""


class InvalidAuthMethodError(TokenServiceError):
    """``auth_method`` liegt nicht in der Whitelist (Issuance-Fehler)."""


class InvalidTokenFormatError(TokenServiceError):
    """Token-String hat nicht das erwartete JWS-Compact-Format.

    Beispiele: nicht 3 Segmente, ungueltige base64url-Chars, nicht-JSON-decode-bar.
    Trigger fuer dieses Error sind strukturelle Probleme VOR der Crypto-Validation.
    """


class InvalidSignatureError(TokenServiceError):
    """Signatur-Verifikation hat fehlgeschlagen.

    Token-Format war OK, alg/kid waren erlaubt, aber die kryptographische
    Signature-Pruefung gegen Header.Payload-Bytes ist gescheitert. Typisch
    bei manipulierten Tokens oder falschem Public Key.
    """


class InvalidClaimError(TokenServiceError):
    """Ein Claim im Token verletzt eine Policy.

    Beispiele: ``iss`` matched nicht, ``alg`` nicht in Allowlist, ``alg=none``,
    fehlendes Pflicht-Feld, falscher Typ.
    """


class ExpiredTokenError(TokenServiceError):
    """Token ist gemaess ``exp``-Claim abgelaufen (auch nach Leeway)."""


# ---------------------------------------------------------------------------
# Konstanten und Helpers
# ---------------------------------------------------------------------------


_SUPPORTED_AUTH_METHODS: frozenset[str] = frozenset({"local", "google", "microsoft"})

# RFC 8725-bis 2026: JWS-Compact-Tokens enthalten nur base64url-Chars plus
# zwei Dots. Wir akzeptieren A-Za-z0-9 plus -_. Damit fangen wir auch Code-
# Injection-Versuche frueh ab (z.B. Whitespace, Curly-Braces).
_VALID_TOKEN_CHARS: frozenset[str] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_."
)


def _b64url_encode(raw: bytes) -> str:
    """Base64url-Encoding ohne Padding (RFC 7515 Section 2 Anhang C)."""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    """Base64url-Decoding, Padding rekonstruiert.

    Raises:
        InvalidTokenFormatError: wenn segment kein gueltiges base64url ist.
    """
    padding = "=" * (-len(segment) % 4)
    try:
        return base64.urlsafe_b64decode(segment + padding)
    except (binascii.Error, ValueError) as exc:
        msg = f"segment is not valid base64url: {exc}"
        raise InvalidTokenFormatError(msg) from exc


def _compact_json(obj: dict[str, object]) -> bytes:
    """JSON-Serialisierung kompakt (kein Whitespace), UTF-8."""
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


# ---------------------------------------------------------------------------
# TokenService: Issue plus Verify
# ---------------------------------------------------------------------------


class TokenService:
    """Stellt Broker-Tokens aus und verifiziert sie (JWS Compact mit ML-DSA-65).

    DI:
    - ``crypto_facade``: Quelle fuer ``sign``/``verify``.
    - ``issuer``: ``iss``-Claim im Payload (z.B. ``"pqc-auth-service"``).
    - ``ttl_seconds``: Token-Lifetime; ``exp = iat + ttl_seconds``.
    - ``allowed_algs``: Allowlist erlaubter alg-Werte beim Verify (case-insensitive).
    - ``exp_leeway_seconds``: Clock-Skew-Toleranz beim exp-Check (nur exp, nicht iat).
    - ``clock``: Optional injizierbar fuer Tests (default: ``time.time``).
    """

    def __init__(
        self,
        *,
        crypto_facade: CryptoFacade,
        issuer: str,
        ttl_seconds: int,
        allowed_algs: list[str] | None = None,
        exp_leeway_seconds: int = 30,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if ttl_seconds <= 0:
            msg = f"ttl_seconds must be positive, got {ttl_seconds}"
            raise ValueError(msg)
        if not issuer:
            msg = "issuer must be a non-empty string"
            raise ValueError(msg)
        if exp_leeway_seconds < 0:
            msg = f"exp_leeway_seconds must be non-negative, got {exp_leeway_seconds}"
            raise ValueError(msg)
        if allowed_algs is None:
            allowed_algs = ["ML-DSA-65"]
        if not allowed_algs:
            msg = "allowed_algs must be a non-empty list"
            raise ValueError(msg)
        self._facade = crypto_facade
        self._issuer = issuer
        self._ttl = ttl_seconds
        # Lowercase-Set vorberechnen fuer case-insensitive O(1)-Lookup.
        self._allowed_algs_lower: frozenset[str] = frozenset(a.lower() for a in allowed_algs)
        self._allowed_algs_original: list[str] = list(allowed_algs)
        self._exp_leeway = exp_leeway_seconds
        self._clock: Callable[[], float] = clock or time.time
        self._logger = get_logger("rib_pqc.token")

    # -----------------------------------------------------------------------
    # AC-1 bis AC-5 PQC-32 (TOK-1): issue
    # -----------------------------------------------------------------------

    def issue(
        self,
        user_id: str,
        auth_method: str,
        external_sub: str | None = None,
    ) -> str:
        """Stellt einen Broker-Token aus.

        Args:
            user_id: Interne User-UUID. Wird zum ``sub``-Claim.
            auth_method: ``"local"``, ``"google"`` oder ``"microsoft"``.
            external_sub: Bei federated Auth der externe sub-Claim.
                Bei local-Auth wird ``null`` im Token gesetzt (Design 5.1).

        Returns:
            JWS-Compact-Token als String.

        Raises:
            InvalidAuthMethodError: wenn auth_method nicht in der Whitelist.
            ValueError: wenn user_id leer ist.
        """
        if not user_id:
            msg = "user_id must be a non-empty string"
            raise ValueError(msg)
        if auth_method not in _SUPPORTED_AUTH_METHODS:
            msg = (
                f"Unsupported auth_method '{auth_method}'. "
                f"Allowed: {sorted(_SUPPORTED_AUTH_METHODS)}"
            )
            raise InvalidAuthMethodError(msg)

        now = int(self._clock())
        exp = now + self._ttl

        alg, kid = self._lookup_signing_metadata()

        header = {"alg": alg, "typ": "JWT", "kid": kid}
        payload = {
            "sub": user_id,
            "iss": self._issuer,
            "iat": now,
            "exp": exp,
            "auth_method": auth_method,
            "external_sub": external_sub,
        }

        header_b64 = _b64url_encode(_compact_json(header))
        payload_b64 = _b64url_encode(_compact_json(payload))

        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        signature, sign_alg, sign_kid = self._facade.sign(
            signing_input, purpose="broker-token"
        )

        if sign_alg != alg or sign_kid != kid:
            msg = (
                f"TokenService header-vs-sign mismatch: header alg={alg} kid={kid}, "
                f"sign returned alg={sign_alg} kid={sign_kid}"
            )
            raise TokenServiceError(msg)

        signature_b64 = _b64url_encode(signature)
        token = f"{header_b64}.{payload_b64}.{signature_b64}"

        self._logger.info(
            "token.issued",
            sub=user_id,
            auth_method=auth_method,
            external_sub_present=external_sub is not None,
            alg=alg,
            kid=kid,
            iat=now,
            exp=exp,
            ttl_seconds=self._ttl,
            token_length=len(token),
        )
        return token

    # -----------------------------------------------------------------------
    # AC-1 bis AC-6 PQC-33 (TOK-2): verify
    # -----------------------------------------------------------------------

    def verify(self, token_str: str) -> dict[str, Any]:
        """Verifiziert einen Broker-Token und liefert die Claims zurueck.

        Pruefkette (in dieser Reihenfolge, fail-fast):
          1. Format-Sanity: Token-String existiert, nur base64url-Chars plus Dots
          2. Strukturelles Splitten: 3 Segmente
          3. Header-Decode: JSON-Parse, alg/kid extrahieren
          4. AC-6: alg-Allowlist-Check (RFC 8725 BCP, case-insensitive, none-Schutz)
          5. Header-kid-Type-Check
          6. Payload-Decode: JSON-Parse, Claims extrahieren
          7. AC-4: iss matched ``settings.token.issuer``
          8. AC-3: exp gegen now (mit Leeway)
          9. AC-2/AC-5: Signature-Verifikation via Facade

        Returns:
            Claims-Dict mit ``sub``, ``iss``, ``iat``, ``exp``, ``auth_method``,
            ``external_sub``.

        Raises:
            InvalidTokenFormatError: Token-String falsch strukturiert.
            InvalidClaimError: Header oder Payload haben unzulaessige Claims.
            ExpiredTokenError: Token ist gemaess exp abgelaufen.
            InvalidSignatureError: Signature-Pruefung fehlgeschlagen.
        """
        # Schritt 1: Format-Sanity
        if not token_str or not isinstance(token_str, str):
            msg = "token must be a non-empty string"
            raise InvalidTokenFormatError(msg)
        # RFC 8725-bis 2026: nur base64url-Chars und Dots erlaubt
        if not all(c in _VALID_TOKEN_CHARS for c in token_str):
            msg = "token contains characters outside [A-Za-z0-9-_.]"
            raise InvalidTokenFormatError(msg)

        # Schritt 2: Strukturelles Splitten
        parts = token_str.split(".")
        if len(parts) != 3:
            msg = f"token must have exactly 3 segments separated by '.', got {len(parts)}"
            raise InvalidTokenFormatError(msg)
        header_b64, payload_b64, signature_b64 = parts
        if not header_b64 or not payload_b64 or not signature_b64:
            msg = "token segments must not be empty"
            raise InvalidTokenFormatError(msg)

        # Schritt 3: Header-Decode
        header_bytes = _b64url_decode(header_b64)
        try:
            header = json.loads(header_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            msg = f"header is not valid JSON: {exc}"
            raise InvalidTokenFormatError(msg) from exc
        if not isinstance(header, dict):
            msg = f"header must be a JSON object, got {type(header).__name__}"
            raise InvalidTokenFormatError(msg)

        # Schritt 4: AC-6 alg-Allowlist (RFC 8725 BCP)
        alg = header.get("alg")
        if not isinstance(alg, str) or not alg:
            msg = "header.alg must be a non-empty string"
            raise InvalidClaimError(msg)
        alg_lower = alg.lower()
        if alg_lower == "none":
            # Explizit. Auch wenn "none" theoretisch in der Allowlist stuende,
            # erlauben wir es per RFC 8725 BCP niemals.
            msg = "alg=none is explicitly forbidden (RFC 8725 BCP)"
            raise InvalidClaimError(msg)
        if alg_lower not in self._allowed_algs_lower:
            msg = (
                f"alg '{alg}' is not in allowlist {self._allowed_algs_original} "
                "(RFC 8725 BCP alg-confusion guard)"
            )
            raise InvalidClaimError(msg)

        # Schritt 5: kid-Type-Check
        kid = header.get("kid")
        if not isinstance(kid, str) or not kid:
            msg = "header.kid must be a non-empty string"
            raise InvalidClaimError(msg)

        # Schritt 6: Payload-Decode
        payload_bytes = _b64url_decode(payload_b64)
        try:
            payload = json.loads(payload_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            msg = f"payload is not valid JSON: {exc}"
            raise InvalidTokenFormatError(msg) from exc
        if not isinstance(payload, dict):
            msg = f"payload must be a JSON object, got {type(payload).__name__}"
            raise InvalidTokenFormatError(msg)

        # Schritt 7: AC-4 iss-Check
        iss = payload.get("iss")
        if iss != self._issuer:
            msg = f"iss '{iss}' does not match expected '{self._issuer}'"
            raise InvalidClaimError(msg)

        # Schritt 8: AC-3 exp-Check mit Leeway (nur exp, nicht iat)
        exp = payload.get("exp")
        if not isinstance(exp, int) or isinstance(exp, bool):
            # bool ist Subclass von int in Python - explizit ausschliessen
            msg = "payload.exp must be an integer (NumericDate per RFC 7519)"
            raise InvalidClaimError(msg)
        now = int(self._clock())
        if now > exp + self._exp_leeway:
            msg = (
                f"token expired: exp={exp}, now={now}, leeway={self._exp_leeway}s "
                f"(diff {now - exp}s past exp)"
            )
            raise ExpiredTokenError(msg)

        # Schritt 9: AC-2/AC-5 Signature-Verifikation via Facade
        signature = _b64url_decode(signature_b64)
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        try:
            sig_ok = self._facade.verify(signing_input, signature, alg, kid)
        except UnknownKidError as exc:
            msg = f"unknown kid '{kid}'"
            raise InvalidClaimError(msg) from exc
        except AlgorithmNotFoundError as exc:
            # alg ist in Token-Allowlist, aber kein Plugin in CryptoRegistry
            # registriert. Konfigurations-Inkonsistenz.
            msg = f"alg '{alg}' has no registered plugin in CryptoRegistry"
            raise InvalidClaimError(msg) from exc
        if not sig_ok:
            msg = "signature verification failed"
            raise InvalidSignatureError(msg)

        # Erfolgs-Logging. sub-Logging ist Tier-2 F-026 (mit F-021 buendeln,
        # vor PQC-30 auf DEBUG reduzieren).
        self._logger.info(
            "token.verified",
            sub=payload.get("sub"),
            auth_method=payload.get("auth_method"),
            external_sub_present=payload.get("external_sub") is not None,
            alg=alg,
            kid=kid,
            iat=payload.get("iat"),
            exp=exp,
        )
        return payload

    # -----------------------------------------------------------------------
    # Internals
    # -----------------------------------------------------------------------

    def _lookup_signing_metadata(self) -> tuple[str, str]:
        """Liefert (alg, kid) die ``Facade.sign`` zurueckliefern wird.

        Aktuell zugegriffen via private Attribute der Facade. Sprint-3-Polish
        koennte einen sauberen Getter ``Facade.signing_metadata()`` ergaenzen
        (siehe deferred Finding F-024).
        """
        return self._facade._default_signature_alg, self._facade._signing_kid
