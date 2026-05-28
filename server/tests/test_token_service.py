"""Tests fuer services/token_service.py.

Stories:
- PQC-32 (TOK-1) Issue: AC-1 bis AC-5.
- PQC-33 (TOK-2) Verify: AC-1 bis AC-6 (incl. RFC 8725 BCP alg-Allowlist).

Tests benoetigen ``oqs`` Python-Library (LibOqsSignature). Ohne liboqs
werden alle Tests via ``pytest.importorskip`` uebersprungen.
"""

from __future__ import annotations

import base64
import json

import pytest

from crypto.facade import CryptoFacade
from crypto.registry import CryptoRegistry
from services.token_service import (
    ExpiredTokenError,
    InvalidAuthMethodError,
    InvalidClaimError,
    InvalidSignatureError,
    InvalidTokenFormatError,
    TokenService,
    TokenServiceError,
)

oqs = pytest.importorskip("oqs", reason="liboqs-python not installed in this environment")

from crypto.adapters.liboqs_signature import LibOqsSignature  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def registry() -> CryptoRegistry:
    registry = CryptoRegistry()
    registry.register_signature("ML-DSA-65", LibOqsSignature("ML-DSA-65"))
    return registry


@pytest.fixture
def facade(registry: CryptoRegistry) -> CryptoFacade:
    plugin = registry.get_signature("ML-DSA-65")
    pk, sk = plugin.keygen()
    return CryptoFacade(
        registry=registry,
        default_signature_alg="ML-DSA-65",
        signing_kid="auth-signing-key-v1",
        signing_secret_key=sk,
        verifying_keys_by_kid={"auth-signing-key-v1": pk},
    )


@pytest.fixture
def fixed_clock() -> callable:  # type: ignore[type-arg]
    """Klock-Fixture liefert immer 1700000000 (2023-11-14 22:13:20 UTC)."""
    return lambda: 1700000000


