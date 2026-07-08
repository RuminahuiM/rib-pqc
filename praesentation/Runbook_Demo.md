# Runbook Kolloquium-Demo, 08.07.2026, 08:30

> Alles vor Ort in dieser Reihenfolge. Gesamtdauer Setup ca. 15 Min, also spätestens 08:00 anfangen. Bei jedem Schritt steht, wie du prüfst, dass er geklappt hat.

## Packliste

- Notebook plus Netzteil, iPhone plus Kabel (Akku!), zweites Testgerät falls vorhanden
- iPhone-Hotspot aktiviert lassen können (Datenvolumen prüfen)
- Wireshark installiert, Expo Go auf dem eigenen iPhone

## Setup vor Ort (ca. 08:00)

**1. Netzwerk (5 Min).** Standard: dein iPhone-Hotspot (wie bei der Generalprobe). Notebook verbinden, dann:

```bash
ipconfig
```

IPv4 des WLAN-Adapters notieren. Bei iPhone-Hotspot ist es fast sicher wieder `172.20.10.3`. **Falls die IP anders ist:** `app/.env` anpassen (beide Zeilen) und daran denken, Metro danach mit `-c` zu starten. Schul-WLAN nur versuchen, wenn Zeit übrig ist, Hotspot ist der sichere Pfad.

**2. Server-Stack (2 Min).** Im Repo:

```bash
cd infra
docker compose up -d
docker compose ps
```

Erwartung: redis healthy, auth-service healthy, nginx up (darf "unhealthy" anzeigen, F-140, kosmetisch).

**3. Demo-User prüfen (1 Min).**

```bash
docker compose exec auth-service python -m admin list-users
```

`demo@example.com` muss existieren (Passwort: `demo-passwort-12345`). Optional zweiten User anlegen:

```bash
echo "demo-passwort-12345" | docker compose exec -T auth-service python -m admin create-user --email demo2@example.com --password-stdin
```

**4. Metro starten (2 Min).**

```bash
cd ../app
npx expo start -c
```

QR-Code bleibt im Terminal sichtbar, das ist der QR für die Experten (der auf der Folie ist nur Platzhalter mit der Generalproben-IP, im Zweifel immer den Terminal-QR zeigen).

**5. Selbsttest (3 Min), komplette Kette einmal durch:**

- iPhone-Safari: `http://<IP>:8080/health` liefert JSON (Netzwerk ok)
- Expo Go: QR scannen, App lädt
- Login `demo@example.com` / `demo-passwort-12345`
- Home: Status-Karte, Kanal amber
- Profil öffnen, zurück: Kanal grün mit ML-KEM-768 plus Session-ID

**6. Beweis-Werkzeuge vorbereiten (3 Min).**

- Wireshark starten, WLAN-Interface, Anzeigefilter: `tcp.port == 8080 && http`. Einmal Profil in der App neu laden, prüfen dass der POST /api/profile erscheint. Capture laufen lassen.
- iOS-26-TLS-Log vorbereiten: iPhone-Safari auf `https://<IP>:8443/pqc-test` (Zertifikatswarnung akzeptieren), dann:

```bash
cd ../infra
docker compose exec nginx tail -5 /opt/nginx/logs/access.log
```

Die Zeile mit `X25519MLKEM768` (oder `0x11ec`) im Terminal stehen lassen, das zeigst du in der Demo.

**7. Bildschirm:** Beamer anschliessen, offen halten: PowerPoint, Wireshark, das Terminal mit der nginx-Log-Zeile, Metro-Terminal (QR). Alt-Tab-Reihenfolge einmal üben.

## Demo-Ablauf während der Präsi (Folie 5, max 3.5 Min)

1. Folie 5 zeigen, Hotspot-Name plus Passwort ansagen, Experten scannen den METRO-QR (Beamer kurz aufs Terminal).
2. Während die App lädt: weiterreden (Skript in den Folien-Notizen).
3. Experten: Login, Profil öffnen, Home zeigt grün. Satz: "Sie haben soeben mit meinem Server einen quantensicheren Schlüssel getauscht."
4. Beamer auf Wireshark: POST /api/profile, Follow HTTP Stream, Ciphertext zeigen.
5. Beamer aufs Terminal: nginx-Zeile mit X25519MLKEM768 ("mein iPhone spricht das per iOS 26 nativ").
6. Zurück zu Folie 6/7.

## Fallback-Kaskade (nicht diskutieren, einfach umschalten)

1. **Experten-Handy klemmt:** dein iPhone ist eingeloggt, zeig es dort, Publikums-Teil überspringen.
2. **Metro/Expo klemmt:** Terminal-Demo im Container, zeigt alle 8 Schritte inkl. Replay-Block live:

```bash
cd infra
docker compose exec auth-service python -m scripts.demo_d008
```

3. **Alles klemmt:** Screenshots von der Generalprobe (heute Nacht gemacht? sonst heute früh beim Selbsttest: Home grün, Wireshark-Stream, nginx-Log) plus Folie 6 als stilisierter Beweis.

## Nach der Präsi

- `docker compose down` erst nach der Fragerunde (falls jemand die Demo nochmal sehen will).
- Uncommitted Changes von heute Nacht committen (login.tsx, home.tsx, nginx.conf ssl_curve, praesentation/), Vorschlag: `Demo D-009 + DOC-2: Kolloquiums-Demo-Fixes und Pitch-Deck`.
- Danach: Bericht fertigstellen (Abgabe Mitternacht).
