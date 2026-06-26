/**
 * Jest-Konfiguration fuer die rib-pqc App.
 *
 * Story: PQC-26 CRY-6 (Client-Side Crypto-Abstraction).
 *
 * Setup:
 * - ``preset: ts-jest`` fuer TypeScript-Support ohne separate Compile-Step.
 * - ``testEnvironment: node`` weil die Crypto-Module reine JS-Logik sind
 *   (kein React-Renderer noetig). React-Component-Tests in spaeteren APP-
 *   Stories (PQC-55/56) koennen ein zusaetzliches Project mit
 *   ``jest-expo``-Preset bekommen.
 * - ``testMatch`` deckt nur die ``__tests__``-Ordner und ``.test.ts`` ab,
 *   damit nicht das ganze Expo-Source aufgescannt wird.
 */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  testMatch: [
    "**/__tests__/**/*.test.ts",
    "**/__tests__/**/*.test.tsx",
  ],
  moduleFileExtensions: ["ts", "tsx", "js", "json"],
  transform: {
    "^.+\\.tsx?$": ["ts-jest", { isolatedModules: true }],
  },
  // App-Source-Root expliziter Scope (vermeidet Scan von node_modules/.expo).
  roots: ["<rootDir>/src"],
};