@pytest.fixture
def token_service(facade: CryptoFacade, fixed_clock: callable) -> TokenService:  # type: ignore[type-arg]
    return TokenService(
        crypto_facade=facade,
        issuer="pqc-auth-service",
        ttl_seconds=3600,
        clock=fixed_clock,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _b64url_decode(segment: str) -> bytes:
    """Inverse von _b64url_encode (RFC 7515 Anhang C). Padding rekonstruieren."""
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _decode_token(token: str) -> tuple[dict, dict, bytes]:
    """Token in (header_dict, payload_dict, signature_bytes) zerlegen."""
    header_b64, payload_b64, signature_b64 = token.split(".")
    header = json.loads(_b64url_decode(header_b64))
    payload = json.loads(_b64url_decode(payload_b64))
    signature = _b64url_decode(signature_b64)
    return header, payload, signature


# ---------------------------------------------------------------------------
# Konstruktor-Validierung
# ---------------------------------------------------------------------------


def test_token_service_init_rejects_non_positive_ttl(facade: CryptoFacade) -> None:
    with pytest.raises(ValueError, match="ttl_seconds must be positive"):
        TokenService(crypto_facade=facade, issuer="x", ttl_seconds=0)


def test_token_service_init_rejects_empty_issuer(facade: CryptoFacade) -> None:
    with pytest.raises(ValueError, match="issuer must be a non-empty"):
        TokenService(crypto_facade=facade, issuer="", ttl_seconds=3600)


# ---------------------------------------------------------------------------
# AC-1: JWS-Compact-Format mit 3 Segmenten
# ---------------------------------------------------------------------------


def test_issue_returns_three_base64url_segments(token_service: TokenService) -> None:
    token = token_service.issue("user-abc", "local")
    parts = token.split(".")
    assert len(parts) == 3
    # Jedes Segment muss base64url ohne Padding sein
    for part in parts:
        assert "=" not in part
        # Re-decode sollte nicht crashen
        _b64url_decode(part)


# ---------------------------------------------------------------------------
# AC-2: Header-Felder
# ---------------------------------------------------------------------------


def test_issue_header_contains_alg_typ_kid(token_service: TokenService) -> None:
    token = token_service.issue("user-abc", "local")
    header, _, _ = _decode_token(token)
    assert header["alg"] == "ML-DSA-65"
    assert header["typ"] == "JWT"
    assert header["kid"] == "auth-signing-key-v1"


# ---------------------------------------------------------------------------
# AC-3: Payload-Felder
# ---------------------------------------------------------------------------


def test_issue_payload_contains_required_claims(token_service: TokenService) -> None:
    token = token_service.issue("user-abc", "local")
    _, payload, _ = _decode_token(token)
    assert payload["sub"] == "user-abc"
    assert payload["iss"] == "pqc-auth-service"
    assert payload["iat"] == 1700000000
    assert payload["exp"] == 1700000000 + 3600
    assert payload["auth_method"] == "local"
    assert payload["external_sub"] is None


def test_issue_payload_external_sub_for_federated(token_service: TokenService) -> None:
    token = token_service.issue("user-abc", "google", external_sub="google|112233")
    _, payload, _ = _decode_token(token)
    assert payload["auth_method"] == "google"
    assert payload["external_sub"] == "google|112233"


def test_issue_payload_external_sub_null_for_local(token_service: TokenService) -> None:
    """Design 5.1: external_sub immer im Payload, ``null`` bei local."""
    token = token_service.issue("user-abc", "local")
    _, payload, _ = _decode_token(token)
    assert "external_sub" in payload
    assert payload["external_sub"] is None


# ---------------------------------------------------------------------------
# AC-4: TTL-Korrektheit
# ---------------------------------------------------------------------------


def test_issue_exp_equals_iat_plus_ttl(facade: CryptoFacade) -> None:
    """Mit ttl_seconds=7200 muss exp - iat == 7200 sein."""
    service = TokenService(
        crypto_facade=facade,
        issuer="iss-x",
        ttl_seconds=7200,
        clock=lambda: 1700000000,
    )
    token = service.issue("user-abc", "local")
    _, payload, _ = _decode_token(token)
    assert payload["exp"] - payload["iat"] == 7200


# ---------------------------------------------------------------------------
# AC-5: Round-Trip mit Facade.verify
# ---------------------------------------------------------------------------


def test_issue_token_can_be_verified_via_facade(
    token_service: TokenService, facade: CryptoFacade
) -> None:
    """Round-Trip: issued Token wird ueber Facade.verify validiert.

    Das ist der wichtigste Test: er beweist, dass der Token-Service
    JWS-konforme Bytes liefert, die unsere eigene Crypto-Schicht
    verifizieren kann.
    """
    token = token_service.issue("user-abc", "local")
    header_b64, payload_b64, _signature_b64 = token.split(".")
    header, _, signature = _decode_token(token)

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")

    assert facade.verify(signing_input, signature, header["alg"], header["kid"]) is True


def test_issue_tampered_payload_fails_verify(
    token_service: TokenService, facade: CryptoFacade
) -> None:
    """Wenn nach Issue der Payload veraendert wird, muss verify False zurueckliefern."""
    token = token_service.issue("user-abc", "local")
    header_b64, payload_b64, _ = token.split(".")
    header, _, signature = _decode_token(token)

    # Payload "veraendern" -> tampered signing_input
    tampered_input = f"{header_b64}.{payload_b64}TAMPERED".encode("ascii")
    assert facade.verify(tampered_input, signature, header["alg"], header["kid"]) is False


# ---------------------------------------------------------------------------
# Input-Validierung
# ---------------------------------------------------------------------------


def test_issue_rejects_empty_user_id(token_service: TokenService) -> None:
    with pytest.raises(ValueError, match="user_id must be a non-empty"):
        token_service.issue("", "local")


def test_issue_rejects_unsupported_auth_method(token_service: TokenService) -> None:
    with pytest.raises(InvalidAuthMethodError, match="Unsupported auth_method"):
        token_service.issue("user-abc", "facebook")


@pytest.mark.parametrize("auth_method", ["local", "google", "microsoft"])
def test_issue_accepts_each_supported_auth_method(
    token_service: TokenService, auth_method: str
) -> None:
    token = token_service.issue(
        "user-abc",
        auth_method,
        external_sub=None if auth_method == "local" else f"{auth_method}|x",
    )
    _, payload, _ = _decode_token(token)
    assert payload["auth_method"] == auth_method


# ---------------------------------------------------------------------------
# Sanity: TokenServiceError ist als Basis-Klasse erreichbar
# ---------------------------------------------------------------------------


def test_invalid_auth_method_error_is_token_service_error() -> None:
    assert issubclass(InvalidAuthMethodError, TokenServiceError)


# ===========================================================================
# PQC-33 (TOK-2) Verify-Tests: AC-1 bis AC-6
# ===========================================================================


def _b64u_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _make_token_str(
    header: dict,
    payload: dict,
    signature: bytes,
) -> str:
    """Baut einen JWS-Compact-String aus header+payload+signature.

    Hilft Tests Tokens mit speziellen Header/Payload-Inhalten zu konstruieren,
    ohne durch issue() zu gehen (z.B. fuer alg=none, falsche iss, etc).
    """
    header_b64 = _b64u_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64u_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature_b64 = _b64u_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


# ---------------------------------------------------------------------------
# Round-Trip (AC-1, AC-2, AC-5)
# ---------------------------------------------------------------------------


def test_verify_round_trip_local(token_service: TokenService) -> None:
    """AC-1, AC-5: issued Token wird vom selben Service erfolgreich verifiziert."""
    token = token_service.issue("user-abc", "local")
    claims = token_service.verify(token)
    assert claims["sub"] == "user-abc"
    assert claims["iss"] == "pqc-auth-service"
    assert claims["auth_method"] == "local"
    assert claims["external_sub"] is None


def test_verify_round_trip_federated(token_service: TokenService) -> None:
    """Federated Token wird ebenfalls verifiziert, external_sub bleibt erhalten."""
    token = token_service.issue("user-xyz", "google", external_sub="google|123")
    claims = token_service.verify(token)
    assert claims["auth_method"] == "google"
    assert claims["external_sub"] == "google|123"


# ---------------------------------------------------------------------------
# Format-Errors (AC-1)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_token",
    [
        "",
        "no-dots",
        "a.b",
        "a.b.c.d",
        "with space.b.c",
        "tab\there.b.c",
        "a.b.c=padding",
        "a.b.",
        ".b.c",
        "a..c",
    ],
)
def test_verify_rejects_invalid_format(token_service: TokenService, bad_token: str) -> None:
    with pytest.raises(InvalidTokenFormatError):
        token_service.verify(bad_token)


