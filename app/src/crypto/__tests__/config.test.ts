/**
 * Tests fuer crypto/config.ts (PQC-26 CRY-6, AC-3).
 */

import {
  SUPPORTED_KEM_ALGORITHMS,
  SUPPORTED_KEM_DEFAULT,
  SUPPORTED_SIGNATURE_ALGORITHMS,
  SUPPORTED_SIGNATURE_DEFAULT,
  HKDF_INFO_DEFAULT,
  AES_GCM_KEY_LENGTH,
  AES_GCM_NONCE_LENGTH,
  AES_GCM_TAG_LENGTH,
  isKemSupported,
} from "../config";

describe("config: Algorithmus-Whitelisten", () => {
  test("SUPPORTED_KEM_ALGORITHMS enthaelt beide ML-KEM-Varianten", () => {
    expect(SUPPORTED_KEM_ALGORITHMS).toContain("ML-KEM-768");
    expect(SUPPORTED_KEM_ALGORITHMS).toContain("ML-KEM-1024");
    expect(SUPPORTED_KEM_ALGORITHMS).toHaveLength(2);
  });

  test("SUPPORTED_KEM_DEFAULT ist ML-KEM-768", () => {
    expect(SUPPORTED_KEM_DEFAULT).toBe("ML-KEM-768");
  });

  test("SUPPORTED_SIGNATURE enthaelt ML-DSA-65", () => {
    expect(SUPPORTED_SIGNATURE_ALGORITHMS).toEqual(["ML-DSA-65"]);
    expect(SUPPORTED_SIGNATURE_DEFAULT).toBe("ML-DSA-65");
  });

  test("HKDF_INFO_DEFAULT ist b'app-session-v1' (matched Server)", () => {
    const decoded = new TextDecoder().decode(HKDF_INFO_DEFAULT);
    expect(decoded).toBe("app-session-v1");
  });

  test("AES-GCM Konstanten matched NIST SP 800-38D", () => {
    expect(AES_GCM_KEY_LENGTH).toBe(32); // 256 bit
    expect(AES_GCM_NONCE_LENGTH).toBe(12); // 96 bit
    expect(AES_GCM_TAG_LENGTH).toBe(16); // 128 bit
  });
});

describe("isKemSupported", () => {
  test("akzeptiert Whitelist-Werte", () => {
    expect(isKemSupported("ML-KEM-768")).toBe(true);
    expect(isKemSupported("ML-KEM-1024")).toBe(true);
  });

  test("lehnt Pre-Standard-Namen und Sub-CAT-1 ab", () => {
    expect(isKemSupported("Kyber768")).toBe(false);
    expect(isKemSupported("ML-KEM-512")).toBe(false);
    expect(isKemSupported("")).toBe(false);
  });
});
