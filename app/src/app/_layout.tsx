/**
 * Root-Layout fuer den rib-pqc Mobile Client (PQC-20 SKL-2, erweitert in
 * PQC-57 APP-4 mit AuthProvider).
 *
 * Stack-Navigation passt zum Login-Flow:
 *   /login (initial, kein Header) -> push /home (Header sichtbar) -> push /profile
 *
 * AuthProvider wrapt den ganzen Stack damit alle Screens Auth-State haben.
 */

import { Stack } from "expo-router";

import { AuthProvider } from "@/contexts/AuthContext";

export default function RootLayout() {
  return (
    <AuthProvider>
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
    </AuthProvider>
  );
}
