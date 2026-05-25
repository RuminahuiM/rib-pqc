"""Crypto-Abstraction-Layer fuer den Auth-Service.

Story-Kontext: PQC-21 (CRY-1) Algorithm Registry, PQC-22 (CRY-2) Facade,
PQC-25 (CRY-5) liboqs-Adapter.

Application-Code ruft NIE konkrete Algorithmen direkt auf. Stattdessen
geht jede Krypto-Operation durch die ``CryptoFacade``, die ihrerseits das
passende Plugin aus der ``CryptoRegistry`` zieht. Crypto-Agility ist damit
zur reinen Config-Aenderung reduziert.
"""
