# server/

**Auth-Service** (Python 3.12 plus FastAPI plus liboqs-python).

Inhalt wird ab Sprint 1 aufgebaut. Geplante Struktur:

```
server/
├── pyproject.toml
├── main.py                # FastAPI app entry
├── config.py              # pydantic-settings
├── routers/
│   ├── auth.py            # /auth/local/* Endpoints
│   ├── federated.py       # /auth/federated/<provider>/* Endpoints
│   ├── session.py         # /session/* Endpoints
│   └── api.py             # Geschützte /api/* Endpoints
├── crypto/
│   ├── registry.py        # Algorithm-Registry (KEM, Signature)
│   ├── facade.py          # CryptoFacade
│   └── adapters/          # liboqs-Adapter pro Algorithmus
├── models/
│   ├── user.py            # SQLAlchemy User-Model
│   └── session.py         # Redis-Session-Schema
├── services/
│   ├── token_service.py   # Broker-Token Sign/Verify
│   ├── idp_registry.py    # External-IdP-Plugin-Registry
│   └── idp_plugins/       # Google, Microsoft Plugins
└── tests/
    └── ...
```

Bezug zu Backlog-Stories: siehe `../docs/09_product_backlog.md`, Epic AUT, TOK, BRK, SES, DCH, CRY.

Setup (vorläufig):

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # auf Windows: .venv\Scripts\activate
pip install -e .
uvicorn main:app --reload
```
