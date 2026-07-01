/**
 * @jest-environment jsdom
 *
 * Smoke-Tests fuer useSecureClient Hook.
 *
 * Story: PQC-59 APP-6.
 *
 * Test-Strategie:
 * - 2 Smoke-Tests: Hook ausserhalb Provider wirft, baseUrl ist gesetzt.
 * - Voll-Integration-Tests (fetch-Mock + Re-Auth-Retry) sind komplexer und
 *   werden im D-009-Mobile-Demo gegen echten Server gemacht (oder Sprint-4
 *   Polish QUA-5).
 */

import { ReactNode } from "react";
import { renderHook } from "@testing-library/react";

import { AuthProvider } from "@/contexts/AuthContext";
import { SessionProvider } from "@/contexts/SessionContext";
import { useSecureClient } from "@/hooks/useSecureClient";

function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <SessionProvider>{children}</SessionProvider>
    </AuthProvider>
  );
}

describe("useSecureClient", () => {
  // SecureStore-Module ist nicht im jsdom-Test-Env. AuthProvider's loadToken
  // wuerde failen ohne Mock - silencen mit jest-mock auf @/lib/secureStore.
  beforeAll(() => {
    jest.mock("@/lib/secureStore", () => ({
      loadToken: jest.fn().mockResolvedValue(null),
      saveToken: jest.fn().mockResolvedValue(undefined),
      deleteToken: jest.fn().mockResolvedValue(undefined),
    }));
  });

  test("returns API with post, get, baseUrl when inside providers", () => {
    const { result } = renderHook(() => useSecureClient(), {
      wrapper: Providers,
    });
    expect(typeof result.current.post).toBe("function");
    expect(typeof result.current.get).toBe("function");
    expect(typeof result.current.baseUrl).toBe("string");
    expect(result.current.baseUrl.length).toBeGreaterThan(0);
  });

  test("useSecureClient outside SessionProvider throws", () => {
    const originalError = console.error;
    console.error = jest.fn();
    try {
      // Wrap only in AuthProvider, NOT SessionProvider
      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );
      expect(() => renderHook(() => useSecureClient(), { wrapper })).toThrow(
        "useSession must be used within SessionProvider",
      );
    } finally {
      console.error = originalError;
    }
  });
});
