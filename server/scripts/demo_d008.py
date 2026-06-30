"""End-to-End Mini-Demo D-008: PQ-Session + Encrypted /api/profile.

Story-Anker: PQC-46 SES-1, PQC-47 SES-2, PQC-48 SES-3, PQC-49 SES-4,
PQC-50 DCH-1, PQC-51 DCH-2, PQC-52 DCH-3, PQC-53 DCH-4.

Was die Demo zeigt:

1. Login mit Demo-User -> Broker-Token (ML-DSA-65 signiert).
2. ML-KEM-768 Keypair-Generierung Client-Side.
3. POST /session/init -> Server-Encapsulation, session_id + ciphertext zurueck.
4. KEM-Decaps + HKDF -> Session-Key (32 Byte AES-256-GCM-Key) Client-Side.
5. AES-256-GCM Encrypt eines Profile-Request-Payloads (leeres dict `{}`).
6. POST /api/profile mit X-Session-Id + X-Nonce + raw octet-stream Body.
7. Decrypt der Server-Response (X-Nonce-Header + verschluesselter Body).
8. Replay-Test: zweiter Request mit gleicher Nonce -> 400 nonce_reused.

**Voraussetzungen:**

- Server lauft (docker compose up). Default-URL http://localhost:8080.
- Demo-User existiert. Anlegen mit:
  ``docker compose exec auth-service python -m admin create-user
    --email demo@example.com --password demo-passwort-12345``
- liboqs (oqs Python-Bindings) installiert. Im Container vorhanden.

**Lokale Ausfuehrung (im Container):**

::

    docker compose exec auth-service python /app/scripts/demo_d008.py

**Output-Konvention:**

Jeder Schritt printet:
- Header-Zeile mit Schritt-Nummer + Titel
- Wichtige Inputs (truncated bei Bytes)
- Wichtige Outputs (truncated bei Bytes)
- Status (OK / FAIL)
"""

from __future__ import annotations

import base64
import json
import os
import secrets
import sys
from typing import Any

import httpx

# liboqs ist nur im Container/lokal verfuegbar; nicht in der Sandbox.
try:
    import oqs  # type: ignore
except ImportError as exc:
    print(f"ERROR: oqs (liboqs-python) ist nicht installiert: {exc}", file=sys.stderr)
    print("Diese Demo laeuft nur im rib-pqc-auth-service Container.", file=sys.stderr)
    sys.exit(1)

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

BASE_URL = os.environ.get("DEMO_BASE_URL", "http://localhost:8080")
DEMO_EMAIL = os.environ.get("DEMO_EMAIL", "demo@example.com")
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "demo-passwort-12345")
KEM_ALG = "ML-KEM-768"
HKDF_INFO = b"app-session-v1"


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    pad = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + pad)


def _hex_preview(data: bytes, limit: int = 16) -> str:
    head = data[:limit].hex()
    return f"{head}... ({len(data)} bytes)" if len(data) > limit else f"{head} ({len(data)} bytes)"


def _section(num: int, title: str) -> None:
    print()
    print(f"=== Schritt {num}: {title} ===")


