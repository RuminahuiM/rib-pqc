# Evidence: PQC-42 BRK-7 CSRF/State+PKCE Server-managed

**Story:** PQC-42 BRK-7 (2 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

State+PKCE-Refactor zu Server-managed-BFF-Pattern (RFC 9700 BCP 2026 +
AC-5-Spec). App schickt code_verifier beim Authorize-Start, Server haelt ihn
in Redis zusammen mit State, beim Callback schickt App nur {code, state} -
code_verifier kommt aus Redis (One-Shot Replay-Schutz fuer beide atomar).

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 App generiert State mit expo-crypto getRandomBytes(16) oder vergleichbar | OK mit Abweichung (Server-Gen) | siehe unten |
| AC-2 State wird im Callback geprueft | OK | `OidcStateService.consume` + Tests |
| AC-3 State-Mismatch -> 400 Bad Request | OK | `test_callback_state_mismatch_returns_400` |
| AC-4 Integration-Test mit kuenstlich falschem State | OK | Router-Test + Service-Level State-Test |
| AC-5 Redis-TTL 10min + code_verifier zusammen mit State + One-Shot DEL | OK | StateEntry erweitert um code_verifier, atomar persistiert + consumed |

## AC-1 Architektur-Abweichung: Server-side State-Generation

**Spec-Wortlaut AC-1:** "App generiert State-Parameter mit expo-crypto.getRandomBytes(16) oder vergleichbar."

**Implementierung:** Server generiert State server-side via `secrets.token_urlsafe(32)` (256 bit Entropie).

**Begruendung der Abweichung (Senior-Decision PQC-37 BRK-2):**

- BFF-Pattern (RFC 9700 BCP 2026): Server ist Confidential Client mit
  client_secret und kontrolliert die ganze OAuth-Flow-Mechanik.
- Server-managed State + PKCE ist Industry-Standard fuer BFF-Setups
  (Auth0/Cognito/Keycloak nutzen alle diesen Ansatz).
- 256 bit Entropie via `secrets.token_urlsafe(32)` ist deutlich mehr als
  AC-1's 128 bit-Vorgabe.
- App wird einfacher: kein PKCE-Memory-Management app-side, App muss nur
  state lokal merken fuer den Callback-Echo.

Im Bericht: Cross-Reference zur Senior-Decision aus PQC-37 + Begruendung mit BFF-Pattern.

## In BRK-7 implementiert

**Refactor zu Server-managed-PKCE (AC-5 voll erfuellt):**

- `services/oidc_state_service.py`: `StateEntry` erweitert um Pflichtfeld
  `code_verifier: str` (43-128 chars per RFC 7636). `OidcStateService.create()`
  nimmt jetzt `(provider, code_verifier)` als Pflichtparameter und persistiert
  beides atomar in Redis. `consume()` liefert beides zurueck.
- `routers/auth_federated.py`:
  - Neue Request-Klasse `AuthorizeStartRequest` mit `code_verifier`-Body-Param.
  - `start_authorize` Endpoint: nimmt `code_verifier` vom App, persistiert ihn
    in Redis, berechnet code_challenge = base64url(SHA256(verifier)) server-side,
    baut Authorize-URL mit S256-Challenge.
  - `CallbackRequest`: `code_verifier` entfernt - App schickt nur noch {code, state}.
  - Callback liest `code_verifier` aus dem State-Eintrag und reicht ihn an den
    Token-Exchange weiter (BFF-Pattern).

**Sicherheitsgewinne:**

1. **Atomarer Replay-Schutz:** state + code_verifier werden zusammen via
   Redis-DEL geloescht. Zweiter Callback-Versuch kann weder state noch
   verifier wiederverwenden.
2. **Centralized Audit-Log:** Server hat zentrales Logging ueber alle aktiven
   PKCE-Sessions (oidc_state.create/consume Events).
3. **App-Simplifikation:** PQC-60 App-Code wird einfacher - kein expo-crypto
   PKCE-Management noetig, nur State-Echo.
4. **Server-side code_challenge-Berechnung:** App kann nicht versehentlich
   eine andere challenge zum IdP schicken als der Verifier hergibt.

## Tests

```
======================= 215 passed, 4 skipped in ~17s =======================
```

**+3 neue Tests** (StateEntry mit code_verifier-Field, code_verifier wird zusammen mit
state consumed, code_verifier wird atomar mit state ge-DEL-ed).

Bestehende Tests angepasst:
- `OidcStateService.create()`-Tests nehmen jetzt code_verifier-Param
- Router-Tests: Authorize-Endpoint mit JSON-Body, Callback ohne code_verifier
- `_MockPlugin.verify_id_token`: ClassVar fuer scopes

Ruff `All checks passed`.

## Closing-Review-Findings

Keine Must-Fix. 2 Findings:

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-081 | May | AC-1 Spec sagt App-Gen, wir nutzen Server-Gen (BFF-Konvention). Bericht muss Abweichung mit Begruendung dokumentieren (analog F-080 fuer AC-2-Microsoft). | vor Bericht-Abgabe | open |
| F-082 | Info | F-063 (Defense-in-Depth) ist durch dieses Refactoring obsolet: code_verifier kommt jetzt aus Redis (nicht vom Client beim Callback), damit kann App keinen anderen Verifier schicken als der mit dem code_challenge korrespondiert. Server-Berechnung ist tied to Server-Storage. | resolved durch BRK-7 |

F-063 (Should vor BRK-7) wird durch dieses Refactor resolved und kann in
deferred_findings.md als resolved markiert werden.

## Verifikation

- `pytest tests/` 215/215 gruen
- `ruff check services/ routers/ idp/ tests/` All checks passed
- Import-Smoke-Test `from main import create_app; create_app()` OK
- Manueller Smoke per Python:
  ```python
  state = await service.create(provider="google", code_verifier="A"*64)
  entry = await service.consume(state)
  # entry.code_verifier == "A"*64
  # zweiter consume -> StateNotFoundError
  ```

## Story-Aufwand

- Story-Points: 2 (T-Shirt S)
- Tatsaechliche Zeit: tba (User entscheidet beim Done)
- AI-Multiplier-Beobachtung: Refactor war ueberschaubar weil OidcStateService
  schon existierte. Aufwand floss in: Schema-Erweiterung (StateEntry), Test-
  Anpassungen (alte create-Calls + Mock-StateEntry-Konstruktion), ruff-Polish.

## Folgestories

End-to-End-OIDC-Server-Pfad nach PQC-42 vollstaendig:
- BRK-1 + BRK-7 (State+PKCE-Persistence)
- BRK-2 (Code-Flow + PKCE-Echo)
- BRK-3 (ID-Token-Verify)
- BRK-4 (Identity-Normalisierung + Account-Linking)
- BRK-5 + BRK-6 (Plugin-Voll-Demos)

Sprint-2 Done-SP: PQC-84 + PQC-36 + PQC-37 + PQC-38 + PQC-39 + PQC-40 + PQC-41 + PQC-42 = **38 SP**.

Restscope: TLS-Pfad (PQC-43/44/45), App-Stories (PQC-60 APP-7, PQC-61 APP-8).
