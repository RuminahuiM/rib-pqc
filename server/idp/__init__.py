"""External Identity Provider (IdP) Federation.

Story-Kontext:
- PQC-36 (BRK-1): IdpRegistry plus Plugin-Schnittstelle, analog crypto/registry.py.
- PQC-40 (BRK-5): GoogleIdpPlugin Voll-Implementation (verify_id_token gegen JWKS).
- PQC-41 (BRK-6): MicrosoftIdpPlugin Voll-Implementation.
- PQC-39 (BRK-4): claim_mapper-Logik fuer Identity-Normalisierung.
- PQC-38 (BRK-3): verify_id_token mit JWKS-Caching.

Architektur folgt dem crypto/-Pattern (Protocol + Registry + Plugin-Adapter).
"""
