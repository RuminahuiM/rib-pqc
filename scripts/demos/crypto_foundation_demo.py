"""Crypto-Foundation Integration-Demo (PQC-21 + PQC-25 + PQC-22).

Wird im laufenden auth-service-Container ausgefuehrt:

    docker compose exec -T auth-service python < scripts/demos/crypto_foundation_demo.py

Was hier passiert:
1. Settings laden (mit derselben Config, mit der der Service laeuft)
2. Persistierten Signing-Key vom Disk-Volume laden (/data/keys/...)
3. CryptoRegistry plus LibOqsSignature-Adapter aufbauen
4. CryptoFacade instantiieren - identisches Setup wie im Lifespan-Hook
5. Sign/Verify Round-Trip mit ML-DSA-65
6. Tamper-Test: manipulierte Payload schlaegt fehl
7. Unknown-kid: wirft UnknownKidError
8. KEM-Methoden: werfen NotImplementedError mit Verweis auf PQC-23

Output ist strukturiertes JSON pro Step, damit es ins Demo-Markdown
uebernommen werden kann.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, "/app")

from config import get_settings
from crypto import keys
from crypto.adapters.liboqs_signature import LibOqsSignature
from crypto.facade import CryptoFacade, UnknownKidError
from crypto.registry import AlgorithmNotFoundError, CryptoRegistry


def report(step: int, name: str, **fields: object) -> None:
    """Schreibe ein strukturiertes JSON-Event pro Step auf stdout."""
    payload = {"step": step, "name": name, **fields}
    print(json.dumps(payload, default=str))


def main() -> int:
    settings = get_settings()
    report(
        1,
        "settings_loaded",
        app_name=settings.app_name,
        environment=settings.environment,
        signature_alg=settings.crypto.signature.default,
        signing_kid=settings.crypto.signature.signing_kid,
        private_key_path=settings.crypto.signature.private_key_path,
        public_key_path=settings.crypto.signature.public_key_path,
    )

    secret_key = keys.load_key(Path(settings.crypto.signature.private_key_path))
    public_key = keys.load_key(Path(settings.crypto.signature.public_key_path))
    report(
        2,
        "keys_loaded_from_disk",
        secret_key_len=len(secret_key),
        public_key_len=len(public_key),
        fips_204_match_mldsa65={
            "public_key_expected_bytes": 1952,
            "secret_key_expected_bytes": 4032,
            "match": len(public_key) == 1952 and len(secret_key) == 4032,
        },
    )

    registry = CryptoRegistry()
    registry.register_signature("ML-DSA-65", LibOqsSignature("ML-DSA-65"))
    report(
        3,
        "registry_built",
        supported_signature=registry.supported_signature(),
    )

    facade = CryptoFacade(
        registry=registry,
        default_signature_alg=settings.crypto.signature.default,
        signing_kid=settings.crypto.signature.signing_kid,
        signing_secret_key=secret_key,
        verifying_keys_by_kid={settings.crypto.signature.signing_kid: public_key},
    )
    report(
        4,
        "facade_built",
        default_signature_alg=facade.supported_signature_algorithms()[0],
        signing_kid=settings.crypto.signature.signing_kid,
    )

    payload = b"crypto-foundation-demo: hallo PQC-Welt"
    signature, alg, kid = facade.sign(payload, purpose="demo")
    report(
        5,
        "sign_round_trip",
        payload_len=len(payload),
        signature_len=len(signature),
        alg=alg,
        kid=kid,
    )

    verify_ok = facade.verify(payload, signature, alg, kid)
    report(
        6,
        "verify_happy_path",
        result=verify_ok,
        expected=True,
        pass_=verify_ok is True,
    )

    tampered_payload = payload + b" tampered"
    verify_tampered = facade.verify(tampered_payload, signature, alg, kid)
    report(
        7,
        "verify_tampered_payload",
        result=verify_tampered,
        expected=False,
        pass_=verify_tampered is False,
    )

    try:
        facade.verify(payload, signature, alg, "unknown-kid")
        unknown_kid_caught = False
        unknown_kid_msg = "NO exception raised - BUG"
    except UnknownKidError as exc:
        unknown_kid_caught = True
        unknown_kid_msg = str(exc)
    report(
        8,
        "verify_unknown_kid",
        raised_unknown_kid_error=unknown_kid_caught,
        message=unknown_kid_msg,
        pass_=unknown_kid_caught,
    )

    try:
        facade.verify(payload, signature, "Dilithium3", kid)
        unknown_alg_caught = False
        unknown_alg_msg = "NO exception raised - BUG"
    except AlgorithmNotFoundError as exc:
        unknown_alg_caught = True
        unknown_alg_msg = str(exc)
    report(
        9,
        "verify_unknown_alg",
        raised_algorithm_not_found=unknown_alg_caught,
        message=unknown_alg_msg,
        pass_=unknown_alg_caught,
    )

    kem_results: dict[str, bool] = {}
    for method_name, args in [
        ("kem_keygen", ()),
        ("kem_encaps", (b"\x00" * 32, "ML-KEM-768")),
        ("kem_decaps", (b"\x00", b"\x00", "ML-KEM-768")),
    ]:
        try:
            getattr(facade, method_name)(*args)
            kem_results[method_name] = False
        except NotImplementedError:
            kem_results[method_name] = True
    report(
        10,
        "kem_methods_not_implemented",
        results=kem_results,
        pass_=all(kem_results.values()),
    )

    all_pass = (
        verify_ok is True
        and verify_tampered is False
        and unknown_kid_caught
        and unknown_alg_caught
        and all(kem_results.values())
    )
    report(
        11,
        "summary",
        all_checks_pass=all_pass,
        crypto_foundation="ready for TOK-1 / TOK-2 / AUT-3",
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(2)
