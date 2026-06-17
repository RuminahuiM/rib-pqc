# Evidence: PQC-60 APP-7 Google-Login App-Seite

**Story:** PQC-60 APP-7 (5 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

App-Seite implementiert den OIDC-Login-Flow mit Google via `loginWithProvider`
gegen unseren Auth-Service. End-to-End-Code da, Live-Demo deferred wegen
redirect_uri-Architektur (siehe F-086).

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 Tap auf Google-Button oeffnet System-Browser-Tab mit Google /authorize | Code OK | `app/src/app/login.tsx` `handleGoogleLogin` -> `loginWithProvider("google")` -> `WebBrowser.openAuthSessionAsync(authorize_url, returnUrl)` |
| AC-2 PKCE code_verifier + code_challenge korrekt generiert | OK | `generatePkceVerifier()` via `expo-crypto.getRandomBytesAsync(48)` + urlsafe-base64. Server berechnet challenge = S256(verifier) (PQC-42 BRK-7). |
| AC-3 State-Parameter >= 128 bit Entropie | OK (server-generated 256 bit) | Server `secrets.token_urlsafe(32)` = 256 bit (PQC-37 BRK-2). App echoed state aus Authorize-Response zurueck im Callback. |
| AC-4 App POSTet code+verifier an /callback | Erweitert: nur `{code, state}` (BRK-7 BFF) | App POSTet `{code, state}` an Callback. Server liest verifier aus Redis-Eintrag. |
| AC-5 Token in AuthContext + Navigation /home | OK | `await login(result.broker_token); router.replace("/home")` |

## In PQC-60 implementiert

**Neue Files:**

- `app/src/lib/oauthClient.ts` (~169 Zeilen TypeScript): 
  - `generatePkceVerifier()` via expo-crypto.getRandomBytesAsync + urlsafe-base64
  - `loginWithProvider(provider)`: orchestriert den 3-Step-Flow
    (POST /authorize, openAuthSessionAsync, POST /callback)
  - `OAuthError` mit `reason`-Property fuer differenzierte Fehler

**Aenderungen:**

- `app/src/app/login.tsx`: `handleOAuthPlaceholder("Google")` ersetzt durch
  `handleGoogleLogin()` mit echtem Flow. Microsoft bleibt Placeholder
  fuer PQC-61. JSdoc-Header aktualisiert mit F-086-Hinweis.
- `app/package.json`: `expo-crypto ~15.0.7` zu deps.

**Architektur-Abweichung von AC-4 (begruendet):**

AC-4 sagt App sendet `{code, code_verifier}` an Callback. Mit unserem
**BRK-7 Server-managed PKCE** Refactor (PQC-42) sendet App nur noch
`{code, state}`. Server liest code_verifier aus Redis. Vorteile dieser
Abweichung sind in PQC-42 Evidence + F-081 dokumentiert. App-Code ist
einfacher (kein verifier-State im App-Memory ueber Browser-Roundtrip).

## Live-Demo (User-Aufgabe, F-086)

**Limitation:** Aktuelle Google-OAuth-App (PQC-84) ist als **Web Application Type**
registriert mit `redirect_uri = http://localhost:8000/auth/google/callback`
(BFF-Server-Side). Mobile-App-Flow braucht **iOS Application Type** + Custom-
Scheme-redirect_uri (z.B. `app://oauth/google/callback`) damit der System-
Browser zurueck zur App kommen kann.

**Aktueller Effekt beim Live-Test:** User tappt Google-Button, App oeffnet
Browser, User loggt sich bei Google ein, Google redirect zu `localhost:8000`.
Da App auf einem Geraet laeuft (nicht auf dem Container-Host), kann der
Browser-Redirect die App nicht erreichen. `WebBrowser.openAuthSessionAsync`
loest mit `type=cancel` aus.

**Loesungsweg (Sprint 3):**

1. Neue Google-OAuth-App in der Cloud Console registrieren mit Type "iOS"
2. App-Bundle-ID + Custom-Scheme (`app://`) registrieren
3. Server-Config um zweites Provider-Profil ergaenzen (optional
   `idp_providers.google_mobile`) oder bestehende `redirect_uri` anpassen
4. Live-Browser-Demo durchfuehren + Screenshots in Bericht

## AC-Code-Tests (Sandbox)

- TypeScript-Imports: `loginWithProvider`, `OAuthError`, `generatePkceVerifier`
  resolven korrekt
- `npx tsc --noEmit` zeigt keine TS-Errors in `src/lib/oauthClient.ts` oder
  `src/app/login.tsx` (uebrige TS-Errors in der Codebase sind pre-existing
  aus anderen Files, nicht von PQC-60)
- Backend-Tests unveraendert: 215 passed (kein Server-Code-Change in PQC-60)

## Closing-Review-Findings

Keine Must-Fix. 1 Finding:

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-086 | Should | Live-Browser-Demo blocked wegen Google-OAuth-App-Type (Web statt iOS). Sprint-3-Action: neue OAuth-App-Registrierung mit Custom-Scheme-redirect_uri. AC-Code von PQC-60 funktional komplett, Live-Demo erst nach OAuth-App-Type-Switch moeglich. | Sprint 3 (vor Bericht-Demo) | open (User-Action + Server-Config-Update) |

## Story-Aufwand

- Story-Points: 5
- Tatsaechliche Zeit: tba
- AI-Multiplier-Beobachtung: Saubere Trennung von App-Code (komplett
  implementierbar) vs OAuth-App-Type-Registrierung (User-Aktion). Code-
  Teil reduziert sich auf ~170 Zeilen TypeScript + Login-Screen-Update.

## Folgestories

- PQC-61 APP-8 (Microsoft-Login): analoger Pattern, `loginWithProvider("microsoft")`
  in Login-Screen. Vermutlich sehr schnell (15-20 min) weil OAuth-Client
  bereits generisch ist.
- F-086 Sprint-3-Action: OAuth-App-Type-Switch fuer Live-Demo.
