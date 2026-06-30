/**
 * SessionContext: Globaler PQ-Session-State (PQC-58 APP-5).
 *
 * Haelt session_id, session_key (AES-256-GCM-Key, 32 Byte), expires_at und
 * kem_alg fuer die etablierte ML-KEM-Session zum Server. Im Gegensatz zum
 * AuthContext (Broker-Token, secure-store-persistiert) wird der Session-State
 * BEWUSST NICHT persistiert:
 *
 *   - Session-Keys sind kurzlebig (TTL 15 Min) und sollen App-Restart-sicher
 *     komplett verschwinden.
 *   - Bei jedem App-Start muss eine neue Session via `/session/init`
 *     etabliert werden (APP-6 secureClient.ts triggert das on-demand).
 *   - Keine Disk-Spuren = kein Forensik-Risk bei verlorenem Geraet.
 *
 * Sprint-4 Scope (Carry-Over aus Sprint 3):
 *   - Modul liefert nur State + setSession/clearSession.
 *   - Echtes /session/init kommt in PQC-59 (APP-6).
 *   - Auto-Refresh bei Ablauf ist Aufgabe von APP-6 secureClient.
 *
 * Verwendung in Screens und Hooks via `useSession()` Hook.
 */

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

export interface SessionInfo {
  /** URL-safe-base64-codierte 16-Byte session_id (22 chars, kein Padding). */
  session_id: string;
  /** 32-Byte AES-256-GCM-Key. NICHT persistiert. */
  session_key: Uint8Array;
  /** unix-Sekunden, Ablauf-Zeitpunkt. */
  expires_at: number;
  /** KEM-Algorithmus der Session (z.B. "ML-KEM-768"). */
  kem_alg: string;
}

interface SessionContextValue {
  session: SessionInfo | null;
  /** True wenn eine Session existiert UND noch nicht abgelaeufen ist. */
  isSessionValid: boolean;
  /** Setzt eine frische Session (typisch nach /session/init via APP-6). */
  setSession: (info: SessionInfo) => void;
  /** Loescht den Session-State (Logout, Server-Reset, oder TTL-abgelaeufen). */
  clearSession: () => void;
}

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

function _isValid(session: SessionInfo | null): boolean {
  if (session == null) {
    return false;
  }
  const nowSeconds = Math.floor(Date.now() / 1000);
  return session.expires_at > nowSeconds;
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<SessionInfo | null>(null);

  const setSession = useCallback((info: SessionInfo) => {
    setSessionState(info);
  }, []);

  const clearSession = useCallback(() => {
    setSessionState(null);
  }, []);

  // isSessionValid wird beim Render neu berechnet. Reicht fuer App-Layer-
  // Use-Case (caller prueft on read). Kein setInterval/setTimeout fuer
  // background expire (vermeidet Battery + Komplexitaet, wire_format.md
  // Sec 5 Konvention).
  const isSessionValid = _isValid(session);

  const value = useMemo<SessionContextValue>(
    () => ({ session, isSessionValid, setSession, clearSession }),
    [session, isSessionValid, setSession, clearSession],
  );

  return (
    <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
  );
}

/**
 * Hook fuer Screens und APP-6 secureClient: liefert SessionContext-State.
 *
 * Wirft eine Exception wenn ausserhalb von SessionProvider verwendet, damit
 * Component-Tree-Misuse beim Development sofort sichtbar wird.
 */
export function useSession(): SessionContextValue {
  const ctx = useContext(SessionContext);
  if (ctx == null) {
    throw new Error("useSession must be used within SessionProvider");
  }
  return ctx;
}
