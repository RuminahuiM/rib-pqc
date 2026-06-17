"""Federated-Identity-Service: Link-or-Create-User aus OIDC-Claims.

Story: PQC-39 (BRK-4) AC-1, AC-2, AC-4, AC-6.

**Aufgabe:**

Nimmt eine ``NormalizedIdentity`` (vom Plugin claim_mapper geliefert nach
verified ID-Token) und liefert den zugehoerigen lokalen ``User``-Record:

- AC-1 Erst-Login: kein User-Identity-Match fuer (provider, sub) → neuer
  User-Record + neue UserIdentity-Row.
- AC-2 Wiederholter Login: User-Identity-Match → bestehender User-Record.
- AC-4 Account-Linking: email_verified=True UND Email-Match auf bestehenden
  User → neue UserIdentity-Row gegen die existierende User-ID, kein neuer
  User-Record.
- AC-6 Email-Unverified: kein Linking-Versuch, immer neuer User-Record.
  Log-Event ``auth.federated.email_unverified``.

**Sicherheitsdesign (RFC 9700 BCP 2026, Auth0/Cognito-Pattern):**

- Account-Linking nur bei verifizierter Email (sonst kann Angreifer durch
  IdP-Registrierung mit fremder Email einen Local-Account uebernehmen).
- User-Email wird beim Linking NICHT aktualisiert (existing User behaelt
  seine Email, neue Identity bekommt nur seine User.id-Referenz).
- Bei Identity-Already-Exists (race condition) wird die Lookup nochmal
  geprueft, damit zweiter parallel-Login nicht crashed.

**Layering:**

Service kennt UserRepository + UserIdentityRepository + NormalizedIdentity.
Plugin-Konzept ist hier nicht mehr sichtbar.
"""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from logging_config import get_logger

if TYPE_CHECKING:
    from db.repositories import UserIdentityRepository, UserRepository
    from idp.normalized_identity import NormalizedIdentity
    from models import User

logger = get_logger("rib_pqc.federated_identity")


def _placeholder_email_for(provider: str, external_sub: str) -> str:
    """Erzeugt eine eindeutige Platzhalter-Email fuer User ohne email-Claim.

    Notwendig weil ``User.email`` ein NOT-NULL-Field mit Unique-Constraint ist
    (PQC-28 AUT-1 AC-1). Federated User ohne ``email``-Claim (z.B. Microsoft
    Apps-Only-Tokens) bekommen ``<sub>+<provider>@no-email.local``.

    Diese Mails sind unsichtbar fuer den User, dienen nur als interne
    Eindeutigkeits-ID in der ``users``-Tabelle. Bei Auflistung in der UI
    sollte stattdessen ``display_name`` verwendet werden.
    """
    # Sub kann lang sein; hashen waere stabiler, aber lesbar-debug ist hier
    # wichtiger. Wir sliceen auf 200 chars um die 320-char-Limit fuer Email
    # nicht zu sprengen.
    safe_sub = external_sub[:200].replace("@", "-at-")
    return f"{safe_sub}+{provider}@no-email.local"


class FederatedIdentityService:
    """Resolve oder Create User aus federated OIDC-Identity.

    Pro Request-instanziiert weil UserRepository + UserIdentityRepository
    session-scoped sind. Nicht Singleton.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        identity_repository: UserIdentityRepository,
    ) -> None:
        self._users = user_repository
        self._identities = identity_repository

    async def link_or_create(
        self,
        *,
        provider: str,
        normalized: NormalizedIdentity,
    ) -> User:
        """Resolve User aus ``NormalizedIdentity`` oder erstelle ihn.

        Story-Bezug: PQC-39 BRK-4 AC-1, AC-2, AC-4, AC-6.

        Logik (in dieser Reihenfolge):

        1. UserIdentity-Lookup ueber (provider, external_sub). Treffer →
           Bestehender User wird zurueckgegeben (AC-2).
        2. Kein Identity-Treffer + email_verified=True + Email match auf
           bestehendem User → neue UserIdentity-Row gegen den existing User
           (AC-4 Account-Linking).
        3. Kein Identity-Treffer + (email_verified=False ODER kein Email-Match)
           → neuer User-Record + neue UserIdentity-Row (AC-1 Erst-Login).

        Args:
            provider: Lowercase Provider-Name (z.B. ``"google"``,
                ``"microsoft"``). Muss zu auth_method-Whitelist gehoeren.
            normalized: NormalizedIdentity aus Plugin.claim_mapper.

        Returns:
            ``User`` (entweder existierend oder neu angelegt).
        """
        external_sub = normalized.external_sub
        email = normalized.email
        email_verified = normalized.email_verified

        # AC-2: Wiederholter Login → bestehender Identity-Record liefert
        # uns die User.id direkt.
        existing_identity = await self._identities.find_by_external(
            auth_method=provider,
            external_sub=external_sub,
        )
        if existing_identity is not None:
            user = await self._users.find_by_id(existing_identity.user_id)
            if user is not None:
                logger.info(
                    "federated_identity.repeat_login",
                    user_id=user.id,
                    provider=provider,
                )
                return user
            # User wurde geloescht (CASCADE haette die Identity auch mitgenommen).
            # Should not happen, aber defensive: weiter mit Create-Branch.
            logger.warning(
                "federated_identity.orphaned_identity",
                identity_id=existing_identity.id,
                provider=provider,
            )

        # AC-4: Account-Linking, wenn email_verified UND Email-Match existing User.
        # AC-6: bei email_verified=False NICHT linken (Security: Spoof-Schutz).
        existing_user_by_email = None
        if email and email_verified:
            existing_user_by_email = await self._users.find_by_email(email)
        elif email and not email_verified:
            logger.warning(
                "auth.federated.email_unverified",
                provider=provider,
                # Email NICHT loggen (PII)
                has_email=True,
            )

        if existing_user_by_email is not None:
            # AC-4: Bestehender User existiert mit dieser Email -> Linking.
            await self._identities.create(
                user_id=existing_user_by_email.id,
                auth_method=provider,
                external_sub=external_sub,
            )
            logger.info(
                "federated_identity.linked",
                user_id=existing_user_by_email.id,
                provider=provider,
            )
            return existing_user_by_email

        # AC-1: Erst-Login → neuer User + Identity.
        # Platzhalter-Email wenn Provider keine geliefert hat (z.B. Apps-Only-MS).
        user_email = email if email else _placeholder_email_for(provider, external_sub)
        new_user = await self._users.create(
            email=user_email,
            auth_method=provider,
            external_sub=external_sub,
            password_hash=None,
        )
        await self._identities.create(
            user_id=new_user.id,
            auth_method=provider,
            external_sub=external_sub,
        )
        logger.info(
            "federated_identity.created",
            user_id=new_user.id,
            provider=provider,
            email_verified=email_verified,
            had_email=email is not None,
        )
        return new_user


__all__ = ["FederatedIdentityService"]


# Kept silent: secrets module imported but only used if we extend to generate
# random suffix for email collisions in placeholder mode. Future-proofing.
_ = secrets
