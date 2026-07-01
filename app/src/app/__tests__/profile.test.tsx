/**
 * @jest-environment jsdom
 *
 * Smoke-Tests fuer Profile-Screen (PQC-56 APP-3).
 *
 * Test-Strategie:
 * - jest.mock auf @/hooks/useSecureClient + expo-router um den Screen ohne
 *   echte Network/Crypto/Navigation-Setup zu testen.
 * - 3 Tests: rendert, zeigt Loading initial, zeigt Profile nach Mock-Resolve,
 *   redirected zu /login bei SessionExpiredError.
 */

import { act, render, waitFor } from "@testing-library/react";

import { SessionExpiredError } from "@/lib/secureClient";

// Mocks BEVOR der Screen-Import den Module-Eval triggert.
const mockPost = jest.fn();
const mockReplace = jest.fn();

jest.mock("@/hooks/useSecureClient", () => ({
  useSecureClient: () => ({
    post: mockPost,
    get: jest.fn(),
    baseUrl: "http://test",
  }),
}));

jest.mock("expo-router", () => ({
  router: {
    replace: (...args: unknown[]) => mockReplace(...args),
  },
}));

// react-native Components zu schlanken Stubs reduzieren (jsdom kann RN nicht direkt).
jest.mock("react-native", () => {
  const React = require("react");
  const make = (name: string) =>
    function Stub(props: { children?: React.ReactNode }) {
      return React.createElement(name, null, props.children);
    };
  return {
    ActivityIndicator: make("ActivityIndicator"),
    Pressable: make("Pressable"),
    SafeAreaView: make("SafeAreaView"),
    StyleSheet: { create: (s: object) => s },
    Text: make("Text"),
    View: make("View"),
  };
});

import ProfileScreen from "@/app/profile";

describe("ProfileScreen", () => {
  beforeEach(() => {
    mockPost.mockReset();
    mockReplace.mockReset();
  });

  test("renders Loading initially", () => {
    mockPost.mockReturnValue(new Promise(() => {})); // never resolves
    const { container } = render(<ProfileScreen />);
    expect(container.textContent).toContain("Establishing PQ-Session");
  });

  test("renders Profile fields after successful fetch", async () => {
    mockPost.mockResolvedValue({
      user_id: "11111111-1111-1111-1111-111111111111",
      email: "alice@example.com",
      auth_method: "local",
      created_at: "2026-01-01T12:00:00Z",
    });
    const { container } = render(<ProfileScreen />);
    await waitFor(() => {
      expect(container.textContent).toContain("alice@example.com");
    });
    expect(container.textContent).toContain("11111111-1111-1111-1111-111111111111");
    expect(container.textContent).toContain("local");
    expect(container.textContent).toContain("2026-01-01T12:00:00Z");
  });

  test("redirects to /login on SessionExpiredError", async () => {
    mockPost.mockRejectedValue(new SessionExpiredError("test"));
    await act(async () => {
      render(<ProfileScreen />);
    });
    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith("/login");
    });
  });
});
