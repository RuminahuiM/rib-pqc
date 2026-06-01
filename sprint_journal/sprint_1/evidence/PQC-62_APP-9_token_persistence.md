# Evidence: PQC-62 APP-9 Token-Persistenz mit expo-secure-store

- **Jira**: [PQC-62](https://rumidesigns.atlassian.net/browse/PQC-62)
- **Sprint**: 1 (Endspurt-Stretch)
- **Done am**: 2026-05-31
- **Story Points**: 1
- **Worklog**: ~10 Minuten (Bundle mit PQC-57, ueberlappende Implementation)
- **Hängt ab von**: PQC-57 (Done)

## AC-Mapping

| AC | Resultat |
|---|---|
| AC-1 expo-secure-store.setItemAsync speichert Broker-Token | OK: `saveToken()` in `secureStore.ts`, von `AuthContext.login()` aufgerufen |
| AC-2 App-Start laedt Token via getItemAsync | OK: `loadToken()` im `AuthProvider`-useEffect on mount |
| AC-3 Logout entfernt Token via deleteItemAsync | OK: `deleteToken()` im `AuthContext.logout()` und beim Auto-Login wenn Token abgelaufen |
| AC-4 Real-Phone-Test nach App-Neustart eingeloggt | PARTIAL: Dev-Mode-Limitation (siehe F-055). Mechanik korrekt implementiert und beim Hot-Reload verifiziert (Logout -> Token weg -> /login redirect funktioniert), standalone-Build-Test fehlt. |

## Files

PQC-62 ist effektiv die Implementation-Details die PQC-57 AC-3 verlangt. Keine
neuen Files ueber PQC-57 hinaus:
- `app/src/lib/secureStore.ts`: saveToken / loadToken / deleteToken
- `app/src/contexts/AuthContext.tsx`: nutzt die secureStore-Helper

## Senior-Decisions

1. **Zentralisierter secureStore-Wrapper** statt direkter SecureStore-API-Calls in AuthContext. DRY + zukunftssicher (kuenftige Token-Schluessel kommen einfach dazu).
2. **Schluessel-Konvention** `rib_pqc.<purpose>` mit Punktnotation. Aktuell `rib_pqc.broker_token`, spaeter `rib_pqc.refresh_token` etc.
3. **Idempotent delete**: `deleteToken()` faengt Fehler ab, wenn nichts zu loeschen ist.
4. **Lesefehler-Toleranz**: `loadToken()` returned bei Keychain-Corrupt `null` statt Exception. AuthContext interpretiert das als "kein Token, neu einloggen".

## Findings

- **F-055** (Tier-2 Info, open): siehe PQC-57 Evidence. Force-Close-Test im Dev-Mode nicht zuverlaessig.
