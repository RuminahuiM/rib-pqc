# Architektur-Entscheidung: Scope des Auth-Services

**Datum:** 08.05.2026
**Status:** Entschieden
**Gewählte Option:** Option 3 (Custom Auth + Identity Broker + E2E PQC)

---

## 1. Ausgangslage

Im Rahmen der Semesterarbeit "Implementing PQC" muss ein Auth-Service entworfen werden. Der eingereichte Projektrahmen (Formular) sieht vor: Python-Auth-Microservice mit PQC plus React-Native-Demo-App mit PQC-verschlüsselter Kommunikation zwischen App und Backend.

Beim Architektur-Entwurf stellte sich die Frage, wie tief sich das Auth-Thema in das Projekt einbetten soll. Drei plausible Optionen kristallisierten sich heraus. Sie unterscheiden sich primär darin, wie standardkonform der Auth-Service implementiert wird und wie eng er an existierende Identitäts-Ökosysteme angebunden wird.

---

## 2. Recherche und Situationsanalyse

Vor der Entscheidung wurden folgende Aspekte recherchiert (alle Stand Mai 2026):

### 2.1 NIST-Standards

- **FIPS 203 (ML-KEM)** und **FIPS 204 (ML-DSA)**: seit August 2024 final, produktiv einsetzbar.
- **FIPS 205 (SLH-DSA)**: ebenfalls final, aber für unseren Use Case (mobile App-zu-Backend, geringe Latenz wichtig) ungeeignet wegen sehr grosser Signaturen.
- **IETF-Draft `draft-ietf-jose-pqc`** (für PQC-Algorithmen in JWTs): noch nicht ratifiziert, wir würden gegen ein bewegliches Ziel implementieren.

### 2.2 Mobile-TLS-Constraints

- iOS (URLSession) und Android (conscrypt) erlauben App-Code keinen zuverlässigen Zugriff auf die TLS-Cipher-Suite-Negotiation.
- Eine "End-to-End-PQC via TLS"-Behauptung wäre auf mobilen Plattformen technisch unhaltbar.
- Folge: PQ-Verschlüsselung der App-Backend-Kommunikation muss auf Application-Layer passieren, nicht nur auf Transport-Layer.

### 2.3 Identity-Broker-Pattern in der Industrie

- AWS Cognito, Auth0, Keycloak und Zitadel implementieren das Identity-Broker-Pattern: ein zentraler Auth-Service akzeptiert externe OIDC-Provider (Google, Apple, Microsoft) als Auth-Quellen und stellt nach erfolgreicher Federation einen eigenen Token aus.
- Bei den genannten Plattformen ist dieser eigene Token klassisch signiert (RS256, ES256). In unserer Arbeit wäre er ML-DSA-signiert. Genau das wäre der eigentliche Innovations-Punkt.

### 2.4 PQC-Bibliotheks-Landschaft

- **Server-seitig**: `liboqs-python` für ML-KEM und ML-DSA in Python (Wrapper um liboqs vom Open Quantum Safe Projekt).
- **Mobile-seitig**: `@noble/post-quantum` (auditiert, dependency-free) für React Native.
- **Transport-PQ**: `oqs-provider` für OpenSSL 3 hinter nginx.

### 2.5 Realistische Übergangs-Architektur

Die grossen IdPs (Google, Apple, Microsoft) werden 2026 noch keine PQC-OIDC-Tokens ausstellen. Realistisch wird das frühestens 2028 bis 2030 passieren. Eine ehrliche PQ-Architektur in 2026 muss damit umgehen, dass die "erste Etappe" der Authentifizierung klassisch bleibt. Lösung: klassische Federation, danach Übergang auf PQ-Sphäre. Diese Übergangs-Architektur wird in der Branche als "PQ-Uplift Pattern" bezeichnet.

---

## 3. Die drei evaluierten Optionen

### Option 1: Eigener voller OIDC-Provider

