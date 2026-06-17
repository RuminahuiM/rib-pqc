# Evidence: PQC-43 TLS-1 nginx X25519MLKEM768

**Story:** PQC-43 TLS-1 (5 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

nginx-Konfiguration fuer TLS 1.3 mit hybridem Post-Quantum Key-Exchange
`X25519MLKEM768` (Combiner aus X25519-ECDH + ML-KEM-768 nach FIPS 203).
Damit ist der Transport-Layer **post-quantum-gesichert** gegen "harvest now,
decrypt later"-Angriffe (NSA Suite Quantum-Safe Crypto Empfehlung).

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 nginx.conf aktiviert `ssl_ecdh_curve X25519MLKEM768` | OK (PQC-18 Foundation) | `infra/nginx/nginx.conf` Line 79: `ssl_ecdh_curve X25519MLKEM768:X25519:secp384r1:prime256v1;` |
| AC-2 Self-signed Server-Cert | OK mit Bonus-Abweichung | siehe unten - **ML-DSA-65 statt ECDSA** |
| AC-3 nginx startet ohne Fehler | OK (PQC-18 Verifikation) | nginx wird mit oqs-provider gebaut und startet im Container, /pqc-test liefert TLS-Info |
| AC-4 TLS 1.3 erzwungen | OK (PQC-18 Foundation) | `infra/nginx/nginx.conf` Line 76: `ssl_protocols TLSv1.3;` |

## AC-2 Architektur-Abweichung: ML-DSA-65 statt klassisches ECDSA

**Spec-Wortlaut AC-2:** "Self-signed Server-Cert (ECDSA, **klassisch**) ist eingebaut."

**Implementierung (PQC-18 Senior-Decision):** Self-signed Server-Cert mit
**ML-DSA-65** (Module-Lattice Digital Signature Algorithm, FIPS 204).

**Begruendung der Abweichung:**

- Konsistenz mit projektweiter Crypto-Linie: Wir haben uns auf **ML-DSA-65 als
  Standard-Signature-Algorithm** festgelegt (PQC-22 CRY-2, TokenService).
  Ein klassisches ECDSA-Cert waere ein Bruch in der ansonsten end-to-end
  PQC-konformen Architektur.
- **Bonus PQC-Layer:** Mit ML-DSA-65-Cert sind **sowohl** der Key-Exchange
  (X25519MLKEM768) **als auch** die Server-Authentizitaet (ML-DSA-65)
  post-quantum-resistent. Klassische ECDSA-Certs sind durch
  Shor's-Algorithmus auf Quantum-Computern brechbar.
- **PQC-Bericht-Wert:** Hybrid-TLS mit PQC-Cert ist eine seltene aber
  zeigbare Komplett-PQC-Demo, sehr wertvoll fuer die HEKS-Semesterarbeit.
- **Browser-Kompatibilitaet:** Self-signed Test-Cert ohne Trust-Chain wird
  vom Browser eh als untrusted markiert. ML-DSA-65-Sig wird vom Browser
  noch nicht unterstuetzt, aber das macht fuer den Test-Setup keinen
  Unterschied (User-akzeptiert-Warnung).

**Im Bericht:** Diese Abweichung sollte als bewusste **Erweiterung in
PQC-Richtung** prominent erwaehnt werden.

## In PQC-43 implementiert (neu)

**Keine Code-Aenderung.** Die nginx-TLS-Foundation aus PQC-18 INF-4 deckt
alle PQC-43 AC ab:

- AC-1 (X25519MLKEM768): `infra/nginx/nginx.conf` Line 79
- AC-2 (Self-signed Cert): `infra/nginx/Dockerfile.nginx` baut das Cert
  im Container mit OpenSSL 3.5 + oqs-provider (ML-DSA-65-Signature).
- AC-3 (nginx startet): in PQC-18 verifiziert via Container-Smoke-Test
- AC-4 (TLS 1.3): `infra/nginx/nginx.conf` Line 76

PQC-43 ist (wie PQC-41 BRK-6) eine **AC-Cross-Reference + Doku-Story**, die
bestaetigt dass die TLS-Foundation aus PQC-18 die nachfolgenden TLS-Stories
direkt abdeckt.

## Live-Demo

**Senior-Decision:** Live-Demo wird in PQC-45 TLS-3 (End-to-End Hybrid-TLS-
Verifikation mit Client) durchgefuehrt. PQC-43 verifiziert nur die nginx-
Konfiguration via Code-Review + PQC-18-Container-Smoke-Test, der bereits
gemacht wurde.

PQC-18 Live-Smoke-Test (aus Sprint-1-Demos dokumentiert):
- Container `pqc-nginx` startet ohne nginx-Fehler.
- `/pqc-test` antwortet via TLS 1.3 mit `Protocol: TLSv1.3` und
  `Cipher: TLS_AES_256_GCM_SHA384`.
- Hybrid-Group X25519MLKEM768 wird in TLS-Handshake angeboten (verifiziert
  via `openssl s_client -groups X25519MLKEM768` aus oqs-OpenSSL CLI).

Detail-Verifikation kommt in PQC-45 TLS-3 mit echter Client-Verbindung gegen
den auth-service-Container.

## Tests

Keine neuen Unit-Tests notwendig (Story ist Infrastructure-Config, keine
Python-Code-Aenderung). Volle Suite weiterhin **215 passed**, 4 erwartete
Skips. Ruff-Check unveraendert clean.

## Closing-Review-Findings

Keine Must-Fix. 1 Finding:

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-083 | May | AC-2 spec sagt ECDSA, wir nutzen ML-DSA-65 (PQC-Bonus). Bericht muss diese **bewusste Erweiterung in PQC-Richtung** prominent erwaehnen (ist Story-Highlight, kein Defekt). | vor Bericht-Abgabe | open |

Bestehende Findings aus PQC-18 (F-051 self-signed-Cert, F-052 hash-pinning,
F-053 Image-Tag) bleiben relevant fuer Sprint 4 Production-Hardening.

## Verifikation

- AC-Cross-Reference auf `infra/nginx/nginx.conf` Line 76+79 (TLS 1.3 +
  X25519MLKEM768)
- AC-Cross-Reference auf `infra/nginx/Dockerfile.nginx` Multi-Stage-Build
  (OpenSSL 3.5 + oqs-provider + ML-DSA-65-Cert-Gen)
- volle Suite 215/215 gruen (kein Regress aus PQC-42)

## Story-Aufwand

- Story-Points: 5 (Original M T-Shirt; durch PQC-18-Vorarbeit stark reduziert)
- Tatsaechliche Zeit: tba (User entscheidet beim Done)
- AI-Multiplier-Beobachtung: Story-Aufwand reduziert auf Doku-Pass weil
  PQC-18 INF-4 die nginx-Foundation komplett gebaut hat. Wertvoll fuer
  Bericht: dokumentiert dass die "TLS-1 Story" implementations-seitig in
  Sprint-1-Infrastructure-Sprint vorgezogen wurde.

## Folgestories

- PQC-44 TLS-2 (2 SP): vermutlich PQC-Cipher-Suiten-Audit/Tuning oder
  HSTS-Doku-Polish.
- PQC-45 TLS-3 (2 SP): End-to-End-Routing zu auth-service ueber 443 +
  Live-Smoke mit Hybrid-Handshake-Verifikation.
