/**
 * @jest-environment jsdom
 *
 * Tests fuer contexts/SessionContext.tsx.
 *
 * Story: PQC-58 (APP-5).
 *
 * Test-Strategie:
 * - renderHook aus @testing-library/react-native, wrapt useSession in
 *   SessionProvider.
 * - Standalone-Test fuer "useSession ausserhalb Provider wirft Error".
 * - State-Transitions via act() um React-Warning-free zu bleiben.
 * - expires_at-Tests mit Date.now-Manipulation (jest.useFakeTimers).
 */

import { act, renderHook } from "@testing-library/react";

import {
  SessionInfo,
  SessionProvider,
  useSession,
} from "@/contexts/SessionContext";

function makeInfo(overrides: Partial<SessionInfo> = {}): SessionInfo {
  return {
    session_id: "B3wMqL7Yz0fXn2Pt9KaTrA",
    session_key: new Uint8Array(32).fill(0x42),
    expires_at: Math.floor(Date.now() / 1000) + 900,
    kem_alg: "ML-KEM-768",
    ...overrides,
  };
}

describe("SessionContext", () => {
  test("useSession outside provider throws", () => {
    // Suppress React-internal error logs in test output.
    const originalError = console.error;
    console.error = jest.fn();
    try {
      expect(() => renderHook(() => useSession())).toThrow(
        "useSession must be used within SessionProvider",
      );
    } finally {
      console.error = originalError;
    }
  });

  test("initial state: session is null, isSessionValid false", () => {
    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });
    expect(result.current.session).toBeNull();
    expect(result.current.isSessionValid).toBe(false);
  });

  test("setSession populates state, isSessionValid true when not expired", () => {
    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });
    const info = makeInfo();
    act(() => {
      result.current.setSession(info);
    });
    expect(result.current.session).not.toBeNull();
    expect(result.current.session?.session_id).toBe(info.session_id);
    expect(result.current.session?.kem_alg).toBe("ML-KEM-768");
    expect(result.current.session?.session_key).toEqual(info.session_key);
    expect(result.current.isSessionValid).toBe(true);
  });

  test("clearSession resets state", () => {
    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });
    act(() => {
      result.current.setSession(makeInfo());
    });
    expect(result.current.session).not.toBeNull();
    act(() => {
      result.current.clearSession();
    });
    expect(result.current.session).toBeNull();
    expect(result.current.isSessionValid).toBe(false);
  });

  test("isSessionValid false when expires_at is in the past", () => {
    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });
    const expired = makeInfo({
      expires_at: Math.floor(Date.now() / 1000) - 1,
    });
    act(() => {
      result.current.setSession(expired);
    });
    expect(result.current.session).not.toBeNull();
    expect(result.current.isSessionValid).toBe(false);
  });

  test("kem_alg roundtrip for ML-KEM-1024", () => {
    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });
    act(() => {
      result.current.setSession(makeInfo({ kem_alg: "ML-KEM-1024" }));
    });
    expect(result.current.session?.kem_alg).toBe("ML-KEM-1024");
  });
});
