# scripts/

**Demo- und Verifikations-Scripts.**

Inhalt wird ab Sprint 2 aufgebaut. Geplante Inhalte:

- `verify_pq_tls.sh`: Verifiziert via oqs-curl, dass der nginx-Server eine X25519MLKEM768-Handshake anbietet (NFR-Sec-1).
- `benchmark_session.py`: Misst Session-Etablierungs-Latenz für NFR-Perf-1 (siehe Sprint 4).
- `benchmark_token.py`: Misst Token-Verifikations-Latenz für NFR-Perf-2.
- `benchmark_aead.py`: Misst AES-GCM-Overhead pro API-Call für NFR-Perf-3.
- `create_test_user.sh`: Wrapper um Admin-CLI für lokale Test-User-Erstellung.

Bezug zu Backlog-Stories: siehe `../docs/09_product_backlog.md`, Epic QUA und TLS.
