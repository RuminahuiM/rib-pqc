/**
 * Client-Side KEM (ML-KEM-768 / ML-KEM-1024) ueber @noble/post-quantum.
 *
 * Story: PQC-26 CRY-6.
 * Spec: FIPS 203.
 *
 * **API analog server/crypto/adapters/liboqs_kem.py LibOqsKem:**
 * - ``kemKeygen(alg)`` -> ``{publicKey, secretKey}``
 * - ``kemEncapsulate(publicKey, alg)`` -> ``{ciphertext, sharedSecret}``
 * - ``kemDecapsulate(ciphertext, secretKey, alg)`` -> sharedSecret
 *
 * **FIPS-203 Implicit-Rejection (vgl. F-090):** decapsulate liefert bei
 * einem ungueltigen ciphertext einen deterministisch-aus-(sk, ct)-abgeleiteten
 * Pseudo-shared-secret, KEINEN Error. Authentifizierung muss auf AEAD-Layer
 * per Tag erfolgen.
 *
 * **Performance (auf Apple M4 laut noble-post-quantum Bench):**
 * - ML-KEM-768: ~3'780 keygen/s, ~3'220 encapsulate/s, ~4'030 decapsulate/s.
 * - Mobile (iPhone) deutlich langsamer aber fuer Single-Session-Init ok.
 */

import { ml_kem768, ml_kem1024 } from "@noble/post-quantum/ml-kem";
import { type KemAlgorithm } from "./config";

export interface KemKeyPair {
  publicKey: Uint8Array;
  secretKey: Uint8Array;
}

export interface KemEncapsResult {
  ciphertext: Uint8Array;
  sharedSecret: Uint8Array;
}

function getKemImpl(alg: KemAlgorithm) {
  switch (alg) {
    case "ML-KEM-768":
      return ml_kem768;
    case "ML-KEM-1024":
      return ml_kem1024;
    default: {
      const _exhaustive: never = alg;
      throw new Error(`Unsupported KEM algorithm: ${String(_exhaustive)}`);
    }
  }
}

/**
 * Erzeugt ein frisches ML-KEM-Keypair.
 *
 * FIPS-203-Sizes:
 * - ML-KEM-768: publicKey 1184 B, secretKey 2400 B.
 * - ML-KEM-1024: publicKey 1568 B, secretKey 3168 B.
 */
export function kemKeygen(alg: KemAlgorithm): KemKeyPair {
  const impl = getKemImpl(alg);
  return impl.keygen();
}

/**
 * Encapsuliert gegen den ``publicKey``. Liefert (ciphertext, sharedSecret).
 *
 * FIPS-203-Sizes:
 * - ML-KEM-768: ciphertext 1088 B, sharedSecret 32 B.
 * - ML-KEM-1024: ciphertext 1568 B, sharedSecret 32 B.
 */
export function kemEncapsulate(
  publicKey: Uint8Array,
  alg: KemAlgorithm,
): KemEncapsResult {
  const impl = getKemImpl(alg);
  const result = impl.encapsulate(publicKey);
  return {
    ciphertext: result.cipherText,
    sharedSecret: result.sharedSecret,
  };
}

/**
 * Decapsuliert ``ciphertext`` mit dem ``secretKey``. Liefert sharedSecret.
 *
 * **FIPS-203 Implicit-Rejection:** wirft KEINEN Error bei ungueltigem
 * ciphertext, liefert stattdessen ein Pseudo-shared-secret. Aufrufer muss
 * Authentizitaet auf AEAD-Layer pruefen.
 */
export function kemDecapsulate(
  ciphertext: Uint8Array,
  secretKey: Uint8Array,
  alg: KemAlgorithm,
): Uint8Array {
  const impl = getKemImpl(alg);
  return impl.decapsulate(ciphertext, secretKey);
}
