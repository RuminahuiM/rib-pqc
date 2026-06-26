/**
 * Tests fuer crypto/hash.ts (PQC-26 CRY-6, AC-1 hash.ts existiert).
 *
 * NIST FIPS-180-4 SHA-256-Test-Vektor.
 */

import { hashSha256 } from "../hash";

describe("hash SHA-256", () => {
  test("Leerer Input liefert NIST-Test-Vektor", () => {
    // SHA-256("") = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    const out = hashSha256(new Uint8Array(0));
    const hex = Array.from(out)
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    expect(hex).toBe(
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    );
  });

  test("'abc' liefert NIST-Test-Vektor", () => {
    // SHA-256("abc") = ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
    const out = hashSha256(new TextEncoder().encode("abc"));
    const hex = Array.from(out)
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    expect(hex).toBe(
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
    );
  });

  test("Output ist 32 Byte", () => {
    expect(hashSha256(new TextEncoder().encode("test")).length).toBe(32);
  });
});
