/**
 * Hash-Wrapper (SHA-256) ueber @noble/hashes.
 *
 * Story: PQC-26 CRY-6 (AC-1: hash.ts existiert).
 *
 * Aktueller Use-Case: PKCE-code_challenge (S256) und etwaige zukuenftige
 * Hash-Operationen. Wir wrapen explizit damit nachfolgende Stories
 * (z.B. PQC-60 PKCE-Refactor falls noetig) die Hash-Algorithmus-Auswahl
 * an einer Stelle aendern koennen.
 */

import { sha256 } from "@noble/hashes/sha2";

/** SHA-256-Digest. Liefert 32 Byte. */
export function hashSha256(data: Uint8Array): Uint8Array {
  return sha256(data);
}
