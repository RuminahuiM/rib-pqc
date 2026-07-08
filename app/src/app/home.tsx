/**
 * Home-Screen (PQC-20 SKL-2, PQC-55 APP-2, Demo-Polish D-009 07.07.2026).
 *
 * Zeigt nach dem Login den PQC-Sicherheits-Status als Demo-Kernstueck
 * (Kolloquium 08.07.2026, loest F-123 Demo-Banner ein):
 * - Identitaet: ML-DSA-65-signierter Broker-Token (FIPS 204).
 * - Kanal: ML-KEM-768-Session + AES-256-GCM (FIPS 203), live aus
 *   SessionContext sobald der erste verschluesselte API-Call lief.
 */

import { router } from "expo-router";
import { StyleSheet, View, Text, Pressable, SafeAreaView } from "react-native";

import { useAuth } from "@/contexts/AuthContext";
import { useSession } from "@/contexts/SessionContext";

export default function HomeScreen() {
  const { user, logout } = useAuth();
  const { session, isSessionValid } = useSession();

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  const authMethodLabel =
    user?.auth_method === "google"
      ? "Google-Konto (via Identity Broker)"
      : user?.auth_method === "microsoft"
        ? "Microsoft-Konto (via Identity Broker)"
        : "Email und Passwort";

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.greeting}>Welcome back</Text>
        <Text style={styles.body}>
          You are signed in
          {user != null ? ` as ${user.auth_method}-user ${user.user_id}` : ""}.
        </Text>

        <View style={styles.statusCard}>
          <Text style={styles.statusTitle}>
            Du bist jetzt Post-Quantum-gesichert
          </Text>

          <View style={styles.statusRow}>
            <View style={[styles.statusDot, styles.dotActive]} />
            <View style={styles.statusTextBlock}>
              <Text style={styles.statusLabel}>Identitaet</Text>
              <Text style={styles.statusValue}>
                Login via {authMethodLabel}. Dein Token ist mit ML-DSA-65
                signiert (NIST FIPS 204), einer Signatur, die auch ein
                Quantencomputer nicht faelschen kann.
              </Text>
            </View>
          </View>

          <View style={styles.statusRow}>
            <View
              style={[
                styles.statusDot,
                isSessionValid ? styles.dotActive : styles.dotPending,
              ]}
            />
            <View style={styles.statusTextBlock}>
              <Text style={styles.statusLabel}>Verschluesselter Kanal</Text>
              {isSessionValid && session != null ? (
                <Text style={styles.statusValue}>
                  Aktiv: Schluesseltausch via {session.kem_alg} (NIST FIPS
                  203), Daten verschluesselt mit AES-256-GCM. Session{" "}
                  {session.session_id.slice(0, 8)}...
                </Text>
              ) : (
                <Text style={styles.statusValue}>
                  Wird beim ersten API-Call etabliert: ML-KEM-768-Handshake
                  plus AES-256-GCM. Oeffne dein Profil, um den Kanal
                  aufzubauen.
                </Text>
              )}
            </View>
          </View>

          <Text style={styles.statusFootnote}>
            Alles, was diese App sendet, ist gegen "Harvest Now, Decrypt
            Later" geschuetzt: selbst mitgeschnittener Verkehr bleibt auch
            in der Quanten-Aera unlesbar.
          </Text>
        </View>
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
  statusCard: {
    marginTop: 20,
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#DBEAFE",
    padding: 16,
    gap: 14,
  },
  statusTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#0F3D91",
  },
  statusRow: {
    flexDirection: "row",
    gap: 10,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginTop: 5,
  },
  dotActive: {
    backgroundColor: "#16A34A",
  },
  dotPending: {
    backgroundColor: "#F59E0B",
  },
  statusTextBlock: {
    flex: 1,
  },
  statusLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: "#1E293B",
    marginBottom: 2,
  },
  statusValue: {
    fontSize: 13,
    color: "#475569",
    lineHeight: 18,
  },
  statusFootnote: {
    fontSize: 12,
    color: "#64748B",
    lineHeight: 17,
    borderTopWidth: 1,
    borderTopColor: "#E2E8F0",
    paddingTop: 12,
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
