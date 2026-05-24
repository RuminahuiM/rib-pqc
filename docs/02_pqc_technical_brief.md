# PQC Technical Brief — Implementing Post-Quantum Cryptography in a Python Authentication Service

> Companion document to the Einreichungsformular. Captures the technical landscape (May 2026) and the concrete library/version choices for the project.

---

## 1. The threat model

Two distinct quantum threats matter for TLS:

| Threat | Affects | Algorithm needed |
|---|---|---|
| **Confidentiality break** of recorded TLS sessions ("Harvest Now, Decrypt Later") | Key exchange (ECDHE, RSA-KEX) | **ML-KEM** (FIPS 203) |
| **Authenticity / impersonation** once a CRQC exists | Signatures (ECDSA, RSA, EdDSA) on certs and tokens | **ML-DSA** (FIPS 204) or SLH-DSA (FIPS 205) |

The HNDL threat is **already exploitable today** (anyone can record traffic now, decrypt in 10–20 years), so PQ key exchange is more urgent than PQ authentication. This is the reason the industry has rolled out hybrid PQ KEX years before PQ certs.

## 2. NIST PQC standards (Aug 2024, finalized)

- **FIPS 203 — ML-KEM** (Module-Lattice-Based Key-Encapsulation Mechanism). Replaces ECDH/RSA-KEX. Parameter sets: ML-KEM-512, ML-KEM-768 (recommended default), ML-KEM-1024. Public key 800–1568 B, ciphertext 768–1568 B.
- **FIPS 204 — ML-DSA** (Module-Lattice-Based Digital Signature Algorithm). Replaces ECDSA/RSA. Parameter sets: ML-DSA-44, ML-DSA-65 (recommended default), ML-DSA-87. Signatures **2.4–4.6 KB** — much larger than ECDSA's 64–72 B; relevant for token size.
- **FIPS 205 — SLH-DSA** (Stateless Hash-Based, ex-SPHINCS+). Backup signature scheme. Very large signatures (~7–50 KB) but security based purely on hash-function assumptions.

> Naming caveat: many older docs/libraries still say "Kyber" / "Dilithium". These were the names *before* standardization; ML-KEM ≈ Kyber-Round3 with small tweaks (not bit-for-bit identical), same for ML-DSA ≈ Dilithium. Always check whether a library implements the *standardized* version.

## 3. TLS 1.3 integration status

### Key exchange — **production-grade hybrid is here**

`draft-ietf-tls-ecdhe-mlkem-04` (Feb 2026) defines three hybrid groups for the TLS 1.3 `key_share` extension:

| Group | NamedGroup ID | Components |
|---|---|---|
| **X25519MLKEM768** | `0x11ec` | X25519 + ML-KEM-768 |
| SecP256r1MLKEM768 | (TBD) | NIST P-256 + ML-KEM-768 |
| SecP384r1MLKEM1024 | (TBD) | NIST P-384 + ML-KEM-1024 |

For X25519MLKEM768 specifically: client share 1216 B (1184 ML-KEM + 32 X25519), server share 1120 B; shared secret is the concatenation, 64 B total. The "hybrid" property means a break in *either* X25519 or ML-KEM still leaves the connection secure — important because ML-KEM is young, ECDH is not yet broken.

**Deployed default in:**
- Chrome ≥ 131 (Nov 2024)
- Firefox ≥ 132
- Edge ≥ 131
- OpenSSL 3.5 (April 2025) — `-groups X25519MLKEM768`
- Go 1.24 (Feb 2025) — `crypto/tls` native
- AWS endpoints (rolling out 2025–2026), Cloudflare, Apple

> **Bot-detection note:** PQC support is now a fingerprinting signal. Per scrapfly/F5 Labs, ~57 % of browser TLS traffic in 2026 sends PQ key shares. A scraper without PQC stands out — relevant for the auth service's threat model later.

### Authentication / signatures — **still a draft**

`draft-ietf-tls-mldsa-01` defines three new SignatureScheme code points:
- `mldsa44` (0x0904)
- `mldsa65` (0x0905)
- `mldsa87` (0x0906)

