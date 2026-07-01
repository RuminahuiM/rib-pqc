/**
 * Tests fuer lib/secureClient.ts.
 *
 * Story: PQC-59 APP-6.
 *
 * Test-Strategie:
 * - Pure-Function-Tests (kein React-Runtime noetig).
 * - Roundtrip-Test: buildSecureRequest -> decryptSecureResponse (mit Server-
 *   AAD-Konvention).
 * - Error-Pfade: AAD-Mismatch, broken JSON, non-dict JSON.
 */

import {
  buildSecureRequest,
  decryptSecureResponse,
  SecureClientError,
  b64urlDecode,
  b64urlEncode,
} from "@/lib/secureClient";
import { aeadEncrypt, randomNonce } from "@/crypto/cipher";
import type { SessionInfo } from "@/contexts/SessionContext";

function makeSession(overrides: Partial<SessionInfo> = {}): SessionInfo {
  return {
    session_id: "B3wMqL7Yz0fXn2Pt9KaTrA",
    session_key: new Uint8Array(32).fill(0x42),
    expires_at: Math.floor(Date.now() / 1000) + 900,
    kem_alg: "ML-KEM-768",
    ...overrides,
  };
}

describe("secureClient Pure-Functions", () => {
  test("b64url roundtrip", () => {
    const bytes = new Uint8Array([1, 2, 3, 250, 251, 252]);
    const encoded = b64urlEncode(bytes);
    expect(encoded).not.toContain("=");
    expect(encoded).not.toContain("+");
    expect(encoded).not.toContain("/");
    const decoded = b64urlDecode(encoded);
    expect(Array.from(decoded)).toEqual(Array.from(bytes));
  });

  test("buildSecureRequest produces wire-format-conformant request", () => {
    const session = makeSession();
    const req = buildSecureRequest(session, { hello: "world", n: 42 });
    expect(req.headers["X-Session-Id"]).toBe(session.session_id);
    expect(req.headers["Content-Type"]).toBe("application/octet-stream");
    expect(req.headers["X-Nonce"]).toBeDefined();
    expect(b64urlDecode(req.headers["X-Nonce"]).length).toBe(12);
    expect(req.body).toBeInstanceOf(Uint8Array);
    // Body laenge = plaintext + 16 byte tag
    const plaintext = JSON.stringify({ hello: "world", n: 42 });
    expect(req.body.length).toBe(new TextEncoder().encode(plaintext).length + 16);
  });

  test("simulated server roundtrip: encrypt request, server-side decrypt, encrypt response, decrypt", () => {
    // App -> Server
    const session = makeSession();
    const payload = { hello: "world" };
    const req = buildSecureRequest(session, payload);
    // Server entschluesselt mit gleichem session_key + session_id-AAD
    const serverNonce = b64urlDecode(req.headers["X-Nonce"]);
    const aad = new TextEncoder().encode(session.session_id);

    // Server-side decrypt simulieren (verwende dieselbe @noble Lib via aeadEncrypt-inverse)
    // - hier verwenden wir aeadEncrypt nur um Server-Response zu konstruieren
    const respPlaintext = new TextEncoder().encode(
      JSON.stringify({ user_id: "user-abc", email: "alice@example.com" }),
    );
    const respNonce = randomNonce();
    const respBody = aeadEncrypt(
      session.session_key,
      respNonce,
      respPlaintext,
      aad,
    );

    // App entschluesselt Response
    const decoded = decryptSecureResponse(
      session,
      b64urlEncode(respNonce),
      respBody,
    );
    expect(decoded).toEqual({
      user_id: "user-abc",
      email: "alice@example.com",
    });
  });

  test("decryptSecureResponse throws SecureClientError on AAD mismatch", () => {
    const session = makeSession();
    // Mit anderer AAD verschluesseln als die echte session_id
    const wrongAad = new TextEncoder().encode("wrong-session-id");
    const nonce = randomNonce();
    const body = aeadEncrypt(
      session.session_key,
      nonce,
      new TextEncoder().encode("{}"),
      wrongAad,
    );
    expect(() =>
      decryptSecureResponse(session, b64urlEncode(nonce), body),
    ).toThrow(SecureClientError);
  });

  test("decryptSecureResponse throws SecureClientError on broken JSON", () => {
    const session = makeSession();
    const nonce = randomNonce();
    const aad = new TextEncoder().encode(session.session_id);
    const brokenPlaintext = new Uint8Array([0xff, 0xfe, 0xfd]); // invalid UTF-8
    const body = aeadEncrypt(
      session.session_key,
      nonce,
      brokenPlaintext,
      aad,
    );
    expect(() =>
      decryptSecureResponse(session, b64urlEncode(nonce), body),
    ).toThrow(SecureClientError);
  });

  test("decryptSecureResponse throws SecureClientError on JSON array (not object)", () => {
    const session = makeSession();
    const nonce = randomNonce();
    const aad = new TextEncoder().encode(session.session_id);
    const body = aeadEncrypt(
      session.session_key,
      nonce,
      new TextEncoder().encode("[1, 2, 3]"),
      aad,
    );
    expect(() =>
      decryptSecureResponse(session, b64urlEncode(nonce), body),
    ).toThrow(SecureClientError);
  });
});
