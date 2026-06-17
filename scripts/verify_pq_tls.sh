#!/usr/bin/env bash
#
# verify_pq_tls.sh - Verifikation des hybriden Post-Quantum-TLS-Handshakes
#
# Story: PQC-44 TLS-2 (Sprint 2). NFR-Sec-1.
#
# Aufgabe:
#   Verifiziert dass der pqc-nginx-Container einen TLS 1.3 Handshake mit
#   der hybriden Key-Exchange-Group X25519MLKEM768 (NIST ML-KEM-768 + X25519,
#   gemaess RFC draft-kwiatkowski-tls-ecdhe-mlkem) anbietet.
#
# Vorgehen:
#   1. Pruefen dass docker compose laeuft und pqc-nginx-Container UP ist.
#   2. Im pqc-nginx-Container selbst openssl s_client gegen den nginx auf
#      port 443 ausfuehren - der Container hat OpenSSL 3.5 + oqs-provider
#      installiert und kennt die hybride Group X25519MLKEM768.
#   3. Output filtern auf die NamedGroup-Zeile.
#   4. Exit-Code 0 bei Erfolg, 1 sonst.
#
# Verwendung:
#   docker compose -f infra/docker-compose.yml up -d
#   ./scripts/verify_pq_tls.sh
#
# Optional: Output kann via tee in eine Log-Datei umgeleitet werden, die
# dann in der Berichts-Doku als Beweis dient (AC-3):
#   ./scripts/verify_pq_tls.sh | tee sprint_journal/sprint_2/demos/pq_tls_handshake.log

set -euo pipefail

CONTAINER="pqc-nginx"
TARGET_HOST="localhost"
TARGET_PORT="443"
TARGET_GROUP="X25519MLKEM768"

echo "=========================================="
echo "PQC-44 TLS-2 - PQ-TLS Handshake Verifikation"
echo "=========================================="
echo "Container: $CONTAINER"
echo "Target:    $TARGET_HOST:$TARGET_PORT"
echo "Group:     $TARGET_GROUP"
echo "Datum:     $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

# Schritt 1: Container-Verfuegbarkeit pruefen.
if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "FEHLER: Container '$CONTAINER' laeuft nicht."
  echo "Bitte zuerst starten:"
  echo "  cd infra && docker compose up -d"
  exit 1
fi
echo "[OK] Container '$CONTAINER' ist up."

# Schritt 2: openssl s_client gegen nginx-443.
# -groups X25519MLKEM768 zwingt den Handshake auf die hybride Gruppe.
# -tls1_3 wegen NFR-Sec-1 (kein Downgrade auf TLS 1.2).
# Output enthaelt typischerweise "Negotiated TLS1.3 group: X25519MLKEM768"
# (OpenSSL 3.5+ mit oqs-provider).
echo
echo "[INFO] Starte TLS-Handshake mit forced group $TARGET_GROUP ..."
HANDSHAKE_OUTPUT="$(docker exec "$CONTAINER" sh -c "echo '' | openssl s_client \
  -connect ${TARGET_HOST}:${TARGET_PORT} \
  -groups ${TARGET_GROUP} \
  -tls1_3 \
  -servername localhost \
  -brief 2>&1" || true)"

echo
echo "--- s_client Output ---"
echo "$HANDSHAKE_OUTPUT"
echo "--- /s_client Output ---"
echo

# Schritt 3: Output auf NamedGroup pruefen.
if echo "$HANDSHAKE_OUTPUT" | grep -qiE "(Negotiated TLS.*group|key_share|named group).*${TARGET_GROUP}"; then
  echo "[OK] Hybrid-Group $TARGET_GROUP wurde im Handshake verhandelt."
elif echo "$HANDSHAKE_OUTPUT" | grep -qi "Protocol.*TLSv1.3"; then
  # OpenSSL -brief zeigt nicht immer die Group; in dem Fall pruefen wir mit -trace.
  echo "[INFO] -brief hat group nicht gezeigt - versuche detaillierten Trace ..."
  TRACE_OUTPUT="$(docker exec "$CONTAINER" sh -c "echo '' | openssl s_client \
    -connect ${TARGET_HOST}:${TARGET_PORT} \
    -groups ${TARGET_GROUP} \
    -tls1_3 \
    -servername localhost 2>&1 | grep -iE 'group|key_share|negotiated' | head -10" || true)"
  echo "$TRACE_OUTPUT"
  if echo "$TRACE_OUTPUT" | grep -qiE "${TARGET_GROUP}"; then
    echo "[OK] Hybrid-Group $TARGET_GROUP im Trace bestaetigt."
  else
    echo "[WARN] Group $TARGET_GROUP nicht explizit in Output gefunden,"
    echo "       aber TLS 1.3 wurde verhandelt. Manueller Verify-Schritt:"
    echo "       docker exec $CONTAINER openssl s_client \\"
    echo "         -connect localhost:443 -groups $TARGET_GROUP -tls1_3 -trace"
    exit 1
  fi
else
  echo "[FEHLER] TLS-Handshake fehlgeschlagen oder Group nicht verhandelt."
  exit 1
fi

echo
echo "=========================================="
echo "[ERFOLG] PQ-TLS-Handshake mit $TARGET_GROUP verifiziert."
echo "NFR-Sec-1 erfuellt."
echo "=========================================="