Wir bauen einen standardkonformen OIDC-Provider gemäss OpenID Connect 1.0 und OAuth 2.0. Mit allen Standard-Endpunkten (`/authorize`, `/token`, `/userinfo`, `/jwks.json`, `/.well-known/openid-configuration`), Client-Registrierung, Consent-Flow, Refresh-Tokens. Tokens werden ML-DSA-signiert. Theoretisch könnten sich andere Apps beim Provider anmelden und unsere User-Identitäten nutzen ("Login with my PQC IdP").

**Mehrwert:** höchste Standards-Compliance. Demonstriert tiefes Verständnis der OIDC-Spec. Volle Wiederverwendbarkeit der Identity-Infrastruktur.

**Nachteil:** hoher Boilerplate-Anteil. Etwa 60-70% des Codes gehen in OIDC-Mechanik, nicht in PQC. Riskiert, dass die eigentliche PQC-Tiefe zu kurz kommt.

### Option 2: Reines Custom Auth mit Mock-App

Wir bauen einen eigenen Auth-Service mit eigenem Token-Format (keine OIDC-Compliance). Eine Mock-App authentifiziert sich mit Email/Passwort beim Auth-Service, bekommt einen ML-DSA-signierten Token, etabliert dann eine ML-KEM-PQ-Session für die Daten-Kommunikation. Application-Layer-Verschlüsselung via AES-256-GCM.

**Mehrwert:** voller Fokus auf PQC. Maximaler Anteil PQC-Code im Projekt (ca. 60%).

**Nachteil:** nicht standardkonform. Externe User können sich nicht anmelden. Nicht produktiv einsetzbar. Wirkt wie reines Schul-Beispiel ohne Realitäts-Anker.

### Option 3: Custom Auth + Identity Broker (Federation)

Wie Option 2, aber zusätzlich mit der Fähigkeit, externe OIDC-Provider (Google und Microsoft, Apple als optionales Stretch-Goal) als Auth-Quellen zu konsumieren.

Der Auth-Service wird zum Identity Broker. Er akzeptiert sowohl lokale Credentials (Email/Passwort) als auch federated Logins via Google/Microsoft, normalisiert die Identitäten zu einem einheitlichen internen User-Modell und stellt in beiden Fällen einen eigenen ML-DSA-signierten Token aus. Danach läuft die App-Layer ML-KEM PQ-Session genau wie in Option 2.

**Mehrwert:** realistische Architektur, die dem entspricht was man in 2026 produktiv liefern würde. Demonstriert sowohl das Konsumieren von OIDC (Client-Seite) als auch eigene Auth-Logik. "PQ-Uplift Pattern" als ehrliche Übergangs-Architektur kommunizierbar.

**Nachteil:** leicht erhöhter Aufwand gegenüber Option 2 (zusätzliche OIDC-Client-Logik, Identity-Normalizer, Provider-Konfiguration für jeden externen IdP).

---

## 4. Vergleich

| Kriterium | Option 1: Full OIDC Provider | Option 2: Pure Custom Auth | Option 3: Custom Auth + Broker |
|---|---|---|---|
| **Standards-Compliance** | Hoch (OIDC-Provider-Rolle) | Keine | Mittel (OIDC-Client-Rolle, Token-Format eigen) |
| **Aufwand** | ~100-140h | ~50-70h | ~70-100h |
| **Anteil PQC-Code am Gesamtcode** | ~25% (Rest ist OIDC-Boilerplate) | ~60% | ~50% |
| **Realitäts-Anker** | Theoretisch ja, aber niemand würde 2026 einen neuen IdP selbst hosten | Niedrig (reine Demo) | Hoch (entspricht industrieller Praxis) |
| **Externe Login-Möglichkeit** | Nein (wir wären der Provider) | Nein | Ja (Google, Microsoft) |
| **Wiederverwendbarkeit der Architektur** | Hoch, aber nicht zielgerichtet | Niedrig | Hoch, zielgerichtet |
| **Risiko Sprint-Crunch** | Hoch | Niedrig | Mittel |
| **Bewertungs-Story** | "Voller OIDC-Provider mit PQC gebaut" | "PQC-Tiefe maximiert" | "Realistische 2026-Architektur, heute deploybar" |

