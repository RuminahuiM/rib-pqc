# ADR-005: Microsoft-App-Registrierung als Single-Tenant

**Status:** Akzeptiert (Sprint-2-Planning, PQC-84 BRK-0)

## Kontext

Multi-Tenant-Apps bei Microsoft Entra brauchen einen App-Approval-Prozess mit Wartezeit von Stunden bis Tagen. Das haette die Federation-Stories (BRK-5/6) blockieren koennen (Risiken R-T04, R-S05).

## Entscheidung

Registrierung als Single-Tenant-App: Nur Accounts des eigenen Tenants koennen sich anmelden, dafuer entfaellt der Approval-Prozess komplett.

## Konsequenzen

- R-T04 und R-S05 wurden gegenstandslos; kein Wartezeit-Risiko im komprimierten Zeitplan.
- Fuer die Demo ausreichend (eigener Test-Account); ein produktives System wuerde Multi-Tenant plus Approval nachziehen.