def test_verify_rejects_non_string(token_service: TokenService) -> None:
    """Defensive: nicht-String-Input wird sauber abgefangen."""
    with pytest.raises(InvalidTokenFormatError):
        token_service.verify(None)  # type: ignore[arg-type]


def test_verify_rejects_non_json_header(token_service: TokenService) -> None:
    """Header-Segment ist base64url aber nicht JSON."""
    bad_header = _b64u_encode(b"not json{{{")
    bad_payload = _b64u_encode(b'{"iss":"x"}')
    bad_sig = _b64u_encode(b"sig")
    token = f"{bad_header}.{bad_payload}.{bad_sig}"
    with pytest.raises(InvalidTokenFormatError):
        token_service.verify(token)


# ---------------------------------------------------------------------------
# AC-6: alg-Allowlist (RFC 8725 BCP)
# ---------------------------------------------------------------------------


def test_verify_rejects_alg_none(token_service: TokenService) -> None:
    """alg=none ist auch dann verboten wenn es in der Allowlist stuende."""
    token = _make_token_str(
        {"alg": "none", "typ": "JWT", "kid": "auth-signing-key-v1"},
        {"iss": "pqc-auth-service", "exp": 9999999999, "sub": "u",
         "auth_method": "local", "external_sub": None, "iat": 1700000000},
        b"sig",
    )
    with pytest.raises(InvalidClaimError, match="alg=none"):
        token_service.verify(token)


@pytest.mark.parametrize("variant", ["None", "NONE", "nOnE", "none"])
def test_verify_rejects_alg_none_case_insensitive(
    token_service: TokenService, variant: str
) -> None:
    """alg=none-Schutz greift case-insensitive (Curity-Empfehlung)."""
    token = _make_token_str(
        {"alg": variant, "typ": "JWT", "kid": "auth-signing-key-v1"},
        {"iss": "pqc-auth-service", "exp": 9999999999, "sub": "u",
         "auth_method": "local", "external_sub": None, "iat": 1700000000},
        b"sig",
    )
    with pytest.raises(InvalidClaimError, match="alg=none"):
        token_service.verify(token)


