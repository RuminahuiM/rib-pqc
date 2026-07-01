/**
 * useSecureClient: React-Hook fuer Encrypted-Channel-HTTP-Calls.
 *
 * Story: PQC-59 APP-6.
 * Bezug: docs/wire_format.md Sec 3 + Sec 5, AC-1/2/3.
 *
 * **API:**
 *
 * ```typescript
 * const client = useSecureClient();
 * const profile = await client.post("/api/profile", {});
 * ```
 *
 * **Verhalten:**
 *
 * 1. `ensureSession()` wird transparent vor jedem Request aufgerufen.
 *    Wenn keine valide Session existiert, etabliert er sie via POST
 *    `/session/init` mit dem Broker-Token aus `useAuth`.
 * 2. Request-Body wird mit dem Session-Key AES-256-GCM-verschluesselt
 *    (via `buildSecureRequest` aus `lib/secureClient.ts`).
 * 3. Response-Body wird mit dem Session-Key entschluesselt.
 * 4. Bei HTTP 401 `session_expired` wird die Session geclearet, neu
 *    etabliert und der Request 1x retried. Beim zweiten Fehlschlag oder
 *    bei `invalid_token` wird `SessionExpiredError` geworfen.
 *
 * **BASE_URL:** Default `http://localhost:8000`, override via
 * `EXPO_PUBLIC_API_URL` (Expo-Konvention fuer Public-Env-Vars).
 *
 * **Out-of-Scope:**
 * - Profile-Screen-Integration (APP-3 PQC-56)
 * - Logout-Flow (APP-2 PQC-55)
 * - TLS-verify=false config (Dev-Setup, Server hat self-signed cert)
 */

import { useCallback, useMemo } from "react";

import { useAuth } from "@/contexts/AuthContext";
import { useSession, type SessionInfo } from "@/contexts/SessionContext";
import {
  HKDF_INFO_DEFAULT,
  SUPPORTED_KEM_DEFAULT,
  type KemAlgorithm,
} from "@/crypto/config";
import { deriveSessionKey } from "@/crypto/hkdf";
import { kemDecapsulate, kemKeygen } from "@/crypto/kem";
import {
  b64urlDecode,
  b64urlEncode,
  buildSecureRequest,
  decryptSecureResponse,
  parsePlaintextErrorResponse,
  SecureClientError,
  SessionExpiredError,
} from "@/lib/secureClient";

const BASE_URL =
  (process.env.EXPO_PUBLIC_API_URL ?? "").trim() || "http://localhost:8000";

const SESSION_INIT_PATH = "/session/init";

interface SessionInitResponse {
  session_id: string;
  ciphertext: string;
  expires_in: number;
  kem_alg: string;
}

interface SecureClientApi {
  post: (path: string, body: Record<string, unknown>) => Promise<Record<string, unknown>>;
  get: (path: string) => Promise<Record<string, unknown>>;
  /** Liefert die Base-URL fuer Debug/Display. */
  baseUrl: string;
}

