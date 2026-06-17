# Evidence: PQC-40 BRK-5 Google IdP-Plugin

**Story:** PQC-40 BRK-5 (5 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

Google-Provider-Plugin als voll funktionales OIDC-Federation-Modul registriert.
Damit ist Login mit Google funktional (vorbereitet fuer App-Story PQC-60).

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 idp_plugins/google.py implementiert Plugin-Schnittstelle | OK (BRK-1+3+4) | `server/idp/plugins/google.py`. `test_google_plugin_satisfies_idp_protocol` (isinstance IdpProvider). Verify + Mapper voll-impl. |
| AC-2 Discovery-URL `accounts.google.com/.well-known/openid-configuration` | OK (BRK-1) | `GoogleProviderConfig.discovery_url` Default + Live-Verify aus PQC-84 BRK-0. |
| AC-3 Claim-Mapper extrahiert `sub` als External-Sub | OK (BRK-4) | `GoogleIdpPlugin.claim_mapper` Line 74-78, `test_google_claim_mapper_happy_path` |
| AC-4 Client-ID + Secret aus ENV-Variablen | OK (BRK-0+1) | Pydantic-Settings `RIB_IDP_PROVIDERS__GOOGLE__CLIENT_ID/SECRET`, F-058 Misconfig-Validation |
| AC-5 Manuelle Demo liefert Broker-Token | Code OK, Live-Demo deferred | siehe unten |

## In BRK-5 implementiert (neu)

**Broker-Token-Ausgabe im federated-Callback (AC-5 Code-Teil):**

- `routers/auth_federated.py`: Nach `link_or_create` ruft Router
  `token_service.issue(user_id, auth_method, external_sub)` und gibt einen
  ML-DSA-65-signierten Broker-Token (JWS-Compact) im Response zurueck.
- `CallbackResponse` erweitert um `broker_token: str` + `broker_token_expires_in: int`.
- Pattern identisch zu PQC-30 AUT-3 lokaler Login (`routers/auth.py`),
  damit App-Code einheitlich bleibt (1 Token-Format fuer alle Auth-Methods).

**Test:**

```python
def test_callback_returns_broker_token(client: TestClient) -> None:
    r = client.post("/auth/federated/google/callback", json=_callback_payload())
    assert r.status_code == 200
    body = r.json()
    assert body["broker_token"] == "mock.broker.token"
    assert body["broker_token_expires_in"] == 3600
```

Gruen. Volle Suite: **212 passed**, 4 erwartete Skips (liboqs-Sandbox).
Ruff `All checks passed`.

## AC-5 Manuelle Live-Demo

**Senior-Decision:** Verschoben zu PQC-60 APP-7 (Google-Login App-Seite).

**Begruendung:**

- Der OIDC-Authorization-Code-Flow + PKCE ist in PQC-37 BRK-2 so designed, dass
  die App-Seite den code_verifier (PKCE) generiert und behaelt. Server-side
  haben wir kein Tool um manuell einen PKCE-Pair zu generieren und den
  vollstaendigen Browser-Flow durchzuziehen ohne App.
- PQC-60 APP-7 implementiert die App-Seite mit `expo-auth-session`, das PKCE
  out-of-the-box managed. Dann laeuft der echte End-to-End-Flow durch.
- AC-5 (Code-Teil: Broker-Token wird ausgestellt) ist via Router-Test
  funktional verifiziert. Real-World-Demo ist Cross-Story-Referenz mit PQC-60.

**Tracking:** PQC-60 APP-7 wird im Done-Comment cross-referenced.

## Architektur-Bestaetigung

Die BRK-5-Story bestaetigt, dass die in BRK-1..BRK-4 gebaute Architektur die
"Plugin-Voll-Demo" pro Provider mit minimalem Aufwand ermoeglicht:

- BRK-1 hat das Plugin-Skeleton geliefert.
- BRK-2 hat den Code-Flow gebaut (provider-agnostic).
- BRK-3 hat verify_id_token implementiert.
- BRK-4 hat claim_mapper + link_or_create implementiert.
- BRK-5 = nur Broker-Token-Ausgabe + Live-Demo (AC-Check, kein Plugin-Neucode).

Das ist das Ziel der Plugin-Architektur: neue Provider (Apple in STR-2 PQC-76)
brauchen nur ihre Plugin-Implementierung, alle Infrastructure-Stories sind
bereits durch.

## Closing-Review-Findings

Keine Must-Fix. Findings aus BRK-5:

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-078 | Info | `TokenService._ttl` ist Private-Attribute (Underscore-Prefix). Wir greifen darauf zu fuer broker_token_expires_in. Sauber waere eine Public-Property `TokenService.ttl`. Pattern wird in routers/auth.py PQC-30 schon genauso gemacht (F-021 bekommt Begleitung). | bei naechstem TokenService-Touch, mit F-021 buendeln | open |
| F-079 | May | AC-5 "Manuelle Demo" wird in PQC-60 APP-7 cross-referenced verifiziert. Im Studienprojekt-Bericht muss die Cross-Story-Demo-Referenz erwaehnt werden, damit Reviewer den AC-Erfuellungspfad nachvollziehen koennen. | vor Bericht-Abgabe | open |

## Verifikation

- `pytest tests/` 212/212 gruen, 4 erwartete Skips
- `ruff check services/ routers/ idp/` All checks passed
- AC-Cross-Reference: AC-1..AC-4 via bestehende Code-Files + Tests verifiziert
- AC-5 Code-Teil: Router-Test verifiziert Broker-Token im Response
- AC-5 Live-Demo: deferred zu PQC-60 APP-7

## Story-Aufwand

- Story-Points: 5 (urspruenglich M T-Shirt, aber durch BRK-1..BRK-4 stark abgefedert)
- Tatsaechliche Zeit: tba (User entscheidet beim Done)
- AI-Multiplier-Beobachtung: 5 SP durch Pattern-Replikation auf wenige Edit-Calls
  reduziert. Story-Aufwand realistisch eher SP=1-2, aber AC-5 Live-Demo-Setup
  haette ohne BRK-1..BRK-4 5 SP gerechtfertigt.

## Folgestories

- PQC-41 BRK-6 Microsoft analog (gleicher Pattern, vermutlich noch schneller)
- PQC-60 APP-7 fuehrt die AC-5 Live-Demo durch
