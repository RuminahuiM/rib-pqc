# Demo D-006: Mobile-Login auf iPhone via Expo Go

**Demo-ID:** D-006
**Datum:** 31.05.2026
**Stories integriert:** PQC-20 (SKL-2 Expo-Skeleton), PQC-54 (APP-1 Login-Screen), PQC-57 (APP-4 AuthContext), PQC-62 (APP-9 Token-Persistenz)
**Maschine:** iPhone (echtes Geraet) via Expo Go App, Expo SDK 54, Metro-Bundler vom Dev-Laptop
**Vorgaenger-Demos:** D-004 (Server-Login-Pipeline)
**Status:** funktional als UI-Flow, Mentor-tauglich. Mobile-Login-Foundation steht.

## Was diese Demo zeigt

End-to-End Live-Verifikation des Mobile-Login-Flows auf einem echten iPhone. Die App laedt via QR-Scan in Expo Go, zeigt beim Start einen Loading-Spinner, leitet bei fehlendem Token auf den Login-Screen, validiert die Eingaben, persistiert den Token in expo-secure-store, navigiert in den eingeloggten Bereich und kann wieder ausloggen.

Wichtig fuer die ehrliche Einordnung: Das ist in Sprint 1 ein Fake-Login (UI only). Der "Anmelden"-Button speichert einen hardcodierten Dummy-Token, es geht noch kein echter HTTP-Call an den Auth-Service. Der echte Server-Call kommt in Story PQC-59 (APP-6 secureClient). D-006 demonstriert also die App-State-Maschine und die Token-Persistenz-Mechanik, nicht die Server-Kommunikation.

## Demo-Ablauf (Schritt fuer Schritt auf dem iPhone)

```text
1. App laden:        QR-Code aus dem Metro-Bundler mit der Kamera scannen,
                     Expo Go oeffnet die App.
2. App-Start:        index.tsx zeigt Loading-Spinner waehrend secure-store
                     asynchron gelesen wird (is_loading-Flag).
3. Redirect:         Kein Token in secure-store vorhanden, also Auto-Redirect
                     auf /login.
4. Validation-Test:  Leeres Formular absenden zeigt Inline-Fehler
                     ("gueltige Email", "mindestens 8 Zeichen").
5. Login:            Gueltige Eingaben (alice@example.com / password123)
                     -> Loading-State -> AuthContext.login(DUMMY_TOKEN)
                     -> Token in secure-store gespeichert -> push auf /home.
6. Home-Screen:      Welcome-Message zeigt user_id "demo-user" und
                     auth_method "local" (aus dem Token-Payload abgeleitet).
7. Profile:          "View Profile" navigiert auf /profile.
8. Logout:           "Logout" loescht den Token aus secure-store
                     (deleteToken) und leitet zurueck auf /login.
```

## Screenshots

Die zugehoerigen iPhone-Screenshots gehoeren in denselben Ordner, benannt nach der Demo-Konvention:

```
sprint_journal/sprint_1/demos/images/D-006_screenshot_01.png   # Login-Screen
sprint_journal/sprint_1/demos/images/D-006_screenshot_02.png   # Validation-Errors
sprint_journal/sprint_1/demos/images/D-006_screenshot_03.png   # Home nach Login
sprint_journal/sprint_1/demos/images/D-006_screenshot_04.png   # Profile / Logout
```

Hinweis: Diese Screenshots sind vom User aufzunehmen und abzulegen. Solange sie fehlen, dient die obige Schritt-fuer-Schritt-Liste als textueller Beleg.

## Interpretation

| Beleg | Bedeutung |
|---|---|
| **Loading-Spinner vor Redirect** | Kein UI-Flicker zwischen /home und /login. Auto-Login prueft den Token-Ablauf clientseitig (jwt-decode exp-Check) bevor der State gesetzt wird. |
| **Validation-Errors** | Client-seitige Form-Validierung (Email-Regex, PW min. 8 Zeichen). Der Server validiert spaeter ohnehin autoritativ mit Pydantic EmailStr. |
| **Token-Persistenz** | Der Token wird ueber den zentralen secureStore-Wrapper (`rib_pqc.broker_token`) in expo-secure-store abgelegt. Logout entfernt ihn wieder. Mechanik via Hot-Reload verifiziert (Logout -> Token weg -> /login-Redirect). |
| **user_info aus Token-Payload** | Home zeigt sub und auth_method, die aus dem Token-Payload abgeleitet werden. Kein separater /api/profile-Call in Sprint 1 (kommt in PQC-56 APP-3). |

## Was D-006 bedeutet und was nicht

Bedeutet: Die Mobile-Foundation steht. Navigation, globaler Auth-State (AuthContext), Token-Persistenz und der Logout-Pfad funktionieren auf einem echten iPhone. Die UI fuer alle drei Login-Optionen (Email/Passwort, Google, Microsoft) ist vorhanden.

Bedeutet nicht: Es gibt keinen echten Server-Call. Der Token ist ein Dummy mit Fake-Signatur, kein vom Auth-Service ausgestellter ML-DSA-65-Token. Google und Microsoft sind Placeholder-Buttons (zeigen nur einen Hinweis-Dialog, OAuth-Flow folgt in PQC-60/61). Und es gibt noch keine PQ-Session und keine verschluesselten API-Calls (Sprint 3).

## Bewusste Limitations und Findings

- F-055 (Tier-2 Info, open): Auto-Login nach Force-Close von Expo Go funktioniert im Dev-Mode nicht zuverlaessig. Ein belastbarer Persistenz-Test braucht einen standalone .ipa-Build (TestFlight). Deshalb ist PQC-62 AC-4 bewusst als PARTIAL akzeptiert. Trigger: Sprint 4, falls TestFlight-Deploy.

## Mentor-Hinweis fuer 01.06.2026 Termin

Optionale Demo, falls Zeit bleibt. Beim Vorfuehren explizit sagen, dass es ein Fake-Login ist (Dummy-Token, kein Server-Call). Der Wert der Demo liegt in der App-Architektur (State-Management, Persistenz, Navigation), die in Sprint 3 die echte PQ-Kommunikation tragen wird. Nicht als "die App spricht schon mit dem Backend" verkaufen.

## Quellen und Referenzen

- Story PQC-54: https://rumidesigns.atlassian.net/browse/PQC-54
- Story PQC-57: https://rumidesigns.atlassian.net/browse/PQC-57
- Story PQC-62: https://rumidesigns.atlassian.net/browse/PQC-62
- Evidence: `evidence/PQC-54_APP-1_login_screen.md`, `evidence/PQC-57_APP-4_auth_context.md`, `evidence/PQC-62_APP-9_token_persistence.md`
- Code: `app/src/app/login.tsx`, `app/src/contexts/AuthContext.tsx`, `app/src/lib/secureStore.ts`, `app/src/lib/token.ts`
