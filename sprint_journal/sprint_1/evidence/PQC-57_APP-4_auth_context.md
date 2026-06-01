# Evidence: PQC-57 APP-4 AuthContext (globaler Auth-State)

- **Jira**: [PQC-57](https://rumidesigns.atlassian.net/browse/PQC-57)
- **Sprint**: 1 (Endspurt-Stretch)
- **Done am**: 2026-05-31
- **Story Points**: 2
- **Worklog**: ~25 Minuten

## AC-Mapping

| AC | Resultat |
|---|---|
| AC-1 React Context mit broker_token, user_info, is_authenticated | OK: `AuthContext` in `app/src/contexts/AuthContext.tsx` mit `AuthState` (broker_token, user, is_authenticated, is_loading) |
| AC-2 login(token) und logout() Methoden | OK: useCallback-stabile `login()` und `logout()`, persistieren ueber secureStore-Wrapper |
| AC-3 Token persistiert mit expo-secure-store | OK: `app/src/lib/secureStore.ts` Wrapper (saveToken/loadToken/deleteToken), AuthContext nutzt diese |
| AC-4 Auto-Login bei App-Start wenn Token gueltig | OK: useEffect on mount laedt Token, prueft `isExpired()` (jwt-decode), setzt State. Loading-Spinner via `is_loading` flag |

## Files

- `app/src/contexts/AuthContext.tsx` (NEU, 135 Zeilen): Provider + useAuth-Hook, Auto-Login Logic
- `app/src/lib/secureStore.ts` (NEU): expo-secure-store Wrapper
- `app/src/lib/token.ts` (NEU): JWS-Decoding + Expiry-Check mit jwt-decode
- `app/src/app/_layout.tsx`: AuthProvider wrap
- `app/src/app/index.tsx`: Auth-aware Redirect mit Loading-State
- `app/src/app/home.tsx`: Logout-Button via `useAuth().logout()`
- `app/package.json`: `jwt-decode` als deps

## Senior-Decisions

1. **Client-side JWS-Decode mit exp-Check** statt naivem "Token vorhanden = authenticated". Best-practice fuer UX (kein /home -> /login Flicker bei abgelaufenem Token), kein spaeterer Umbau.
2. **`jwt-decode` Library** (3KB, well-tested, klare API) statt selbst geschriebener base64url-Decode.
3. **Loading-Spinner** im `index.tsx` waehrend secure-store-Load (asynchron). Vermeidet UI-Flicker.
4. **deriveUserFromToken** als pure Helper-Funktion (kein State). User-Info wird aus Token-Payload (sub, auth_method, external_sub) abgeleitet. Sprint-1: kein separater /api/profile-Call (kommt in PQC-56 APP-3).
5. **`useAuth()` wirft Exception ausserhalb von AuthProvider** statt undefined-Return. Component-Tree-Misuse wird im Dev sofort sichtbar.

## Findings

- **F-055** (Tier-2 Info, open): Auto-Login nach Force-Close von Expo Go funktioniert im Dev-Mode nicht zuverlaessig. Echter Test braucht standalone .ipa-Build.
