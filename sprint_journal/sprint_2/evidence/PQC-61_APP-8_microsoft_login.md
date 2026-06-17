# Evidence: PQC-61 APP-8 Microsoft-Login App-Seite

**Story:** PQC-61 APP-8 (5 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

App-Seite Microsoft-Entra-Login via OIDC. Analog PQC-60 APP-7, dank
generischem `loginWithProvider`-Hook fast trivial.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 Wie APP-7, aber Microsoft | OK | `handleMicrosoftLogin -> loginWithProvider("microsoft")` in `login.tsx` |
| AC-2 Tenant-Konfiguration dokumentiert | OK | Single-Tenant via `RIB_IDP_PROVIDERS__MICROSOFT__TENANT_ID` (PQC-84 BRK-0). App-Code tenant-agnostic. JSDoc-Header in login.tsx + dieses Evidence-File. |
| AC-3 Token im AuthContext + Navigation /home | OK | `await login(result.broker_token); router.replace("/home")` |

## In PQC-61 implementiert

**Code-Aenderung minimal dank PQC-60-Vorarbeit:**

- `app/src/app/login.tsx`:
  - Generischer `handleOAuthLogin(provider, label)`-Helper (Refactor aus
    PQC-60 `handleGoogleLogin`).
  - `handleGoogleLogin` + `handleMicrosoftLogin` jetzt One-Liner Closures.
  - Microsoft-Button: `onPress=handleMicrosoftLogin` ersetzt Placeholder.
  - JSDoc-Header erweitert mit Microsoft-Tenant-Konfiguration-Hinweis.
  - Note-Text aktualisiert: beide Provider voll implementiert.

**Keine Aenderung im `oauthClient.ts`** noetig - der Hook ist seit PQC-60
generisch (`ProviderName = "google" | "microsoft"`).

## Tenant-Konfiguration (AC-2)

**Single-Tenant-Setup (Senior-Decision PQC-84 BRK-0):**

- Server-Side: `RIB_IDP_PROVIDERS__MICROSOFT__TENANT_ID=<tenant-id>` in
  `.env`. `MicrosoftProviderConfig.tenant_id` komponiert daraus die
  Discovery-URL und Issuer:
  - `issuer = https://login.microsoftonline.com/<tenant>/v2.0`
  - `discovery_url = .../<tenant>/v2.0/.well-known/openid-configuration`
- App-Side: keine Tenant-Info noetig. App ruft generisches
  `/auth/federated/microsoft/authorize` auf, Server baut Authorize-URL
  mit korrektem Tenant in der Path-Komponente.

**Multi-Tenant moeglich:** `tenant_id="common"` oder
`"organizations"` in Server-Config setzen, alles uebrige aendert sich
nicht.

**Sicherheits-Bonus:** Microsoft-Plugin verifiziert beim ID-Token-Receive
zusaetzlich den `tid`-Claim gegen `tenant_id` (PQC-38 BRK-3). Token aus
anderem Tenant -> `invalid_tenant`-Error. Defense-in-Depth.

## Tests + Verifikation

- `npx tsc --noEmit` zeigt keine TS-Errors in `src/app/login.tsx` (uebrige
  TS-Errors in der Codebase sind pre-existing aus anderen Files, nicht
  von PQC-61)
- Bestehende Backend-Tests unveraendert: 215 passed
- Manuelle Verifikation: Microsoft-Button-Klick triggert exakt denselben
  Flow wie Google-Button, nur mit Provider-Parameter `microsoft`

## AC-Code-Level-Demo (User-Aktion)

Analog PQC-60 ist die **echte Browser-Demo blocked durch F-086**
(redirect_uri Server-Side, App-Side-Return braucht Custom-Scheme).

**Manuelle Server-Demo aktuell moeglich (gleicher Flow wie Google):**

```bash
# 1. Container hochfahren
cd infra && docker compose up -d

# 2. PKCE-Verifier generieren (Python einzeiler)
VERIFIER=$(python -c "import secrets;print(secrets.token_urlsafe(48))")

# 3. Authorize-URL anfordern
curl -s -X POST http://localhost:8000/auth/federated/microsoft/authorize \
  -H "Content-Type: application/json" \
  -d "{\"code_verifier\":\"$VERIFIER\"}" | jq .

# 4. authorize_url im Browser oeffnen, mit Microsoft-Test-Account einloggen
# 5. Aus der Callback-URL code+state kopieren
# 6. Callback POST
curl -s -X POST http://localhost:8000/auth/federated/microsoft/callback \
  -H "Content-Type: application/json" \
  -d "{\"code\":\"<code>\",\"state\":\"<state>\"}" | jq .
```

## Closing-Review-Findings

Keine Must-Fix. Keine neuen Findings - F-086 (OAuth-App-Type-Switch) gilt
weiterhin auch fuer Microsoft.

## Story-Aufwand

- Story-Points: 5
- Tatsaechliche Zeit: tba
- AI-Multiplier-Beobachtung: Story dank generischem oauthClient sehr
  schnell. Aenderung ist im Wesentlichen 1 Button-Handler-Wiring +
  Refactor zu generischem Helper. Bestaetigt das Plugin-Architektur-
  Versprechen auch app-side.

## Sprint-2-Status nach PQC-61

**End-to-End-Sprint-2 funktional komplett:**

| Story | SP | Status |
|---|---|---|
| PQC-84 BRK-0 OAuth-App-Setup | 3 | Done |
| PQC-36 BRK-1 IdP-Registry | 5 | Done |
| PQC-37 BRK-2 OIDC Code Flow PKCE | 8 | Done |
| PQC-38 BRK-3 ID-Token-Verify | 5 | Done |
| PQC-39 BRK-4 Identity-Normalisierung | 5 | Done |
| PQC-40 BRK-5 Google Voll-Demo | 5 | Done |
| PQC-41 BRK-6 Microsoft Voll-Demo | 5 | Done |
| PQC-42 BRK-7 CSRF/State Server-managed | 2 | Done |
| PQC-43 TLS-1 X25519MLKEM768 | 5 | Done |
| PQC-44 TLS-2 PQ-Handshake-Verify | 2 | Done |
| PQC-45 TLS-3 nginx Reverse Proxy | 2 | Done |
| PQC-60 APP-7 Google-Login App | 5 | Done |
| PQC-61 APP-8 Microsoft-Login App | 5 | Done |
| **Sprint-2 Done** | **57 SP** | **gegenueber 62 SP geplant = 92%** |

**Restscope Sprint-2:** keine Must-Stories mehr. F-086 (OAuth-App-Type-Switch
fuer Live-Demo) ist Sprint-3-Polish.

## Folgestories

Sprint-2 ist faktisch fertig. Naechste Schritte:

1. **Sprint-2-Demo** mit User-Aktion (alle Live-Demo-Findings durchziehen
   und Screenshots fuer Bericht sammeln).
2. **Sprint-3 starten** (vermutlich Doku-Polish + Bericht-Vorbereitung +
   F-086 OAuth-App-Type-Switch fuer echte Live-Browser-Demo).
</thinking>
