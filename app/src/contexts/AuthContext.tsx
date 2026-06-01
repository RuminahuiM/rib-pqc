/**
 * AuthContext: Globaler Auth-State (PQC-57 APP-4).
 *
 * Halt Broker-Token, User-Info, isAuthenticated-Flag und Loading-State.
 * Login/Logout-Methoden integrieren expo-secure-store (PQC-62 APP-9).
 * Auto-Login beim App-Start prueft client-side ob persistierter Token
 * noch nicht abgelaufen ist (jwt-decode exp-Claim).
 *
 * Verwendung in Screens via `useAuth()` Hook.
 *
 * Sprint-1 Scope:
 *   - `login(token)` ist die Schnittstelle die Login-Screen (PQC-54)
 *     aufruft mit einem Dummy-Token. Echter Server-Call kommt in PQC-59
 *     (APP-6 secureClient).
 *   - `user_info` ist Sprint-1 nur der `sub`-Claim aus dem Token-Payload.
 *     Profile-Daten kommen in PQC-56 (APP-3 /api/profile-Call).
 */

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { deleteToken, loadToken, saveToken } from "@/lib/secureStore";
import { decodePayload, isExpired } from "@/lib/token";

interface UserInfo {
  user_id: string;
  auth_method: string;
  external_sub: string | null;
}

interface AuthState {
  broker_token: string | null;
  user: UserInfo | null;
  is_authenticated: boolean;
  is_loading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (token: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function deriveUserFromToken(token: string): UserInfo | null {
  const payload = decodePayload(token);
  if (payload == null) {
    return null;
  }
  return {
    user_id: payload.sub,
    auth_method: payload.auth_method,
    external_sub: payload.external_sub ?? null,
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    broker_token: null,
    user: null,
    is_authenticated: false,
    is_loading: true,
  });

  // Auto-Login beim Mount: Token aus secure-store laden, exp-pruefen, set state
  useEffect(() => {
    let cancelled = false;

    async function restore() {
      const token = await loadToken();

      if (cancelled) {
        return;
      }

      if (token == null || isExpired(token)) {
        // Kein Token oder abgelaufen: secure-store cleanen wenn was drin war
        if (token != null) {
          await deleteToken();
        }
        setState({
          broker_token: null,
          user: null,
          is_authenticated: false,
          is_loading: false,
        });
        return;
      }

      setState({
        broker_token: token,
        user: deriveUserFromToken(token),
        is_authenticated: true,
        is_loading: false,
      });
    }

    void restore();

    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (token: string) => {
    await saveToken(token);
    setState({
      broker_token: token,
      user: deriveUserFromToken(token),
      is_authenticated: true,
      is_loading: false,
    });
  }, []);

  const logout = useCallback(async () => {
    await deleteToken();
    setState({
      broker_token: null,
      user: null,
      is_authenticated: false,
      is_loading: false,
    });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ ...state, login, logout }),
    [state, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook fuer Screens: liefert AuthContext-State + login/logout.
 *
 * Wirft eine Exception wenn ausserhalb von AuthProvider verwendet, damit
 * Component-Tree-Misuse beim Development sofort sichtbar wird.
 */
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx == null) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
