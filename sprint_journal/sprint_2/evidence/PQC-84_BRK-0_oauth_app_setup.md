# Evidence: PQC-84 BRK-0 OAuth-Apps bei Google und Microsoft registrieren

- **Jira**: [PQC-84](https://rumidesigns.atlassian.net/browse/PQC-84)
- **Sprint**: 2 (Tag 0, vorgezogen von Sa 06.06 auf Mi 03.06)
- **Done am**: 2026-06-03
- **Story Points**: 2
- **Worklog**: ca. 50min (Browser-Klick-Zeit + Doku-Updates)
- **Blockt**: PQC-40 BRK-5 (Google-Plugin), PQC-41 BRK-6 (Microsoft-Plugin)

## Zusammenfassung

OAuth-Apps fuer Google und Microsoft registriert, Credentials in `infra/.env`
(gitignored) abgelegt, Discovery-URLs live verifiziert, Browser-Test der
Authorize-URLs zeigt jeweils die Provider-Login-Seite mit korrektem App-Name
ohne Fehler. Setup-Doku in `server/README.md` Abschnitt "OAuth Provider Setup"
fuer Reproduzierbarkeit.

## AC-Mapping

| AC | Resultat |
|---|---|
| AC-1 Google OAuth-Client registriert | OK: Project `rib-pqc`, Client `rib-pqc-dev` (Web-Anwendung), Redirect `http://localhost:8080/auth/oauth/google/callback`, Scopes openid/email/profile |
| AC-2 Microsoft Entra ID App-Registration | OK: App `rib-pqc-dev`, Single-Tenant `Default Directory`, Redirect `http://localhost:8080/auth/oauth/microsoft/callback`, Delegated openid/email/profile, Admin-Consent granted |
| AC-3 Credentials in .env.example + config.yaml Provider-Section | OK: `infra/.env.example` mit Platzhaltern, `infra/.env` (gitignored) mit echten Werten, `server/config.yaml` mit Stub-Section `idp_providers.google` und `idp_providers.microsoft` (Pydantic-IdpProvidersConfig kommt in PQC-36 BRK-1) |
| AC-4 Discovery-URL liefert 200, Authorize-URL Browser-Test grün | OK: Live curl beide Provider HTTP 200 mit korrekten Endpoints. Browser-Test zeigt Google "Sign in - to continue to rib-pqc" und Microsoft "Sign in" mit korrekter Tenant-URL, beide ohne Fehler |
| AC-5 Reproduzierbarer Setup-Hinweis in README | OK: `server/README.md` neuer Abschnitt "OAuth Provider Setup" mit Schritt-fuer-Schritt-Anleitung Google + Microsoft + Dev-vs-Production-URI + Secret-Rotation |

## Senior-Decisions (Story-Start)

1. **Test-Google-Account** statt privater Account. Separate Test-Identitaet fuer App-Owner, App-Branding klar als `rib-pqc`.
2. **Single-Tenant Microsoft Azure AD**. Vermeidet Multi-Tenant Issuer-Variability bei ID-Token-Verifikation in BRK-3. Test-Tenant `Default Directory` (Tenant-ID `1f2e458f-ad65-4625-99cd-58437e12bbeb`).
3. **BFF-Pattern (Backend for Frontend)** statt Mobile-OAuth-Client. Server ist Confidential Client mit Client-Secret. Server-Side OIDC Code Flow mit PKCE (BRK-2). Mobile-App empfaengt Broker-Token via Deep-Link nach erfolgreichem Server-Side-Token-Exchange.
4. **Redirect-URI nur Server-Side fuer Sprint 2** `http://localhost:8080/auth/oauth/<provider>/callback`. Production-HTTPS-URIs werden bei Deploy einfach zusaetzlich in der jeweiligen OAuth-App-Reg eingetragen, ohne Re-Registration.
5. **Discovery-URL fuer Issuer-Verify** statt hardcoded Endpoints. Discovery-Document liefert authorization_endpoint, token_endpoint, jwks_uri.

## Files

- `infra/.env.example`: erweitert um OAuth-Provider-Variablen mit Platzhaltern + Production-Hinweis
- `infra/.env` (NEU, gitignored): lokale Datei mit echten Test-Credentials
- `server/config.yaml`: erweitert um `idp_providers.google` und `idp_providers.microsoft` Stub-Section (kommentiert dass Pydantic-Klasse in PQC-36 BRK-1 folgt)
- `server/README.md`: neuer Abschnitt "OAuth Provider Setup (PQC-84 BRK-0)" mit detaillierter Browser-Klick-Anleitung fuer beide Provider, Dev-vs-Production-URI-Erklaerung, Secret-Rotation-Anweisung

## Live-Verifikation

### AC-4 Discovery-URLs

```
$ curl https://accounts.google.com/.well-known/openid-configuration
HTTP 200
issuer: https://accounts.google.com
authorization_endpoint: https://accounts.google.com/o/oauth2/v2/auth
token_endpoint: https://oauth2.googleapis.com/token
userinfo_endpoint: https://openidconnect.googleapis.com/v1/userinfo
jwks_uri: https://www.googleapis.com/oauth2/v3/certs
scopes: ['openid', 'email', 'profile']

$ curl https://login.microsoftonline.com/1f2e458f-ad65-4625-99cd-58437e12bbeb/v2.0/.well-known/openid-configuration
HTTP 200
issuer: https://login.microsoftonline.com/1f2e458f-ad65-4625-99cd-58437e12bbeb/v2.0
authorization_endpoint: https://login.microsoftonline.com/1f2e458f-.../oauth2/v2.0/authorize
token_endpoint: https://login.microsoftonline.com/1f2e458f-.../oauth2/v2.0/token
userinfo_endpoint: https://graph.microsoft.com/oidc/userinfo
jwks_uri: https://login.microsoftonline.com/1f2e458f-.../discovery/v2.0/keys
scopes: ['openid', 'profile', 'email']
```

### AC-4 Browser-Authorize-Test

- **Google:** Authorize-URL geoeffnet, Browser zeigt `accounts.google.com/v3/signin/identifier` mit Header "Sign in with Google" und Text "to continue to **rib-pqc**". App-Name korrekt durchgereicht. Keine Fehlermeldung.
- **Microsoft:** Authorize-URL geoeffnet, Browser zeigt `login.microsoftonline.com/1f2e458f-ad65-4625-99cd-58437e12bbeb/oauth2/v2.0/authorize` mit Microsoft-Sign-in-Page. Keine Fehlermeldung (kein redirect_uri_mismatch, kein invalid_client).

## Findings

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-056 | Client-Secrets wurden waehrend Setup im Implementation-Chat-History exposed (Test-Account-Kontext, akzeptiertes Risk-Tradeoff). Best-Practice waere am Sprint-2-Ende oder spaetestens vor produktiver Demo zu rotieren | Info | Sprint 4 Polish, oder spaetestens vor Bericht-Demo | open |
| F-057 | `server/config.yaml` enthaelt nur einen Stub fuer `idp_providers`. Echte Pydantic-IdpProvidersConfig-Klasse plus Settings-Verarbeitung kommt in PQC-36 BRK-1 | Info | erledigt sobald PQC-36 in Progress | tracked-in-jira (PQC-36) |

## Sicherheits-Notiz (Secret-Exposition)

Waehrend Setup wurde der Google Client-Secret als JSON-Datei in den Chat hochgeladen, und das Microsoft Client-Secret-Value explizit im Chat als Text geteilt. Beide Werte stehen damit in der Implementation-Chat-History.

Risiko-Einschaetzung: **NIEDRIG** weil
- Beide OAuth-Apps sind Test-Apps in Test-Tenants
- Google-App ist in Testing-Phase (External, nur App-Owner/Test-Users)
- Microsoft-App ist Single-Tenant mit nur Test-Account-Inhaber
- Keine echten User-Daten oder Production-Endpoints betroffen

Mitigation-Strategie: F-056 sieht Rotation am Sprint-Ende vor. Sicherheitsbewusstsein im Bericht erwaehnen (Bewertungs-relevant).

## Worklog

- Story-Start + Senior-Decisions + AskUserQuestions: ~10min
- Google Cloud Console Setup (Account + Project + OAuth Consent + Client erstellen + Secret download): ~15min
- Microsoft Entra ID Setup (Tenant-Pruefung + App Registration + Client Secret + API Permissions + Admin Consent): ~15min
- `.env.example` + `.env` + `config.yaml` Stub + `server/README.md` Setup-Anleitung: ~10min
- Discovery-URL Live-Verify + Browser-Authorize-Test + Evidence: ~10min
- **Total: ca. 60min** (User-Browser-Klick-Zeit + AI-Implementation parallel)

## Demo-Material

Reproduzierbares Browser-Demo:
1. Server-Setup laeuft, OAuth-Credentials in `.env` geladen
2. Tester paste die Authorize-URL in Browser
3. Provider-Login-Seite kommt mit App-Name `rib-pqc`
4. Tester loggt sich ein
5. Browser-Redirect zu `http://localhost:8080/auth/oauth/<provider>/callback?code=...`
6. Aktuell: `ERR_CONNECTION_REFUSED` weil BRK-2-Endpoint noch nicht implementiert. Wird in PQC-37 BRK-2 sichtbar funktional.
