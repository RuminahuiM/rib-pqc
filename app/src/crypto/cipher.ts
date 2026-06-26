/**
 * AES-256-GCM Wrapper ueber @noble/ciphers.
 *
 * Story: PQC-26 CRY-6 + PQC-50 DCH-1 (App-Side AEAD).
 * Spec: NIST SP 800-38D, 12-Byte-Nonce.
 *
 * **Konvention:**
 * - Key: 32 Byte (HKDF-Output aus PQC-47 SES-2).
 * - Nonce: 12 Byte CSPRNG (``randomNonce()``), pro Request einmalig.
 * - Output: ciphertext || tag (concatenated, @noble/ciphers default).
 * - Tag-Laenge: 16 Byte (Default).
 *
 * Server-Pendant: ``CryptoFacade.aead_encrypt/aead_decrypt`` aus
 * ``server/crypto/facade.py``.
 *
 * **Nonce-Eindeutigkeit (F-092):** NIST SP 800-38D Section 8.2 verlangt
 * dass jede Nonce pro Key nur einmal verwendet wird. ``randomNonce()`` mit
 * CSPRNG-Quelle erfuellt das mit astronomisch hoher Wahrscheinlichkeit.
 * Replay-Schutz via Nonce-Tracking ist Server-Sache (DCH-4).
 */

import { gcm } from "@noble/ciphers/aes";
import { randomBytes } from "@noble/ciphers/utils";
import { AES_GCM_NONCE_LENGTH } from "./config";

export class AeadDecryptError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AeadDecryptError";
  }
}

/** Erzeugt eine frische 12-Byte-CSPRNG-Nonce (NIST SP 800-38D). */
export function randomNonce(): Uint8Array {
  return randomBytes(AES_GCM_NONCE_LENGTH);
}

/**
 * AES-256-GCM Encrypt. Returns ``ciphertext || tag`` konkateniert.
 *
 * @param key 32-Byte AES-256-Schluessel (HKDF-Output).
 * @param nonce 12-Byte Nonce, pro Request einmalig.
 * @param plaintext Bytes die verschluesselt werden.
 * @param aad Optional Additional Authenticated Data.
 */
export function aeadEncrypt(
  key: Uint8Array,
  nonce: Uint8Array,
  plaintext: Uint8Array,
  aad: Uint8Array = new Uint8Array(0),
): Uint8Array {
  const cipher = gcm(key, nonce, aad);
  return cipher.encrypt(plaintext);
}

/**
 * AES-256-GCM Decrypt. Wirft ``AeadDecryptError`` bei Tag-Mismatch.
 *
 * @param key 32-Byte AES-256-Schluessel.
 * @param nonce 12-Byte Nonce wie beim Encrypt-Call.
 * @param ciphertextAndTag ``ciphertext || tag`` aus ``aeadEncrypt``.
 * @param aad Muss identisch zur Encrypt-Seite sein.
 */
export function aeadDecrypt(
  key: Uint8Array,
  nonce: Uint8Array,
  ciphertextAndTag: Uint8Array,
  aad: Uint8Array = new Uint8Array(0),
): Uint8Array {
  const cipher = gcm(key, nonce, aad);
  try {
    return cipher.decrypt(ciphertextAndTag);
  } catch (err) {
    throw new AeadDecryptError(
      `AEAD tag verification failed (key/nonce/aad mismatch or tampered ciphertext): ${String(err)}`,
    );
  }
}
