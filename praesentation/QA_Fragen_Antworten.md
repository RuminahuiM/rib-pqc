# Q&A-Vorbereitung Kolloquium (5 Min Fragerunde, 08.07.2026)

> Kurz vor der Präsi einmal durchlesen. Antworten sind als Sprechtext formuliert, jeweils 20-30 Sekunden. Backup-Folien: B1 Handshake, B2 Qualität/offene Punkte, B3 Projektvorgehen.

## Fachliche Fragen (wahrscheinlich)

**F: Warum nicht einfach warten, bis TLS überall Post-Quantum kann?**
Drei Gründe. Erstens Harvest Now, Decrypt Later: Daten, die heute mitgeschnitten werden, sind rückwirkend betroffen, warten schützt sie nicht. Zweitens hat Android bis heute kein PQ-TLS im System-Stack, ohne Zeitplan. Drittens endet TLS am Load-Balancer, meine Applikations-Schicht schützt Ende-zu-Ende darüber hinaus. Für unkritische Apps ist Warten trotzdem legitim, das sage ich auch auf der Einordnungs-Folie.

**F: Was ist ML-KEM / ML-DSA genau?**
Die zwei zentralen NIST-Standards aus dem Post-Quantum-Wettbewerb, finalisiert im August 2024 als FIPS 203 und 204. Beide basieren auf Gitter-Problemen (Module Lattices), für die weder klassische noch Quanten-Algorithmen effizient bekannt sind. ML-KEM ist ein Schlüssel-Einkapselungs-Mechanismus, also der Ersatz für den Diffie-Hellman-Schlüsseltausch, ML-DSA ersetzt RSA/ECDSA-Signaturen. Vorher hiessen sie Kyber und Dilithium.

**F: Ist AES-256 denn quantensicher?**
Ja, nach heutigem Stand. Gegen symmetrische Verschlüsselung hilft Quantencomputern nur der Grover-Algorithmus, der halbiert effektiv die Schlüssellänge: AES-256 bietet dann noch immer 128 Bit Sicherheit, das gilt als ausreichend. Deshalb braucht es PQ-Algorithmen nur für Schlüsseltausch und Signaturen.

**F: Was ist der Preis? Irgendwas muss doch teurer sein.**
Die Grössen. Ein ML-KEM-768-Public-Key ist 1184 Bytes statt 32 bei X25519, eine ML-DSA-65-Signatur ist rund 3.3 KB statt 64 Bytes, meine Tokens sind entsprechend grösser. Das kostet Bandbreite, nicht Rechenzeit, und war in meinen Messungen nie der Engpass. Genau deshalb loggt mein nginx auch grosse ClientHellos sauber.

**F: Was passiert, wenn ML-KEM auch gebrochen wird?**
Zwei Antworten. Auf Transport-Ebene fahre ich hybrid: X25519MLKEM768 kombiniert klassisch und PQ, ein Angreifer müsste beide brechen. Und in meiner Architektur ist Crypto-Agility ein Designprinzip: Algorithmen stecken hinter einer Registry mit Algorithmus-Aushandlung im Protokoll, ein Wechsel auf z.B. ML-KEM-1024 ist ein Konfigurations-Update, kein Umbau. Die App handelt den Algorithmus beim Session-Aufbau aus.

**F: Der Demo-Traffic lief über HTTP, ist das nicht unsicher?**
Bewusste Demo-Entscheidung, und genau der Punkt der Architektur: Die Vertraulichkeit trägt dort die Applikations-Schicht allein, das haben Sie im Wireshark gesehen. In Produktion liefe zusätzlich TLS darunter, beide Schichten zusammen. Für die Experten-Handys war HTTP der ehrlichste Beweis, dass die App-Schicht selbst trägt.

**F: Wie authentisch ist der Session-Handshake? Kann sich jemand dazwischenschalten?**
Der Session-Init ist an den ML-DSA-signierten Broker-Token gebunden, nur authentifizierte Clients bekommen eine Session. Der Ciphertext jeder Nachricht ist per AAD an die Session-ID gebunden, und Replay wird über Nonce-Tracking in Redis geblockt. Einen dokumentierten Schwachpunkt nenne ich offen: Die unterschiedlichen Fehlercodes erlauben theoretisch Session-ID-Enumeration, Finding F-142, Fix als SEC-6 geplant (Backup-Folie B2).