def test_verify_rejects_unknown_alg(token_service: TokenService) -> None:
    """alg ausserhalb der Allowlist wird abgelehnt (alg-confusion-Schutz)."""
    token = _make_token_str(
        {"alg": "HS256", "typ": "JWT", "kid": "auth-signing-key-v1"},
        {"iss": "pqc-auth-service", "exp": 9999999999, "sub": "u",
         "auth_method": "local", "external_sub": None, "iat": 1700000000},
        b"sig",
    )
    with pytest.raises(InvalidClaimError, match="not in allowlist"):
        token_service.verify(token)


def test_verify_rejects_missing_alg(token_service: TokenService) -> None:
    token = _make_token_str(
        {"typ": "JWT", "kid": "auth-signing-key-v1"},
        {"iss": "pqc-auth-service", "exp": 9999999999, "sub": "u",
         "auth_method": "local", "external_sub": None, "iat": 1700000000},
        b"sig",
    )
    with pytest.raises(InvalidClaimError, match="alg"):
        token_service.verify(token)


def test_verify_accepts_alg_case_insensitive_when_in_allowlist(
    facade: CryptoFacade, fixed_clock,  # type: ignore[no-untyped-def]
) -> None:
    """Allowlist ist case-insensitive: 'ml-dsa-65' matched 'ML-DSA-65'.

    Wir koennen das nicht direkt mit issue+verify testen weil issue() den
    Header-alg vom Facade bekommt (uppercase). Stattdessen: Token mit
    case-variant bauen, signature manuell durch facade.sign holen.
    """
    # Token-bytes mit 'ml-dsa-65' im Header bauen
    header = {"alg": "ml-dsa-65", "typ": "JWT", "kid": "auth-signing-key-v1"}
    payload = {"iss": "pqc-auth-service", "exp": 9999999999, "iat": 1700000000,
               "sub": "u", "auth_method": "local", "external_sub": None}
    header_b64 = _b64u_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64u_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    sig, _, _ = facade.sign(signing_input, purpose="test")
    sig_b64 = _b64u_encode(sig)
    token = f"{header_b64}.{payload_b64}.{sig_b64}"

    svc = TokenService(
        crypto_facade=facade, issuer="pqc-auth-service", ttl_seconds=3600,
        clock=fixed_clock,
    )
    claims = svc.verify(token)
    assert claims["sub"] == "u"


def test_verify_rejects_missing_kid(token_service: TokenService) -> None:
    token = _make_token_str(
        {"alg": "ML-DSA-65", "typ": "JWT"},
        {"iss": "pqc-auth-service", "exp": 9999999999, "sub": "u",
         "auth_method": "local", "external_sub": None, "iat": 1700000000},
        b"sig",
    )
    with pytest.raises(InvalidClaimError, match="kid"):
        token_service.verify(token)


# ---------------------------------------------------------------------------
# AC-4: iss-Check
# ---------------------------------------------------------------------------


def test_verify_rejects_wrong_issuer(token_service: TokenService) -> None:
    token = _make_token_str(
        {"alg": "ML-DSA-65", "typ": "JWT", "kid": "auth-signing-key-v1"},
        {"iss": "evil-issuer", "exp": 9999999999, "sub": "u",
         "auth_method": "local", "external_sub": None, "iat": 1700000000},
        b"sig",
    )
    with pytest.raises(InvalidClaimError, match="iss"):
        token_service.verify(token)


# ---------------------------------------------------------------------------
# AC-3: exp-Check mit Leeway (nur auf exp, nicht iat)
# ---------------------------------------------------------------------------


def test_verify_rejects_expired_token_outside_leeway(
    facade: CryptoFacade, fixed_clock,  # type: ignore[no-untyped-def]
) -> None:
    """Token expired 100s past leeway 30s -> ExpiredTokenError."""
    issuer_svc = TokenService(
        crypto_facade=facade, issuer="pqc-auth-service", ttl_seconds=3600,
        exp_leeway_seconds=30, clock=fixed_clock,
    )
    token = issuer_svc.issue("user-a", "local")
    # Move clock 3700s forward (TTL 3600 + 100s past leeway-window of 30s)
    verifier_svc = TokenService(
        crypto_facade=facade, issuer="pqc-auth-service", ttl_seconds=3600,
        exp_leeway_seconds=30, clock=lambda: 1700000000 + 3700,
    )
    with pytest.raises(ExpiredTokenError, match="expired"):
        verifier_svc.verify(token)


