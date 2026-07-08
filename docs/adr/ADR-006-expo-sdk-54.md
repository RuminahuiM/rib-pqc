# ADR-006: Expo SDK 54 fix fuer den Projekt-Lebenszyklus

**Status:** Akzeptiert (31.05.2026, Sprint 1, PQC-20 SKL-2)

## Kontext

Beim App-Skeleton fuehrte das neueste SDK (56) zu Dependency-Konflikten (ERESOLVE, Node-Version), und die Demo laeuft ueber Expo Go auf einem echten iPhone: Die installierte Expo-Go-Version aus dem App Store bestimmt, welche SDK-Versionen ueberhaupt lauffaehig sind.

## Entscheidung

SDK 54 wird fuer den gesamten Projekt-Lebenszyklus fixiert, kein SDK-Upgrade waehrend des Projekts.

## Konsequenzen

- Stabile, reproduzierbare Demo-Umgebung auf dem iPhone bis zum Kolloquium.
- Bewusster Verzicht auf neuere SDK-Features; fuer ein Demo-Projekt ohne Relevanz.
