/**
 * Wrapper um expo-secure-store fuer Token-Persistenz (PQC-62 APP-9).
 *
 * Auf iOS speichert expo-secure-store im Keychain, auf Android in
 * EncryptedSharedPreferences. Beide sind hardware-backed (Secure Enclave
 * / TEE) wo verfuegbar.
 *
 * Best-Practice: zentralisierter Wrapper mit Try/Catch und gleicher API
 * fuer alle Token-Operationen. AuthContext nutzt diesen Wrapper, statt
 * direkt SecureStore-API aufzurufen.
 *
 * Schluessel-Konvention: 'rib_pqc.<purpose>' mit Punktnotation. Aktuell
 * nur ein Schluessel ('rib_pqc.broker_token'), kuenftig moeglich
 * 'rib_pqc.refresh_token', 'rib_pqc.user_id' etc.
 */

import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "rib_pqc.broker_token";

/**
 * Persistiert den Broker-Token in der hardware-backed Keychain.
 *
 * Bei einem Schreibfehler (z.B. Keychain locked) wird die Exception
 * weitergereicht damit AuthContext entsprechend reagieren kann.
 */
export async function saveToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

/**
 * Laedt den persistierten Broker-Token, oder null wenn keiner gespeichert.
 *
 * Bei einem Lesefehler (z.B. Keychain corrupt) wird null zurueckgegeben
 * damit App-Start nicht crasht. AuthContext behandelt null wie "kein Token,
 * User soll sich neu einloggen".
 */
export async function loadToken(): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch {
    return null;
  }
}

/**
 * Loescht den persistierten Broker-Token. Wird bei Logout aufgerufen.
 *
 * Idempotent: wenn kein Token gespeichert ist, ist das kein Fehler.
 */
export async function deleteToken(): Promise<void> {
  try {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  } catch {
    // Idempotent: kein Fehler wenn nichts zu loeschen ist
  }
}
