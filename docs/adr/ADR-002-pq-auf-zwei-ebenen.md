# ADR-002: PQ auf zwei Ebenen (TLS-Layer und Application-Layer)

**Status:** Akzeptiert (Sprint 0), durch R-T08 bestaetigt (17.06.2026, Sprint 2)

## Kontext

iOS und Android erlauben App-Code keinen Zugriff auf die TLS-Cipher-Aushandlung (Constraint C-Tech-1). Eine "End-to-End-PQC via TLS"-Behauptung waere auf Mobile nicht haltbar. Waehrend Sprint 2 hat sich zusaetzlich bestaetigt, dass die System-TLS-Stacks X25519MLKEM768 noch gar nicht unterstuetzen (R-T08).

## Entscheidung

PQC wirkt auf zwei Ebenen: hybrides PQ-TLS (X25519MLKEM768) server-seitig via nginx/oqs-provider fuer alle faehigen Clients, plus eine eigene PQ-Session auf Application-Layer (ML-KEM-768, HKDF, AES-256-GCM) fuer die App-Kommunikation.

## Konsequenzen

- Ende-zu-Ende-PQ fuer die App unabhaengig vom OS-TLS-Stack; R-T08 hat das Projekt dadurch nicht gefaehrdet.
- Defense-in-Depth: beide Schichten muessten gebrochen werden.
- Mehraufwand: eigenes Wire-Format inkl. Replay-Schutz musste spezifiziert werden ([`../wire_format.md`](../wire_format.md)).
