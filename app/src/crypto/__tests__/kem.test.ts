/**
 * Tests fuer crypto/kem.ts (PQC-26 CRY-6, AC-2).
 *
 * Server-Pendant: server/tests/test_liboqs_kem.py. Beide Tests validieren
 * gegen FIPS-203-Sizes (Table 3) und die NIST-Implicit-Rejection-Spec.
 */

import { kemKeygen, kemEncapsulate, kemDecapsulate } from "../kem";

describe.each(["ML-KEM-768", "ML-KEM-1024"] as const)(
  "kem %s round-trip",
  (alg) => {
    test("keygen liefert publicKey + secretKey mit korrekten FIPS-203-Sizes", () => {
      const { publicKey, secretKey } = kemKeygen(alg);
      const expectedSizes = {
        "ML-KEM-768": { pk: 1184, sk: 2400 },
        "ML-KEM-1024": { pk: 1568, sk: 3168 },
      } as const;
      expect(publicKey.length).toBe(expectedSizes[alg].pk);
      expect(secretKey.length).toBe(expectedSizes[alg].sk);
    });

    test("encapsulate + decapsulate liefert identischen sharedSecret", () => {
      const { publicKey, secretKey } = kemKeygen(alg);
      const { ciphertext, sharedSecret: ssA } = kemEncapsulate(publicKey, alg);
      const ssB = kemDecapsulate(ciphertext, secretKey, alg);
      expect(Buffer.from(ssA).equals(Buffer.from(ssB))).toBe(true);
      expect(ssA.length).toBe(32);
    });
  },
);

describe("kem ML-KEM-768 Properties", () => {
  test("zwei keygen-Aufrufe liefern unterschiedliche Keys", () => {
    const { publicKey: pk1 } = kemKeygen("ML-KEM-768");
    const { publicKey: pk2 } = kemKeygen("ML-KEM-768");
    expect(Buffer.from(pk1).equals(Buffer.from(pk2))).toBe(false);
  });

  test("zwei encapsulate gegen denselben pk liefern unterschiedliche outputs", () => {
    const { publicKey } = kemKeygen("ML-KEM-768");
    const r1 = kemEncapsulate(publicKey, "ML-KEM-768");
    const r2 = kemEncapsulate(publicKey, "ML-KEM-768");
    expect(Buffer.from(r1.ciphertext).equals(Buffer.from(r2.ciphertext))).toBe(false);
    expect(Buffer.from(r1.sharedSecret).equals(Buffer.from(r2.sharedSecret))).toBe(false);
  });

  test("FIPS-203 implicit rejection: wrong secretKey liefert Pseudo-secret, KEIN Error", () => {
    const { publicKey: pkAlice } = kemKeygen("ML-KEM-768");
    const { secretKey: skBob } = kemKeygen("ML-KEM-768");
    const { ciphertext, sharedSecret: ssAlice } = kemEncapsulate(pkAlice, "ML-KEM-768");
    // Decaps mit falschem secret-key wirft KEINEN Error, liefert ein
    // deterministisches Pseudo-Shared-Secret (FIPS 203 Alg 18 Step 9).
    const ssBob = kemDecapsulate(ciphertext, skBob, "ML-KEM-768");
    expect(ssBob.length).toBe(32);
    expect(Buffer.from(ssBob).equals(Buffer.from(ssAlice))).toBe(false);
  });
});
