# Evidence: PQC-41 BRK-6 Microsoft IdP-Plugin

**Story:** PQC-41 BRK-6 (5 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

Microsoft-Entra-ID-Provider-Plugin als voll funktionales OIDC-Federation-Modul
registriert. Damit ist Login mit Microsoft funktional (vorbereitet fuer
App-Story PQC-61 APP-8).

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 idp_plugins/microsoft.py implementiert Plugin-Schnittstelle | OK (BRK-1+3+4) | `server/idp/plugins/microsoft.py`, `test_microsoft_plugin_satisfies_idp_protocol` (isinstance IdpProvider). Verify + Mapper voll-impl. |
| AC-2 Discovery-URL | OK mit Abweichung (Single-Tenant) | siehe unten |
| AC-3 Claim-Mapper extrahiert `oid` als External-Sub | OK (BRK-4) | `MicrosoftIdpPlugin.claim_mapper` Line 82-92, `test_microsoft_claim_mapper_happy_path_with_oid` |
| AC-4 Manuelle Demo liefert Broker-Token | Code OK (BRK-5), Live-Demo deferred zu PQC-61 APP-8 | Broker-Token-Ausgabe im federated-Callback ist provider-agnostic (BRK-5) |

## AC-2 Architektur-Abweichung: Single-Tenant statt Multi-Tenant

**Spec-Wortlaut AC-2:**
```
Discovery-URL https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration
```

**Implementierung:**
```
https://login.microsoftonline.com/<TENANT_ID>/v2.0/.well-known/openid-configuration
```

**Begruendung der Abweichung (Senior-Decision aus PQC-84 BRK-0):**

- Studienprojekt-Scope (HEKS-Mitarbeiter-Login) wird klar als Single-Tenant
  modelliert. Multi-Tenant `common` erlaubt jedem Microsoft-Account-Inhaber
  Login, was nicht dem UC-3 entspricht ("Mitarbeiter-Login mit M365").
- Single-Tenant erlaubt zusaetzliche Sicherheit via `tid`-Claim-Check
  (PQC-38 BRK-3 in `MicrosoftIdpPlugin.verify_id_token` Line 118-124):
  Token muss aus unserem konkreten Tenant kommen, sonst `invalid_tenant`-Error.
- Microsoft empfiehlt Single-Tenant fuer Apps die nur einer Organisation
  dienen (Entra ID v2.0 Docs 2026).
- Operationaler Vorteil: `tenant_id` wird via ENV-Var
  `RIB_IDP_PROVIDERS__MICROSOFT__TENANT_ID` konfiguriert, kein Hardcoded-`common`.

**Implementierung:**

`server/config.py` `MicrosoftProviderConfig` komponiert `discovery_url`
zur Laufzeit aus `tenant_id`:

```python
@property
def discovery_url(self) -> str:
    return (
        f"https://login.microsoftonline.com/{self.tenant_id}"
        f"/v2.0/.well-known/openid-configuration"
    )
```

Sollte das Projekt spaeter Multi-Tenant brauchen (z.B. fuer externe Partner),
ist die Erweiterung einfach: `tenant_id="common"` in der Config setzen, dann
matched die Standard-Spec.

## In BRK-6 implementiert (neu)

**Keine Code-Aenderung.** Die Plugin-Architektur aus BRK-1..BRK-5 deckt alle
AC ab:

- AC-1 (Plugin-Schnittstelle): BRK-1 + BRK-3 + BRK-4
- AC-2 (Discovery-URL): BRK-1 (mit Single-Tenant-Override)
- AC-3 (claim_mapper oid): BRK-4
- AC-4 Code-Teil: BRK-5 (Broker-Token-Ausgabe provider-agnostic)

PQC-41 ist primaer eine **AC-Cross-Reference + Doku-Story**, die bestaetigt
dass die Plugin-Architektur ihren Anspruch eingeloest hat: ein neuer Provider
braucht **null Code-Aenderung** ausser seiner Plugin-Klasse + Provider-Config.

## AC-4 Manuelle Live-Demo

**Senior-Decision:** Verschoben zu PQC-61 APP-8 (Microsoft-Login App-Seite),
analog zu PQC-40 BRK-5 AC-5 -> PQC-60.

Begruendung: PKCE-Pair-Generation lebt app-side (`expo-auth-session`).
Server-side ohne App ist kein praktischer End-to-End-Demo moeglich.

Im Bericht: Cross-Story-Demo-Referenz zwischen PQC-41 und PQC-61 erwaehnen.

## Tests

Volle Suite weiterhin **212 passed**, 4 erwartete Skips. Keine neuen Tests
notwendig, weil keine neue Code-Funktionalitaet.

Bestehende Microsoft-Tests gruen:
- `test_microsoft_plugin_satisfies_idp_protocol`
- `test_microsoft_plugin_properties` (tenant_id, discovery_url, issuer)
- `test_microsoft_claim_mapper_happy_path_with_oid`
- `test_microsoft_claim_mapper_preferred_username_fallback`
- `test_microsoft_claim_mapper_no_email_unverified`
- `test_microsoft_claim_mapper_missing_oid_raises`
- `test_init_raises_when_microsoft_enabled_without_tenant_id` (F-058)

## Closing-Review-Findings

Keine Must-Fix. 1 Finding:

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-080 | May | AC-2 Spec sagt `common`, wir nutzen `<tenant>`. Bericht muss diese architektonische Abweichung mit Begruendung (Single-Tenant + tid-Defense-in-Depth) explizit erwaehnen, damit Reviewer den Entscheidungspfad nachvollziehen koennen. Cross-Ref zu PQC-84 Senior-Decision. | vor Bericht-Abgabe | open |

## Verifikation

- `pytest tests/` 212/212 gruen
- `ruff check` All checks passed
- Microsoft-Plugin lifecycle-init im Live-Container (sandbox-test): konfigurierter
  tenant_id wird in issuer-URL komponiert (siehe Settings-Smoke-Test in PQC-38)

## Story-Aufwand

- Story-Points: 5 (Original-Schaetzung; Realitaet stark reduziert durch
  Plugin-Architektur-Vorarbeit)
- Tatsaechliche Zeit: tba (User entscheidet beim Done)
- AI-Multiplier-Beobachtung: 5 SP wurden auf reine Doku reduziert. Bestaetigt
  das Plugin-Architektur-Design: marginalkosten fuer neue Provider gegen Null.

## Folgestories

End-to-End-Server-Pfad ist nach PQC-41 vollstaendig done. Sprint-2-Restscope
auf App-Side (PQC-60 APP-7, PQC-61 APP-8), TLS-Pfad (PQC-43/44/45),
Hardening (PQC-42 BRK-7).