**F: Warum ein eigener Identity Broker statt Keycloak/Auth0?**
Zwei Gründe. Lernziel: Ich wollte die PQC-Integration bis auf Protokollebene selbst verstehen und bauen, das war der Kern der Semesterarbeit. Und praktisch: Keine der etablierten Lösungen bot zum Projektstart ML-DSA-signierte Tokens oder einen PQ-Applikationskanal. Federation mit Google und Microsoft ist trotzdem drin, mein Broker normalisiert deren Identitäten und stellt eigene PQ-Tokens aus.

**F: Läuft das auch auf Android?**
Die App-Schicht ja, die ist plattformunabhängig (React Native plus reine JS-Krypto via noble-post-quantum). Nur das PQ-TLS auf Schicht 1 kann Android system-seitig noch nicht, genau dafür ist die Zwei-Schichten-Architektur da.

## Projektmanagement-Fragen (wahrscheinlich)

**F: Wie bist du vorgegangen?**
Scrum, solo adaptiert: vier Sprints plus Setup-Sprint, mit dokumentierten Plannings, Reviews und Retros. Jira-Board mit über 60 Stories, MoSCoW-priorisiert, Fibonacci-Schätzung, Risk-Register mit aktiv gesteuerten Risiken. Backup-Folie B3 zeigt das.

**F: Was lief schief, was würdest du anders machen?**
Drei ehrliche Punkte. Sprint 3 war ferienbedingt zu optimistisch geplant, der Carry-Over musste in Sprint 4 per fokussiertem Marathon-Tag aufgeholt werden, Lesson: Ferien als Ferien planen. Zweitens hat mein AI-gestützter Workflow weniger nachvollziehbare Commits erzeugt als klassische Arbeit, das hat mein Mentor zu Recht angemerkt, fürs nächste Projekt: kleinere Schritte, granularere Commits. Drittens hätte ich die Container-Tests früher aufsetzen sollen: Der erste echte liboqs-Testlauf diese Woche fand zwei latente Bugs, die die Sandbox-Tests monatelang übersprungen hatten.

**F: Wie viel hat die AI gemacht, wie viel du?**
Transparent gemessen: Ich habe pro Story die tatsächliche Zeit gegen die Schätzung erfasst, Multiplier zwischen 2.8x und 10x je nach Story-Typ. Die AI war Pair-Engineer für Code-Generierung und Doku-Synthese, Architektur-Entscheidungen, Priorisierung, Reviews und alle Abnahmen liefen über mich, jede Story hat ein von mir geprüftes Evidence-File. Die Reflexion dazu ist ein eigenes Kapitel im Bericht.

**F: Wie hast du Qualität sichergestellt?**
Definition of Done pro Story, Closing-Review-Prozedur mit Findings-Tracking (145 Findings dokumentiert), 420 automatisierte Tests inklusive End-to-End-Integrationstest der kompletten Kette, seit dieser Woche reproduzierbar im Docker-Container mit echter liboqs-Krypto.

## Unangenehme Fragen (möglich, ruhig bleiben)

**F: Ist die Abgabe nicht zu spät? / Wo ist der Bericht?**
Abgabe des Berichts ist heute um Mitternacht, die Präsentation ist der vereinbarte Kolloquiums-Termin. Der Bericht ist in Finalisierung, alle Inhalte (Sprint-Journale, Evidence, Benchmarks, Findings) liegen versioniert im Repo.

**F: Die App zeigt nur Login und Profil, ist das nicht wenig?**
Der sichtbare Umfang ist bewusst klein, die Substanz liegt unter der Oberfläche: zwei PQ-Schichten, Broker mit Federation, Key-Rotation, Replay-Schutz, 420 Tests. Ich habe Tiefe vor Breite priorisiert, ein Feature mehr im UI hätte nichts über PQC bewiesen.

**F: 0x11ec im Log statt X25519MLKEM768, was ist das?**
Die IANA-Codepoint-ID von X25519MLKEM768. Ältere nginx/OpenSSL-Kombinationen kennen den Klarnamen der Gruppe noch nicht und loggen die Hex-ID, der Handshake selbst ist derselbe.
