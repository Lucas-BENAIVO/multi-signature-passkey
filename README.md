# multi-signature-passkey

Application de signature électronique multiple avec Passkey.

## Architecture

| Dossier | Rôle |
|---------|------|
| `backend/` | Application web Django (gestion, documents, vérification) |
| `mobile/` | Application Flutter (authentification Passkey, signature RSA) |
| `docs/` | Documentation technique |

## Principe

- Django : utilisateurs, dépôt de documents, affectation des signataires, vérification et stockage des signatures
- Mobile : Passkey, consultation, signature avec clé privée RSA (jamais envoyée au serveur)
- Signature sur l'empreinte SHA-256 du document (pas sur le fichier entier)

## Stack

- Backend : Django + API
- Mobile : Flutter
- Crypto : RSA, SHA-256, Passkey (WebAuthn)
