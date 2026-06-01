/**
 * Home-Screen (PQC-20 SKL-2, Logout in PQC-57 APP-4 angeschlossen).
 *
 * Sprint-1: Skeleton mit Logout-Button (ruft AuthContext.logout, der den
 * Token aus secure-store loescht und State leert) und Profile-Navigation.
 * Echter Home-Content (Token-Status, Test-API-Calls) kommt in PQC-55 (APP-2).
 */

import { router } from "expo-router";
import { StyleSheet, View, Text, Pressable, SafeAreaView } from "react-native";

import { useAuth } from "@/contexts/AuthContext";

export default function HomeScreen() {
  const { user, logout } = useAuth();

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.greeting}>Welcome back</Text>
        <Text style={styles.body}>
          You are signed in
          {user != null ? ` as ${user.auth_method}-user ${user.user_id}` : ""}.
          Token-Status and protected API calls will follow in PQC-55 (APP-2).
        </Text>
      </View>

      <View style={styles.buttons}>
        <Pressable
          style={[styles.button, styles.buttonPrimary]}
          onPress={() => router.push("/profile")}
        >
          <Text style={styles.buttonTextPrimary}>View Profile</Text>
        </Pressable>

        <Pressable style={styles.button} onPress={handleLogout}>
          <Text style={styles.buttonText}>Logout</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F7FA",
    paddingHorizontal: 24,
    paddingVertical: 24,
    justifyContent: "space-between",
  },
  section: {
    marginTop: 24,
  },
  greeting: {
    fontSize: 28,
    fontWeight: "700",
    color: "#1E293B",
    marginBottom: 12,
  },
  body: {
    fontSize: 14,
    color: "#475569",
    lineHeight: 20,
  },
  buttons: {
    gap: 12,
    marginBottom: 24,
  },
  button: {
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    backgroundColor: "#FFFFFF",
  },
  buttonPrimary: {
    backgroundColor: "#208AEF",
    borderColor: "#208AEF",
  },
  buttonText: {
    fontSize: 16,
    color: "#1E293B",
    fontWeight: "500",
  },
  buttonTextPrimary: {
    fontSize: 16,
    color: "#FFFFFF",
    fontWeight: "600",
  },
});
