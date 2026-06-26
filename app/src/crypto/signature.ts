/**
 * Client-Side Signature-Verify (ML-DSA-65) ueber @noble/post-quantum.
 *
 * Story: PQC-26 CRY-6 (AC-1: signature.ts existiert).
 *
 * **Scope:**
 * - Client verifiziert nur (Broker-Token-Verify im App-Layer, falls
 *   nicht-vertrauender-Server-Setup; aktuell trust-the-server-Modell).
 * - Sign ist Server-Only (TokenService.issue, PQC-32). Auf der App-Seite
 *   gibt es deshalb absichtlich keine sign()-Funktion - das wuerde einen
 *   App-Side-Signing-Key voraussetzen den wir explizit nicht haben wollen
 *   (siehe Design-Doc).
 *
 * **API analog server/crypto/adapters/liboqs_signature.py:**
 * - ``signatureVerify(message, signature, publicKey, alg)`` -> bool.
 */

import { ml_dsa65 } from "@noble/post-quantum/ml-dsa";
import { type SignatureAlgorithm } from "./config";

/**
 * Verifiziert eine ML-DSA-65-Signatur ueber ``message`` gegen ``publicKey``.
 *
 * @returns true bei gueltiger Signatur, false sonst. Wirft KEINE Exception
 *   bei format-issues (defensive analog Server-Side LibOqsSignature.verify).
 */
export function signatureVerify(
  message: Uint8Array,
  signature: Uint8Array,
  publicKey: Uint8Array,
  alg: SignatureAlgorithm,
): boolean {
  if (alg !== "ML-DSA-65") {
    return false;
  }
  try {
    return ml_dsa65.verify(publicKey, message, signature);
  } catch {
    return false;
  }
}
