"""
Vérification cryptographique des signatures RSA.

Aligné avec le sujet :
- signature sur l'empreinte SHA-256 (pas le fichier entier)
- vérification avec la clé publique stockée côté Django
- la clé privée ne quitte jamais le mobile

Schéma (mobile et serveur doivent être identiques) :
- message = digest SHA-256 brut (32 octets)
- padding = PSS (MGF1-SHA256)
- hash algorithm = Prehashed(SHA256)
- signature_value = Base64
"""

from __future__ import annotations

import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from django.core.exceptions import ValidationError
from django.db import transaction

from documents.models import Document, DocumentSigner
from signatures.models import Signature


def verify_rsa_signature(
    *,
    public_key_pem: str,
    sha256_hex: str,
    signature_b64: str,
) -> bool:
    """Vérifie une signature RSA sur une empreinte SHA-256 (hex)."""
    if not public_key_pem or not public_key_pem.strip():
        return False
    if len(sha256_hex) != 64:
        return False

    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
        )
        digest = bytes.fromhex(sha256_hex)
        signature = base64.b64decode(signature_b64, validate=True)
        public_key.verify(
            signature,
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            Prehashed(hashes.SHA256()),
        )
    except (ValueError, TypeError, InvalidSignature):
        return False

    return True


def refresh_document_status(document: Document) -> Document:
    """
    Met à jour le statut global du document (sujet §2.5).
    Complètement signé seulement si toutes les signatures obligatoires
    sont présentes, valides, et portent sur l'empreinte actuelle.
    """
    required_signer_ids = set(
        document.signers.filter(is_required=True).values_list('user_id', flat=True),
    )

    if not required_signer_ids:
        document.status = Document.Status.PENDING
        document.save(update_fields=['status', 'updated_at'])
        return document

    valid_signatures = document.signatures.filter(
        is_valid=True,
        document_sha256=document.sha256,
        signer_id__in=required_signer_ids,
    )
    valid_signer_ids = set(valid_signatures.values_list('signer_id', flat=True))

    if required_signer_ids <= valid_signer_ids:
        new_status = Document.Status.FULLY_SIGNED
    elif valid_signer_ids:
        new_status = Document.Status.PARTIALLY_SIGNED
    else:
        new_status = Document.Status.PENDING

    if document.status != new_status:
        document.status = new_status
        document.save(update_fields=['status', 'updated_at'])

    return document


@transaction.atomic
def register_signature(
    *,
    document: Document,
    signer,
    signature_b64: str,
    document_sha256: str | None = None,
) -> Signature:
    """
    Enregistre et vérifie une signature pour un document.
    """
    sha256 = document_sha256 or document.sha256

    if not DocumentSigner.objects.filter(document=document, user=signer).exists():
        raise ValidationError('Ce utilisateur n’est pas signataire de ce document.')

    if not sha256 or sha256 != document.sha256:
        raise ValidationError(
            'L’empreinte signée ne correspond pas à la version actuelle du document.',
        )

    if not signer.has_rsa_public_key:
        raise ValidationError('Aucune clé publique RSA enregistrée pour ce signataire.')

    is_valid = verify_rsa_signature(
        public_key_pem=signer.rsa_public_key,
        sha256_hex=sha256,
        signature_b64=signature_b64,
    )

    signature, _created = Signature.objects.update_or_create(
        document=document,
        signer=signer,
        defaults={
            'document_sha256': sha256,
            'signature_value': signature_b64,
            'is_valid': is_valid,
        },
    )

    refresh_document_status(document)
    return signature
