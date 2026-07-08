# ADR-003: liboqs-python (Server) und @noble/post-quantum (Mobile)

**Status:** Akzeptiert (Sprint 0, Tech-Stack-Entscheidung)

## Kontext

Fuer ML-KEM/ML-DSA braucht es Bibliotheken auf Server (Python) und Mobile (React Native). pyca/cryptography shipped 2026 noch kein ML-DSA; react-native-crystals implementiert die Vor-Standardisierungs-Versionen (Kyber/Dilithium), nicht FIPS 203/204. Details in [`../06_tech_stack.md`](../06_tech_stack.md).

## Entscheidung

Server: `liboqs-python` (Open-Quantum-Safe-Bindings, FIPS-konforme Algorithmen), TLS via `oqs-provider` fuer OpenSSL 3 hinter nginx. Mobile: `@noble/post-quantum` (auditiert, dependency-free, pure TypeScript) plus `@noble/ciphers` fuer AES-GCM.

## Konsequenzen

- Beide Seiten implementieren die standardisierten Verfahren; Kompatibilitaet via Cross-Validation-Vector abgesichert (F-098).
- liboqs ist nicht FIPS-140-3-validiert: fuer Produktion waere ein validierter Provider ein eigenes Arbeitspaket (Bericht, Kapitel 13).
- Versionen im Dockerfile gepinnt gegen ABI-Breakage (R-T01, mitigated 25.05).
