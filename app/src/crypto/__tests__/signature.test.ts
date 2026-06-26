/**
 * Tests fuer crypto/signature.ts (PQC-26 CRY-6).
 *
 * Verify-Only auf Client-Side. Sign-Side ist Server-Only (TokenService.issue
 * aus PQC-32). Wir nutzen ml_dsa65.sign nur im Test um einen verifizierbaren
 * Token zu erzeugen.
 */

import { ml_dsa65 } from "@noble/post-quantum/ml-dsa";
import { signatureVerify } from "../signature";

describe("signature ML-DSA-65 verify", () => {
  test("akzeptiert echte Signatur", () => {
    const { publicKey, secretKey } = ml_dsa65.keygen();
    const msg = new TextEncoder().encode("broker-token-body");
    const sig = ml_dsa65.sign(secretKey, msg);
    expect(signatureVerify(msg, sig, publicKey, "ML-DSA-65")).toBe(true);
  });

  test("lehnt tampered message ab", () => {
    const { publicKey, secretKey } = ml_dsa65.keygen();
    const msg = new TextEncoder().encode("original");
    const sig = ml_dsa65.sign(secretKey, msg);
    const tampered = new TextEncoder().encode("tampered");
    expect(signatureVerify(tampered, sig, publicKey, "ML-DSA-65")).toBe(false);
  });

  test("lehnt tampered signature ab", () => {
    const { publicKey, secretKey } = ml_dsa65.keygen();
    const msg = new TextEncoder().encode("payload");
    const sig = ml_dsa65.sign(secretKey, msg);
    sig[10] ^= 0x01;
    expect(signatureVerify(msg, sig, publicKey, "ML-DSA-65")).toBe(false);
  });

  test("lehnt wrong public key ab", () => {
    const alice = ml_dsa65.keygen();
    const bob = ml_dsa65.keygen();
    const msg = new TextEncoder().encode("payload");
    const sig = ml_dsa65.sign(alice.secretKey, msg);
    expect(signatureVerify(msg, sig, bob.publicKey, "ML-DSA-65")).toBe(false);
  });

  test("malformed inputs propagieren als false (no exception)", () => {
    // @ts-expect-error - test fuer defensive Exception-Catch
    expect(signatureVerify(new Uint8Array(0), new Uint8Array(0), new Uint8Array(0), "ML-DSA-65")).toBe(false);
  });
});
