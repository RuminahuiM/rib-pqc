/**
 * Profile-Screen Placeholder (PQC-20 SKL-2 AC-3).
 *
 * Sprint-1: nur Skeleton mit Demo-User-Data. Echter Profile-Content (Call zu
 * GET /api/profile, ML-DSA-65 Token-Verifikation auf der Server-Seite) kommt
 * in PQC-56 (APP-3) bzw. PQC-52 (DCH-3 geschuetzter API-Endpoint).
 */

import { StyleSheet, View, Text, SafeAreaView } from "react-native";

export default function ProfileScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>demo@example.com</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Auth Method</Text>
        <Text style={styles.value}>local</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Token Signature Algorithm</Text>
        <Text style={styles.value}>ML-DSA-65 (FIPS 204)</Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Sprint-1 Skeleton. Echter /api/profile-Call kommt in PQC-56 (APP-3).
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
});