def test_verify_accepts_token_within_leeway(
    facade: CryptoFacade, fixed_clock,  # type: ignore[no-untyped-def]
) -> None:
    """Token 20s ueber exp, aber Leeway 30s -> verify OK."""
    issuer_svc = TokenService(
        crypto_facade=facade, issuer="pqc-auth-service", ttl_seconds=3600,
        exp_leeway_seconds=30, clock=fixed_clock,
    )
    token = issuer_svc.issue("user-a", "local")
    verifier_svc = TokenService(
        crypto_facade=facade, issuer="pqc-auth-service", ttl_seconds=3600,
        exp_leeway_seconds=30, clock=lambda: 1700000000 + 3620,
    )
    claims = verifier_svc.verify(token)
    assert claims["sub"] == "user-a"


def test_verify_rejects_non_integer_exp(token_service: TokenService) -> None:
    token = _make_token_str(
        {"alg": "ML-DSA-65", "typ": "JWT", "kid": "auth-signing-key-v1"},
        {"iss": "pqc-auth-service", "exp": "not-a-number", "sub": "u",
         "auth_method": "local", "external_sub": None, "iat": 1700000000},
        b"sig",
    )
    with pytest.raises(InvalidClaimError, match="exp"):
        token_service.verify(token)


# ---------------------------------------------------------------------------
# AC-2/AC-5: Signature-Verifikation via Facade
# ---------------------------------------------------------------------------


def test_verify_rejects_tampered_signature(
    facade: CryptoFacade, fixed_clock,  # type: ignore[no-untyped-def]
) -> None:
    """Strukturell gueltiger Token, aber Signature ist zufaellige bytes."""
    issuer_svc = TokenService(
        crypto_facade=facade, issuer="pqc-auth-service", ttl_seconds=3600,
        clock=fixed_clock,
    )
    token = issuer_svc.issue("user-a", "local")
    header_b64, payload_b64, _real_sig = token.split(".")
    fake_sig_b64 = _b64u_encode(b"X" * 3309)  # ML-DSA-65 sig size = 3309
    tampered_token = f"{header_b64}.{payload_b64}.{fake_sig_b64}"
    with pytest.raises(InvalidSignatureError, match="signature"):
        issuer_svc.verify(tampered_token)


def test_verify_rejects_tampered_payload_byte(
    facade: CryptoFacade, fixed_clock,  # type: ignore[no-untyped-def]
) -> None:
    """Payload-Modification fuehrt zu Signature-Mismatch.

    Wir konstruieren einen Token mit ECHTER Signature von Payload-A, aber
    Payload-B im Token. Signature kann den Payload-Tampering nicht maskieren.
    """
    svc = TokenService(
        crypto_facade=facade, issuer="pqc-auth-service", ttl_seconds=3600,
        clock=fixed_clock,
    )
    token_a = svc.issue("user-a", "local")
    token_b = svc.issue("user-b", "local")
    hb_a, pb_a, _sig_a = token_a.split(".")
    _hb_b, _pb_b, sig_b = token_b.split(".")
    # Mische: Header+Payload von A, Signature von B
    frankenstein = f"{hb_a}.{pb_a}.{sig_b}"
    with pytest.raises(InvalidSignatureError):
        svc.verify(frankenstein)


# ---------------------------------------------------------------------------
# Konstruktor-Validierung der neuen Felder
# ---------------------------------------------------------------------------


def test_init_rejects_negative_leeway(facade: CryptoFacade) -> None:
    with pytest.raises(ValueError, match="leeway"):
        TokenService(
            crypto_facade=facade, issuer="x", ttl_seconds=3600,
            exp_leeway_seconds=-1,
        )


def test_init_rejects_empty_allowed_algs(facade: CryptoFacade) -> None:
    with pytest.raises(ValueError, match="allowed_algs"):
        TokenService(
            crypto_facade=facade, issuer="x", ttl_seconds=3600,
            allowed_algs=[],
        )


def test_init_defaults_allowed_algs_to_ml_dsa_65(facade: CryptoFacade) -> None:
    """allowed_algs=None default zu ML-DSA-65 (lowercase comparable)."""
    svc = TokenService(
        crypto_facade=facade, issuer="x", ttl_seconds=3600,
    )
    assert "ml-dsa-65" in svc._allowed_algs_lower
