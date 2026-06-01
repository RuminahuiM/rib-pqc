/**
 * Root-Index-Screen (PQC-20 SKL-2, erweitert in PQC-57 APP-4).
 *
 * Reagiert auf Auth-State:
 *   - is_loading=true: Loading-Indicator (Auto-Login laeuft, Token aus
 *     secure-store wird geladen)
 *   - is_authenticated=true: Redirect zu /home
 *   - sonst: Redirect zu /login
 *
 * Damit kein UI-Flicker zwischen /home und /login beim App-Start, der
 * Loading-Spinner ueberbrueckt den short async-call zu expo-secure-store.
 */

import { Redirect } from "expo-router";
import { ActivityIndicator, StyleSheet, View } from "react-native";

import { useAuth } from "@/contexts/AuthContext";

export default function Index() {
  const { is_authenticated, is_loading } = useAuth();

  if (is_loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#208AEF" />
      </View>
    );
  }

  if (is_authenticated) {
    return <Redirect href="/home" />;
  }

  return <Redirect href="/login" />;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F7FA",
    alignItems: "center",
    justifyContent: "center",
  },
});
