# Evidence: PQC-54 APP-1 Login-Screen mit drei Optionen (UI only)

- **Jira**: [PQC-54](https://rumidesigns.atlassian.net/browse/PQC-54)
- **Sprint**: 1 (Endspurt-Stretch)
- **Done am**: 2026-05-31
- **Story Points**: 2
- **Worklog**: ~15 Minuten
- **Hängt ab von**: PQC-20 (SKL-2), PQC-57 (APP-4)

## AC-Mapping

| AC | Resultat |
|---|---|
| AC-1 Login-Screen rendert drei Buttons | OK: Email/Pass (Primary), Continue with Google, Continue with Microsoft |
| AC-2 Email/Pass-Form mit zwei Inputs + Anmelden-Button | OK: TextInputs (email + password) + "Anmelden"-Pressable |
| AC-3 Google/Microsoft als Placeholder | OK: tap zeigt Alert "OAuth-Flow kommt in PQC-60/61" |
| AC-4 Form-Validierung (Email-Regex + PW min 8 Zeichen) | OK: regex `^[^\s@]+@[^\s@]+\.[^\s@]+$` plus length-Check, inline error-text unter Inputs |
| AC-5 Plain RN-Komponenten ohne Design-Library | OK: nur View/Text/Pressable/TextInput/SafeAreaView/StyleSheet, kein UI-Library |

## Files

- `app/src/app/login.tsx`: Form mit TextInputs, Validation, Submit-Button mit Loading-State, OAuth-Placeholder-Buttons

## Senior-Decisions

1. **Fake-Login mit hardcoded Dummy-Token (JWS-Compact-Format)**: Sprint-1 "UI only" Scope. Submit speichert via `AuthContext.login()` einen statischen Token in secure-store. Echter Server-Call kommt in PQC-59 (APP-6 secureClient).
2. **Email-Regex** simpliziert: `^[^\s@]+@[^\s@]+\.[^\s@]+$`. Gut genug fuer Sprint-1, Server (Pydantic EmailStr) validiert ohnehin nochmal autoritativ.
3. **PW min. 8 Zeichen** client-side. Server hat sein eigenes Min-Length im LoginRequest-Schema.
4. **Inline-Error-Texte** unter Inputs statt Alert, mit roter Border am fehlerhaften Input. UX-Standard.
5. **`isSubmitting`-Flag** disabled die Form waehrend Submit (auch wenn der Dummy-Login synchron ist, vorbereitet fuer echten async Call in PQC-59).
6. **Dummy-Token mit `exp=2100`** statt naehe-an-jetzt. Vermeidet F-055-Symptom dass Auto-Login Token als expired sieht.

## Findings

- Keine neuen findings, alle inline gefixt.
- F-055 (siehe PQC-57/62 Evidence): Force-Close-Persistenz im Expo Go Dev-Mode.