These MUST NOT be used in TLS 1.2 or earlier. **No public CA issues ML-DSA leaf certs at scale yet** (early 2026 rollouts at AWS Private CA, Microsoft ADCS, Cloudflare are limited to test surfaces). For the project this means:

- Server cert stays ECDSA (production-realistic)
- *Optional* parallel demo: a self-signed ML-DSA leaf from our own test CA, verified with `openssl s_client` + a custom trust store

Composite signatures (`draft-reddy-tls-composite-mldsa-09`) — combining ECDSA *and* ML-DSA in one cert — are an ongoing alternative direction; out of scope for this project but worth a footnote in the Bericht.

## 4. Library landscape (May 2026)

### Server side (Python + nginx + OpenSSL)

| Component | Version | Role |
|---|---|---|
| **OpenSSL** | 3.5+ | Provider API, native X25519MLKEM768 group |
| **liboqs** | ≥ 0.14 (Jul 2025) | C library implementing ML-KEM, ML-DSA, SLH-DSA |
| **oqs-provider** | ≥ 0.10 (Jul 2025) | OpenSSL 3 provider that exposes liboqs algorithms to OpenSSL apps (nginx, curl, …) |
| **nginx** | ≥ 1.27 | Reverse proxy / TLS termination |
| **liboqs-python** | latest | Python bindings — useful for in-Python ML-DSA token signing if not using OpenSSL EVP |

Recommended path: **build OpenSSL 3.5 + oqs-provider + nginx in a Docker image** based on `openquantumsafe/oqs-ossl3` to avoid a 2-day yak-shave. Sample stack:

```dockerfile
FROM openquantumsafe/oqs-ossl3:latest
# oqs-ossl3 already has openssl 3.x + oqs-provider configured
RUN apt-get update && apt-get install -y nginx
# nginx_oqs.conf: ssl_ecdh_curve X25519MLKEM768:X25519:secp256r1;
```

**Python in-process options for ML-DSA token signing:**

1. `liboqs-python` — direct bindings, simplest. `from oqs import Signature; sig = Signature("ML-DSA-65")`.
2. `pyca/cryptography` — does **not** ship ML-DSA in 45.x (May 2026). Watch for a future minor release.
3. Call OpenSSL via subprocess — works, but ugly.

Plan: **liboqs-python** for token signing in FastAPI, OpenSSL/oqs-provider for nginx TLS termination.

### Client side (React Native + Expo)

| Library | What it provides | Notes |
|---|---|---|
| **`@noble/post-quantum`** | ML-KEM-{512,768,1024}, ML-DSA-{44,65,87}, SLH-DSA, in pure TS | Audited, dependency-free. Needs a `getRandomValues` polyfill on RN — `react-native-get-random-values` does the job. |
| `react-native-crystals` | Older Kyber768 + Dilithium3 native module | Pre-standardization; **avoid for new work** unless you need native perf. |
| Expo SecureStore | Platform keystore | For storing the device-side ML-KEM keypair, ML-DSA verification key. |

> Important: **RN/Expo does not let you choose TLS cipher suites or KEM groups** — that's controlled by iOS URLSession and Android's BoringSSL/conscrypt fork. As of mid-2026 this means an Expo Go app talking to our nginx will likely use whatever the OS picks (possibly hybrid PQ on recent Android, classical on most iOS). This is *fine* for our architecture: PQC at the TLS layer is a server-side property we verify with browsers/`openssl s_client`; the app does its own PQC at the application layer.

## 5. Architecture for this project

```
┌─────────────────────────┐    TLS 1.3 (X25519MLKEM768)    ┌─────────────────────────┐
│  React Native (Expo)    │ ◄─────────────────────────────► │ nginx + oqs-provider    │
│                         │   (negotiated by OS, opaque)   │  (TLS termination)      │
│  ┌──────────────────┐   │                                │           │             │
│  │ App-layer PQC    │   │   ML-KEM-768 handshake ───────►│           ▼             │
│  │  - @noble/PQ     │   │   AES-GCM body crypto          │  FastAPI (Uvicorn)      │
│  │  - ML-DSA verify │ ◄────── ML-DSA-65 signed token ────│  - liboqs-python        │
│  └──────────────────┘   │                                │  - SQLite/Postgres      │
└─────────────────────────┘                                └─────────────────────────┘
```

