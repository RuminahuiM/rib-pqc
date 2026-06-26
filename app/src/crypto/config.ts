/**
 * Client-Side Crypto-Configuration (analog server/config.py CryptoConfig).
 *
 * Story: PQC-26 CRY-6.
 *
 * Standalone-Konstanten, kein Lifecycle-Service. App-Code referenziert die
 * Defaults z.B. fuer Session-Init: ``{kem_alg: SUPPORTED_KEM_DEFAULT}``.
 *
 * **Crypto-Agility-Prinzip:** Alle Algorithmus-Namen folgen NIST-Standard
 * ("ML-KEM-768", nicht "Kyber768"). Bei einem Algorithmus-Wechsel werden
 * nur diese Konstanten + die zugehoerigen Wrapper-Funktionen angepasst,
 * nicht jeder Aufrufer.
 */

export const SUPPORTED_KEM_ALGORITHMS = ["ML-KEM-768", "ML-KEM-1024"] as const;
export type KemAlgorithm = (typeof SUPPORTED_KEM_ALGORITHMS)[number];
export const SUPPORTED_KEM_DEFAULT: KemAlgorithm = "ML-KEM-768";

export const SUPPORTED_SIGNATURE_ALGORITHMS = ["ML-DSA-65"] as const;
export type SignatureAlgorithm =
  (typeof SUPPORTED_SIGNATURE_ALGORITHMS)[number];
export const SUPPORTED_SIGNATURE_DEFAULT: SignatureAlgorithm = "ML-DSA-65";

/**
 * HKDF-Konvention (PQC-47 SES-2): Domain-Separation-Info-Bytes muessen
 * mit Server-SessionConfig.hkdf_info uebereinstimmen.
 */
export const HKDF_INFO_DEFAULT = new TextEncoder().encode("app-session-v1");

/** AES-256-GCM Key-Laenge in Bytes (passt zum HKDF-Default-Output). */
export const AES_GCM_KEY_LENGTH = 32;

/** AES-GCM Nonce-Laenge in Bytes (NIST SP 800-38D Default). */
export const AES_GCM_NONCE_LENGTH = 12;

/** AES-GCM Tag-Laenge in Bytes (NIST SP 800-38D Default). */
export const AES_GCM_TAG_LENGTH = 16;

/** Liefert true wenn ``alg`` ein vom Client unterstuetzter KEM ist. */
export function isKemSupported(alg: string): alg is KemAlgorithm {
  return (SUPPORTED_KEM_ALGORITHMS as readonly string[]).includes(alg);
}
