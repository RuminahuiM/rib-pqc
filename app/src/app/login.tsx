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

// Dummy-Token fuer Sprint-1 Fake-Login. ML-DSA-65-signed JWS-Compact-Format
// (header.payload.signature, alle base64url) damit jwt-decode + exp-Check
// funktionieren. Payload: sub=demo-user, exp=Jan 1 2100 (weit in der Zukunft,
// damit der Fake-Login niemals expired ist beim Auto-Login-Test). Signature
// ist DUMMY (nicht echt ML-DSA-signiert). Echter Token kommt durch Server-
// Call in PQC-59 (APP-6 secureClient).
const DUMMY_TOKEN_HEADER = "eyJhbGciOiJNTC1EU0EtNjUiLCJ0eXAiOiJKV1QiLCJraWQiOiJkdW1teSJ9";
const DUMMY_TOKEN_PAYLOAD =
  // {"iss":"pqc-auth-service","sub":"demo-user","iat":1748563200,"exp":4102444800,"auth_method":"local","external_sub":null}
  "eyJpc3MiOiJwcWMtYXV0aC1zZXJ2aWNlIiwic3ViIjoiZGVtby11c2VyIiwiaWF0IjoxNzQ4NTYzMjAwLCJleHAiOjQxMDI0NDQ4MDAsImF1dGhfbWV0aG9kIjoibG9jYWwiLCJleHRlcm5hbF9zdWIiOm51bGx9";
const DUMMY_TOKEN_SIGNATURE = "ZHVtbXktc2lnbmF0dXJlLW5vdC1yZWFsLU1MLURTQS02NQ";
const DUMMY_TOKEN = `${DUMMY_TOKEN_HEADER}.${DUMMY_TOKEN_PAYLOAD}.${DUMMY_TOKEN_SIGNATURE}`;

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
      // Sprint-1 Fake-Login: dummy-token. Echter Server-Call in PQC-59 APP-6.
      await login(DUMMY_TOKEN);
      router.replace("/home");
    } catch (err) {
      Alert.alert("Login fehlgeschlagen", String(err));
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
enter",
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
ize: 16,
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