def main() -> int:
    print(f"Demo D-008: End-to-End-Roundtrip gegen {BASE_URL}")
    print(f"Demo-User: {DEMO_EMAIL}")
    print(f"KEM: {KEM_ALG}, AEAD: AES-256-GCM, KDF: HKDF-SHA256")

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        # 1. Login -> Broker-Token
        _section(1, "Login -> Broker-Token")
        resp = client.post(
            "/auth/local/login",
            json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
        )
        if resp.status_code != 200:
            print(f"FAIL Login: HTTP {resp.status_code} {resp.text}")
            return 1
        token = resp.json()["access_token"]
        print(f"Token preview: {token[:40]}... ({len(token)} chars)")
        print("Status: OK")

        # 2. ML-KEM-768 Keypair Client-Side
        _section(2, "ML-KEM-768 Keypair Client-Side")
        with oqs.KeyEncapsulation(KEM_ALG) as kem:
            client_pk = kem.generate_keypair()
            client_sk = kem.export_secret_key()
            print(f"client_pk: {_hex_preview(client_pk)}")
            print(f"client_sk: {_hex_preview(client_sk)} (NEVER print outside demo)")

            # 3. POST /session/init
            _section(3, "POST /session/init -> session_id + ciphertext")
            resp = client.post(
                "/session/init",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "kem_alg": KEM_ALG,
                    "encapsulation_key": _b64url(client_pk),
                },
            )
            if resp.status_code != 200:
                print(f"FAIL session/init: HTTP {resp.status_code} {resp.text}")
                return 1
            session_data = resp.json()
            session_id = session_data["session_id"]
            ciphertext_b64 = session_data["ciphertext"]
            expires_in = session_data["expires_in"]
            ciphertext_bytes = _b64url_decode(ciphertext_b64)
            print(f"session_id: {session_id} ({len(session_id)} chars)")
            print(f"ciphertext: {_hex_preview(ciphertext_bytes)}")
            print(f"expires_in: {expires_in}s")
            print("Status: OK")

            # 4. KEM-Decaps + HKDF (Client-Side)
            _section(4, "KEM-Decaps + HKDF-Session-Key")
            shared_secret = kem.decap_secret(ciphertext_bytes)
        # kem context closes hier, session_key bleibt erhalten.
        print(f"shared_secret: {_hex_preview(shared_secret)}")
        # HKDF-SHA256 mit session_id ASCII-Bytes als Salt.
        session_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=session_id.encode("ascii"),
            info=HKDF_INFO,
        ).derive(shared_secret)
        print(f"session_key: {_hex_preview(session_key)} (32 byte AES-256-GCM-Key)")
        print("Status: OK")

        # 5. AES-256-GCM Encrypt Profile-Request
        _section(5, "Encrypt Profile-Request mit AES-256-GCM")
        aad = session_id.encode("ascii")
        request_nonce = secrets.token_bytes(12)
        request_plaintext = json.dumps({}).encode("utf-8")
        cipher = AESGCM(session_key)
        request_body = cipher.encrypt(request_nonce, request_plaintext, aad)
        print(f"plaintext: {request_plaintext!r}")
        print(f"X-Nonce: {_b64url(request_nonce)}")
        print(f"X-Session-Id: {session_id}")
        print(f"body (ct||tag): {_hex_preview(request_body)}")
        print("Status: OK")

        # 6. POST /api/profile
        _section(6, "POST /api/profile")
        resp = client.post(
            "/api/profile",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64url(request_nonce),
                "Content-Type": "application/octet-stream",
            },
            content=request_body,
        )
        if resp.status_code != 200:
            print(f"FAIL /api/profile: HTTP {resp.status_code} {resp.text}")
            return 1
        print(f"HTTP {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('content-type')}")
        response_nonce_b64 = resp.headers["x-nonce"]
        print(f"X-Nonce (response): {response_nonce_b64}")
        print(f"response body: {_hex_preview(resp.content)}")
        print("Status: OK")

        # 7. Decrypt Response
        _section(7, "Decrypt Response + Profile-Plaintext")
        response_nonce = _b64url_decode(response_nonce_b64)
        response_plaintext = cipher.decrypt(response_nonce, resp.content, aad)
        profile: dict[str, Any] = json.loads(response_plaintext.decode("utf-8"))
        print(f"profile (Klartext): {json.dumps(profile, indent=2)}")
        print("Status: OK")

        # 8. Replay-Test
        _section(8, "Replay-Test - gleiche Nonce nochmal -> 400 nonce_reused")
        replay_resp = client.post(
            "/api/profile",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64url(request_nonce),  # gleiche Nonce!
                "Content-Type": "application/octet-stream",
            },
            content=request_body,
        )
        print(f"HTTP {replay_resp.status_code}")
        print(f"body: {replay_resp.text}")
        if replay_resp.status_code == 400 and replay_resp.json() == {
            "detail": {"error": "nonce_reused"},
        }:
            print("Status: OK (Replay korrekt erkannt)")
        else:
            print("Status: FAIL (Replay-Schutz hat nicht gegriffen)")
            return 1

    print()
    print("=== DEMO D-008 KOMPLETT ===")
    print("Alle 8 Schritte erfolgreich. Encrypted Channel funktioniert E2E.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
