# ADR-001: Identity Broker mit PQ-Uplift statt Full-OIDC-Provider

**Status:** Akzeptiert (08.05.2026, Sprint 0)

## Kontext

Der Projektrahmen verlangt einen Python-Auth-Microservice mit PQC plus Demo-App. Offen war, wie tief das Auth-Thema geht: eigener vollwertiger OIDC-Provider, reines Custom Auth als Schul-Beispiel, oder Custom Auth plus Anbindung externer Provider. Drei Optionen wurden evaluiert, Details und Vergleichstabelle in [`../03_entscheidung_auth_architektur.md`](../03_entscheidung_auth_architektur.md).

## Entscheidung

Option 3: Custom Auth plus Identity Broker. Der Service akzeptiert lokale Logins und federated Logins via Google/Microsoft, normalisiert die Identitaeten und stellt in beiden Faellen einen eigenen ML-DSA-65-signierten Broker-Token aus ("PQ-Uplift").

## Konsequenzen

- Rund 50% des Codes bleibt echter PQC-Anteil, kein OIDC-Provider-Boilerplate.
- Realistische 2026er-Architektur (Pattern wie Cognito/Keycloak/Zitadel), demonstrier- und erklaerbar.
- Ehrliche Limitation: Die Pre-Auth-Etappe zu Google/Microsoft bleibt klassisch signiert, bis die Provider PQC-Tokens ausstellen (dokumentiert im Bericht, Abschnitt 9.4).
