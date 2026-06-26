/**
 * Tests fuer crypto/cipher.ts (PQC-26 CRY-6 + PQC-50 DCH-1 App-Side).
 */

import {
  aeadEncrypt,
  aeadDecrypt,
  randomNonce,
  AeadDecryptError,
} from "../cipher";

function freshKey(): Uint8Array {
  const k = new Uint8Array(32);
  crypto.getRandomValues(k);
  return k;
}

describe("cipher AES-256-GCM", () => {
  test("encrypt + decrypt roundtrip", () => {
    const key = freshKey();
    const nonce = randomNonce();
    const plaintext = new TextEncoder().encode("hello pq session");
    const blob = aeadEncrypt(key, nonce, plaintext);
    const restored = aeadDecrypt(key, nonce, blob);
    expect(new TextDecoder().decode(restored)).toBe("hello pq session");
  });

  test("randomNonce liefert 12 Byte CSPRNG", () => {
    const n1 = randomNonce();
    const n2 = randomNonce();
    expect(n1.length).toBe(12);
    expect(n2.length).toBe(12);
    expect(Buffer.from(n1).equals(Buffer.from(n2))).toBe(false);
  });

  test("output ist ciphertext concatenated with tag (NIST SP 800-38D)", () => {
    const key = freshKey();
    const nonce = randomNonce();
    const plaintext = new Uint8Array(50).fill(0xaa);
    const blob = aeadEncrypt(key, nonce, plaintext);
    expect(blob.length).toBe(plaintext.length + 16); // tag 16 byte hinten an
  });

  test("AAD authentisch aber nicht verschluesselt", () => {
    const key = freshKey();
    const nonce = randomNonce();
    const plaintext = new TextEncoder().encode("payload");
    const aad = new TextEncoder().encode("session-id=abc");
    const blob = aeadEncrypt(key, nonce, plaintext, aad);
    const restored = aeadDecrypt(key, nonce, blob, aad);
    expect(new TextDecoder().decode(restored)).toBe("payload");
  });

  test("tampered ciphertext wirft AeadDecryptError", () => {
    const key = freshKey();
    const nonce = randomNonce();
    const blob = aeadEncrypt(key, nonce, new TextEncoder().encode("payload"));
    const tampered = new Uint8Array(blob);
    tampered[0] ^= 0x01;
    expect(() => aeadDecrypt(key, nonce, tampered)).toThrow(AeadDecryptError);
  });

  test("tampered tag wirft AeadDecryptError", () => {
    const key = freshKey();
    const nonce = randomNonce();
    const blob = aeadEncrypt(key, nonce, new TextEncoder().encode("payload"));
    const tampered = new Uint8Array(blob);
    tampered[tampered.length - 1] ^= 0x01;
    expect(() => aeadDecrypt(key, nonce, tampered)).toThrow(AeadDecryptError);
  });

  test("wrong key wirft AeadDecryptError", () => {
    const key = freshKey();
    const nonce = randomNonce();
    const blob = aeadEncrypt(key, nonce, new TextEncoder().encode("payload"));
    const wrongKey = freshKey();
    expect(() => aeadDecrypt(wrongKey, nonce, blob)).toThrow(AeadDecryptError);
  });

  test("wrong AAD wirft AeadDecryptError", () => {
    const key = freshKey();
    const nonce = randomNonce();
    const plaintext = new TextEncoder().encode("payload");
    const blob = aeadEncrypt(key, nonce, plaintext, new TextEncoder().encode("AAD-A"));
    expect(() =>
      aeadDecrypt(key, nonce, blob, new TextEncoder().encode("AAD-B")),
    ).toThrow(AeadDecryptError);
  });
});


// --- PQC-50 DCH-1: Dezidierte Cross-Compatibility-Tests ---

describe("PQC-50 DCH-1: AES-GCM mit randomNonce + Random-Plaintext", () => {
  test("random-length Plaintext (1..1024 byte) roundtrip", () => {
    const key = freshKey();
    const nonce = randomNonce();
    const len = 1 + Math.floor(Math.random() * 1024);
    const plaintext = new Uint8Array(len);
    crypto.getRandomValues(plaintext);
    const blob = aeadEncrypt(key, nonce, plaintext);
    const restored = aeadDecrypt(key, nonce, blob);
    expect(Buffer.from(restored).equals(Buffer.from(plaintext))).toBe(true);
  });

  test("randomNonce + Server-konformer AAD-Roundtrip (session_id als bytes)", () => {
    // Simulation der DCH-2/DCH-3-Konvention: session_id wird als AAD gebunden.
    const key = freshKey();
    const nonce = randomNonce();
    const sessionIdAad = new TextEncoder().encode("sess_AB1234567890CDEF");
    const plaintext = new TextEncoder().encode('{"path":"/api/profile"}');
    const blob = aeadEncrypt(key, nonce, plaintext, sessionIdAad);
    const restored = aeadDecrypt(key, nonce, blob, sessionIdAad);
    expect(new TextDecoder().decode(restored)).toBe('{"path":"/api/profile"}');
  });
});