---

## 5. Entscheidung: Option 3

Wir entscheiden uns für **Option 3: Custom Auth + Identity Broker + E2E PQC**.

Drei Gründe für die Wahl:

### 5.1 Höchster Mehrwert für Demo UND echte Nutzbarkeit

Option 3 funktioniert sowohl als Demo (man kann einfach mit Email/Passwort durch den Custom-Flow gehen und alle PQC-Aspekte sauber zeigen) als auch in einem realistischen Setting (man kann sich mit dem eigenen Google- oder Microsoft-Konto anmelden und bekommt PQ-Verschlüsselung dazu). Die beiden Aspekte konkurrieren nicht, sondern ergänzen sich. Damit erfüllt die Lösung sowohl die Anforderung "demonstriert PQC" als auch "ist in der echten Welt sinnvoll".

### 5.2 Option 1 wäre zu aufwändig für den verfügbaren Zeitrahmen

Ein voller OIDC-Provider zu bauen frisst zu viel Zeit in standardkonformer Boilerplate, die wenig mit dem eigentlichen PQC-Thema zu tun hat. Im 8.5-Wochen-Zeitfenster bei 10-15 Stunden pro Woche wäre das Risiko hoch, dass die PQC-Tiefe zu kurz kommt. Bei einem Projekt mit dem Titel "Implementing PQC" wäre das das falsche Trade-off.

### 5.3 Niemand braucht 2026 einen weiteren OIDC-Provider

Die meisten User vertrauen ohnehin lieber einem der grossen etablierten OIDC-Provider (Google, Apple, Microsoft) als einem unbekannten neuen Provider. Einen weiteren OIDC-Provider zu bauen, um ihn dann niemandem geben zu können, ist akademisch interessant, aber praktisch wenig wertvoll. Wertvoller ist: zeigen, wie man die bestehenden vertrauenswürdigen Provider nutzt und ihre klassische Auth in eine PQ-sichere Session überführt. Genau das macht Option 3.

---

## 6. Ehrliche Limitation (muss im Bericht erwähnt werden)

Die "erste Etappe" der Federation-Authentifizierung (User zu Google bzw. Microsoft) ist nicht PQ-sicher, weil Google und Microsoft 2026 noch klassisch signierte ID-Tokens (RS256) ausstellen. Erst ab dem Broker-Token, der von unserem Auth-Service ausgestellt wird, ist alles PQ-sicher.

Das ist keine Schwäche unserer Architektur, sondern eine Limitation des aktuellen Ökosystems. Sobald Google und Microsoft PQC-Tokens ausstellen (erwartet 2028 bis 2030), wird unsere Architektur automatisch end-to-end PQ-sicher, ohne Code-Änderungen am Broker. Nur die externen JWKS-Endpunkte würden andere Schlüssel liefern, was unsere Crypto-Abstraction-Layer transparent verarbeitet.

Aus Sicherheitssicht ist die klassische Pre-Auth in 2026 vertretbar: ein "Harvest Now, Decrypt Later"-Angreifer könnte zwar die Google-OIDC-Kommunikation aufzeichnen und in 10 Jahren entschlüsseln, würde dabei aber nur einen längst abgelaufenen Google-ID-Token erbeuten, der nicht mehr zum Login bei unserem Service taugt. Die eigentlichen Daten-Payloads in der PQ-Session zwischen App und Backend bleiben PQ-geschützt.

---

## 7. Nächste Schritte

1. **Requirements Engineering**: funktionale (FR) und nicht-funktionale (NFR) Anforderungen sowie Constraints (C) sauber definieren.
2. **Tech-Stack-Entscheidungen**: konkrete Libraries, Versionen und Tools pro Komponente festlegen, gemessen an den Requirements aus Schritt 1.
3. **Detail-Design**: Komponenten-Diagramm, Sequenz-Diagramme für die wichtigsten Flows (Custom-Login, Federated-Login, Session-Etablierung, geschützter API-Call), Datenfluss-Diagramm.
