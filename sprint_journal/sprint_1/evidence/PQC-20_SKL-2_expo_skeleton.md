# Evidence: PQC-20 SKL-2 Expo-Skeleton mit Navigation und drei Screens

- **Jira**: [PQC-20](https://rumidesigns.atlassian.net/browse/PQC-20)
- **Sprint**: 1 (Endspurt, Carry-Over aus Sprint 0)
- **Done am**: 2026-05-30
- **Story Points**: 3
- **Worklog**: ~90 Minuten

## Zusammenfassung

Expo-Skeleton mit React Native + Expo Router + TypeScript angelegt. Drei
Placeholder-Screens (Login, Home, Profile) als Stack-Navigation. PQC-relevante
Mobile-Deps (`@noble/post-quantum`, `@noble/ciphers`, `expo-secure-store`,
`expo-auth-session`) installiert. App laeuft im Live-Test auf iPhone via
Expo Go.

**Schluessel-Entscheidung:** SDK 54 statt 56 (siehe F-054 + R-N01) fuer
App-Store-Expo-Go-Kompatibilitaet (iPhone-Demo-Constraint).

## AC-Mapping

| AC | Resultat |
|---|---|
| AC-1 `app/`-Ordner mit Expo SDK 51+ TypeScript | OK: Expo SDK 54.0.x, TypeScript 5.9.x |
| AC-2 Expo Router mit Routen /login /home /profile | OK: `src/app/_layout.tsx` mit `Stack`, vier Routes (`index` redirected zu `/login`, plus die drei AC-Routes) |
| AC-3 Drei Placeholder-Screens existieren + navigierbar | OK: live auf iPhone verifiziert, Login -> Home -> Profile Stack-Push, Back-Button funktioniert |
| AC-4 App startet `npx expo start` im Simulator und auf Test-Phone | OK: iPhone via Expo Go App-Store-Version, QR-Scan, App laedt zu Login-Screen |
| AC-5 Deps `@noble/post-quantum`, `@noble/ciphers`, `expo-secure-store`, `expo-auth-session` | OK: alle 4 in `package.json` |

## Files

- `app/` (NEU): Expo-Projekt via `npx create-expo-app@latest app --template default`, danach Downgrade auf SDK 54
- `app/src/app/_layout.tsx`: Stack-Navigation mit 4 Screens, blauer nginx-Header-Style
- `app/src/app/index.tsx`: Redirect zu `/login`
- `app/src/app/login.tsx`: Login-Placeholder mit 3 Buttons (Email/Password, Google, Microsoft)
- `app/src/app/home.tsx`: Home-Placeholder mit "View Profile" und "Logout"
- `app/src/app/profile.tsx`: Profile-Placeholder mit Demo-Felder (email, auth_method, signing-algorithm)
- `app/package.json`: SDK-54-konforme Versionen, 4 AC-5-Deps eingetragen

## Senior-Decisions

1. **Init-Strategie:** `expo-router/typescript` Template via `npx create-expo-app@latest app --template default`. SDK 56 wurde initial installiert, dann auf SDK 54 downgraded.
2. **AC-4-Verify:** iPhone via Expo Go App-Store-Version (statt iOS Simulator). Demo-relevant.
3. **app/-Pfad:** Direkt im Repo-Root `app/` (Monorepo-Style neben `server/` und `infra/`).
4. **SDK-Strategie:** SDK 54 fuer **gesamten Projekt-Lebenszyklus** (Mai bis Juli 2026), nicht nur Sprint 1. Begruendung: iPhone-Expo-Go aus App Store unterstuetzt zum Stand 30.05.2026 max SDK 54. Upgrade auf SDK 55/56 nur wenn App Store nachzieht. Memory-Eintrag `project-pqc-expo-sdk` persistiert.
5. **Navigation-Pattern:** Stack-Navigation (login -> home -> profile) statt Tab-Navigation. Passt zum Auth-Flow.
6. **Theme-Provider:** weggelassen weil SDK 54 expo-router `ThemeProvider` nicht direkt exportiert (kommt aus `@react-navigation/native`). Skeleton braucht das nicht.

## Build-Issues (alle in-story gefixt)

1. **Node 18 zu alt fuer `create-expo-app@4`:** `ReferenceError: File is not defined` weil File-API erst Node 20+. Fix: nvm-windows + Node 22 LTS via Setup-Script `infra/scripts/setup-node22.sh`.
2. **Expo Go App-Store-Version inkompatibel mit SDK 56:** Render-Error "Project is incompatible with this version of Expo Go". Fix: Downgrade auf SDK 54 (`npm install expo@~54.0.0 && npx expo install --fix`).
3. **ERESOLVE-Konflikt bei `npx expo install --fix`:** `react-server-dom-webpack@19.2.6` peer-deps blockieren `expo-router@6.0.24` weil `react@19.1.0` benoetigt wird. Fix: Clean Slate (`rm -rf node_modules package-lock.json`) + `npm install --legacy-peer-deps`.
4. **Runtime-Render-Error in `_layout.tsx`:** `ThemeProvider`, `DarkTheme`, `DefaultTheme` werden in expo-router 6.x (SDK 54) nicht mehr aus expo-router exportiert (kommen aus `@react-navigation/native`). Fix: ThemeProvider entfernt, nur Stack genutzt.

## Live-Verifikation auf iPhone

User-Bestaetigung (2026-05-30):
- App laedt via Expo Go QR-Scan
- Login-Screen zeigt drei Buttons
- "Email / Password" tippen -> push zu /home
- "View Profile" tippen -> push zu /profile
- Header-Back-Button funktioniert

## Findings (Tier-2-Polish + Risk-Empfehlung)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-054 | SDK 54 statt 56 (App-Store-Expo-Go-Kompatibilitaet). FINAL fuer Projekt-Lebenszyklus, kein Upgrade-Pfad geplant solange iPhone-Demo-Constraint besteht. | Info | Sprint 4 falls App-Store SDK 55/56 nachzieht (unwahrscheinlich vor 04.07.2026) | open |

**Risk-Register-Empfehlung (Hand-Off Co-SM-Chat):**
- R-N01: Expo SDK Version nicht in App Store verfuegbar. Wahrscheinlichkeit HOCH (bereits eingetreten), Impact NIEDRIG (Downgrade <5min, alle Features in SDK 54 verfuegbar). Mitigated in PQC-20.

## Aufwand

- Story-Start + Senior-Decisions + AskUserQuestions: ~10min
- Node 22 Setup via nvm-windows (Side-Quest, Node 18 zu alt): ~10min
- create-expo-app + initial Routes-Customization: ~15min
- SDK 56 Inkompatibilitaet entdecken + WebSearch + Strategie-Entscheidung: ~15min
- SDK 54 Downgrade + ERESOLVE-Fix + ThemeProvider-Fix: ~25min
- Live-Verify auf iPhone + Evidence-Schreiben: ~15min
- **Total: ~90min**
