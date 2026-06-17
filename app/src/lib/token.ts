/**
 * Token-Helper: JWS-Compact-Token-Decoding und Expiry-Check.
 *
 * Story-Bezug: PQC-57 APP-4 AC-4 (Auto-Login bei App-Start nur wenn Token
 * noch gueltig). Best-practice statt naivem "Token vorhanden = authenticated":
 * client-side exp-Claim-Pruefung vermeidet einen Flicker /home -> /login
 * wenn der Token abgelaufen ist.
 *
 * Sicherheits-Hinweis: client-side exp-Pruefung ist NICHT sicherheits-
 * relevant. Der Server (PQC-33 TOK-2 TokenService.verify) entscheidet
 * autoritativ. Diese Pruefung ist reines UX-Polish.
 */

import { jwtDecode } from "jwt-decode";

interface BrokerTokenPayload {
  iss: string;
  sub: string;
  iat: number;
  exp: number;
  auth_method: string;
  external_sub?: string | null;
}

/**
 * Dekodiert den Token-Payload (zweiter Base64URL-Segment des JWS-Compact).
 *
 * Wirft KEINE Exception bei ungueltigem Token sondern returned null.
 * AuthContext interpretiert null wie "Token-Format kaputt, User muss
 * sich neu einloggen".
 */
export function decodePayload(token: string): BrokerTokenPayload | null {
  try {
    return jwtDecode<BrokerTokenPayload>(token);
  } catch {
    return null;
  }
}

/**
 * Prueft ob der Token abgelaufen ist (exp-Claim < jetzt).
 *
 * Returns:
 *   - true wenn abgelaufen oder Token ungueltig (defensiv: bei Zweifel
 *     User neu einloggen lassen)
 *   - false wenn Token noch gueltig
 *
 * Hinweis: kein Leeway hier (im Gegensatz zu Server-Side wo wir 30s Leeway
 * haben). Client-side ist konservativer, damit User nicht in einen Token-
 * Edge-Case rennt wo Client glaubt valid, Server aber expired sieht.
 */
export function isExpired(token: string): boolean {
  const payload = decodePayload(token);
  if (payload == null) {
    return true;
  }
  const nowSeconds = Math.floor(Date.now() / 1000);
  return payload.exp < nowSeconds;
}
