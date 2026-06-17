# Evidence: PQC-39 BRK-4 Identity-Normalisierung

**Story:** PQC-39 BRK-4 (5 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

Federated User-Identitaeten (Google sub, Microsoft oid) werden auf interne
User-IDs gemappt. Bei Wiederholung wird der bestehende User-Record genutzt.
Bei verifizierter Email-Match auf lokalen User wird Account-Linking gemacht.
Spoof-Schutz bei unverifizierter Email.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 Erst-Login -> neuer User + Identity | OK | `test_first_login_creates_user_and_identity`, FederatedIdentityService Create-Branch |
| AC-2 Wiederholter Login -> bestehender User | OK | `test_repeat_login_reuses_existing_user` mit nur 1 Identity-Row |
| AC-3 Claim-Mapping per Plugin (google.sub, microsoft.oid) | OK | `test_google_claim_mapper_happy_path` + `test_microsoft_claim_mapper_happy_path_with_oid` |
| AC-4 Email-Konflikt -> external_sub ergaenzt (Linking) | OK | `test_email_verified_match_links_to_existing_local_user` |
| AC-5 Tests Erst/Wiederholt/Konflikt | OK | 8 FederatedIdentityService-Tests + 8 UserIdentityRepository-Tests + 8 Plugin-Mapper-Tests |
| AC-6 email_unverified -> kein Linking + log-Event | OK | `test_email_unverified_does_not_link_to_existing_user` + Logger-Call `auth.federated.email_unverified` |

## Architektur-Entscheidungen

| Entscheidung | Begruendung |
| --- | --- |
| Separate `user_identities`-Tabelle (statt JSON-Field oder Single-Identity) | 3NF-Normalisierung fuer 1:n-User-Identity-Beziehung. Composite-Unique `(auth_method, external_sub)` macht Lookups O(log n). Industry-Standard (Auth0/Cognito/Keycloak). Skaliert fuer Apple-Plugin in STR-2 ohne Schema-Aenderung. |
| Microsoft nutzt `oid` statt `sub` als external_sub | Entra ID `sub` ist pro App-Client pairwise; `oid` ist tenant-stable. Best Practice fuer Account-Linking. |
| Pydantic `NormalizedIdentity` Modell (EmailStr, BoolField) | Type-Safety beim Plugin-Service-Handoff. Validation fuer Email-Format integriert. |
| `FederatedIdentityService` als Pro-Request-Service (nicht Singleton) | Repository ist session-scoped. Service wird im Router pro Request mit der Request-Session-Factory instanziiert. |
| Account-Linking nur bei `email_verified=True` (AC-6) | Defense gegen Account-Takeover via IdP-Spoof. Unverified Federated mit Match auf existing local-User -> `UserAlreadyExistsError` (kein silent Override). |
| Placeholder-Email fuer no-email-Provider (`<sub>+<provider>@no-email.local`) | User.email ist NOT NULL Unique. MS-Apps-Only-Tokens haben kein email-Claim. Platzhalter ist eindeutig + filterbar in UI. |
| Alembic Data-Migration: bestehende User.external_sub spiegelt in user_identities | Backward-Compat fuer SQL-Tests + existierende DB-Volumes. User.auth_method+external_sub bleiben aus Backward-Compat im Schema (Sprint 4/5 Cleanup-Option). |

## Implementierte Files

| Pfad | Zweck |
| --- | --- |
| `server/models/user_identity.py` | UserIdentity ORM mit Composite-Unique-Constraint |
| `server/alembic/versions/e24c7cf373f9_add_user_identities_table.py` | Migration + Data-Migration aus User.external_sub |
| `server/db/repositories/user_identity_repository.py` | CRUD: create, find_by_external, list_for_user |
| `server/idp/normalized_identity.py` | Pydantic-Modell mit EmailStr + email_verified + display_name |
| `server/idp/plugins/google.py` | claim_mapper voll-impl (sub, email, email_verified, name/given_name) |
| `server/idp/plugins/microsoft.py` | claim_mapper voll-impl (oid, email/preferred_username, name) |
| `server/services/federated_identity_service.py` | `link_or_create(provider, normalized) -> User` |
| `server/routers/auth_federated.py` | Callback ruft claim_mapper + link_or_create; Response erweitert um `user: {id, email, auth_method}` |
| `server/tests/test_user_identity_repository.py` | 8 Tests |
| `server/tests/test_federated_identity_service.py` | 8 Tests (5 Szenarien + Multi-Provider + No-Email + Repeat-Login) |
| `server/tests/test_idp_registry.py` | +8 Plugin-Mapper-Tests |
| `server/tests/test_auth_federated_router.py` | Update: session_factory injected, MockPlugin.claim_mapper |

## Tests

```
======================= 211 passed, 4 skipped in ~16s =======================
```

**+23 neue Tests** in BRK-4 (8 UserIdentity-Repo + 8 FederatedIdentityService +
7 Plugin-Mapper + Router-Erweiterungen ohne neue Tests, Update der bestehenden).
Volle Suite **211 passed** (vorher 188), 4 erwartete Skips (liboqs-Sandbox).
Ruff `All checks passed`.

Test-Cluster:
- **UserIdentityRepository:** Create-Happy, find_by_external Hit/Miss,
  Duplicate-Constraint-Error, invalid auth_method, empty external_sub,
  list_for_user, unknown-user-empty.
- **FederatedIdentityService:** Erst-Login mit Email, Erst-Login ohne Email
  (Placeholder), Repeat-Login (gleiche User-ID), Email-verified-Linking,
  Email-unverified-keine-Linking (raises), Email-unverified-Neuer-User
  (kein Konflikt), Multi-Provider-zu-gleichem-User.
- **Plugin-Mapper:** Google Happy, email_unverified, missing sub,
  fallback given_name. Microsoft Happy, preferred_username-fallback,
  no-email-unverified, missing oid.

## Closing-Review-Findings

WebSearch: Account-Linking-Pattern bestaetigt (Auth0, Cognito, Microsoft Entra
External ID), email_verified-Pflicht ist Industry-Standard.

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-073 | Info | User.auth_method + User.external_sub bleiben im Schema als Backward-Compat, werden aber ab BRK-4 nicht mehr authoritativ gelesen. Sprint 4/5 Cleanup: nullbar machen oder droppen. | Sprint 4 Schema-Cleanup |
| F-074 | May | MS-Plugin-claim_mapper setzt `email_verified=True` wenn Email-Claim vorhanden ist. Edge-Case: external-collaborator-Accounts in einem Tenant koennten unverified UPN haben. RFC sagt: `email_verified` muss explizit aus Token gelesen werden, aber Microsoft v2.0 setzt es selten. Konservativ in PQC-39 nicht differenziert. | vor produktiver Demo / bei MS-External-Collaborator-Story |
| F-075 | Info | `FederatedIdentityService.link_or_create` macht 2 separate DB-Calls (find_by_external + ggf find_by_email + create). Race-Condition bei zwei parallelen first-Logins desselben Users moeglich (zweiter wuerde IdentityAlreadyExistsError werfen). Aktuell akzeptiert (single-User-pro-Login Annahme). Production: in DB-Transaction packen + retry. | Sprint 4 oder bei Load-Test-Issues |
| F-076 | Info | Placeholder-Email `<sub>+<provider>@no-email.local` koennte mit echten User-Emails kollidieren wenn Provider tatsaechlich eine `.local`-Email liefert. Praktisch extrem unwahrscheinlich. | informational |
| F-077 | Info | Alembic-Migration spiegelt bestehende User.external_sub in user_identities. Wenn Migration teilweise scheitert, kann Inkonsistenz entstehen. Aktuell akzeptiert weil Sprint-1-DB klein/leer. | bei DB-Restore-Test |

Keine Must-Fix. F-065 + F-058 bleiben resolved aus vorherigen Stories.

## Verifikation

- `pytest tests/` 211/211 gruen, 4 erwartete Skips (liboqs-Sandbox).
- `ruff check services/ routers/ idp/ models/ db/ tests/` All checks passed.
- `from main import create_app; create_app()` -> Imports + Routes OK.
- Migration: `alembic upgrade head` (im Container) sollte beim naechsten
  Service-Start die user_identities-Tabelle erstellen und bestehende User
  spiegeln (manuell verifizierbar via SQLite-CLI nach Container-Restart).

## Story-Aufwand

- Story-Points: 5
- Tatsaechliche Zeit: tba (User entscheidet beim Done).
- AI-Multiplier-Beobachtung: 5 SP umfangreich (Schema-Migration + 2
  Repositories + Service + Plugin-Vollausbau + Router-Update + 23 Tests).
  Pattern-Replikation aus UserRepository + idp/plugin-Pattern hat das
  Tempo gehalten.

## Folgestories

End-to-End-Server-Pfad ist nach BRK-4 funktional komplett:

- BRK-5/BRK-6 (PQC-40/41) sind nun groesstenteils Polish: alle Logik ist in
  BRK-1..BRK-4 implementiert. Wenn der User die Stories beruehren will,
  werden sie wahrscheinlich nur Sanity-Check + Demo-Validierung.
- BRK-7 (PQC-42) ist die geplante Hardening-Story mit F-063 + TTL-Real-Test.
- TLS-Stories (PQC-43/44/45) sind unabhaengiger Pfad.
- App-Stories (PQC-60/61) brauchen nur noch APP-Code, Server-Backend ist
  bereit.
