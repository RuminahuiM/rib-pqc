# ADR-004: JWS-Compact-Token mit ML-DSA-65 trotz fehlendem JOSE-Standard

**Status:** Akzeptiert (Sprint 1, PQC-32/33)

## Kontext

Der Broker-Token braucht ein Format. Der IETF-Draft `draft-ietf-jose-pqc` (PQC-Algorithmen in JWTs) ist nicht ratifiziert; gegen ein bewegliches Ziel zu implementieren waere riskant. Ein komplett eigenes Format waere aber schwer nachvollziehbar.

## Entscheidung

JWS-Compact-Struktur (Header.Payload.Signatur, base64url) beibehalten, Signatur mit ML-DSA-65, `alg`-Header als dokumentierte Projekt-Konvention ([`../wire_format.md`](../wire_format.md) Abschnitt 2). Verifikation nach RFC 8725 Best Practices (alg-Allowlist, none-Block, exp-Leeway 30 s).

## Konsequenzen

- Vertraute Token-Struktur, Standard-Tooling zum Debuggen bleibt nutzbar.
- Sobald der JOSE-PQC-Draft ratifiziert ist, ist die Umstellung ein Header-Mapping, kein Redesign.
- ~3.3 KB Signatur macht den Token gross: bei Bedarf Transport im Body statt Header (T4 im Technical Brief).
