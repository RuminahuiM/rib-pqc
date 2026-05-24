# Requirements: PQC Auth-Service mit Identity Broker und E2E PQ-Kommunikation

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 08.05.2026
**Status:** Vollständig (alle Phasen plus Traceability Matrix und Glossar)

---

## Inhaltsverzeichnis

1. [Einleitung und Kontext](#1-einleitung-und-kontext)
2. [Stakeholder und Projekt-Ziele](#2-stakeholder-und-projekt-ziele)
3. [Use Cases](#3-use-cases)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Constraints](#6-constraints)
7. [Traceability Matrix](#7-traceability-matrix)
8. [Glossar](#8-glossar)
9. [Versionsverlauf](#9-versionsverlauf)

---

## 1. Einleitung und Kontext

### 1.1 Problemstellung

Klassische asymmetrische Kryptografie (RSA, ECC, ECDSA) wird durch hinreichend leistungsfähige Quantencomputer mittels Shor-Algorithmus brechbar. Auch wenn solche Quantencomputer 2026 noch nicht praktisch verfügbar sind, müssen Daten, die heute übertragen werden, bereits jetzt gegen zukünftige Entschlüsselung geschützt werden. Diese Bedrohung wird als "Harvest Now, Decrypt Later" bezeichnet und betrifft insbesondere langfristig sensible Daten wie Authentifizierungs-Sessions, Identity-Claims und persönliche Nutzerdaten.

Die NIST-Post-Quantum-Cryptography-Standards (FIPS 203, 204, 205) sind seit August 2024 final verfügbar, die industrielle Adoption steckt aber 2026 noch in einer frühen Phase. Insbesondere im Bereich Mobile Authentication existieren kaum produktnahe End-to-End-PQC-Implementationen, weil die grossen Identity Provider (Google, Apple, Microsoft) noch klassisch signierte Tokens ausstellen und die mobilen Betriebssysteme keinen zuverlässigen Zugriff auf TLS-Cipher-Suite-Negotiation erlauben.

### 1.2 Lösungsansatz

Das Projekt entwirft und implementiert einen PQC-basierten Authentifizierungs- und Verschlüsselungs-Stack für eine mobile React-Native-Demo-App, der:

- post-quantum-sichere Authentifizierungs-Tokens (ML-DSA-65) ausstellt
- post-quantum-sichere End-to-End-Verschlüsselung der Kommunikation zwischen App und Backend ermöglicht (ML-KEM-768 für Session-Establishment, AES-256-GCM für Payloads)
- klassische externe OIDC-Provider (Google, Microsoft) als Auth-Quellen einbindet ("Identity Broker / PQ-Uplift Pattern")
- Crypto-Agility als zentrales Architektur-Prinzip implementiert, sodass Algorithmen ohne Code-Änderungen austauschbar sind

### 1.3 Abgrenzung

Das Projekt ist explizit kein Production-System. Es ist eine Schul-Semesterarbeit mit demonstrativem Charakter. Folgende Aspekte sind bewusst nicht im Scope:

- Externes Security-Audit oder formelle Verifikation
- Skalierungs- und Hochverfügbarkeits-Architektur
- Self-Service-User-Management (Signup, Passwort-Reset, Email-Verifikation)
- Voller standardkonformer OIDC-Provider (verworfen zugunsten von Option 3, siehe `03_entscheidung_auth_architektur.md`)
- Compliance-Zertifizierungen (DSGVO, eIDAS, etc.)

---

## 2. Stakeholder und Projekt-Ziele

### 2.1 Stakeholder

| Stakeholder | Rolle | Hauptinteresse |
|---|---|---|
| **Dodoe Rumiñahui Mannale** | Entwickler, Autor der Arbeit | Erfolgreicher Abschluss der Semesterarbeit, persönlicher Lerneffekt im PQC-Bereich, Aufbau zukünftig nutzbarer Architektur-Erfahrung |
| **Dozent (TBZ)** | Bewerter | Nachvollziehbare Architektur, sauber dokumentierte Entscheidungen, korrekte Anwendung der NIST-PQC-Standards, klare Trennung von Bewährtem und Innovation |
| **Fiktive End-User der Mock-App** | Persona | Einfache Bedienung (Login mit Email/Passwort oder Login mit Google/Microsoft), unsichtbare Verschlüsselung |
| **Future Maintainer** | Zukünftiger Entwickler (Dodoe in 6 Monaten oder Industrie-Engineer) | Verständliche Architektur, austauschbare Algorithmen, erweiterbare IdP-Registry |
| **Externe Identity Provider** | Google, Microsoft | Standardkonforme OIDC-Client-Integration durch unseren Auth-Service |
| **Standards-Bodies (NIST, IETF)** | Indirekte Stakeholder | Korrekte Anwendung der definierten Algorithmen und Protokolle |

### 2.2 Projekt-Ziele

**G-1: PQC-Demonstration in produktnahem Kontext.**
Das Projekt zeigt, wie NIST-PQC-Standards (FIPS 203, FIPS 204) in einem realistischen Mobile-Auth-Szenario implementiert werden können. Es ist keine reine Algorithmus-Demo, sondern ein vertikaler Schnitt durch eine vollständige Architektur.

**G-2: End-to-End PQ-Sicherheit der Kommunikation.**
Nach erfolgreichem Login ist die gesamte Kommunikation zwischen Mobile App und Backend post-quantum-verschlüsselt. Auch ein Angreifer, der Verkehr aufzeichnet und in 10 Jahren einen Quantencomputer hat, kann die Nutzdaten nicht entschlüsseln.

**G-3: Identity-Broker-Pattern für Übergangsphase.**
Die Architektur akzeptiert klassische Identitäts-Claims von externen OIDC-Providern (Google, Microsoft) und überführt diese in eine PQ-sichere Session ("PQ-Uplift"). Damit ist die Lösung in der Übergangsphase 2026-2030 produktiv einsetzbar, in der externe IdPs noch klassisch arbeiten.

**G-4: Crypto-Agility als Architektur-Prinzip.**
Alle Krypto-Operationen laufen durch eine zentrale Abstraction Layer. Algorithmen sind als Plugins in einer Registry verwaltet. Ein zukünftiger Algorithmus-Wechsel (z.B. von ML-KEM-768 zu ML-KEM-1024 oder zu einem neuen NIST-Standard) erfordert nur Konfigurations-Änderungen, keine Code-Änderungen am Application-Code.

**G-5: Vollständige Projekt-Dokumentation.**
Das Projekt liefert nicht nur Code, sondern eine durchgehende Dokumentation: Architektur-Entscheidungen, Requirements, Tech-Stack-Begründungen, Design-Diagramme, Implementations-Notizen, Quellenverzeichnis. Diese Dokumentation ist die Hauptbewertungs-Grundlage für die Semesterarbeit.

### 2.3 Erfolgskriterien (auf Projekt-Ebene)

Das Projekt gilt als erfolgreich, wenn:

- die Mock-App sich sowohl mit lokalen Credentials als auch mit Google und Microsoft einloggen kann
- nach Login eine ML-KEM-768-basierte Session etabliert wird
- mindestens ein geschützter API-Call demonstriert wird, bei dem Payload AES-256-GCM-verschlüsselt mit einem aus ML-KEM-Shared-Secret abgeleiteten Schlüssel übertragen wird
- der eingesetzte Algorithmus (sowohl für KEM als auch für Signaturen) per Config umgeschaltet werden kann, ohne Application-Code zu verändern
- die Architektur und Implementation in Form eines Berichts und einer Präsentation dokumentiert sind, beides bis zur Abgabe (04-05.07.2026)

---

## 3. Use Cases

Jeder Use Case beschreibt ein konkretes Szenario im fertigen System. Aus diesen Use Cases werden in Phase 3 die Functional Requirements abgeleitet. Format pro Use Case: Priorität, Akteure, Beschreibung, Vorbedingungen, Hauptablauf, Alternativ-Abläufe, Fehler-Szenarien, Nachbedingungen, Acceptance Criteria.

Prioritäten-Schema: **Must** (für die Kernfunktion zwingend), **Should** (wichtig, aber nicht blockierend), **Could** (Stretch-Goal, wenn Zeit reicht).

---

### UC-1: Lokaler Login mit Email/Passwort

**Priorität:** Must

**Akteure**
- Primär: End-User der Mock-App
- Sekundär: Auth-Service (Local-Auth-Komponente)

**Beschreibung**
Ein registrierter User authentifiziert sich gegenüber dem Auth-Service mit Email und Passwort und erhält im Erfolgsfall einen ML-DSA-signierten Broker-Token.

**Vorbedingungen**
- User-Record existiert im lokalen User-Store
- Auth-Service ist erreichbar
- Mock-App hat eine aktive Internet-Verbindung

**Hauptablauf**
1. User öffnet die Mock-App und sieht den Login-Screen mit den Optionen [Email/Passwort, Google, Microsoft]
2. User wählt "Login mit Email/Passwort"
3. User gibt Email und Passwort ein und tippt auf "Anmelden"
4. App sendet `POST /auth/local/login` an den Auth-Service mit Body `{ email, password }`
5. Auth-Service holt den User-Record aus dem User-Store und vergleicht den Passwort-Hash (Argon2id)
6. Auth-Service generiert einen Broker-Token (ML-DSA-65 signiert) mit Claims `{ sub, iss, iat, exp, auth_method: "local" }`
7. Auth-Service antwortet mit `200 OK` und Body `{ broker_token, expires_in }`
8. App speichert den Token im sicheren Speicher (Keychain/Keystore)
9. App navigiert zum Home-Screen

**Alternativ-Abläufe**
Keine.

**Fehler-Szenarien**
- E-1: Falsche Credentials. Auth-Service antwortet `401 Unauthorized` mit Body `{ error: "invalid_credentials" }`. App zeigt eine generische Fehlermeldung.
- E-2: User-Record nicht gefunden. Auth-Service antwortet `401` mit identischem Body wie E-1, um User-Enumeration zu verhindern.
- E-3: Netzwerk-Fehler. App zeigt "Server nicht erreichbar".
- E-4: Auth-Service hat keinen aktiven Signier-Schlüssel. `500 Internal Server Error`. App zeigt allgemeine Fehlermeldung.

**Nachbedingungen**
- Erfolg: App besitzt einen gültigen Broker-Token, User ist als `auth_method=local` markiert
- Misserfolg: kein Token vorhanden, klare Fehlermeldung in der UI

**Acceptance Criteria**
- Erfolgreicher Login liefert einen Token, der mit dem Public-Key des Auth-Service ML-DSA-verifizierbar ist
- Token-Payload enthält die Claims `sub`, `iss`, `iat`, `exp`, `auth_method: "local"`
- Falsche Credentials und nicht-existierender User liefern identische `401`-Responses (kein User-Enumeration)
- Passwort-Hashes nutzen Argon2id mit den empfohlenen Parametern (m=64MB, t=3, p=4)

---

### UC-2: Login mit Google (Federated)

**Priorität:** Must

**Akteure**
- Primär: End-User der Mock-App
- Sekundär: Google OIDC OP, Auth-Service (Broker-Komponente)

**Beschreibung**
Ein User authentifiziert sich bei Google via OIDC Authorization Code Flow mit PKCE. Der Auth-Service verifiziert das Google-ID-Token und stellt einen eigenen ML-DSA-signierten Broker-Token aus.

**Vorbedingungen**
- Auth-Service ist bei Google als OIDC-Client registriert (client_id, redirect_uri konfiguriert)
- User hat ein Google-Konto
- Mock-App hat eine aktive Internet-Verbindung

**Hauptablauf**
1. User wählt "Login mit Google" im Login-Screen
2. App generiert PKCE `code_verifier` und `code_challenge`, sowie einen `state`-Parameter
3. App öffnet einen Browser-Tab mit Google's `/authorize`-URL inklusive `code_challenge` und `state`
4. User authentifiziert sich bei Google (Google-eigene Login-UI, ggf. mit 2FA)
5. Google leitet zurück zur App-redirect-URI mit `code` und `state`
6. App validiert den `state`-Parameter, sendet `POST /auth/federated/google/callback` mit `{ code, code_verifier }` an den Auth-Service
7. Auth-Service tauscht `code` plus `code_verifier` gegen Google-Tokens via Google's `/token`-Endpoint
8. Auth-Service verifiziert das Google-ID-Token: Signatur gegen Google-JWKS, Ablaufzeit, Issuer, Audience
9. Auth-Service mapped den Google-`sub` auf einen internen `user_id` (legt einen neuen Record an, falls nicht vorhanden)
10. Auth-Service generiert einen Broker-Token (ML-DSA-65) mit Claims `{ sub: internal_user_id, iss, iat, exp, auth_method: "google", external_sub: google_sub }`
11. Auth-Service antwortet mit `200 OK` und Body `{ broker_token, expires_in }`
12. App speichert den Token, navigiert zum Home-Screen

**Alternativ-Abläufe**
- Alt-4a: User bricht den Google-Login ab. Google leitet zurück mit einem Error-Parameter. App zeigt "Login abgebrochen" und kehrt zum Login-Screen zurück.

**Fehler-Szenarien**
- E-1: State-Mismatch (möglicher CSRF-Angriff). App lehnt den Callback ab und zeigt einen Sicherheitsfehler.
- E-2: Google liefert einen Error-Code im Callback. Auth-Service antwortet `400 Bad Request`. App zeigt die entsprechende Meldung.
- E-3: Auth-Service kann das Google-Token nicht verifizieren (Signatur stimmt nicht, Token abgelaufen). `401 Unauthorized`. App zeigt "Federation fehlgeschlagen".
- E-4: Google-JWKS-Endpoint nicht erreichbar. `503 Service Unavailable`. App zeigt "Vorübergehender Fehler".

**Nachbedingungen**
- Erfolg: App besitzt einen Broker-Token, lokaler User-Record ist mit dem Google-`sub` verknüpft
- Misserfolg: kein Token, User-Record bleibt unverändert

**Acceptance Criteria**
- Erster Login eines Google-Users legt einen User-Record an, mit Claim `auth_method: "google"`
- Wiederholter Login derselben Google-Identität führt zu demselben internen `user_id`
- PKCE wird durchgängig eingesetzt (kein `client_secret` in der mobilen App)
- Das Google-Token wird nicht persistiert, nur der eigene Broker-Token wird an die App ausgegeben
- Der `state`-Parameter hat mindestens 128 Bit Entropie und ist pro Login-Versuch eindeutig

---

### UC-3: Login mit Microsoft (Federated)

**Priorität:** Should

**Akteure**
- Primär: End-User der Mock-App
- Sekundär: Microsoft Entra OIDC OP, Auth-Service (Broker-Komponente)

**Beschreibung**
Analog UC-2, aber mit Microsoft Entra (Azure AD) als externem IdP.

**Vorbedingungen**
- Auth-Service ist bei Microsoft als OIDC-Client registriert
- User hat ein Microsoft-Konto (persönliches Microsoft-Konto oder Microsoft-365-Account)
- Mock-App hat eine aktive Internet-Verbindung

**Hauptablauf**
Strukturell identisch mit UC-2, mit folgenden Unterschieden:
- Endpunkte: Microsoft `/authorize`, `/token` und `/jwks` (aus Discovery-Dokument `https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration` ermittelt)
- Claim-Mapping: Microsoft-`oid` (Object ID) statt `sub` als external identifier (Microsoft-Spezifikum)
- Tenant: `common` (akzeptiert sowohl Privat- als auch Geschäftskonten)
- Broker-Token-Claim `auth_method: "microsoft"`

**Alternativ-Abläufe**
Wie UC-2.

**Fehler-Szenarien**
Wie UC-2, plus:
- E-5: Microsoft Token enthält keinen `oid`-Claim (unerwartete Token-Struktur). `400 Bad Request`, klare Log-Meldung.

**Nachbedingungen**
- Erfolg: App besitzt einen Broker-Token, User-Record ist mit der Microsoft-`oid` verknüpft

**Acceptance Criteria**
- Wie UC-2, plus:
- Tenant-Handling: Auth-Service akzeptiert das `common`-Tenant-Endpoint
- Claim `auth_method: "microsoft"` wird korrekt gesetzt
- Microsoft-`oid` wird als external identifier verwendet, nicht `sub`

---

### UC-4: Etablierung der PQ-Session nach Login

**Priorität:** Must

**Akteure**
- Primär: Mock-App (authentifizierter User)
- Sekundär: Auth-Service (Session-Manager-Komponente)

**Beschreibung**
Nach erfolgreichem Login etabliert die App eine post-quantum-sichere Session mit dem Backend via ML-KEM-768-Handshake. Aus dem geteilten Geheimnis wird ein AES-256-GCM-Session-Key abgeleitet.

**Vorbedingungen**
- App besitzt einen gültigen Broker-Token (aus UC-1, UC-2 oder UC-3)
- Auth-Service hat den Algorithmus "ML-KEM-768" in seiner Algorithmus-Registry

**Hauptablauf**
1. App generiert ein ML-KEM-768-Keypair (`pk_app`, `sk_app`)
2. App sendet `POST /session/init` mit Header `Authorization: Bearer <broker_token>` und Body `{ kem_alg: "ML-KEM-768", encapsulation_key: <pk_app base64> }`
3. Auth-Service verifiziert den Broker-Token (ML-DSA-Signatur, Ablaufzeit)
4. Auth-Service prüft `kem_alg` gegen die Algorithmus-Registry und akzeptiert "ML-KEM-768"
5. Auth-Service ruft `Encaps(pk_app)` auf und erhält `(ciphertext, shared_secret)`
6. Auth-Service generiert eine `session_id` (UUID v4)
7. Auth-Service leitet ab: `session_key = HKDF(shared_secret, info="app-session-v1", salt=session_id)`
8. Auth-Service speichert `{session_id, session_key, user_id, expires_at}` im Session-Store
9. Auth-Service antwortet mit `200 OK` und Body `{ session_id, ciphertext, expires_in }`
10. App ruft `Decaps(ciphertext, sk_app)` auf und erhält dasselbe `shared_secret`
11. App leitet `session_key = HKDF(shared_secret, info="app-session-v1", salt=session_id)` ab
12. App hält `session_id` und `session_key` ausschliesslich im Arbeitsspeicher (nicht persistiert)

**Alternativ-Abläufe**
- Alt-4a: Algorithmus-Negotiation. Falls der Auth-Service den angefragten `kem_alg` nicht unterstützt, antwortet er mit `406 Not Acceptable` und Body `{ supported_algorithms: ["ML-KEM-768", ...] }`. App wählt einen unterstützten Algorithmus und sendet erneut.

**Fehler-Szenarien**
- E-1: Broker-Token ungültig (abgelaufen, falsche Signatur). `401 Unauthorized`. App leitet zu Re-Authentication weiter (siehe UC-6).
- E-2: KEM-Algorithmus nicht unterstützt. `406 Not Acceptable` mit Liste unterstützter Algorithmen.
- E-3: `Encaps`-Operation schlägt unerwartet fehl. `500 Internal Server Error`. Server-seitig geloggt.
- E-4: Session-Store nicht erreichbar (z.B. Redis down). `503 Service Unavailable`.

**Nachbedingungen**
- Erfolg: App und Auth-Service teilen denselben `session_key`. Session-Record existiert mit TTL.
- Misserfolg: kein Session-Record vorhanden, klare Fehlermeldung in der UI.

**Acceptance Criteria**
- App-Layer-PQ-Session wird in unter 500ms etabliert (Bedingung: lokales Netzwerk, gemessen am Server)
- `session_key` ist auf App- und Server-Seite bit-identisch (testbar via dedicated Echo-Endpoint mit XOR-Vergleich)
- Session läuft nach konfiguriertem TTL ab (Default: 15 Minuten). Nachfolgende Requests mit derselben `session_id` werden mit `401` abgewiesen.
- `session_key` wird zu keinem Zeitpunkt persistiert, weder serverseitig (nur In-Memory / TTL-Cache) noch im App-Storage

---

### UC-5: Geschützter API-Call über die PQ-Session

**Priorität:** Must

**Akteure**
- Primär: Mock-App (mit etablierter Session)
- Sekundär: Auth-Service (Resource-Server-Komponente)

**Beschreibung**
Die App ruft einen geschützten API-Endpoint auf. Der Payload wird mit AES-256-GCM verschlüsselt unter Verwendung des `session_key` aus UC-4.

**Vorbedingungen**
- App und Auth-Service haben eine etablierte PQ-Session (UC-4 erfolgreich)
- Session ist nicht abgelaufen

**Hauptablauf**
1. App will einen API-Call zu `/api/profile` machen
2. App generiert eine frische 96-bit Nonce (per CSPRNG)
3. App verschlüsselt das Request-Payload (z.B. `{}` für GET-Analog) mit AES-256-GCM unter Verwendung von `session_key` und Nonce
4. App sendet `POST /api/profile` mit den Headers `X-Session-Id: <session_id>` und `X-Nonce: <base64-nonce>`, Body ist `<ciphertext+auth_tag>`
5. Auth-Service liest die `session_id` aus dem Header, holt den `session_key` aus dem Session-Store
6. Auth-Service entschlüsselt den Body mit AES-256-GCM und prüft den Authentication Tag
7. Auth-Service verarbeitet den Request (z.B. lädt das User-Profil aus der DB)
8. Auth-Service verschlüsselt das Response-Payload (`{ user_id, email, auth_method, created_at }`) mit AES-256-GCM und einer frischen Nonce
9. Auth-Service sendet `200 OK` mit Header `X-Nonce: <new-nonce>` und verschlüsseltem Body

**Alternativ-Abläufe**
Keine.

**Fehler-Szenarien**
- E-1: `session_id` unbekannt oder abgelaufen. `401 Unauthorized` (Antwort im Klartext, da Session-Key nicht ableitbar). App leitet zu UC-4 weiter.
- E-2: Authentication Tag passt nicht (möglicher Tampering-Versuch). `400 Bad Request`. Vorfall wird serverseitig in einem Security-Log festgehalten.
- E-3: Decrypted Payload ist kein valides JSON. `400 Bad Request`, klare Log-Meldung.

**Nachbedingungen**
- Erfolg: App erhält die entschlüsselte Response, hat die angefragten Daten
- Misserfolg: keine Daten erhalten, klare Fehlermeldung oder Re-Auth-Trigger

**Acceptance Criteria**
- Verschlüsselte Payloads sind im Wireshark-Capture nicht als Klartext erkennbar (manuelle Verifikation während der Demo)
- Jeder Request und jede Response verwendet eine unique Nonce (testbar durch Replay-Versuch)
- Falsche Tag-Verifikation führt zu sofortigem Abbruch ohne weitere Payload-Verarbeitung
- API-Endpoint liefert keine sensitiven Daten im Klartext zurück, selbst bei Tag-Fehler

---

### UC-6: Token-Ablauf und Re-Authentication

**Priorität:** Should

**Akteure**
- Primär: End-User (oder App-Logik im Hintergrund)
- Sekundär: Auth-Service

**Beschreibung**
Wenn der Broker-Token oder die PQ-Session abläuft, wird der User in einen sauberen Re-Authentication-Flow geleitet.

**Vorbedingungen**
- App hat einen abgelaufenen Token oder eine abgelaufene Session

**Hauptablauf**
1. App versucht einen API-Call (UC-5)
2. Auth-Service antwortet `401 Unauthorized` mit Body `{ error: "session_expired" }` oder `{ error: "token_expired" }`
3. App erkennt die `401`-Response und löscht den lokalen Token sowie Session-Key
4. App navigiert zurück zum Login-Screen, zeigt Hinweis "Bitte erneut anmelden"
5. User durchläuft UC-1, UC-2 oder UC-3 erneut
6. App durchläuft UC-4 (Session-Etablierung)
7. App wiederholt den ursprünglichen API-Call mit den neuen Credentials

**Alternativ-Abläufe**
- Alt-1a: Soft-Expiry. App prüft den `exp`-Claim des Tokens lokal und initiiert Re-Auth proaktiv, bevor ein `401` zurückkommt.

**Fehler-Szenarien**
- E-1: User bricht Re-Login ab. App zeigt einen "Login erforderlich"-Bildschirm und blockiert Zugriff auf den Home-Screen.

**Nachbedingungen**
- Erfolg: frische Auth und Session etabliert, ursprünglicher API-Call erfolgreich abgeschlossen
- Misserfolg: User bleibt im Login-Zustand

**Acceptance Criteria**
- App speichert keine abgelaufenen Tokens oder Session-Keys (testbar durch Inspizieren des Secure Storage nach `401`)
- Jede `401`-Response triggert einen Re-Auth-Flow, niemals stillschweigendes Wegwerfen
- User-Experience bleibt verständlich (klare Meldung warum erneut eingeloggt werden muss)

---

### UC-7: Algorithmus-Wechsel via Config (Crypto-Agility-Demonstration)

**Priorität:** Must

**Akteure**
- Primär: Operator (Dodoe im Demo-Modus)
- Sekundär: Auth-Service

**Beschreibung**
Der eingesetzte KEM-Algorithmus wird per Konfigurations-Änderung von ML-KEM-768 auf einen anderen Algorithmus umgeschaltet. Der Application-Code im Auth-Service wird dabei nicht verändert. Diese Demonstration ist der zentrale Beweis für die Crypto-Agility-Eigenschaft der Architektur.

**Vorbedingungen**
- Auth-Service hat mindestens zwei KEM-Algorithmen in der Registry registriert (z.B. ML-KEM-768 und ML-KEM-1024)
- Auth-Service läuft mit aktueller Config `crypto.kem.default = "ML-KEM-768"`

**Hauptablauf**
1. Operator ändert in `config.yaml` den Wert `crypto.kem.default` von `"ML-KEM-768"` auf `"ML-KEM-1024"`
2. Operator startet den Auth-Service neu (oder triggert Config-Reload, falls implementiert)
3. Auth-Service lädt die Config und prüft `crypto.kem.default` gegen die Algorithmus-Registry
4. App versucht eine neue Session zu etablieren via UC-4 mit `kem_alg: "ML-KEM-768"` (App weiss noch nicht von der Änderung)
5. Auth-Service antwortet mit `406 Not Acceptable` und Body `{ supported_algorithms: ["ML-KEM-1024"] }`
6. App nutzt nun `ML-KEM-1024` für die Session-Etablierung
7. Session-Etablierung gelingt mit dem neuen Algorithmus

**Alternativ-Abläufe**
- Alt-2a: Hot-Reload. Falls der Auth-Service Config-Hot-Reload unterstützt, kein Restart nötig.

**Fehler-Szenarien**
- E-1: Konfigurierter Algorithmus nicht in der Registry. Auth-Service verweigert den Start und loggt eine klare Fehlermeldung ("Configured algorithm 'X' not found in registry").

**Nachbedingungen**
- Erfolg: nach dem Restart läuft der Auth-Service mit dem neuen Default-Algorithmus, neue Sessions verwenden den neuen Algorithmus, der Application-Code im Auth-Service ist unverändert
- Misserfolg: Service startet nicht, Config muss korrigiert werden

**Acceptance Criteria**
- Demonstration kann live im Bewertungs-Termin gezeigt werden
- Diff zwischen alter und neuer Konfiguration umfasst nur Config-Dateien (z.B. `config.yaml`), keine `.py`-Dateien
- Die App muss kein Update bekommen, sondern erkennt die Algorithmus-Änderung allein über die Negotiation-Response
- Im Bericht wird die Live-Demo durch ein dokumentiertes Vorher-Nachher-Diff der Config-Files unterstützt

---

### UC-8: Neuer externer IdP wird hinzugefügt (Erweiterbarkeit)

**Priorität:** Could (Stretch-Goal)

**Akteure**
- Primär: Operator
- Sekundär: Auth-Service

**Beschreibung**
Ein neuer externer OIDC-Provider (z.B. Apple Sign In) wird zur IdP-Registry hinzugefügt, ohne Änderungen an der bestehenden Architektur oder am bestehenden Provider-Code.

**Vorbedingungen**
- Apple-Sign-In-OIDC-Client ist bei Apple registriert (client_id, redirect_uri)
- Apple's OIDC-Discovery-Endpoint ist erreichbar

**Hauptablauf**
1. Operator legt eine neue Konfig-Sektion `idp_providers.apple` an mit `{ client_id, redirect_uri, discovery_url, scopes, claim_mapping }`
2. Operator registriert in der IdP-Registry einen neuen Eintrag `"apple" → AppleProvider` (Provider-Klasse implementiert ein gemeinsames Interface)
3. Auth-Service wird neu gestartet
4. App-UI bekommt einen neuen Button "Login mit Apple" (manuelles App-Update mit neuer Provider-Konfig)
5. UC-2 bzw. UC-3 Flow wird für Apple analog ausgeführt

**Alternativ-Abläufe**
Keine.

**Fehler-Szenarien**
- E-1: Apple-Discovery-Endpoint beim Start nicht erreichbar. Auth-Service loggt eine Warnung, die anderen IdPs funktionieren trotzdem (defensive Initialisierung pro Provider).
- E-2: Claim-Mapping fehlerhaft. Apple-Login liefert ein Token mit unerwarteter Claim-Struktur. Auth-Service antwortet mit `400`, klare Log-Meldung mit dem fehlenden Claim-Pfad.

**Nachbedingungen**
- Erfolg: Apple-Login funktioniert end-to-end. Bestehende Provider (Google, Microsoft) sind unverändert funktionsfähig.
- Misserfolg: Apple-Login schlägt fehl, andere Provider unverändert.

**Acceptance Criteria**
- Diff zwischen alter und neuer Architektur umfasst nur den neuen Plugin-Eintrag und die Konfig, keine Code-Änderungen an Google- oder Microsoft-Provider
- Apple-User können sich einloggen und die Mock-App in vollem Umfang nutzen
- Demonstrierbar im Bewertungs-Termin (sofern Apple als Stretch-Goal implementiert wird)

---

## 4. Functional Requirements

Aus den Use Cases abgeleitet, gruppiert nach Architektur-Komponente. Jeder FR hat eine eindeutige ID, eine Priorität und eine Trace-Referenz zu den UCs, aus denen er abgeleitet ist.

Gruppen:

- **FR-Auth-X**: Custom-Auth-Logik (lokaler User-Store)
- **FR-Broker-X**: OIDC-Client-Logik (Federation mit Google und Microsoft)
- **FR-Token-X**: Token-Ausstellung und -Verifikation
- **FR-Session-X**: PQ-Session-Etablierung
- **FR-DataChannel-X**: Verschlüsselter Daten-Kanal
- **FR-Crypto-X**: Crypto-Abstraction-Layer

---

### 4.1 FR-Auth: Custom-Auth-Logik

#### FR-Auth-1: User-Authentifizierung via Email und Passwort

**Priorität:** Must

**Beschreibung**
Das System authentifiziert User anhand von Email und Passwort gegen einen lokalen User-Store mit Argon2id-gehashten Passwörtern.

**Vorbedingungen**
- User-Record existiert im User-Store mit gespeichertem Argon2id-Hash
- Auth-Service läuft und ist erreichbar

**Nachbedingungen**
- Erfolg: User-Identität ist verifiziert, interne `user_id` ist verfügbar für nachfolgende Token-Ausstellung
- Misserfolg: System antwortet mit `401`, keine Identitäts-Information wird ausgegeben

**Fehler-Szenarien**
- Falsche Credentials: Response `401` mit generischer Fehlermeldung
- User nicht gefunden: Response `401` mit identischer Antwort (kein User-Enumeration)
- User-Store-Fehler: Response `500`

**Acceptance Criteria**
- Passwort-Vergleich erfolgt mit konstanter Zeit (Argon2id verify, timing-attack-resistant)
- Argon2id-Parameter: m=64MB, t=3, p=4
- Bei falscher Eingabe enthält die Response keine Hinweise auf User-Existenz oder fehlerhaftes Feld

**Abgeleitet aus:** UC-1

---

#### FR-Auth-2: User-Provisioning via Admin-CLI

**Priorität:** Must

**Beschreibung**
Das System bietet eine Admin-CLI zur Anlage von Test-Usern. Im Schulprojekt-Kontext gibt es keinen Self-Service-Signup; User werden vor dem Demo-Termin geseeded.

**Vorbedingungen**
- Operator hat CLI-Zugriff auf den Server
- Keine bestehende User-Record-Konflikte

**Nachbedingungen**
- Neuer User-Record existiert im User-Store mit Argon2id-gehashtem Passwort

**Fehler-Szenarien**
- Email bereits vorhanden: CLI gibt Fehler zurück, kein Überschreiben
- Schwaches Passwort: CLI warnt, akzeptiert es aber (kein Production-Validator)

**Acceptance Criteria**
- Mindestens 2-3 Test-User können vor dem Demo geseeded werden
- Passwörter werden ausschliesslich Argon2id-gehasht gespeichert, niemals im Klartext
- CLI ist via `docker compose exec` oder lokales Python-Skript aufrufbar

**Abgeleitet aus:** UC-1 (als Vorbedingung)

---

### 4.2 FR-Broker: OIDC-Client-Logik (Federation)

#### FR-Broker-1: External-IdP-Registry mit Plugin-Architektur

**Priorität:** Must

**Beschreibung**
Das System verwaltet externe OIDC-Provider in einer Registry als austauschbare Plugins. Jeder Provider implementiert ein gemeinsames Provider-Interface mit Methoden wie `discover()`, `verify_token()` und `map_claims()`.

**Vorbedingungen**
- Provider-Konfiguration ist verfügbar (Config-File)
- Provider-Klasse ist im Code registriert

**Nachbedingungen**
- Registry ist initialisiert mit allen konfigurierten Providern
- Provider sind zur Laufzeit per Name abrufbar

**Fehler-Szenarien**
- Provider fehlerhaft konfiguriert (z.B. fehlende client_id): Service-Start verweigert mit klarer Meldung
- Provider-Discovery-Endpoint beim Start nicht erreichbar: Provider als "degraded" markiert, andere Provider funktionieren weiter

**Acceptance Criteria**
- Mindestens 2 Provider in der Registry initialisierbar (Google und Microsoft)
- Neuer Provider hinzufügen erfordert nur einen neuen Plugin-Eintrag plus Konfig, keine Änderungen am bestehenden Provider-Code
- Provider-Lookup-Latenz vernachlässigbar (Dictionary-Lookup, unter 1ms)

**Abgeleitet aus:** UC-2, UC-3, UC-8

---

#### FR-Broker-2: OIDC Authorization Code Flow mit PKCE

**Priorität:** Must

**Beschreibung**
Das System implementiert den OIDC Authorization Code Flow mit PKCE (Proof Key for Code Exchange, RFC 7636) als OIDC-Client gegenüber externen IdPs.

**Vorbedingungen**
- IdP ist in der Registry vorhanden und konfiguriert
- App hat ein gültiges `state` und PKCE-`code_verifier`/`code_challenge` generiert

**Nachbedingungen**
- System hat einen vom IdP ausgestellten Access- und ID-Token erhalten

**Fehler-Szenarien**
- `state`-Mismatch im Callback (möglicher CSRF): Abbruch mit klarer Fehlermeldung
- Code-Exchange beim IdP fehlgeschlagen: Response `400` mit Provider-Fehler im Log
- Discovery-Endpoint nicht erreichbar: Response `503`

**Acceptance Criteria**
- PKCE wird durchgängig verwendet mit `code_challenge_method=S256`
- `state`-Parameter hat mindestens 128 Bit Entropie und ist pro Login-Versuch eindeutig
- `client_secret` wird ausschliesslich im Backend gehalten, nie an die mobile App ausgeliefert

**Abgeleitet aus:** UC-2, UC-3

---

#### FR-Broker-3: ID-Token-Verifikation gegen IdP-JWKS

**Priorität:** Must

**Beschreibung**
Das System verifiziert eingehende ID-Tokens externer IdPs gegen deren JWKS-Endpoint. Geprüft werden: Signatur, Issuer, Audience, Ablaufzeit und Not-Before-Time.

**Vorbedingungen**
- ID-Token ist vorhanden (aus FR-Broker-2)
- JWKS ist gecached oder Live-Fetch ist möglich

**Nachbedingungen**
- Erfolg: Token-Claims sind verifiziert und auslesbar
- Misserfolg: Verifikation schlägt fehl, Request wird abgewiesen

**Fehler-Szenarien**
- Signatur ungültig: `401`
- Token abgelaufen, falscher Issuer oder falsche Audience: `401`
- JWKS-Endpoint nicht erreichbar UND Cache leer: `503`

**Acceptance Criteria**
- JWKS wird gecached mit angemessenem TTL (z.B. 1h), kein Refetch bei jedem Login
- Bei JWKS-Endpoint-Fehler greift Cache (graceful degradation), Service bleibt funktionsfähig
- Signatur-Verifikation klappt für RS256 und ES256 (die von Google/Microsoft genutzten Algorithmen)

**Abgeleitet aus:** UC-2, UC-3

---

#### FR-Broker-4: Identity-Normalisierung (External Sub zu Internal User ID)

**Priorität:** Must

**Beschreibung**
Das System mapped externe Identitäts-Claims (z.B. Google-`sub`, Microsoft-`oid`) auf eine einheitliche interne `user_id`. Beim ersten Login eines externen Users wird ein neuer User-Record angelegt.

**Vorbedingungen**
- Externes Token ist verifiziert (FR-Broker-3)
- Claim-Mapping für den Provider ist konfiguriert

**Nachbedingungen**
- Interne `user_id` ist verfügbar
- Bei erstem Login: neuer User-Record im User-Store angelegt
- Bei wiederholtem Login: bestehender User-Record gefunden

**Fehler-Szenarien**
- Erwarteter Claim fehlt im Token (z.B. kein `oid` von Microsoft): `400` mit klarer Log-Meldung
- User-Store nicht erreichbar: `503`

**Acceptance Criteria**
- Wiederholter Login derselben externen Identität führt immer zum selben internen `user_id`
- Claim-Mapping ist pro Provider konfigurierbar (Provider-spezifische Eigenheiten wie Microsoft-`oid` vs Google-`sub`)
- Erster Login legt User-Record mit Claim `auth_method` automatisch an

**Abgeleitet aus:** UC-2, UC-3, UC-8

---

### 4.3 FR-Token: Token-Ausstellung und -Verifikation

#### FR-Token-1: Broker-Token-Ausstellung mit ML-DSA-Signatur

**Priorität:** Must

**Beschreibung**
Nach erfolgreicher Authentifizierung (lokal oder federated) stellt das System einen eigenen Broker-Token aus, signiert mit ML-DSA-65 gemäss FIPS 204.

**Vorbedingungen**
- User-Identität ist verifiziert (durch FR-Auth-1 oder FR-Broker-4)
- Aktiver Signier-Schlüssel ist verfügbar

**Nachbedingungen**
- Signierter Broker-Token ist verfügbar und an die App ausgeliefert

**Fehler-Szenarien**
- Signier-Schlüssel nicht verfügbar: `500`, Service-Logging

**Acceptance Criteria**
- Token enthält die Pflicht-Claims: `sub`, `iss`, `iat`, `exp`, `auth_method`
- Token-Header enthält `alg` (z.B. "ML-DSA-65") und `kid` (Key ID für Rotation)
- Signatur ist mit dem entsprechenden Public-Key verifizierbar (FR-Token-2)
- Token-TTL ist konfigurierbar, Default 1h

**Abgeleitet aus:** UC-1, UC-2, UC-3

---

#### FR-Token-2: Broker-Token-Verifikation

**Priorität:** Must

**Beschreibung**
Das System verifiziert eingehende Broker-Tokens stateless. Geprüft werden Signatur (via `kid`-spezifizierten Public-Key), Issuer und Ablaufzeit.

**Vorbedingungen**
- Token ist vorhanden im Request-Header
- Public-Key für `kid` ist im System bekannt

**Nachbedingungen**
- Erfolg: Token-Claims sind extrahiert und verifiziert
- Misserfolg: Request wird mit `401` abgewiesen

**Fehler-Szenarien**
- Signatur ungültig: `401`
- Token abgelaufen: `401` mit `error="token_expired"`
- Unbekannte `kid`: `401` mit klarer Log-Meldung
- Falscher Issuer: `401`

**Acceptance Criteria**
- Verifikation funktioniert ohne Datenbank-Lookup (stateless)
- Verifikations-Latenz unter 10ms (typisch für ML-DSA-65 verify)
- Fehlerhafte Tokens werden nicht im Klartext geloggt (nur Token-ID/Hash)

**Abgeleitet aus:** UC-4, UC-5, UC-6

---

#### FR-Token-3: Schlüssel-Rotation für Token-Signierung

**Priorität:** Must

**Beschreibung**
Das System unterstützt die Rotation des ML-DSA-Signier-Schlüssels. Alte Public-Keys bleiben für die TTL bereits ausgestellter Tokens verifizierbar.

**Vorbedingungen**
- Neuer ML-DSA-Schlüssel ist generiert

**Nachbedingungen**
- Neue Tokens werden mit dem neuen Schlüssel signiert
- Alte Tokens bleiben bis zu ihrem Ablauf verifizierbar

**Fehler-Szenarien**
- Rotation während aktiver Last: Tokens, die zwischen Generierung und Aktivierung ausgestellt wurden, dürfen nicht ungültig werden

**Acceptance Criteria**
- `kid` (Key ID) ist in jedem Token-Header
- Mehrere Public-Keys können parallel zur Verifikation verfügbar sein
- Rotation ist via CLI durchführbar (kein API-Endpoint nötig im Schul-Scope)
- Alte Public-Keys werden nach `(token-TTL + Sicherheits-Puffer)` aus der Verifikations-Liste entfernt

**Abgeleitet aus:** G-4 (Crypto-Agility-Ziel), indirekt UC-7

---

### 4.4 FR-Session: PQ-Session-Etablierung

#### FR-Session-1: ML-KEM-basierte Session-Etablierung

**Priorität:** Must

**Beschreibung**
Das System etabliert nach erfolgreicher Broker-Token-Verifikation eine PQ-Session via ML-KEM Encaps/Decaps gemäss FIPS 203. Default-Variante: ML-KEM-768.

**Vorbedingungen**
- Broker-Token ist valide (FR-Token-2)
- Angefragter KEM-Algorithmus ist in der Crypto-Abstraction-Layer-Registry (FR-Crypto-1)
- App hat ihr KEM-Keypair generiert und den Public-Key gesendet

**Nachbedingungen**
- Erfolg: Beide Seiten haben dasselbe `shared_secret`
- Misserfolg: Kein gemeinsames `shared_secret`, Session-Etablierung wird abgebrochen

**Fehler-Szenarien**
- KEM-Algorithmus nicht in Registry: `406` mit Liste unterstützter Algorithmen
- `Encaps`-Operation schlägt unerwartet fehl: `500`
- App-Public-Key hat falsche Länge oder Format: `400`

**Acceptance Criteria**
- Etablierung in unter 500ms auf lokalem Netzwerk (Mess-Punkt: Server-Eingang Request bis Server-Ausgang Response)
- `shared_secret` wird niemals übertragen, nur `encapsulation_key` und `ciphertext`
- ML-KEM-Operationen kommen aus auditierten Libraries (Server: liboqs-python, App: @noble/post-quantum)

**Abgeleitet aus:** UC-4

---

#### FR-Session-2: Session-Key-Ableitung via HKDF

**Priorität:** Must

**Beschreibung**
Aus dem `shared_secret` der KEM-Operation wird via HKDF (RFC 5869) ein 256-Bit Session-Key abgeleitet. Diese Trennung von KEM-Secret und Session-Key ist Standard-Praxis und ermöglicht zukünftige Erweiterungen (z.B. Hybrid mit klassischem ECDH).

**Vorbedingungen**
- `shared_secret` aus KEM ist verfügbar (FR-Session-1)
- `session_id` wurde generiert

**Nachbedingungen**
- 256-Bit Session-Key ist auf App- und Server-Seite bit-identisch

**Fehler-Szenarien**
- HKDF-Parameter mismatch zwischen Client und Server: Session-Key wäre unterschiedlich, alle nachfolgenden verschlüsselten Requests scheitern (manifestiert sich als `400` Tag-Fehler in FR-DataChannel-1)

**Acceptance Criteria**
- `info`-Parameter ist versioniert (z.B. `"app-session-v1"`) für Forward-Kompatibilität
- `salt` ist die `session_id` (eindeutig pro Session)
- HKDF-Hash-Algorithmus ist SHA-256
- Session-Key-Länge: 32 Bytes (256 Bit)

**Abgeleitet aus:** UC-4

---

#### FR-Session-3: Session-Store mit TTL

**Priorität:** Must

**Beschreibung**
Das System speichert aktive Sessions als Tupel `{session_id, session_key, user_id, expires_at, kem_alg}` mit Time-to-Live. Sessions werden nach Ablauf automatisch entfernt.

**Vorbedingungen**
- Keine

**Nachbedingungen**
- Aktive Sessions sind über `session_id` nachschlagbar
- Abgelaufene Sessions sind nicht mehr abrufbar

**Fehler-Szenarien**
- Session-Store nicht erreichbar (z.B. Redis down): `503`, Service-Logging

**Acceptance Criteria**
- Session-Keys werden nicht über Service-Restarts hinaus persistiert (In-Memory oder TTL-Cache)
- Default-TTL: 15 Minuten, konfigurierbar via Config-File
- Lookup-Latenz unter 5ms (auch bei vielen aktiven Sessions)

**Abgeleitet aus:** UC-4

---

#### FR-Session-4: Algorithmus-Negotiation

**Priorität:** Must

**Beschreibung**
Wenn der Client einen KEM-Algorithmus anfragt, der vom Server nicht unterstützt wird oder nicht der Default ist, antwortet der Server mit der Liste der aktuell unterstützten Algorithmen. Der Client kann darauf basierend einen neuen Request mit einem unterstützten Algorithmus stellen.

**Vorbedingungen**
- Crypto-Registry hat mindestens einen Algorithmus

**Nachbedingungen**
- Client kennt die unterstützten Algorithmen und kann den passenden wählen

**Fehler-Szenarien**
- Keine gemeinsamen Algorithmen zwischen Client und Server: Verbindung nicht etablierbar, Client muss aktualisiert werden

**Acceptance Criteria**
- Response-Code `406 Not Acceptable` mit Body `{ supported_algorithms: [...] }`
- Client kann auf Basis dieser Liste einen Retry machen, ohne App-Code-Änderung
- Implementiert den zentralen Mechanismus, der UC-7 (Algorithmus-Wechsel) ohne Code-Update auf der Client-Seite ermöglicht

**Abgeleitet aus:** UC-4 (Alt-4a), UC-7

---

### 4.5 FR-DataChannel: Verschlüsselter Daten-Kanal

#### FR-DataChannel-1: AES-256-GCM-Verschlüsselung für Payloads

**Priorität:** Must

**Beschreibung**
Alle Request- und Response-Payloads zwischen App und geschützten API-Endpoints werden mit AES-256-GCM verschlüsselt. Der Session-Key (FR-Session-2) wird als symmetrischer Schlüssel verwendet.

**Vorbedingungen**
- Etablierte PQ-Session mit gültigem `session_key`

**Nachbedingungen**
- Erfolg: Payload ist verschlüsselt übertragen und auf der Gegenseite korrekt entschlüsselbar
- Misserfolg: Authentication Tag passt nicht, Request wird abgewiesen

**Fehler-Szenarien**
- Authentication Tag ungültig: `400`, Vorfall im Security-Log
- Decrypted Payload ist kein valides JSON: `400`, klare Log-Meldung
- Nonce-Header fehlt oder ist nicht 96 Bit: `400`

**Acceptance Criteria**
- Frische 96-bit Nonce pro Nachricht, generiert via CSPRNG
- Nonces werden innerhalb einer Session nicht wiederverwendet (AES-GCM-Sicherheits-Anforderung)
- Wireshark-Capture zeigt keine Klartext-Payloads
- Verschlüsselungs-Overhead pro Nachricht: 28 Bytes (12 Nonce + 16 Tag)

**Abgeleitet aus:** UC-5

---

#### FR-DataChannel-2: Header-basiertes Session-Routing

**Priorität:** Must

**Beschreibung**
Eingehende verschlüsselte Requests tragen `session_id` und Nonce in HTTP-Headers (`X-Session-Id`, `X-Nonce`). Der Server nutzt die `session_id` um den passenden Session-Key aus dem Session-Store zu finden.

**Vorbedingungen**
- Etablierte Session (Session-Record im Store)

**Nachbedingungen**
- Server kann das Request-Payload entschlüsseln
- Response trägt eine eigene frische Nonce in `X-Nonce`

**Fehler-Szenarien**
- `X-Session-Id`-Header fehlt: `400`
- `X-Nonce`-Header fehlt oder hat falsche Länge: `400`
- `session_id` unbekannt oder Session abgelaufen: `401`

**Acceptance Criteria**
- Headers sind im Klartext übertragen (nur Routing-Information, keine Geheimnisse)
- Routing-Latenz vernachlässigbar (unter 1ms, Dictionary-Lookup)
- Korrupte oder gefälschte `session_id` führt zu sofortigem `401`, keine Token-Verifikation versucht

**Abgeleitet aus:** UC-5

---

### 4.6 FR-Crypto: Crypto-Abstraction-Layer

#### FR-Crypto-1: Algorithmus-Registry für KEM und Signatur

**Priorität:** Must

**Beschreibung**
Das System verwaltet eine Registry von Krypto-Algorithmen (KEM und Signatur). Jeder Algorithmus wird mit einem Namen, einer Implementation und Metadaten (Schlüssel-Längen, Output-Längen) registriert.

**Vorbedingungen**
- Plugins für mindestens je einen KEM- und einen Signatur-Algorithmus sind registriert

**Nachbedingungen**
- Registry ist initialisiert und zur Laufzeit abfragbar

**Fehler-Szenarien**
- Doppelter Eintrag (gleicher Name): Service-Start wird verweigert mit klarer Fehlermeldung
- Plugin lädt nicht (z.B. fehlende Library): Service-Start wird verweigert

**Acceptance Criteria**
- Mindestens 2 KEM-Algorithmen registriert (z.B. ML-KEM-768 und ML-KEM-1024) für Crypto-Agility-Demonstration
- Mindestens 1 Signatur-Algorithmus registriert (ML-DSA-65), erweiterbar
- Registry-Lookup zur Laufzeit erfolgt in unter 1ms (Dictionary-basiert)

**Abgeleitet aus:** G-4 (Crypto-Agility-Ziel), UC-7

---

#### FR-Crypto-2: Konfigurations-basierte Algorithmus-Auswahl

**Priorität:** Must

**Beschreibung**
Der Default-Algorithmus für jede Algorithmus-Kategorie (KEM, Signatur) ist via Konfigurations-File einstellbar. Application-Code referenziert niemals einen konkreten Algorithmus-Namen, sondern ruft die abstrakte Crypto-Layer-Schnittstelle auf.

**Vorbedingungen**
- Konfigurations-File ist vorhanden und parsbar
- Konfigurierter Algorithmus ist in der Registry (FR-Crypto-1)

**Nachbedingungen**
- System nutzt den konfigurierten Algorithmus für alle Crypto-Operationen

**Fehler-Szenarien**
- Konfigurierter Algorithmus nicht in Registry: Service-Start verweigert mit klarer Fehlermeldung ("Configured algorithm 'X' not found in registry")
- Konfigurations-File fehlt oder ist nicht parsbar: Service-Start verweigert

**Acceptance Criteria**
- Config-Change ohne Code-Change führt zu Algorithmus-Wechsel (Beweis für UC-7)
- Diff zwischen alter und neuer Konfiguration umfasst ausschliesslich Config-Files
- Application-Code-Suche nach konkreten Algorithmus-Namen (z.B. grep nach "ML-KEM-768" in .py-Files) findet keine Treffer ausserhalb der Crypto-Layer-Implementation

**Abgeleitet aus:** G-4, UC-7

---

#### FR-Crypto-3: Algorithmus-Identifier in allen Krypto-Artefakten

**Priorität:** Must

**Beschreibung**
Jedes Krypto-Artefakt (Token, Session-Record, verschlüsselte Nachricht, Handshake-Request) trägt einen Algorithmus-Identifier. Dadurch kann der Empfänger den passenden Algorithmus zur Verifikation oder Entschlüsselung wählen.

**Vorbedingungen**
- Keine

**Nachbedingungen**
- Empfänger kann basierend auf dem Algorithmus-Identifier die korrekte Operation auswählen

**Fehler-Szenarien**
- Algorithmus-Identifier fehlt im Artefakt: Request wird mit `400` abgewiesen (kein implizites Fallback)
- Identifier referenziert nicht-registrierten Algorithmus: `406` (für KEM) oder `401` (für Tokens)

**Acceptance Criteria**
- `alg`-Header in jedem Broker-Token (z.B. `"ML-DSA-65"`)
- `kem_alg`-Feld in jedem Session-Init-Request
- `kid`-Header in jedem Token (für Schlüssel-Auswahl bei Rotation)
- Konsistente Namens-Konventionen: NIST-Standardnamen (ML-KEM-768, ML-DSA-65) statt Legacy-Namen (Kyber, Dilithium)

**Abgeleitet aus:** G-4, alle PQ-bezogenen UCs (UC-1, UC-2, UC-3, UC-4, UC-5)

---

#### FR-Crypto-4: Hybrid-Key-Combiner

**Priorität:** Could (Stretch-Goal)

**Beschreibung**
Das System kombiniert den PQ-KEM-Shared-Secret mit einem klassischen ECDH-Shared-Secret (X25519) via HKDF zu einem hybriden Session-Key. Ein Angreifer müsste sowohl das PQ-Verfahren als auch das klassische Verfahren brechen, um den Session-Key zu kompromittieren.

**Vorbedingungen**
- Beide Schlüssel-Exchanges (ML-KEM und X25519) waren erfolgreich

**Nachbedingungen**
- Hybrid-Session-Key ist abgeleitet, verwendet beide Geheimnisse

**Fehler-Szenarien**
- Einer der Exchanges schlägt fehl: Gesamte Etablierung scheitert. Kein Downgrade auf ein einzelnes Verfahren zugelassen.

**Acceptance Criteria**
- HKDF-Eingabe: Konkatenation `ML-KEM-secret || X25519-secret`
- Eingebauter Schutz gegen Downgrade-Angriffe (Server verlangt immer beide oder lehnt ab)
- Bericht enthält Erklärung des Defense-in-Depth-Prinzips

**Abgeleitet aus:** G-2, UC-4 (als Stretch-Erweiterung)

---

## 5. Non-Functional Requirements

NFRs beschreiben Qualitäts-Eigenschaften, die das gesamte System betreffen, nicht einzelne Funktionen. Format pro NFR: Priorität, Beschreibung, Begründung, Acceptance Criteria (messbar oder klar prüfbar), Bezogen auf (Trace zu Zielen, UCs und FRs).

Gruppen:

- **NFR-Sec-X**: Sicherheits-Anforderungen
- **NFR-Perf-X**: Performance-Anforderungen
- **NFR-Maint-X**: Wartbarkeit und Crypto-Agility
- **NFR-Use-X**: Usability
- **NFR-Ops-X**: Logging und Monitoring
- **NFR-Doc-X**: Dokumentations-Anforderungen

---

### 5.1 NFR-Sec: Sicherheits-Anforderungen

#### NFR-Sec-1: Hybride PQ-Sicherheit auf Transport-Layer

**Priorität:** Must

**Beschreibung**
Der Auth-Service wird hinter nginx mit oqs-provider deployed, sodass TLS-Handshakes mit der hybriden NamedGroup `X25519MLKEM768` durchgeführt werden können.

**Begründung**
Defense-in-Depth-Prinzip: zusätzlich zur App-Layer-PQ-Verschlüsselung ist auch der Transport-Layer PQ-sicher abgesichert. Demonstriert die realistische Übergangs-Architektur, in der hybride TLS-Cipher-Suites schon ausgerollt werden, bevor reine PQ-Cipher-Suites stabil sind.

**Acceptance Criteria**
- `openssl s_client -groups X25519MLKEM768 -connect <host>:<port>` verbindet erfolgreich
- TLS-Verbindung kann im Bewertungs-Termin live demonstriert werden (z.B. mit Wireshark zur Bestätigung der Cipher-Suite)
- Im Bericht ist die Server-Konfiguration dokumentiert

**Bezogen auf:** G-1, G-2

---

#### NFR-Sec-2: Schutz vor Replay-Angriffen

**Priorität:** Must

**Beschreibung**
Jede verschlüsselte Nachricht muss eindeutig identifizierbar sein (frische Nonce pro Nachricht), um Replay-Angriffe zu verhindern.

**Begründung**
AES-GCM mit Nonce-Reuse ist katastrophal (Wiederverwendung führt zum Verlust der Vertraulichkeit). Replay-Angriffe sind ein Standard-Angriffsvektor und müssen explizit adressiert werden.

**Acceptance Criteria**
- Testbar durch Replay-Versuch: ein abgefangener und erneut gesendeter Request muss zumindest funktional erkennbar fehlschlagen
- Nonces werden via CSPRNG generiert (`/dev/urandom` oder Plattform-Äquivalent)
- Innerhalb einer Session-TTL (15 Min) ist die Wahrscheinlichkeit einer Nonce-Kollision verschwindend klein (96 Bit Entropie)

**Bezogen auf:** UC-5, FR-DataChannel-1

---

#### NFR-Sec-3: Kein Klartext für Geheimnisse

**Priorität:** Must

**Beschreibung**
Sensitive Daten (Passwörter, Session-Keys, Private-Keys, externe Tokens) dürfen niemals im Klartext geloggt, gespeichert oder über die Wire (ausserhalb der zugehörigen Verschlüsselung) übertragen werden.

**Begründung**
Klartext-Geheimnisse sind die häufigste Ursache für reale Sicherheitsvorfälle (Logs, Backups, Crash-Dumps, etc.).

**Acceptance Criteria**
- Passwörter: nur als Argon2id-Hash im User-Store, niemals im Klartext gespeichert
- Session-Keys: nur In-Memory im Auth-Service, niemals in Logs oder auf der Wire
- Externe ID-Tokens (Google, Microsoft): nicht persistiert nach Verifikation
- Private-Keys: in einem Key-Store oder Datei mit restriktiven File-Permissions, nicht in Git committed
- Log-Output enthält keine Klartext-Tokens, nur Hashes oder IDs

**Bezogen auf:** alle Sec-relevanten FRs

---

#### NFR-Sec-4: Schutz vor User-Enumeration

**Priorität:** Must

**Beschreibung**
Fehlermeldungen bei Login-Versuchen dürfen nicht enthüllen, ob ein User-Account existiert oder nicht.

**Begründung**
User-Enumeration ist eine typische Vorstufe für gezielte Angriffe (Brute-Force, Phishing). Identische Responses verhindern, dass ein Angreifer Account-Existenz inferieren kann.

**Acceptance Criteria**
- Falsche Credentials und nicht-existierender User liefern identische Responses (gleicher Status-Code, gleicher Body)
- Antwort-Zeit ist statistisch ähnlich (kein Timing-Channel-Angriff via Argon2id-Overhead vs Early-Exit)
- Federated Login: bei unbekannten externen Identitäten wird trotzdem geantwortet ohne anzudeuten, dass ein User-Mapping fehlt

**Bezogen auf:** FR-Auth-1, FR-Broker-4

---

#### NFR-Sec-5: Schutz vor CSRF in OIDC-Flows

**Priorität:** Must

**Beschreibung**
Der `state`-Parameter im OIDC Authorization Code Flow schützt vor CSRF-Angriffen. Der State-Wert muss im Callback verifiziert werden, sonst Abbruch.

**Begründung**
OIDC-Standard-Anforderung. Ohne State-Verifikation kann ein Angreifer einen Login-Flow auf einer fremden Identität abschliessen.

**Acceptance Criteria**
- State-Parameter wird vor Authorization-Request generiert (128 Bit Entropie via CSPRNG)
- State wird sicher gespeichert (App-State oder Session-Cookie) bis Callback eintrifft
- Bei Callback wird State byte-exact verglichen, jeder Mismatch führt zu Abbruch
- State-Werte sind nicht wiederverwendbar (one-time-use)

**Bezogen auf:** UC-2, UC-3, FR-Broker-2

---

#### NFR-Sec-6: Defense-in-Depth durch Hybrid-Verschlüsselung

**Priorität:** Could (Stretch-Goal)

**Beschreibung**
Wenn der Hybrid-Key-Combiner (FR-Crypto-4) implementiert ist, gilt: ein Angreifer muss sowohl das PQ-Verfahren als auch das klassische Verfahren brechen, um den Session-Key zu kompromittieren.

**Begründung**
Defense-in-Depth ist Best Practice in Übergangsphasen, in denen neue Algorithmen noch nicht über Jahre getestet sind. Falls eine PQ-Implementation einen Fehler hat, schützt das klassische Verfahren immer noch.

**Acceptance Criteria**
- Schriftlich im Bericht dokumentiert (Sicherheits-Analyse-Sektion)
- Implementiert wie in FR-Crypto-4 spezifiziert
- Eingebauter Schutz gegen Downgrade-Angriffe (kein Fallback auf nur ein Verfahren)

**Bezogen auf:** G-2, FR-Crypto-4

---

### 5.2 NFR-Perf: Performance-Anforderungen

#### NFR-Perf-1: Latenz für PQ-Session-Etablierung

**Priorität:** Must

**Beschreibung**
Die Etablierung einer PQ-Session (UC-4) darf auf lokalem Netzwerk nicht länger als 500ms dauern, gemessen vom Server-Request-Eingang bis Server-Response-Ausgang.

**Begründung**
User-Experience: Login + Session-Etablierung sollte sich nicht zäh anfühlen. 500ms ist eine grosszügige Obergrenze, in der Praxis erwartet man eher 50-100ms.

**Acceptance Criteria**
- Gemessen via Server-Logs (Request-In bis Response-Out Timestamps)
- Mindestens 95% der Etablierungen unter 500ms
- Mess-Werte sind im Bericht dokumentiert

**Bezogen auf:** UC-4, FR-Session-1

---

#### NFR-Perf-2: Latenz für Token-Verifikation

**Priorität:** Should

**Beschreibung**
Die Verifikation eines Broker-Tokens (ML-DSA-65 verify) sollte unter 10ms liegen.

**Begründung**
Diese Operation läuft potenziell bei jedem API-Call (FR-Session-1 Vorbedingung). Hohe Verifikations-Latenz würde die End-to-End-Latenz aller geschützten Calls erhöhen.

**Acceptance Criteria**
- Gemessen via Benchmark-Skript
- 99-Perzentil unter 10ms
- Mess-Werte im Bericht dokumentiert

**Bezogen auf:** FR-Token-2

---

#### NFR-Perf-3: Verschlüsselungs-Overhead pro API-Call

**Priorität:** Should

**Beschreibung**
Der zusätzliche Overhead durch AES-GCM-Verschlüsselung plus Header-Routing pro API-Call sollte unter 50ms liegen.

**Begründung**
User-Experience: verschlüsselte Calls dürfen sich nicht spürbar langsamer anfühlen als unverschlüsselte.

**Acceptance Criteria**
- Gemessen mit einem Test-Endpoint, der minimale Business-Logik enthält
- Vergleichbar mit klassischer TLS-only Verschlüsselung (oft im Bereich von wenigen ms zusätzlich)
- Mess-Werte dokumentiert

**Bezogen auf:** UC-5, FR-DataChannel-1

---

### 5.3 NFR-Maint: Wartbarkeit und Crypto-Agility

#### NFR-Maint-1: Crypto-Agility ohne Code-Änderung

**Priorität:** Must

**Beschreibung**
Der Wechsel eines Krypto-Algorithmus erfordert ausschliesslich eine Config-Änderung, keine Änderung am Application-Code.

**Begründung**
Kern-Projekt-Ziel G-4. Das ist die zentrale Eigenschaft der Architektur und gleichzeitig der Hauptbeleg für die Bewertung.

**Acceptance Criteria**
- Wie in FR-Crypto-2 spezifiziert
- Plus: ein Reviewer kann durch Diff von alter und neuer Config sofort sehen, was sich geändert hat, ohne den Code zu öffnen
- Live-Demo via UC-7

**Bezogen auf:** G-4, UC-7, FR-Crypto-2

---

#### NFR-Maint-2: Erweiterbarkeit der IdP-Registry

**Priorität:** Must

**Beschreibung**
Ein neuer externer OIDC-Provider kann ohne Architektur-Eingriff hinzugefügt werden, nur durch Hinzufügen eines Plugin-Eintrags plus einer Konfigurations-Sektion.

**Begründung**
Erweiterbarkeit für zukünftige Integrationen und realistisches Industrie-Pattern (Auth0/Cognito/Keycloak machen es genauso).

**Acceptance Criteria**
- UC-8 demonstriert dies (Apple als Beispiel-Stretch)
- Diff zwischen alter und neuer Architektur umfasst ausschliesslich Plugin-Eintrag und Konfig, keine Code-Änderungen an bestehenden Providern

**Bezogen auf:** UC-8, FR-Broker-1

---

#### NFR-Maint-3: Modularer Code-Aufbau

**Priorität:** Should

**Beschreibung**
Der Code ist in klar abgegrenzte Module aufgeteilt (Auth, Broker, Token, Session, DataChannel, Crypto). Jedes Modul hat eine klare Schnittstelle.

**Begründung**
Wartbarkeit und Verständlichkeit für Future Maintainer und für die Bewertung.

**Acceptance Criteria**
- Code-Review zeigt klare Modul-Grenzen
- Keine Cross-Modul-Abhängigkeiten, die ein Modul-übergreifendes Refactoring beim Wechsel einer Implementation erzwingen würden
- Im Bericht ist die Modul-Struktur dokumentiert (z.B. als Komponenten-Diagramm)

**Bezogen auf:** alle FR-Gruppen

---

### 5.4 NFR-Use: Usability

#### NFR-Use-1: Login-UI ist intuitiv

**Priorität:** Should

**Beschreibung**
Die Login-UI bietet die drei Optionen (Email/Passwort, Google, Microsoft) klar erkennbar und einfach bedienbar.

**Begründung**
Auch für eine Mock-App soll die UX nachvollziehbar sein. Eine unverständliche UI würde von der eigentlichen PQC-Story ablenken.

**Acceptance Criteria**
- Subjektive Bewertung im Demo-Termin: ein erstmaliger Nutzer findet den richtigen Login-Button ohne Anleitung
- Buttons sind klar beschriftet (kein "Login mit federated provider 1")
- Branding der externen IdPs (Google-Logo, Microsoft-Logo) wird verwendet, wenn die Provider es vorschreiben (Compliance mit ihren Brand-Guidelines)

**Bezogen auf:** UC-1, UC-2, UC-3

---

#### NFR-Use-2: Klare Fehlermeldungen für den User

**Priorität:** Should

**Beschreibung**
Fehlersituationen führen zu verständlichen, handlungs-orientierten Meldungen für den End-User (z.B. "Bitte erneut anmelden" statt "401 Unauthorized").

**Begründung**
Technical Errors als User-facing Meldungen sind verwirrend und ein Zeichen für unfertige Software.

**Acceptance Criteria**
- Alle Fehler-Szenarien aus den UCs haben eine entsprechende User-facing Meldung in der App
- Meldungen sind in der Sprache der App (Deutsch oder English, konsistent)
- HTTP-Status-Codes erscheinen nie direkt im UI

**Bezogen auf:** alle UCs

---

### 5.5 NFR-Ops: Logging und Monitoring

#### NFR-Ops-1: Strukturiertes Logging

**Priorität:** Should

**Beschreibung**
Der Auth-Service produziert strukturierte Logs (JSON) mit Severity-Levels (DEBUG, INFO, WARN, ERROR), Timestamps und Request-IDs.

**Begründung**
Strukturierte Logs sind durchsuchbar, filterbar und können maschinell ausgewertet werden. Auch im Schulprojekt-Kontext ist das gute Praxis und macht Debugging einfacher.

**Acceptance Criteria**
- Logs sind im JSON-Format ausgegeben (eine Zeile pro Eintrag)
- Jeder Eintrag hat mindestens: `timestamp`, `level`, `request_id`, `message`
- Request-IDs sind durchgängig über alle Log-Einträge eines Requests
- Konfigurierbar via Config: Log-Level pro Modul

**Bezogen auf:** alle UCs

---

#### NFR-Ops-2: Security-relevante Events werden geloggt

**Priorität:** Must

**Beschreibung**
Sicherheits-Events (failed logins, invalid tokens, tampering attempts) werden separat als Security-Log erfasst, getrennt vom normalen Application-Log.

**Begründung**
Forensik und Anomalie-Erkennung. Auch im Demo-Kontext relevant, weil im Bericht eine Sicherheits-Analyse erwartet wird.

**Acceptance Criteria**
- Mindestens diese Events werden ins Security-Log geschrieben: Failed Local Login, Failed Federated Login, Invalid Broker Token, AES-GCM Tag Failure, Session Expiry
- Security-Log-Einträge enthalten kontextuelle Daten (IP, User-Agent, Request-ID), aber keine Klartext-Tokens oder Passwörter
- Security-Log kann separat ausgewertet werden (eigene Datei oder eigener Log-Stream)

**Bezogen auf:** UC-1, UC-2, UC-3, UC-5, UC-6

---

#### NFR-Ops-3: Health-Check-Endpoint

**Priorität:** Should

**Beschreibung**
Der Auth-Service bietet einen `/health`-Endpoint, der den Service-Status zurückgibt (Service läuft, Registries initialisiert, Connectivity zu Dependencies).

**Begründung**
Operations-Best-Practice. Auch im Demo-Kontext nützlich, um vor dem Bewertungs-Termin schnell den Service-Zustand zu prüfen.

**Acceptance Criteria**
- `GET /health` antwortet mit `200 OK` und Body `{ status: "ok", version, uptime, registry_status }` wenn alles funktioniert
- `503 Service Unavailable` wenn kritische Dependencies fehlen (z.B. Session-Store nicht erreichbar)
- Endpoint ist nicht authentifiziert (öffentlich zugänglich, gibt aber keine sensitiven Daten preis)

**Bezogen auf:** Operations / Demo-Vorbereitung

---

### 5.6 NFR-Doc: Dokumentations-Anforderungen

#### NFR-Doc-1: Vollständiger Bericht zur Abgabe

**Priorität:** Must

**Beschreibung**
Bis zur Abgabe am 04.07-05.07.2026 liegt ein vollständiger Projektbericht vor mit den Sektionen: Einleitung, Theorie, Architektur, Implementation, Bewertung, Anhang.

**Begründung**
Hauptbewertungs-Grundlage für die Semesterarbeit.

**Acceptance Criteria**
- Bericht hat alle geplanten Sektionen
- Inhalt ist nachvollziehbar (keine offenen Verweise, keine Platzhalter)
- Konsistent (Begriffe einheitlich, Diagramme matchend zum Text)
- PDF-formatiert und abgabe-tauglich

**Bezogen auf:** G-5

---

#### NFR-Doc-2: Architektur-Entscheidungen sind dokumentiert

**Priorität:** Must

**Beschreibung**
Wichtige Architektur-Entscheidungen werden in eigenen Notiz-Dokumenten festgehalten (siehe z.B. `03_entscheidung_auth_architektur.md`). Diese fliessen in den Bericht ein.

**Begründung**
Nachvollziehbarkeit für Bewertung und Future Maintainer. Architecture Decision Records (ADRs) sind Industrie-Standard.

**Acceptance Criteria**
- Mindestens diese Entscheidungs-Dokumente liegen vor zur Abgabe: Auth-Architektur (Option 3 vs. Alternativen), Tech-Stack-Wahl, Crypto-Agility-Pattern
- Jedes Dokument enthält: Kontext, Optionen, Entscheidung, Begründung

**Bezogen auf:** G-5

---

#### NFR-Doc-3: Quellenverzeichnis ist vollständig

**Priorität:** Must

**Beschreibung**
Alle externen Quellen werden in `04_quellen.md` gepflegt und für den Bericht übernommen. Das Format-Konvertieren ins TBZ-Zitierformat erfolgt im Bericht-Sprint.

**Begründung**
Wissenschaftliche Praxis und Pflicht für die Bewertung.

**Acceptance Criteria**
- Bericht hat ein vollständiges Quellenverzeichnis mit korrekten Zitierungen
- Alle wichtigen Quellen (NIST-Standards, IETF-Drafts, Libraries, Schlüssel-Papers) sind enthalten
- Format entspricht der TBZ-Vorgabe

**Bezogen auf:** G-5

---

#### NFR-Doc-4: Live-Demo-Drehbuch

**Priorität:** Should

**Beschreibung**
Für die Bewertungs-Präsentation existiert ein schriftliches Demo-Drehbuch: was wird gezeigt, in welcher Reihenfolge, was beweist es jeweils.

**Begründung**
Bewertungs-Vorbereitung. Live-Demos können schiefgehen; ein gutes Drehbuch plus Backup-Material (Screenshots, Video-Aufzeichnung) reduziert das Risiko.

**Acceptance Criteria**
- Drehbuch liegt vor, mindestens 1 Woche vor Bewertungs-Termin
- Enthält Schritt-für-Schritt-Plan inklusive Test der Crypto-Agility-Demo (UC-7)
- Backup-Material (Screenshots, Video-Aufzeichnung) verfügbar, falls Live-Demo scheitert

**Bezogen auf:** G-5, UC-7

---

## 6. Constraints

Constraints beschreiben harte Grenzen, die das Projekt von aussen einschränken. Anders als FRs und NFRs haben Constraints keine Priorität, weil sie nicht wählbar sind. Format pro Constraint: Beschreibung, Auswirkung auf das Projekt, Quelle/Begründung.

Gruppen:

- **C-Tech-X**: Technische Constraints
- **C-Time-X**: Zeit-Constraints
- **C-Org-X**: Organisatorische Constraints

---

### 6.1 C-Tech: Technische Constraints

#### C-Tech-1: Mobile-TLS-Cipher-Suite-Constraint

**Beschreibung**
Mobile Betriebssysteme (iOS via URLSession, Android via conscrypt) erlauben App-Code keine zuverlässige Kontrolle über die TLS-Cipher-Suite-Negotiation.

**Auswirkung auf das Projekt**
Die Mock-App kann nicht direkt sicherstellen, dass die TLS-Verbindung zum Auth-Service eine PQ-Cipher-Suite verwendet. Deshalb ist End-to-End-PQ-Verschlüsselung als App-Layer-Lösung (ML-KEM + AES-GCM) implementiert, parallel zur klassischen TLS-Schicht. Eine "End-to-End-PQ-TLS"-Behauptung wäre auf mobilen Plattformen technisch unhaltbar.

**Quelle**
iOS Platform Documentation (URLSession), Android conscrypt Documentation. Stand 2026.

---

#### C-Tech-2: PQC-Bibliotheks-Verfügbarkeit

**Beschreibung**
pyca/cryptography 45.x bietet Stand 2026 noch keine ML-DSA/ML-KEM-Implementierungen. Die einzigen produktiv nutzbaren PQC-Bibliotheken sind liboqs (Open Quantum Safe Project), liboqs-python (Python-Wrapper) und `@noble/post-quantum` für JavaScript.

**Auswirkung auf das Projekt**
Tech-Stack-Wahl ist eingeschränkt. Andere Python-PQC-Libraries werden nicht akzeptiert wegen mangelnder Reife. Mobile-Seite muss `@noble/post-quantum` verwenden, alternative RN-Libraries wie `react-native-crystals` sind verworfen wegen pre-Standardization-Status (basieren noch auf Kyber/Dilithium statt ML-KEM/ML-DSA).

**Quelle**
Recherche zur PQC-Library-Landschaft, dokumentiert in `04_quellen.md`.

---

#### C-Tech-3: IETF-Draft-Status für PQC in JOSE

**Beschreibung**
Der IETF-Draft `draft-ietf-jose-pqc` (definiert PQC-`alg`-Werte für JWS/JWE) ist Stand Mai 2026 noch nicht ratifiziert.

**Auswirkung auf das Projekt**
Token-Implementation muss gegen einen sich ändernden Standard arbeiten. Im Bericht wird dieser Status ehrlich dokumentiert. Verwendete `alg`-Werte folgen der jeweils aktuellen Draft-Version. Bei Ratifikation des Standards wäre eine kleine Anpassung der `alg`-Strings nötig (falls die finalen Namen anders als die Draft-Namen sind).

**Quelle**
IETF JOSE Working Group, Draft-Tracker. Stand 2026.

---

#### C-Tech-4: Externe IdP-Tokens sind klassisch signiert

**Beschreibung**
Google und Microsoft stellen 2026 noch klassisch signierte ID-Tokens (RS256) aus. PQC-Tokens werden bei diesen grossen Anbietern frühestens 2028-2030 erwartet.

**Auswirkung auf das Projekt**
Die "Pre-Authentication"-Phase (User-Authentifizierung beim externen IdP) ist nicht PQ-sicher. Das ist die ehrliche Limitation des PQ-Uplift-Patterns. Architektur-Notiz `03_entscheidung_auth_architektur.md` dokumentiert dies und der Bericht erwähnt es explizit als bewusste Übergangs-Architektur.

**Quelle**
Google OIDC Documentation, Microsoft Identity Platform Documentation. Beide Stand 2026.

---

#### C-Tech-5: Container-basierte Demo-Architektur

**Beschreibung**
Der Server-Stack läuft via Docker Compose, gebaut auf `openquantumsafe/oqs-ossl3` als Base-Image für nginx + oqs-provider + OpenSSL 3.5+.

**Auswirkung auf das Projekt**
Vereinfacht das Setup erheblich (kein manueller Build von liboqs und oqs-provider). Demo-Termin: Service wird lokal hochgefahren, kein Cloud-Hosting nötig. Vorbereitungszeit auf einem neuen Rechner ist überschaubar (Docker-Pull plus Compose-Up).

**Quelle**
Architektur-Entscheidung 2026-05-03 nach Recherche zum oqs-provider-Build-Aufwand.

---

#### C-Tech-6: Mobile Plattform via Expo Managed Workflow

**Beschreibung**
Die Mock-App läuft auf iOS und Android via Expo SDK 51+. Web-Browser wird nicht als Ziel-Plattform unterstützt. Native-Modules (Expo Ejected Workflow) sind nicht zugelassen.

**Auswirkung auf das Projekt**
Vereinfacht Setup und Deployment auf Test-Geräten (Expo Go App auf dem Handy reicht). Schränkt aber Library-Optionen ein (z.B. keine Native-PQC-Bibliotheken). `@noble/post-quantum` ist mit Expo Managed Workflow kompatibel, was die Wahl gerechtfertigt hat.

**Quelle**
Tech-Stack-Wahl, dokumentiert in den Projekt-Memory-Files.

---

### 6.2 C-Time: Zeit-Constraints

#### C-Time-1: Harte Abgabe-Deadline

**Beschreibung**
Abgabe am 04.07-05.07.2026, inklusive Bericht, Code-Stand und Vorbereitung der Bewertungs-Präsentation. Keine Flexibilität bei dieser Deadline.

**Auswirkung auf das Projekt**
Der gesamte Scope muss bis dahin geliefert sein. Bei Verzug wird zuerst auf Could-Items verzichtet (Apple-IdP, Hybrid-Combiner), dann auf Should-Items (Microsoft-IdP, Soft-Token-Expiry, optimierte Performance-Targets). Die Must-Items definieren das absolute Minimum für eine erfolgreiche Abgabe.

**Quelle**
TBZ-Schul-Vorgabe, Semesterarbeit 3 ITCNE25.

---

#### C-Time-2: Verfügbare Arbeitszeit

**Beschreibung**
Solo-Entwickler. Circa 10 bis 15 Stunden pro Woche verfügbar. Gesamt-Verfügbarkeit ab Start der Recherche (08.05.2026) bis zur Abgabe: ca. 8.5 Wochen, also 85 bis 130 Stunden netto. Mit Claude/Claude-Code als Multiplier ergibt das ca. 100 bis 200 effektive Stunden Output.

**Auswirkung auf das Projekt**
Sprint-Plan und Scope-Entscheidungen müssen dieser Realität entsprechen. Stretch-Goals werden nur angegangen, wenn die Must-Items signifikant vor Deadline fertig sind. Wenn die Must-Items spät dran sind, müssen sukzessive Could- und Should-Items gestrichen werden.

**Quelle**
Persönliche Verfügbarkeit, Schul-Alltag parallel.

---

#### C-Time-3: Sprint-Struktur

**Beschreibung**
Vor-Sprint-Phase (Recherche, Architektur, Projektplan, Setup) läuft 08.05 bis 05.06.2026. Sprint 0 (Setup) ist 06.06 bis 11.06.2026. Folgende Sprints sind jeweils 2 Wochen lang bis zur Abgabe.

**Auswirkung auf das Projekt**
Aktuelle Vorbereitungsphase ist intensiv (Recherche, Doku, Architektur). Sprint 0 muss am Ende einen lauffähigen Server-Stack haben, damit Sprint 1 direkt mit der Implementation starten kann. Verschiebt sich Sprint 0, verschieben sich alle folgenden Sprints, mit Risiko für die Abgabe.

**Quelle**
Persönliche Planung, dokumentiert im Projektplan.

---

### 6.3 C-Org: Organisatorische Constraints

#### C-Org-1: Solo-Entwickler ohne Code-Reviewer

**Beschreibung**
Keine Team-Kollaboration. Code-Reviews durch Drittpersonen sind nicht vorgesehen. Claude und Claude Code dienen als "Pair-Programming-Partner" und als Erklärungs-Quelle für unbekannte Technologien.

**Auswirkung auf das Projekt**
Eigenverantwortung für Code-Qualität, Architektur-Konsistenz und Dokumentations-Vollständigkeit. Selbst-Reviews und systematische Vorgehensweise (z.B. Requirements-getriebenes Arbeiten) sind essenziell, um Lücken zu vermeiden.

**Quelle**
Schulprojekt-Format der Semesterarbeit.

---

#### C-Org-2: Schulprojekt-Charakter, kein Production-System

**Beschreibung**
Das Projekt wird zum Zweck der Bewertung gebaut, nicht für produktiven Einsatz. Bewertbarkeit und Demonstrierbarkeit sind wichtiger als Production-Härte.

**Auswirkung auf das Projekt**
Aufwand fliesst in Code-Klarheit, Dokumentation und Demo-Tauglichkeit statt z.B. in Disaster-Recovery, Multi-Region-Setup, Audit-Compliance oder Performance-Tuning für hohe Last. Diese Punkte sind in Sektion 1.3 (Abgrenzung) bewusst aus dem Scope genommen.

**Quelle**
Selbst-gewählte Abgrenzung, abgestimmt mit dem Dozenten.

---

#### C-Org-3: Bewertungs-Kontext (TBZ Semesterarbeit)

**Beschreibung**
Die Bewertung erfolgt durch den Dozenten via Code-Review, Bericht-Lektüre und Live-Präsentation. Die Note basiert auf vier Säulen: technische Umsetzung, Architektur-Qualität, Dokumentations-Qualität und Präsentation.

**Auswirkung auf das Projekt**
Alle vier Säulen brauchen Aufmerksamkeit, nicht nur der Code. Insbesondere die Dokumentations-Säule (Bericht, Architektur-Doku, Quellenverzeichnis, Demo-Drehbuch) ist genauso wichtig wie der Code selbst. Das ist auch der Grund, warum NFR-Doc-X eine ganze NFR-Gruppe ist.

**Quelle**
TBZ Schul-Konvention, Semesterarbeits-Format.

---

#### C-Org-4: Dozent-Abstimmung bereits erfolgt

**Beschreibung**
Architektur-Aufwertung (Option 3 mit Identity Broker statt ursprünglich eingereichtem reinem Custom-Auth-Service) wurde mit dem Dozenten abgesprochen und genehmigt.

**Auswirkung auf das Projekt**
Der aktuelle Scope ist genehmigt. Bei weiteren grösseren Scope-Änderungen (z.B. Rückkehr zu Option 1 oder massiver Stretch-Ausbau) ist erneute Abstimmung nötig. Innerhalb des genehmigten Scope können kleinere Anpassungen (z.B. Priorisierung von Could-Items) eigenständig erfolgen.

**Quelle**
Persönliche Abstimmung mit dem Dozenten, ca. 06-07.05.2026.

---

#### C-Org-5: TBZ-Bericht-Format

**Beschreibung**
Der Abschluss-Bericht muss bestimmten TBZ-Vorgaben entsprechen (Format, Länge, Zitierstil). Konkrete Vorgaben sind in den TBZ-Ressourcen-Unterlagen dokumentiert (Workspace-Ordner `../tbz_resources`).

**Auswirkung auf das Projekt**
Der Bericht-Sprint muss diese Vorgaben respektieren. Das Quellen-Arbeitsdokument (`04_quellen.md`) muss vor Bericht-Erstellung ins TBZ-Format konvertiert werden. Format-Details sollten vor dem Bericht-Sprint nochmal aktiv geprüft werden, um spätere Überraschungen zu vermeiden.

**Quelle**
TBZ-Ressourcen-Ordner im Workspace.

---

## 7. Traceability Matrix

Die Traceability Matrix zeigt, wie Use Cases, Functional Requirements und Non-Functional Requirements miteinander verbunden sind und wie sie die Projekt-Ziele (G-1 bis G-5) abdecken. Sie dient als Werkzeug für Test-Planung, Bewertbarkeit und Lücken-Identifikation.

### 7.1 Use Case zu Functional Requirement Mapping

| Use Case | Implementierende FRs |
|---|---|
| UC-1: Lokaler Login mit Email/Passwort | FR-Auth-1, FR-Auth-2, FR-Token-1 |
| UC-2: Login mit Google | FR-Broker-1, FR-Broker-2, FR-Broker-3, FR-Broker-4, FR-Token-1 |
| UC-3: Login mit Microsoft | FR-Broker-1, FR-Broker-2, FR-Broker-3, FR-Broker-4, FR-Token-1 |
| UC-4: PQ-Session-Etablierung | FR-Token-2, FR-Session-1, FR-Session-2, FR-Session-3, FR-Session-4, FR-Crypto-1, FR-Crypto-3 |
| UC-5: Geschützter API-Call | FR-Token-2, FR-Session-3, FR-DataChannel-1, FR-DataChannel-2 |
| UC-6: Token-Ablauf und Re-Authentication | FR-Token-2, FR-Session-3 |
| UC-7: Algorithmus-Wechsel via Config | FR-Crypto-1, FR-Crypto-2, FR-Crypto-3, FR-Session-4 |
| UC-8: Neuer externer IdP hinzufügen | FR-Broker-1 |

### 7.2 NFR Coverage Mapping

| NFR | Bezogen auf |
|---|---|
| NFR-Sec-1: Hybride PQ-TLS | G-1, G-2 (System-weit) |
| NFR-Sec-2: Replay-Schutz | UC-5, FR-DataChannel-1 |
| NFR-Sec-3: Kein Klartext für Geheimnisse | Alle FR-Gruppen (System-weite Policy) |
| NFR-Sec-4: User-Enumeration-Schutz | FR-Auth-1, FR-Broker-4 |
| NFR-Sec-5: CSRF-Schutz | UC-2, UC-3, FR-Broker-2 |
| NFR-Sec-6: Defense-in-Depth Hybrid | G-2, FR-Crypto-4 (Stretch) |
| NFR-Perf-1: Session-Latenz unter 500ms | UC-4, FR-Session-1 |
| NFR-Perf-2: Token-Verify-Latenz unter 10ms | FR-Token-2 |
| NFR-Perf-3: Verschlüsselungs-Overhead unter 50ms | UC-5, FR-DataChannel-1 |
| NFR-Maint-1: Crypto-Agility ohne Code-Change | G-4, UC-7, FR-Crypto-2 |
| NFR-Maint-2: IdP-Erweiterbarkeit | UC-8, FR-Broker-1 |
| NFR-Maint-3: Modularer Code-Aufbau | Alle FR-Gruppen (System-weit) |
| NFR-Use-1: Intuitive Login-UI | UC-1, UC-2, UC-3 |
| NFR-Use-2: Klare Fehlermeldungen | Alle UCs |
| NFR-Ops-1: Strukturiertes Logging | Alle UCs (Ops-Schicht) |
| NFR-Ops-2: Security-Events loggen | UC-1, UC-2, UC-3, UC-5, UC-6 |
| NFR-Ops-3: Health-Check-Endpoint | Operations (kein direkter UC-Bezug) |
| NFR-Doc-1: Vollständiger Bericht | G-5 |
| NFR-Doc-2: Architektur-Doku | G-5 |
| NFR-Doc-3: Quellenverzeichnis | G-5 |
| NFR-Doc-4: Demo-Drehbuch | G-5, UC-7 |

### 7.3 Goal Coverage

| Projekt-Ziel | Adressiert durch |
|---|---|
| G-1: PQC-Demonstration in produktnahem Kontext | UC-1, UC-4, UC-5, UC-7, FR-Token-X, FR-Session-X, FR-Crypto-X, NFR-Sec-1 |
| G-2: End-to-End PQ-Sicherheit | UC-4, UC-5, FR-Session-1, FR-Session-2, FR-DataChannel-1, FR-Crypto-4 (Stretch), NFR-Sec-1, NFR-Sec-6 (Stretch) |
| G-3: Identity-Broker-Pattern für Übergangsphase | UC-2, UC-3, FR-Broker-1, FR-Broker-2, FR-Broker-3, FR-Broker-4 |
| G-4: Crypto-Agility als Architektur-Prinzip | UC-7, UC-8, FR-Crypto-1, FR-Crypto-2, FR-Crypto-3, FR-Token-3, FR-Session-4, NFR-Maint-1, NFR-Maint-2 |
| G-5: Vollständige Projekt-Dokumentation | NFR-Doc-1, NFR-Doc-2, NFR-Doc-3, NFR-Doc-4 |

### 7.4 Beobachtungen aus der Matrix

- **FR-Token-1 (Broker-Token-Ausstellung) ist der zentrale FR**, der von allen drei Login-Use-Cases (UC-1, UC-2, UC-3) genutzt wird. Ein Fehler hier blockiert alle Auth-Pfade.
- **FR-Crypto-1 und FR-Crypto-3 sind quer-schneidend**: praktisch jeder PQ-bezogene Use Case verwendet sie indirekt. Die Algorithmus-Registry und der Algorithmus-Identifier sind System-Fundament.
- **NFR-Sec-3 (Kein Klartext) und NFR-Maint-3 (Modularer Code) sind System-Eigenschaften** ohne spezifischen UC-Bezug. Sie gelten überall und werden im Code-Review verifiziert, nicht in einem dedizierten Test.
- **UC-8 (neuer IdP) ist isoliert**: er bezieht sich nur auf FR-Broker-1 (Plugin-Architektur). Das beweist die Architektur-Eigenschaft "Erweiterbarkeit ohne Eingriff in bestehende Provider".
- **G-5 (Dokumentation) ist ausschliesslich durch NFRs adressiert, nicht durch FRs.** Das ist konsistent damit, dass Dokumentation eine Qualität ist, kein Feature.
- **G-4 (Crypto-Agility) hat die breiteste FR-Abdeckung**: 5 FRs aus 3 Gruppen, plus 2 NFRs. Das spiegelt wider, dass Crypto-Agility nicht ein einzelnes Feature ist, sondern ein durchgehendes Architektur-Prinzip.

---

## 8. Glossar

Definitionen der zentralen Begriffe, die im Dokument verwendet werden. Alphabetisch sortiert.

**AES-256-GCM**
Advanced Encryption Standard mit 256-Bit Schlüssel im Galois/Counter Mode. Symmetrisches Authenticated-Encryption-Verfahren, das gleichzeitig Vertraulichkeit (Verschlüsselung) und Integrität (Authentication Tag) liefert. Im Projekt für die Payload-Verschlüsselung im App-Layer-Daten-Kanal verwendet. Erfordert eine einzigartige Nonce pro Verschlüsselung mit demselben Schlüssel.

**Argon2id**
Aktuell empfohlener Password-Hashing-Algorithmus, Gewinner der Password Hashing Competition 2015. Resistent gegen GPU- und ASIC-basierte Brute-Force-Angriffe durch Memory-Hardness. Empfohlene Parameter im Projekt: m=64MB, t=3, p=4. Siehe FR-Auth-1.

**Authorization Code Flow**
OAuth-2.0- und OIDC-Standard-Flow, in dem der Client einen Authorization Code beim IdP abruft und diesen anschliessend gegen Access- und ID-Tokens tauscht. Im Projekt mit PKCE-Erweiterung verwendet, damit auch mobile Apps ohne `client_secret` sicher arbeiten. Definiert in RFC 6749.

**Broker-Token**
Der vom Auth-Service ausgestellte Token nach erfolgreicher lokaler oder federated Authentifizierung. Im Projekt ein ML-DSA-65-signiertes Token, das den User gegenüber dem Resource-Server identifiziert.

**Crypto-Abstraction-Layer**
Software-Schicht, durch die alle Krypto-Operationen abstrahiert laufen. Application-Code kennt keine konkreten Algorithmus-Namen, sondern ruft generische Schnittstellen auf (z.B. `sign(payload)` statt `mldsa65_sign(payload)`). Voraussetzung für Crypto-Agility.

**Crypto-Agility**
Architektur-Eigenschaft, die es erlaubt, kryptographische Algorithmen ohne Code-Änderung auszutauschen. Realisiert via Algorithmus-Registry und Konfigurations-basierte Auswahl. Zentrales Projekt-Ziel G-4.

**Decaps**
Decapsulation. KEM-Operation auf der Empfänger-Seite, die mit dem Private-Key aus einem Ciphertext den Shared Secret wiederherstellt. Gegenstück zu Encaps.

**Encaps**
Encapsulation. KEM-Operation auf der Sender-Seite, die mit einem Public-Key einen Shared Secret und einen Ciphertext erzeugt. Der Ciphertext wird an den Empfänger gesendet, der mit seinem Private-Key denselben Shared Secret rekonstruieren kann.

**Federation (Identity)**
Praxis, in der ein Service externe Identity Provider akzeptiert (z.B. Google, Microsoft), statt eigene User-Verwaltung zu betreiben. Der Service vertraut der Authentifizierung des externen Providers und stellt eigene Tokens für die internen Berechtigungen aus.

**FIPS 203**
NIST Federal Information Processing Standard, der ML-KEM (Module-Lattice-Based Key-Encapsulation Mechanism) definiert. Seit August 2024 final.

**FIPS 204**
NIST Federal Information Processing Standard, der ML-DSA (Module-Lattice-Based Digital Signature Algorithm) definiert. Seit August 2024 final.

**FIPS 205**
NIST Federal Information Processing Standard, der SLH-DSA (Stateless Hash-Based Digital Signature Algorithm) definiert. Seit August 2024 final. Im Projekt nur konzeptionell erwähnt, nicht produktiv eingesetzt.

**HKDF**
HMAC-based Extract-and-Expand Key Derivation Function. Standardisiert in RFC 5869. Im Projekt verwendet, um aus dem ML-KEM-Shared-Secret einen AES-256-GCM-Session-Key abzuleiten.

**Hybrid PQ**
Kombination klassischer und post-quantum Kryptographie, sodass ein Angreifer beide Verfahren brechen müsste, um das Geheimnis zu kompromittieren. Defense-in-Depth-Prinzip. Im Projekt eingesetzt auf TLS-Layer (X25519MLKEM768) und optional als Stretch-Goal auf App-Layer (FR-Crypto-4).

**Identity Broker**
Architektur-Pattern, in dem ein zentraler Auth-Service externe OIDC-Provider als Auth-Quellen akzeptiert und nach erfolgreicher Federation einen eigenen Token ausstellt. Damit sind die Application-Clients vom konkreten externen IdP entkoppelt. Verwendet z.B. von AWS Cognito, Auth0, Keycloak und Zitadel.

**IETF-Draft**
Internet Engineering Task Force Document im Entwurfsstadium. Noch nicht ratifizierter Standard, aber technisch oft schon implementiert. Beispiel im Projekt: `draft-ietf-jose-pqc` (PQC-Algorithmen in JOSE), Stand 2026 noch nicht final.

**JWE**
JSON Web Encryption. Standard für verschlüsselte JWTs. Im Projekt nicht direkt verwendet, weil der Auth-Service signiert statt verschlüsselt und die App-Layer-Verschlüsselung ein eigenes Format nutzt.

**JWKS**
JSON Web Key Set. Endpoint, der die öffentlichen Schlüssel eines Token-Issuers in standardisiertem Format bereitstellt, damit andere Services die Tokens verifizieren können. Im Projekt verwendet, um Google- und Microsoft-Tokens zu verifizieren.

**JWS**
JSON Web Signature. Standard für signierte JWTs. Im Projekt verwenden die Broker-Tokens das JWS-Format mit ML-DSA-Signatur.

**JWT**
JSON Web Token. Standardisiertes, kompaktes Token-Format basierend auf JSON. Header und Payload sind base64-codiert, optional signiert (JWS) oder verschlüsselt (JWE). Definiert in RFC 7519.

**KEM**
Key Encapsulation Mechanism. Kryptographisches Primitiv mit drei Operationen: KeyGen (generiert Public/Private Key Pair), Encaps (erzeugt Shared Secret und Ciphertext mit Public Key), Decaps (rekonstruiert Shared Secret aus Ciphertext mit Private Key). ML-KEM ist das im Projekt verwendete PQ-KEM.

**liboqs**
Open-Source-Library des Open Quantum Safe Project mit Implementationen aller NIST-PQC-Standards. Wird im Projekt server-seitig via `liboqs-python` und im TLS-Stack via `oqs-provider` verwendet.

**Mock-App**
Die React-Native-Demo-App im Projekt. "Mock" im Sinne von "vereinfacht zu Demo-Zwecken", nicht ein produktives Produkt. Hat einen Login-Screen, einen Home-Screen und einen Test-API-Call.

**ML-DSA**
Module-Lattice-Based Digital Signature Algorithm. Post-Quantum-Signatur-Algorithmus, ehemals CRYSTALS-Dilithium genannt. Im Projekt wird ML-DSA-65 (Security Level 3) für Broker-Token-Signaturen verwendet. Standardisiert in FIPS 204.

**ML-KEM**
Module-Lattice-Based Key-Encapsulation Mechanism. Post-Quantum-KEM, ehemals CRYSTALS-Kyber genannt. Im Projekt wird ML-KEM-768 (Security Level 3) für die PQ-Session-Etablierung verwendet. Standardisiert in FIPS 203.

**NIST**
National Institute of Standards and Technology. US-amerikanische Behörde, die unter anderem die PQC-Standards FIPS 203, 204 und 205 veröffentlicht hat.

**Nonce**
"Number used once". Einzigartiger Wert pro Verschlüsselungs-Operation, der gewährleistet, dass identische Klartexte zu unterschiedlichen Chiffrentexten führen. Bei AES-GCM kritisch: Nonce-Wiederverwendung führt zum Verlust der Vertraulichkeit. Im Projekt sind Nonces 96 Bit lang und werden via CSPRNG generiert.

**OAuth 2.0**
Autorisations-Framework, definiert in RFC 6749. Erlaubt Clients, beschränkten Zugriff auf User-Ressourcen zu erhalten, ohne die User-Credentials zu sehen. Basis-Schicht unter OIDC.

**OIDC**
OpenID Connect. Identity-Layer auf Basis von OAuth 2.0. Standardisiert das Konzept eines ID-Tokens (signiertes JWT mit User-Identität) und die zugehörigen Flows. Definiert in OpenID Connect Core 1.0.

**OpenID Provider (OP)**
In OIDC-Terminologie: die Entität, die User-Identitäten verifiziert und Tokens ausstellt. Im Projekt: Google und Microsoft als externe OPs, die unser Auth-Service als OIDC-Client konsumiert.

**oqs-provider**
OpenSSL 3 Provider Plugin, das ML-KEM und ML-DSA als TLS-Cipher-Suites verfügbar macht. Im Projekt eingesetzt hinter nginx für die hybride TLS-Konfiguration (X25519MLKEM768).

**PKCE**
Proof Key for Code Exchange, RFC 7636. Erweiterung des OAuth-2.0-Authorization-Code-Flows, die sicherstellt, dass der Authorization Code nicht von einem Angreifer eingelöst werden kann. Verzichtet auf `client_secret`, was es für mobile Apps geeignet macht.

**PQC**
Post-Quantum Cryptography. Sammelbegriff für kryptographische Verfahren, die auch gegen Angriffe mit Quantencomputern (insbesondere Shor's Algorithmus) sicher sind. Hauptthema des Projekts.

**PQ-Uplift Pattern**
Architektur-Muster, in dem klassische Identitäts-Claims (z.B. von Google) in einer Übergangsphase angenommen werden, danach aber alle weitere Kommunikation in eine PQ-sichere Sphäre überführt wird. Dokumentiert in `03_entscheidung_auth_architektur.md` als ehrliche Limitation des Identity-Broker-Patterns in 2026.

**Pre-Authentication**
Im PQ-Uplift-Pattern: die erste Etappe der Authentifizierung (User zum externen IdP), die noch klassisch abgesichert ist. Im Projekt-Kontext: die Phase, bevor der Broker den eigenen PQ-Token ausstellt.

**Quantum-Computer**
Computer, der mit Qubits statt klassischen Bits rechnet. Hinreichend leistungsfähige Quantum-Computer können klassische asymmetrische Kryptographie (RSA, ECC) via Shor's Algorithmus brechen. PQC ist die Antwort darauf.

**Relying Party (RP)**
In OIDC-Terminologie: der Client, der sich auf die Authentifizierung durch einen OpenID Provider verlässt. Im Projekt ist die Mock-App eine RP gegenüber Google und Microsoft (vermittelt durch den Auth-Service als Broker).

**Replay-Angriff**
Angriffsform, in der ein Angreifer einen abgefangenen Request unverändert nochmals sendet. Bei kryptographisch nicht abgesicherten Systemen kann dies zu unautorisierten Aktionen führen. Im Projekt durch frische Nonces pro Nachricht (FR-DataChannel-1) und Session-TTL adressiert.

**Resource Server**
In OAuth-2.0-Terminologie: der Server, der die geschützten API-Endpunkte hostet. Im Projekt sind Auth-Service und Resource Server derselbe Microservice, konzeptionell aber getrennt.

**RSA / ECC / ECDSA**
Klassische asymmetrische Kryptographie-Verfahren. Anfällig gegen Quantum-Computer-Angriffe via Shor's Algorithmus. Werden im Projekt nur klassen-übergreifend in der hybriden TLS-Schicht (X25519 als ECDH-Variante) und in den externen IdP-Tokens (RS256) verwendet.

**Session-Key**
Symmetrischer Schlüssel für eine spezifische Session zwischen App und Backend. Im Projekt ein 256-Bit Schlüssel, abgeleitet via HKDF aus dem ML-KEM-Shared-Secret. Verwendet für AES-256-GCM-Verschlüsselung der Payloads.

**Shared Secret**
Geheimnis, das zwischen zwei Parteien etabliert wurde, ohne über einen unsicheren Kanal übertragen worden zu sein. Im Projekt: das Ergebnis der ML-KEM-Encaps/Decaps-Operationen. Wird via HKDF zum Session-Key weiterverarbeitet.

**Shor's Algorithmus**
Quantenalgorithmus von Peter Shor (1994), der das Faktorisierungsproblem und das diskrete-Logarithmus-Problem in polynomieller Zeit löst. Macht klassische RSA und ECC unter dem Vorbehalt eines hinreichend grossen Quantum-Computers gebrochen. Hauptmotivation für PQC.

**SLH-DSA**
Stateless Hash-Based Digital Signature Algorithm. Post-Quantum-Signatur-Algorithmus, ehemals SPHINCS+ genannt. Im Projekt nicht produktiv eingesetzt (ungeeignet für Mobile-Use-Case wegen sehr grosser Signaturen). Standardisiert in FIPS 205.

**TLS 1.3**
Transport Layer Security Version 1.3, definiert in RFC 8446. Im Projekt verwendet mit hybrider PQ-NamedGroup `X25519MLKEM768` für die Transport-Layer-Sicherheit zwischen Mock-App und Auth-Service (server-seitig erzwungen via oqs-provider).

**User-Enumeration**
Angriffsform, in der ein Angreifer die Existenz von User-Accounts inferieren kann, z.B. durch unterschiedliche Fehlermeldungen für "falsches Passwort" vs "User nicht gefunden". Vorstufe für gezielte Angriffe (Phishing, Brute-Force). Im Projekt durch identische Responses (NFR-Sec-4) verhindert.

**X25519MLKEM768**
Hybride TLS-NamedGroup, kombiniert klassisches X25519 (Curve25519 ECDH) mit ML-KEM-768. NamedGroup-ID `0x11ec`. Definiert im IETF-Draft `draft-ietf-tls-ecdhe-mlkem-04`. Im Projekt server-seitig via nginx + oqs-provider verwendet.

---

## 9. Versionsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 0.1 | 08.05.2026 | Initial-Skelett erstellt. Phase 1 (Kontext und Stakeholder) ausgefüllt. |
| 0.2 | 08.05.2026 | Phase 2 (Use Cases) ausgefüllt: UC-1 bis UC-8 mit Akteuren, Hauptablauf, Fehler-Szenarien und Acceptance Criteria. |
| 0.3 | 08.05.2026 | Priorität in jedem Use Case an den Anfang verschoben. UC-3 (Microsoft) von Must auf Should runtergestuft, um Puffer für eventuelle Probleme zu schaffen. |
| 0.4 | 08.05.2026 | Phase 3 (Functional Requirements) ausgefüllt: 19 FRs in 6 Gruppen (Auth, Broker, Token, Session, DataChannel, Crypto) mit Vor-/Nachbedingungen, Fehler-Szenarien, Acceptance Criteria und Traceability zu Use Cases. |
| 0.5 | 08.05.2026 | FR-Token-3 (Schlüssel-Rotation) von Should auf Must hochgestuft. Phase 4 (Non-Functional Requirements) ausgefüllt: 21 NFRs in 6 Gruppen (Sec, Perf, Maint, Use, Ops, Doc) inklusive Logging/Monitoring als NFR-Gruppe. |
| 0.6 | 08.05.2026 | Phase 5 (Constraints) ausgefüllt: 14 Constraints in 3 Gruppen (Tech, Time, Org) mit Beschreibung, Auswirkung auf das Projekt und Quelle/Begründung. |
| 1.0 | 08.05.2026 | Traceability Matrix (Sektion 7) und Glossar (Sektion 8) ausgefüllt. Damit ist die Requirements-Phase vollständig abgeschlossen. Dokument ist bereit als Referenz für Tech-Stack-Entscheidungen und Implementation. |
