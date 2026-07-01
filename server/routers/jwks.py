"""JWKS-Endpoint fuer Token-Verifikation (PQC-35 TOK-4).

Story: PQC-35 TOK-4.
Bezug: RFC 7517 (JSON Web Key Set), Design 5.1, draft-ietf-cose-dilithium,
draft-ietf-jose-pqc-akp.

**Endpoint:**

- ``GET /auth/.well-known/jwks.json``: liefert alle ML-DSA-Public-Keys aus
  ``CryptoFacade.verifying_keys_by_kid`` im RFC-7517-JWK-Set-Format.

**JWK-Format (Pre-Standard fuer PQ-Algorithmen):**

.. code-block:: json

    {
      "keys": [
        {
          "kty": "AKP",
          "alg": "ML-DSA-65",
          "kid": "auth-signing-key-v1",
          "use": "sig",
          "x": "<base64url(public-key-bytes)>"
        }
      ]
    }

**Pre-Standard-Hinweis:** ``ML-DSA-65`` ist KEIN offizieller JOSE-IANA-Wert.
Aktuell laeuft die Standardisierung in:

- draft-ietf-cose-dilithium (COSE Algorithms for ML-DSA)
- draft-ietf-jose-pqc-akp (JOSE Algorithm Key Pair fuer PQ-Algorithmen)

``kty=AKP`` (Algorithm Key Pair) ist die aktuell vorgeschlagene Generic-PQ-kty,
``x`` ist der raw-Public-Key-Octet-Wert (base64url, kein Padding). Bei
finaler Standardisierung muss das Format ggf. angepasst werden.

**Cache-Control:** ``max-age=3600`` (1h). JWKS-Konsumenten cachen die Antwort
und refetchen bei Verify-Failure (Force-Refresh-Pattern wie unsere
OidcJwksService aus Sprint 2).
"""

from __future__ import annotations

import base64
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response

from crypto.facade import CryptoFacade

router = APIRouter(prefix="/auth", tags=["jwks"])


def _get_facade(request: Request) -> CryptoFacade:
    return request.app.state.crypto_facade  # type: ignore[no-any-return]


def _b64url_no_pad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


@router.get("/.well-known/jwks.json")
async def get_jwks(
    facade: Annotated[CryptoFacade, Depends(_get_facade)],
    response: Response,
) -> dict[str, list[dict[str, Any]]]:
    """Liefert das JWKS mit allen registrierten Public-Keys.

    Story: PQC-35 TOK-4.

    Returns:
        ``{"keys": [...]}`` mit je einem JWK-Dict pro registriertem Public-Key.
    """
    all_keys = facade.verifying_keys()
    keys_list: list[dict[str, Any]] = []
    for kid in sorted(all_keys):
        public_key_bytes = all_keys[kid]
        keys_list.append(
            {
                "kty": "AKP",
                "alg": "ML-DSA-65",
                "kid": kid,
                "use": "sig",
                "x": _b64url_no_pad(public_key_bytes),
            },
        )
    response.headers["Cache-Control"] = "public, max-age=3600"
    return {"keys": keys_list}
