/**
 * HKDF-SHA256 Wrapper (RFC 5869) ueber @noble/hashes.
 *
 * Story: PQC-26 CRY-6 + PQC-47 SES-2 (App-Side AC-2).
 * Bezug: docs/wire_format.md Sec 4, server/services/session_key_derivation.py.
 *
 * **Konvention fuer Session-Key-Ableitung (PQC-47):**
 * - IKM: ML-KEM-sharedSecret (32 Byte, FIPS 203).
 * - Info: ``HKDF_INFO_DEFAULT`` aus ``config.ts`` (= ``b"app-session-v1"``).
 * - Salt: ``session_id`` als ASCII-bytes des urlsafe-base64-Strings.
 * - Length: 32 Byte (AES-256-GCM-Key).
 *
 * Server-Pendant ist ``derive_session_key()`` in
 * ``server/services/session_key_derivation.py``. Cross-Validation via
 * deterministischen Test-Vektor (F-098, siehe __tests__/hkdf.test.ts).
 */

import { hkdf } from "@noble/hashes/hkdf";
import { sha256 } from "@noble/hashes/sha2";
import { AES_GCM_KEY_LENGTH } from "./config";

/**
 * HKDF-SHA256 Schluessel-Ableitung (RFC 5869).
 *
 * @param ikm Input Keying Material (z.B. ML-KEM-sharedSecret).
 * @param info Domain-Separation-Bytes.
 * @param salt Salt-Bytes (z.B. session_id.encode("ascii")).
 * @param length Output-Laenge in Bytes, Default 32 (AES-256-GCM-Key).
 */
export function deriveKey(
  ikm: Uint8Array,
  info: Uint8Array,
  salt: Uint8Array,
  length: number = AES_GCM_KEY_LENGTH,
): Uint8Array {
  return hkdf(sha256, ikm, salt, info, length);
}

/**
 * Convenience-Wrapper fuer Session-Key-Ableitung gemaess SES-2-Konvention.
 *
 * @param sharedSecret ML-KEM-sharedSecret (32 Byte).
 * @param sessionId urlsafe-base64-String wie aus Server SES-1-Response.
 * @param hkdfInfo Domain-Info aus ``config.HKDF_INFO_DEFAULT``.
 */
export function deriveSessionKey(
  sharedSecret: Uint8Array,
  sessionId: string,
  hkdfInfo: Uint8Array,
): Uint8Array {
  const salt = new TextEncoder().encode(sessionId);
  return deriveKey(sharedSecret, hkdfInfo, salt, AES_GCM_KEY_LENGTH);
}
