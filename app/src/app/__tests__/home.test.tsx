/**
 * @jest-environment jsdom
 *
 * Smoke-Tests fuer Home-Screen (PQC-55 APP-2).
 *
 * Test-Strategie:
 * - jest.mock auf @/contexts/AuthContext (User + Logout-Stub), expo-router
 *   (router.push/replace-Stubs) und react-native (lightweight Component-Stubs).
 * - 2 Tests: rendert Greeting + Buttons, Logout-Klick triggert logout + redirect.
 */

import { act, fireEvent, render } from "@testing-library/react";

const mockLogout = jest.fn();
const mockPush = jest.fn();
const mockReplace = jest.fn();

jest.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    user: { user_id: "user-123", auth_method: "local", external_sub: null },
    logout: mockLogout,
    broker_token: "stub",
    is_authenticated: true,
    is_loading: false,
    login: jest.fn(),
  }),
}));

jest.mock("@/contexts/SessionContext", () => ({
  useSession: () => ({
    session: null,
    isSessionValid: false,
    setSession: jest.fn(),
    clearSession: jest.fn(),
  }),
}));

jest.mock("expo-router", () => ({
  router: {
    push: (...args: unknown[]) => mockPush(...args),
    replace: (...args: unknown[]) => mockReplace(...args),
  },
}));

jest.mock("react-native", () => {
  const React = require("react");
  const make = (name: string) =>
    function Stub(props: {
      children?: React.ReactNode;
      onPress?: () => void | Promise<void>;
    }) {
      return React.createElement(
        name,
        props.onPress != null ? { onClick: props.onPress } : null,
        props.children,
      );
    };
  return {
    Pressable: make("Pressable"),
    SafeAreaView: make("SafeAreaView"),
    StyleSheet: { create: (s: object) => s },
    Text: make("Text"),
    View: make("View"),
  };
});

import HomeScreen from "@/app/home";

describe("HomeScreen (PQC-55 APP-2)", () => {
  beforeEach(() => {
    mockLogout.mockReset();
    mockPush.mockReset();
    mockReplace.mockReset();
  });

  test("renders greeting, profile link and logout button", () => {
    const { container } = render(<HomeScreen />);
    expect(container.textContent).toContain("Welcome back");
    expect(container.textContent).toContain("user-123");
    expect(container.textContent).toContain("View Profile");
    expect(container.textContent).toContain("Logout");
  });

  test("logout button triggers AuthContext.logout + router.replace('/login')", async () => {
    mockLogout.mockResolvedValueOnce(undefined);
    const { getByText } = render(<HomeScreen />);
    const logoutButton = getByText("Logout");
    await act(async () => {
      fireEvent.click(logoutButton);
    });
    expect(mockLogout).toHaveBeenCalledTimes(1);
    expect(mockReplace).toHaveBeenCalledWith("/login");
  });
});
