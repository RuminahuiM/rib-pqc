/**
 * Profile-Screen mit echtem /api/profile-Aufruf (PQC-56 APP-3).
 *
 * Sprint-4 Carry-Over: ersetzt das Sprint-1-Skeleton durch echte Implementation.
 *
 * Flow:
 * 1. Beim Mount ruft useSecureClient.post("/api/profile", {}).
 * 2. Loading-State waehrend des Calls (ActivityIndicator).
 * 3. Success: UC-5-Felder anzeigen (user_id, email, auth_method, created_at).
 * 4. Error:
 *    - SessionExpiredError -> router.replace("/login") (Re-Auth durch User).
 *    - Generic Error -> Error-Banner mit Retry-Button.
 *
 * Wire-Format-Konformitaet: useSecureClient verschluesselt Body automatisch via
 * AES-256-GCM, decoded Server-Response analog (docs/wire_format.md Sec 5).
 */

import { useCallback, useEffect, useState } from "react";
import { router } from "expo-router";
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { useSecureClient } from "@/hooks/useSecureClient";
import { SessionExpiredError } from "@/lib/secureClient";

interface ProfilePayload {
  user_id: string;
  email: string;
  auth_method: string;
  created_at: string;
}

function isProfilePayload(value: unknown): value is ProfilePayload {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const v = value as Record<string, unknown>;
  return (
    typeof v.user_id === "string" &&
    typeof v.email === "string" &&
    typeof v.auth_method === "string" &&
    typeof v.created_at === "string"
  );
}

export default function ProfileScreen() {
  const client = useSecureClient();
  const [profile, setProfile] = useState<ProfilePayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await client.post("/api/profile", {});
      if (!isProfilePayload(data)) {
        setError("Unexpected response format from /api/profile.");
        setLoading(false);
        return;
      }
      setProfile(data);
      setLoading(false);
    } catch (e) {
      if (e instanceof SessionExpiredError) {
        // Re-Auth: zurueck zu Login. AuthContext bleibt erhalten, Session leer.
        router.replace("/login");
        return;
      }
      const msg = e instanceof Error ? e.message : String(e);
      setError(`Failed to load profile: ${msg}`);
      setLoading(false);
    }
  }, [client]);

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#208AEF" />
          <Text style={styles.hint}>Establishing PQ-Session...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error !== null) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorBanner}>
          <Text style={styles.errorTitle}>Error</Text>
          <Text style={styles.errorText}>{error}</Text>
        </View>
        <Pressable
          style={styles.retryButton}
          onPress={() => void loadProfile()}
          accessibilityRole="button"
          accessibilityLabel="Retry loading profile"
        >
          <Text style={styles.retryButtonText}>Retry</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  // Success: profile != null garantiert.
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.label}>User ID</Text>
        <Text style={styles.value}>{profile?.user_id}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>{profile?.email}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Auth Method</Text>
        <Text style={styles.value}>{profile?.auth_method}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Created At</Text>
        <Text style={styles.value}>{profile?.created_at}</Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Profile loaded via PQ-Session (ML-KEM-768 + AES-256-GCM, App-Layer-PQ).
        </Text>
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
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  hint: {
    marginTop: 16,
    fontSize: 14,
    color: "#475569",
  },
  section: {
    marginBottom: 24,
  },
  label: {
    fontSize: 12,
    color: "#94A3B8",
    fontWeight: "600",
    textTransform: "uppercase",
    marginBottom: 4,
  },
  value: {
    fontSize: 16,
    color: "#1E293B",
  },
  footer: {
    marginTop: "auto",
    paddingTop: 24,
    borderTopWidth: 1,
    borderTopColor: "#E2E8F0",
  },
  footerText: {
    fontSize: 12,
    color: "#94A3B8",
    textAlign: "center",
  },
  errorBanner: {
    backgroundColor: "#FEE2E2",
    borderLeftWidth: 4,
    borderLeftColor: "#DC2626",
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#991B1B",
    marginBottom: 4,
  },
  errorText: {
    fontSize: 14,
    color: "#7F1D1D",
  },
  retryButton: {
    backgroundColor: "#208AEF",
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    alignSelf: "flex-start",
  },
  retryButtonText: {
    color: "#FFFFFF",
    fontWeight: "600",
    fontSize: 14,
  },
});