export function useSecureClient(): SecureClientApi {
  const auth = useAuth();
  const session = useSession();

  /**
   * Etabliert eine neue PQ-Session via /session/init mit dem aktuellen
   * Broker-Token. Setzt das Ergebnis im SessionContext via setSession.
   *
   * Returns die frische SessionInfo. Wirft SessionExpiredError wenn der
   * Broker-Token abgelaeufen ist (HTTP 401).
   */
  const establishSession = useCallback(
    async (kemAlg: KemAlgorithm = SUPPORTED_KEM_DEFAULT): Promise<SessionInfo> => {
      if (auth.broker_token == null) {
        throw new SessionExpiredError("no broker token - login required");
      }
      const { publicKey, secretKey } = kemKeygen(kemAlg);

      const resp = await fetch(`${BASE_URL}${SESSION_INIT_PATH}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${auth.broker_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          kem_alg: kemAlg,
          encapsulation_key: b64urlEncode(publicKey),
        }),
      });

      if (resp.status === 401) {
        throw new SessionExpiredError("broker token rejected by /session/init");
      }
      if (!resp.ok) {
        const detail = await parsePlaintextErrorResponse(resp);
        throw new SecureClientError(
          `/session/init failed with HTTP ${resp.status}`,
          { status: resp.status, detail: detail ?? undefined },
        );
      }

      const data = (await resp.json()) as SessionInitResponse;
      const sharedSecret = kemDecapsulate(
        b64urlDecode(data.ciphertext),
        secretKey,
        kemAlg,
      );
      const sessionKey = deriveSessionKey(
        sharedSecret,
        data.session_id,
        HKDF_INFO_DEFAULT,
      );
      const expiresAt = Math.floor(Date.now() / 1000) + data.expires_in;

      const info: SessionInfo = {
        session_id: data.session_id,
        session_key: sessionKey,
        expires_at: expiresAt,
        kem_alg: data.kem_alg,
      };
      session.setSession(info);
      return info;
    },
    [auth.broker_token, session],
  );

  /**
   * Stellt sicher dass eine valide Session existiert. Etabliert sonst eine
   * neue via establishSession.
   */
  const ensureSession = useCallback(async (): Promise<SessionInfo> => {
    if (session.isSessionValid && session.session != null) {
      return session.session;
    }
    return await establishSession();
  }, [session, establishSession]);

  /**
   * Sendet einen verschluesselten POST-Request und liefert die entschluesselte
   * Response. Implementiert AC-1/2/3 inklusive 1x-Auto-Retry bei 401
   * session_expired.
   */
  const post = useCallback(
    async (
      path: string,
      body: Record<string, unknown>,
    ): Promise<Record<string, unknown>> => {
      let currentSession = await ensureSession();
      // Attempt #1
      let resp = await sendOnce(currentSession, path, body);
      if (resp.status === 401) {
        const detail = await parsePlaintextErrorResponse(resp.clone());
        if (detail === "session_expired" || detail === "session_missing") {
          // Re-auth: clear stale session, establish fresh, retry once
          session.clearSession();
          currentSession = await establishSession();
          resp = await sendOnce(currentSession, path, body);
          if (resp.status === 401) {
            const detail2 = await parsePlaintextErrorResponse(resp.clone());
            throw new SessionExpiredError(
              `re-auth retry failed with HTTP 401 ${detail2 ?? ""}`,
            );
          }
        } else {
          throw new SecureClientError(
            `${path} HTTP 401 ${detail ?? ""}`,
            { status: 401, detail: detail ?? undefined },
          );
        }
      }
      if (!resp.ok) {
        const detail = await parsePlaintextErrorResponse(resp.clone());
        throw new SecureClientError(
          `${path} HTTP ${resp.status} ${detail ?? ""}`,
          { status: resp.status, detail: detail ?? undefined },
        );
      }
      // Response decrypten
      const responseNonceB64 = resp.headers.get("X-Nonce");
      if (responseNonceB64 == null) {
        throw new SecureClientError(`${path} response missing X-Nonce header`);
      }
      const encryptedBody = new Uint8Array(await resp.arrayBuffer());
      return decryptSecureResponse(currentSession, responseNonceB64, encryptedBody);
    },
    [ensureSession, establishSession, session],
  );

  const get = useCallback(
    async (path: string): Promise<Record<string, unknown>> => {
      return await post(path, {});
    },
    [post],
  );

  return useMemo<SecureClientApi>(
    () => ({ post, get, baseUrl: BASE_URL }),
    [post, get],
  );
}

/**
 * Interner Helper: einmaliger Request-Send mit Encrypt. Kein Retry-Logic.
 */
async function sendOnce(
  session: SessionInfo,
  path: string,
  body: Record<string, unknown>,
): Promise<Response> {
  const secReq = buildSecureRequest(session, body);
  return fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: secReq.headers,
    body: secReq.body,
  });
}
