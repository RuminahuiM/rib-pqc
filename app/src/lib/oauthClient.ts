/**
 * OAuth-Client fuer External-IdP-Login (Google, Microsoft).
 *
 * Stories: PQC-60 APP-7 (Google), PQC-61 APP-8 (Microsoft).
 *
 * Flow (BFF + Server-managed PKCE, siehe PQC-37 BRK-2 + PQC-42 BRK-7):
 *   1. App generiert PKCE-Verifier (RFC 7636, 43-128 chars urlsafe-base64).
 *   2. App POSTet verifier zu /auth/federated/<provider>/authorize.
 *   3. Server speichert verifier + erzeugt state in Redis, returnt
 *      {authorize_url, state}.
 *   4. App oeffnet authorize_url im System-Browser
 *      (WebBrowser.openAuthSessionAsync).
 *   5. Provider redirect zu unserer registrierten redirect_uri (Server-Side
 *      in PQC-84 als http://localhost:8000/auth/<provider>/callback
 *      konfiguriert).
 *   6. (PROD/DEMO-Limitation, F-086): aktuell kommt der Browser nicht
 *      zur App zurueck, weil redirect_uri Server-Side ist statt
 *      Custom-Scheme. Live-Demo Sprint-3-Polish.
 *   7. App POSTet {code, state} an /auth/federated/<provider>/callback.
 *   8. Server tauscht Code, validiert ID-Token, link_or_create User,
 *      stellt Broker-Token aus.
 *   9. App speichert Broker-Token via AuthContext.login(broker_token).
 */

import * as Crypto from "expo-crypto";
import * as WebBrowser from "expo-web-browser";

const SERVER_BASE_URL = process.env.EXPO_PUBLIC_SERVER_BASE_URL ?? "http://localhost:8000";

export type ProviderName = "google" | "microsoft";

interface AuthorizeStartResponse {
  authorize_url: string;
  state: string;
}

interface CallbackResponse {
  id_token: string;
  access_token?: string;
  expires_in?: number;
  token_type: string;
  user: { id: string; email: string; auth_method: string };
  broker_token: string;
  broker_token_expires_in: number;
}

export class OAuthError extends Error {
  constructor(message: string, public reason?: string) {
    super(message);
    this.name = "OAuthError";
  }
}

/**
 * Generiert einen kryptografisch sicheren PKCE-Verifier (RFC 7636).
 *
 * Story-Bezug: PQC-60 APP-7 AC-2 (PKCE code_verifier korrekt generiert).
 *
 * - 64 Zeichen lang (innerhalb 43-128 Limit)
 * - Zeichensatz: A-Z a-z 0-9 - . _ ~ (unreserved chars per RFC 3986)
 * - Mindestens 256 bit Entropie (deutlich mehr als die geforderten 128 bit
 *   aus AC-3 fuer State).
 */
export async function generatePkceVerifier(): Promise<string> {
  // expo-crypto liefert 32 random bytes, base64url-encoded ergibt das ~43
  // chars. Wir nehmen 48 bytes -> 64 chars urlsafe-base64.
  const randomBytes = await Crypto.getRandomBytesAsync(48);
  return base64urlEncode(randomBytes);
}

function base64urlEncode(bytes: Uint8Array): string {
  // expo-crypto liefert Uint8Array. base64 -> urlsafe (replace +/= mit -_/empty).
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  // btoa ist in modernen RN-Versionen verfuegbar; sonst Buffer-Fallback.
  const base64 = typeof btoa !== "undefined"
    ? btoa(binary)
    : Buffer.from(binary, "binary").toString("base64");
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

/**
 * Startet den OIDC-Login-Flow fuer einen Provider und gibt einen
 * Broker-Token zurueck.
 *
 * Story-Bezug: PQC-60 APP-7 / PQC-61 APP-8.
 *
 * @throws OAuthError bei jeder Stelle die failed.
 */
export async function loginWithProvider(
  provider: ProviderName,
): Promise<CallbackResponse> {
  // AC-2: PKCE code_verifier generieren.
  const codeVerifier = await generatePkceVerifier();

  // 1. Authorize-Start: Server speichert verifier + erzeugt state.
  // AC-3: State-Entropie 256 bit kommt vom Server (secrets.token_urlsafe(32)).
  const startResponse = await fetch(
    `${SERVER_BASE_URL}/auth/federated/${provider}/authorize`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code_verifier: codeVerifier }),
    },
  );
  if (!startResponse.ok) {
    throw new OAuthError(
      `Authorize-Start failed: HTTP ${startResponse.status}`,
      "authorize_start_failed",
    );
  }
  const startData: AuthorizeStartResponse = await startResponse.json();

  // AC-1: System-Browser-Tab mit Google/Microsoft /authorize oeffnen.
  // openAuthSessionAsync blockiert bis Redirect zurueck zur App kommt
  // (via Custom-Scheme oder Web-Auth-Proxy). Live-Demo-Limitation siehe
  // F-086: aktuell ist redirect_uri Server-Side, App-Side-Return blocked.
  const returnUrl = `app://oauth/${provider}/callback`;
  const browserResult = await WebBrowser.openAuthSessionAsync(
    startData.authorize_url,
    returnUrl,
  );

  if (browserResult.type !== "success" || !browserResult.url) {
    // User hat Browser geschlossen oder Redirect kam nicht zur App zurueck
    // (F-086 Limitation).
    throw new OAuthError(
      `OAuth-Session ended without success: type=${browserResult.type}`,
      "browser_cancelled",
    );
  }

  // AC-4: Parse code+state aus Deep-Link-URL.
  const url = new URL(browserResult.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  if (!code || !state) {
    throw new OAuthError(
      "Callback URL missing 'code' or 'state' parameter",
      "callback_params_missing",
    );
  }
  if (state !== startData.state) {
    // Server validiert das auch nochmal via consume(), aber wir checken
    // app-side fuer Fail-Fast.
    throw new OAuthError("State mismatch (CSRF protection)", "state_mismatch");
  }

  // POST callback an Server. code_verifier muss NICHT mitgeschickt werden
  // (BFF-Pattern, PQC-42 BRK-7: Server liest verifier aus Redis-Eintrag).
  const callbackResponse = await fetch(
    `${SERVER_BASE_URL}/auth/federated/${provider}/callback`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, state }),
    },
  );
  if (!callbackResponse.ok) {
    const errorBody = await callbackResponse.json().catch(() => ({}));
    throw new OAuthError(
      `Callback failed: HTTP ${callbackResponse.status} - ${JSON.stringify(errorBody)}`,
      errorBody.detail?.error ?? "callback_failed",
    );
  }
  return await callbackResponse.json();
}