### Two PQC layers, on purpose

1. **Transport (TLS) layer — server-side PQC.** nginx negotiates `X25519MLKEM768` with any client that supports it. Verified with `openssl s_client -groups X25519MLKEM768` and Chrome/Firefox dev-tools. *Why:* this is what the rest of the world is rolling out (AWS, Cloudflare, Google).
2. **Application layer — explicit PQC handshake.** The RN app does its own ML-KEM-768 KEM encapsulation against the server's published ML-KEM public key, derives a session key, AES-GCM-encrypts request bodies. Auth tokens are ML-DSA-65 signed (FIPS 204, replaces RS256/ES256 JWT). *Why:* this guarantees end-to-end PQ even when the OS-controlled mobile TLS isn't PQ-aware. It's also the part that's actually in *our* control.

### Auth flow (happy path)

```
1. Client → POST /auth/register
     body: { username, password, ml_kem_pub }
   Server stores: argon2id(password), ml_kem_pub
   Server returns: { ml_dsa_pub_pem }   # the server's ML-DSA-65 verification key

2. Client → POST /auth/login
     body: { username, password }
   Server: verifies password via argon2id
   Server: builds token JSON { sub, iat, exp, nonce }
   Server: signs token with ML-DSA-65 → b64(sig) appended
   Server returns: { token, sig }

3. Client → POST /session/init
     body: { kem_ct }   # ML-KEM ciphertext encapsulated to server's KEM pub
   Server: ML-KEM decapsulate → session_key (32 B)
   Server: stores (session_id → session_key) for ~15 min

4. Client → GET /me
     headers: Authorization: PQ <token>.<sig>, X-Session: <session_id>
     body: AES-GCM(session_key, plaintext)  # if there is one
   Server: verifies ML-DSA sig on token, looks up session_key, decrypts body
   Server: AES-GCM-encrypts response with same session_key
```

This is a deliberate simplification of a real PAKE/Noise protocol — we're learning, not shipping a product.

## 6. Risks specific to the technical stack

| # | Technical risk | Mitigation |
|---|---|---|
| T1 | `oqs-provider` ABI breakage between liboqs 0.13 → 0.14 → ... | Pin exact versions in Dockerfile; document in README. |
| T2 | RN bundler trips on `@noble/post-quantum` (CommonJS vs. ESM) | Use Expo SDK 51+ (Hermes); test in Sprint 0 spike. |
| T3 | iOS App Transport Security blocks self-signed test cert | Use Expo's `NSAllowsArbitraryLoadsForURLs` for the dev domain; document; production scope is out anyway. |
| T4 | ML-DSA-65 signatures (~3.3 KB) make `Authorization` header too big for some intermediaries | Send `{token, sig}` in JSON body instead of header for non-bearer endpoints; document. |
| T5 | Lack of FIPS 140-3 module for liboqs (it's not validated yet, May 2026) | Note in Bericht: this project demonstrates *standardized algorithms*, not FIPS-validated *implementations*. Production-ready validation is a separate problem. |

## 7. References (verifiable URLs)

- NIST CSRC PQC: https://csrc.nist.gov/projects/post-quantum-cryptography
- FIPS 203 (ML-KEM): https://csrc.nist.gov/pubs/fips/203/final
- FIPS 204 (ML-DSA): https://csrc.nist.gov/pubs/fips/204/final
- IETF hybrid KEX draft: https://datatracker.ietf.org/doc/draft-ietf-tls-ecdhe-mlkem/
- IETF ML-DSA in TLS draft: https://datatracker.ietf.org/doc/draft-ietf-tls-mldsa/
- liboqs: https://github.com/open-quantum-safe/liboqs
- oqs-provider: https://github.com/open-quantum-safe/oqs-provider
- liboqs-python: https://github.com/open-quantum-safe/liboqs-python
- @noble/post-quantum: https://github.com/paulmillr/noble-post-quantum
- Cloudflare PQC docs: https://developers.cloudflare.com/ssl/post-quantum-cryptography/
- F5 Labs "State of PQC on the Web": https://www.f5.com/labs/articles/the-state-of-pqc-on-the-web

---
*Last updated: 2026-05-03*
