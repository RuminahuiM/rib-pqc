/**
 * Root-Layout fuer den rib-pqc Mobile Client (PQC-20 SKL-2, erweitert in
 * PQC-57 APP-4 mit AuthProvider, PQC-58 APP-5 mit SessionProvider).
 *
 * Stack-Navigation passt zum Login-Flow:
 *   /login (initial, kein Header) -> push /home (Header sichtbar) -> push /profile
 *
 * Provider-Tree (outer -> inner):
 *   AuthProvider (persistierter Broker-Token in secure-store)
 *     SessionProvider (in-memory PQ-Session-State, KEIN secure-store)
 *       Stack (Screens)
 *
 * Reihenfolge: AuthProvider aussen weil SessionProvider in APP-6
 * potenziell den Broker-Token aus useAuth lesen wird um /session/init zu
 * authentifizieren.
 */

import { Stack } from "expo-router";

import { AuthProvider } from "@/contexts/AuthContext";
import { SessionProvider } from "@/contexts/SessionContext";

export default function RootLayout() {
  return (
    <AuthProvider>
      <SessionProvider>
        <Stack
          screenOptions={{
            headerStyle: { backgroundColor: "#208AEF" },
            headerTintColor: "#FFFFFF",
            headerTitleStyle: { fontWeight: "600" },
          }}
        >
          <Stack.Screen name="index" options={{ headerShown: false }} />
          <Stack.Screen
            name="login"
            options={{ title: "Login", headerShown: false }}
          />
          <Stack.Screen
            name="home"
            options={{ title: "Home", headerBackVisible: false }}
          />
          <Stack.Screen name="profile" options={{ title: "Profile" }} />
        </Stack>
      </SessionProvider>
    </AuthProvider>
  );
}
