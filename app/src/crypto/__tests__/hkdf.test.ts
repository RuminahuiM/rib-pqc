/**
 * Tests fuer crypto/hkdf.ts (PQC-26 CRY-6 + PQC-47 SES-2 App-Side AC-2/AC-3).
 *
 * **Kritischer Cross-Validation-Test (F-098):** Der HKDF-Output MUSS
 * byte-identisch zum Python-Server-Output sein. Sonst zerfaellt die
 * Session-Key-Identitaet und Encrypted-Channel waere broken.
 *
 * Server-Pendant: server/tests/test_session_key_derivation.py.
 * Server-Output berechnet via:
 *   HKDF(SHA256, ikm=bytes(range(32)), salt=b"test-session-id-22ch",
 *        info=b"app-session-v1", length=32)
 * = 99c8dbb0a477ecbfcce86d97e1b56e44938fb5b0a92875671e4b5064f2aa634f
 */

import { deriveKey, deriveSessionKey } from "../hkdf";
import { HKDF_INFO_DEFAULT } from "../config";

// Deterministischer Test-Vektor matched Python-Server.
const TEST_IKM = new Uint8Array(Array.from({ length: 32 }, (_, i) => i));
const TEST_SESSION_ID = "test-session-id-22ch";
const TEST_INFO = new TextEncoder().encode("app-session-v1");
// Expected: HKDF-SHA256(ikm=0x00..0x1F, salt="test-session-id-22ch" ASCII,
//                       info="app-session-v1", length=32)
const EXPECTED_HEX =
  "99c8dbb0a477ecbfcce86d97e1b56e44938fb5b0a92875671e4b5064f2aa634f";

function bytesToHex(buf: Uint8Array): string {
  return Array.from(buf)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

describe("hkdf F-098 Cross-Validation gegen Python-Server", () => {
  test("deriveSessionKey matched Server-Output byte-identisch", () => {
    const key = deriveSessionKey(TEST_IKM, TEST_SESSION_ID, TEST_INFO);
    expect(key.length).toBe(32);
    expect(bytesToHex(key)).toBe(EXPECTED_HEX);
  });

  test("deriveKey direkt mit ASCII-bytes als Salt matched ebenfalls", () => {
    const salt = new TextEncoder().encode(TEST_SESSION_ID);
    const key = deriveKey(TEST_IKM, TEST_INFO, salt, 32);
    expect(bytesToHex(key)).toBe(EXPECTED_HEX);
  });
});

describe("hkdf RFC 5869 Properties", () => {
  test("deterministisch fuer gleiche Inputs", () => {
    const ikm = new Uint8Array(32).fill(0x42);
    const info = new TextEncoder().encode("test-info");
    const salt = new TextEncoder().encode("test-salt");
    const k1 = deriveKey(ikm, info, salt);
    const k2 = deriveKey(ikm, info, salt);
    expect(Buffer.from(k1).equals(Buffer.from(k2))).toBe(true);
  });

  test("default Output-Laenge ist 32 Byte", () => {
    const key = deriveKey(new Uint8Array(32), new Uint8Array(0), new Uint8Array(0));
    expect(key.length).toBe(32);
  });

  test("custom Output-Laenge respektiert", () => {
    const key = deriveKey(new Uint8Array(32), new Uint8Array(0), new Uint8Array(0), 64);
    expect(key.length).toBe(64);
  });

  test("Domain-Separation per info-Bytes", () => {
    const ikm = new Uint8Array(32).fill(0x42);
    const salt = new TextEncoder().encode("same-salt");
    const a = deriveKey(ikm, new TextEncoder().encode("info-A"), salt);
    const b = deriveKey(ikm, new TextEncoder().encode("info-B"), salt);
    expect(Buffer.from(a).equals(Buffer.from(b))).toBe(false);
  });

  test("Domain-Separation per salt-Bytes", () => {
    const ikm = new Uint8Array(32).fill(0x42);
    const info = new TextEncoder().encode("same-info");
    const a = deriveKey(ikm, info, new TextEncoder().encode("salt-A"));
    const b = deriveKey(ikm, info, new TextEncoder().encode("salt-B"));
    expect(Buffer.from(a).equals(Buffer.from(b))).toBe(false);
  });

  test("deriveSessionKey nutzt HKDF_INFO_DEFAULT korrekt", () => {
    const ikm = new Uint8Array(32).fill(0x42);
    const viaConvenience = deriveSessionKey(ikm, "abc", HKDF_INFO_DEFAULT);
    const viaDirect = deriveKey(
      ikm,
      HKDF_INFO_DEFAULT,
      new TextEncoder().encode("abc"),
      32,
    );
    expect(Buffer.from(viaConvenience).equals(Buffer.from(viaDirect))).toBe(true);
  });
});
