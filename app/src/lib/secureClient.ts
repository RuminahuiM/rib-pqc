/**
 * secureClient: Pure-Functions fuer den Encrypted-Channel-Request-Aufbau.
 *
 * Story: PQC-59 APP-6.
 * Bezug: docs/wire_format.md Sec 3 (Session-Init) + Sec 5 (Encrypted-Channel).
 *
 * Diese Modul-Ebene enthaelt nur **Pure-Functions** ohne React-Dependency.
 * Die Hook-Variante mit useAuth+useSession-Wiring lebt in
 * `app/src/hooks/useSecureClient.ts`. Diese Trennung macht die Crypto-Logik
 * komplett unit-testbar.
 *
 * **Wire-Format-Konformitaet (docs/wire_format.md Sec 5):**
 * - Request: X-Session-Id + X-Nonce headers, raw octet-stream-body
 *   (ciphertext || tag), AAD = session_id.encode("ascii"), Content-Type
 *   application/octet-stream.
 * - Response: X-Nonce-Header (frische Server-Nonce), raw octet-stream-body.
 */

import { aeadDecrypt, aeadEncrypt, AeadDecryptError, randomNonce } from "@/crypto/cipher";
import type { SessionInfo } from "@/contexts/SessionContext";

export class SessionExpiredError extends Error {
  constructor(message: string = "Session expired - re-authentication required") {
    super(message);
    this.name = "SessionExpiredError";
  }
}

export class SecureClientError extends Error {
  /** HTTP-Status falls relevant (z.B. 400/401/500). */
  status?: number;
  /** Detail-Error-Code aus dem Server-Response-Body (z.B. "aead_decrypt_failed"). */
  detail?: string;

  constructor(message: string, opts?: { status?: number; detail?: string }) {
    super(message);
    this.name = "SecureClientError";
    this.status = opts?.status;
    this.detail = opts?.detail;
  }
}

// ---------------------------------------------------------------------------
// base64url-Helpers (no padding, gleiche Konvention wie Server + wire_format)
// ---------------------------------------------------------------------------

function b64urlEncode(data: Uint8Array): string {
  // btoa expects binary string. Use spread + String.fromCharCode for typed arrays.
  const binStr = Array.from(data, (b) => String.fromCharCode(b)).join("");
  return btoa(binStr).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function b64urlDecode(s: string): Uint8Array {
  const pad = "=".repeat((4 - (s.length % 4)) % 4);
  const std = (s + pad).replace(/-/g, "+").replace(/_/g, "/");
  const binStr = atob(std);
  const bytes = new Uint8Array(binStr.length);
  for (let i = 0; i < binStr.length; i++) {
    bytes[i] = binStr.charCodeAt(i);
  }
  return bytes;
}

// ---------------------------------------------------------------------------
// Pure-Function-API
// ---------------------------------------------------------------------------

export interface SecureRequest {
  /** Headers fuer fetch: X-Session-Id, X-Nonce, Content-Type. */
  headers: Record<string, string>;
  /** Body fuer fetch: raw Uint8Array ciphertext||tag. */
  body: Uint8Array;
  /** Die generierte Nonce, fuer Logging/Debug. */
  nonce: Uint8Array;
}

/**
 * Baut einen verschluesselten Request-Body + Headers fuer den DCH-Channel.
 *
 * @param session aktive SessionInfo aus useSession().
 * @param payload JSON-serialisierbares dict.
 * @returns SecureRequest mit headers + body.
 */
export function buildSecureRequest(
  session: SessionInfo,
  payload: Record<string, unknown>,
): SecureRequest {
  const plaintext = new TextEncoder().encode(JSON.stringify(payload));
  const nonce = randomNonce();
  const aad = new TextEncoder().encode(session.session_id);
  const body = aeadEncrypt(session.session_key, nonce, plaintext, aad);
  return {
    headers: {
      "X-Session-Id": session.session_id,
      "X-Nonce": b64urlEncode(nonce),
      "Content-Type": "application/octet-stream",
    },
    body,
    nonce,
  };
}

/**
 * Entschluesselt eine Server-Response. Liest X-Nonce-Header aus Headers,
 * dekodiert den Body via AES-256-GCM, parsed JSON.
 *
 * @param session aktive SessionInfo (gleiche wie beim Request).
 * @param responseNonceB64 Wert des Response-X-Nonce-Headers (base64url).
 * @param encryptedBody raw response body (ciphertext||tag).
 * @returns geparsed Response-Payload als dict.
 *
 * @throws SecureClientError bei Decrypt-Fehler oder JSON-Decode-Fehler.
 */
export function decryptSecureResponse(
  session: SessionInfo,
  responseNonceB64: string,
  encryptedBody: Uint8Array,
): Record<string, unknown> {
  const responseNonce = b64urlDecode(responseNonceB64);
  const aad = new TextEncoder().encode(session.session_id);
  let plaintext: Uint8Array;
  try {
    plaintext = aeadDecrypt(session.session_key, responseNonce, encryptedBody, aad);
  } catch (e) {
    if (e instanceof AeadDecryptError) {
      throw new SecureClientError("response AEAD-decrypt failed", {
        detail: "aead_decrypt_failed",
      });
    }
    throw e;
  }
  const text = new TextDecoder().decode(plaintext);
  try {
    const parsed = JSON.parse(text);
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
      throw new SecureClientError("response payload is not a JSON object", {
        detail: "payload_not_json",
      });
    }
    return parsed as Record<string, unknown>;
  } catch (e) {
    if (e instanceof SecureClientError) throw e;
    throw new SecureClientError("response payload is not valid JSON", {
      detail: "payload_not_json",
    });
  }
}

/**
 * Parsed eine Fehler-Response des Servers ({"detail": {"error": "..."}}).
 * Liefert den Detail-Error-Code oder null wenn das Body-Format unbekannt ist.
 */
export async function parsePlaintextErrorResponse(
  resp: Response,
): Promise<string | null> {
  try {
    const body = (await resp.json()) as { detail?: { error?: string } };
    return body?.detail?.error ?? null;
  } catch {
    return null;
  }
}

export { b64urlEncode, b64urlDecode };
