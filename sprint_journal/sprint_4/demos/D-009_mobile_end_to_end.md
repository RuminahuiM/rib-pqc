# Demo D-009: Mobile End-to-End (Login bis entschluesseltes Profil auf dem iPhone)

**Status:** Erfolgreich durchgefuehrt, live gezeigt am Kolloquium (08.07.2026, 08:30).
**Bezug:** PQC-55 APP-2, PQC-56 APP-3, PQC-58 APP-5, PQC-59 APP-6 (Sprint-4-Carry-Over-Rush), aufbauend auf D-008 (Server-Pfad).
**Datum:** 2026-07-08.
**Trigger:** Sprint-Goal-Meilenstein Mobile-Pfad plus Kolloquium-Live-Demo.

## Was wird demonstriert

Die komplette Kette aus D-008, diesmal mit der echten Expo-App auf dem
iPhone statt einem Client-Script. Beide PQ-Schichten aktiv:

- **Application-Layer-PQ:** ML-KEM-768-Session via `@noble/post-quantum`
  in der App, AES-256-GCM-verschluesselter `/api/profile`-Call.
- **Transport-Layer:** klassisches TLS zwischen iPhone und Server
  (R-T08: iOS-System-TLS unterstuetzt X25519MLKEM768 noch nicht),
  PQ-TLS separat via Browser/openssl nachgewiesen (D-005/D-007).

Ablauf in der App:

1. Expo Go oeffnen, QR aus dem Metro-Terminal scannen, App laedt.
2. Login mit `demo@example.com` (lokaler Flow, ML-DSA-65-Broker-Token).
3. Home-Screen: Status-Karte sichtbar, Kanal-Indikator amber (noch keine Session).
4. Profil oeffnen: App etabliert PQ-Session (ML-KEM-768 KeyGen, POST
   /session/init, Decaps plus HKDF via SessionContext/secureClient).
5. Profil-Daten erscheinen: Response wurde AES-256-GCM-verschluesselt
   uebertragen und in der App entschluesselt.
6. Zurueck auf Home: Kanal-Indikator gruen mit "ML-KEM-768" plus Session-ID.

## Voraussetzungen und Befehlsfolge

Identisch mit dem Kolloquiums-Runbook (`praesentation/Runbook_Demo.md`),
Kurzfassung:

```bash
# 1. Server-Stack
cd infra
docker compose up -d
docker compose ps        # redis healthy, auth-service healthy, nginx up

# 2. Demo-User pruefen
docker compose exec auth-service python -m admin list-users

# 3. Metro / Expo
cd ../app
npx expo start -c        # QR mit Expo Go auf dem iPhone scannen
```

App und Server muessen im selben Netz sein (iPhone-Hotspot, IP in
`app/.env`, danach Metro mit `-c` neu starten).

## Erwartete Outputs

- Login liefert Broker-Token (Home-Screen erreichbar).
- Erster Profil-Aufruf: `POST /session/init` im Server-Log, danach
  `POST /api/profile` mit `X-Session-Id`/`X-Nonce`-Headern.
- Profil-JSON wird in der App angezeigt (entschluesselt).
- Kanal-Status gruen: `ML-KEM-768` plus Session-ID sichtbar.

## Verifikation

- Automatisiert abgesichert durch den End-to-End-Integration-Test
  (PQC-67 QUA-5, `server/tests/test_integration_e2e_flow.py`): exakt
  dieselbe Kette inklusive Replay- und Isolation-Negativfaellen,
  420 Tests gruen im Container-Run vom 07.07.2026.
- Live-Durchlauf am Kolloquium 08.07.2026 erfolgreich.
