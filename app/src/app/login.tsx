/**
 * Login-Screen (PQC-20 SKL-2 + PQC-54 APP-1 Form, PQC-60 APP-7 Google-Login).
 *
 * Form mit Email/Passwort-Inputs + Validation. Submit ruft
 * AuthContext.login() mit Dummy-Token auf (Sprint-1 Fake-Login, echter
 * Server-Call kommt in PQC-59 APP-6 secureClient).
 *
 * Google-Button (PQC-60 APP-7) und Microsoft-Button (PQC-61 APP-8) rufen
 * `loginWithProvider(provider)` und persistieren den Broker-Token im
 * AuthContext. Live-Demo-Limitation siehe F-086 (redirect_uri Server-Side,
 * App-Side-Return blocked bis OAuth-App-Type-Switch zu iOS/Custom-Scheme
 * in Sprint 3, gilt fuer beide Provider).
 *
 * Microsoft-Tenant-Konfiguration (PQC-61 AC-2): Single-Tenant via
 * RIB_IDP_PROVIDERS__MICROSOFT__TENANT_ID auf der Server-Seite (siehe
 * PQC-84 Evidence). App-Code ist tenant-agnostic - die Tenant-ID wird
 * vom Server in die Authorize-URL eingebaut.
 */

import { router } from "expo-router";
import { useState } from "react";
import {
  Alert,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { useAuth } from "@/contexts/AuthContext";
import { loginWithProvider, OAuthError } from "@/lib/oauthClient";

// BASE_URL analog zu useSecureClient.ts: EXPO_PUBLIC_API_URL, Fallback
// localhost (Simulator). Fuer LAN-Demo: app/.env setzt die Notebook-IP.
const BASE_URL =
  (process.env.EXPO_PUBLIC_API_URL ?? "").trim() || "http://localhost:8000";

/**
 * Echter Local-Login gegen POST /auth/local/login (AUT-3, PQC-31).
 *
 * Ersetzt den Sprint-1-Fake-Login mit Dummy-Token: dessen nicht-echte
 * ML-DSA-Signatur waere beim nachfolgenden /session/init mit 401
 * abgewiesen worden (entdeckt bei D-009-Vorbereitung, 07.07.2026).
 * Response-Contract: `{broker_token, expires_in}` (routers/auth.py).
 */
async function localLogin(email: string, password: string): Promise<string> {
  const resp = await fetch(`${BASE_URL}/auth/local/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!resp.ok) {
    if (resp.status === 401) {
      throw new Error("Email oder Passwort falsch.");
    }
    throw new Error(`Login fehlgeschlagen (HTTP ${resp.status}).`);
  }
  const body = (await resp.json()) as { broker_token?: string };
  if (!body.broker_token) {
    throw new Error("Server-Antwort ohne broker_token.");
  }
  return body.broker_token;
}

// RFC 5322 simplified: gut genug fuer Sprint-1 Form-Validation. Echter
// Server validiert ohnehin nochmal mit Pydantic EmailStr.
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PASSWORD_MIN_LENGTH = 8;

export default function LoginScreen() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  function validate(): boolean {
    let valid = true;

    if (!EMAIL_REGEX.test(email)) {
      setEmailError("Bitte eine gueltige Email-Adresse eingeben.");
      valid = false;
    } else {
      setEmailError(null);
    }

    if (password.length < PASSWORD_MIN_LENGTH) {
      setPasswordError(
        `Passwort muss mindestens ${PASSWORD_MIN_LENGTH} Zeichen lang sein.`,
      );
      valid = false;
    } else {
      setPasswordError(null);
    }

    return valid;
  }

  async function handleEmailPasswordSubmit() {
    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const brokerToken = await localLogin(email.trim().toLowerCase(), password);
      await login(brokerToken);
      router.replace("/home");
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      Alert.alert("Login fehlgeschlagen", message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleOAuthLogin(
    provider: "google" | "microsoft",
    label: string,
  ) {
    setIsSubmitting(true);
    try {
      const result = await loginWithProvider(provider);
      // AC-5: Broker-Token in AuthContext, Navigation zu /home.
      await login(result.broker_token);
      router.replace("/home");
    } catch (err) {
      const message =
        err instanceof OAuthError
          ? `${err.message}${err.reason ? ` (${err.reason})` : ""}`
          : String(err);
      Alert.alert(`${label} Login fehlgeschlagen`, message);
    } finally {
      setIsSubmitting(false);
    }
  }

  const handleGoogleLogin = () => handleOAuthLogin("google", "Google");
  const handleMicrosoftLogin = () => handleOAuthLogin("microsoft", "Microsoft");

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>rib-pqc</Text>
        <Text style={styles.subtitle}>Sign in to continue</Text>
      </View>

      <View style={styles.form}>
        <View style={styles.field}>
          <Text style={styles.label}>Email</Text>
          <TextInput
            style={[styles.input, emailError != null && styles.inputError]}
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            autoComplete="email"
            keyboardType="email-address"
            placeholder="alice@example.com"
            placeholderTextColor="#94A3B8"
            editable={!isSubmitting}
          />
          {emailError != null && (
            <Text style={styles.errorText}>{emailError}</Text>
          )}
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Passwort</Text>
          <TextInput
            style={[styles.input, passwordError != null && styles.inputError]}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            autoComplete="current-password"
            placeholder="mindestens 8 Zeichen"
            placeholderTextColor="#94A3B8"
            editable={!isSubmitting}
          />
          {passwordError != null && (
            <Text style={styles.errorText}>{passwordError}</Text>
          )}
        </View>

        <Pressable
          style={[
            styles.button,
            styles.buttonPrimary,
            isSubmitting && styles.buttonDisabled,
          ]}
          onPress={handleEmailPasswordSubmit}
          disabled={isSubmitting}
        >
          <Text style={styles.buttonTextPrimary}>
            {isSubmitting ? "Bitte warten…" : "Anmelden"}
          </Text>
        </Pressable>

        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>oder</Text>
          <View style={styles.dividerLine} />
        </View>

        <Pressable
          style={styles.button}
          onPress={handleGoogleLogin}
          disabled={isSubmitting}
        >
          <Text style={styles.buttonText}>Continue with Google</Text>
        </Pressable>

        <Pressable
          style={styles.button}
          onPress={handleMicrosoftLogin}
          disabled={isSubmitting}
        >
          <Text style={styles.buttonText}>Continue with Microsoft</Text>
        </Pressable>
      </View>

      <Text style={styles.note}>
        Sprint-1 Fake-Login mit Dummy-Token. Echter lokaler Server-Call
        kommt in PQC-59 (APP-6 secureClient). Google/Microsoft via OIDC
        bereits durch PQC-60/61 implementiert; Live-Browser-Demo wartet
        auf OAuth-App-Type-Switch (siehe F-086).
      </Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F7FA",
    paddingHorizontal: 24,
    paddingVertical: 32,
  },
  header: {
    alignItems: "center",
    marginTop: 24,
    marginBottom: 24,
  },
  title: {
    fontSize: 36,
    fontWeight: "700",
    color: "#208AEF",
  },
  subtitle: {
    fontSize: 16,
    color: "#64748B",
    marginTop: 8,
  },
  form: {
    gap: 12,
  },
  field: {
    gap: 6,
  },
  label: {
    fontSize: 12,
    color: "#475569",
    fontWeight: "600",
    textTransform: "uppercase",
  },
  input: {
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: "#FFFFFF",
    color: "#1E293B",
  },
  inputError: {
    borderColor: "#DC2626",
  },
  errorText: {
    fontSize: 12,
    color: "#DC2626",
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
    marginTop: 6,
  },
  buttonDisabled: {
    opacity: 0.6,
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
  divider: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginVertical: 4,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: "#CBD5E1",
  },
  dividerText: {
    fontSize: 12,
    color: "#94A3B8",
  },
  note: {
    fontSize: 12,
    color: "#94A3B8",
    textAlign: "center",
    marginTop: "auto",
  },
});
