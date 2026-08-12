from django.conf import settings
from django.db import models

from documents.models import Document


class Signature(models.Model):
    """
    Signature électronique d'un document.
    Porte sur l'empreinte SHA-256 (pas sur le fichier entier).
    La clé privée ne quitte jamais le mobile ; le serveur vérifie avec la clé publique.
    """

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='signatures',
    )
    signer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='signatures',
    )
    document_sha256 = models.CharField(
        max_length=64,
        help_text='Empreinte SHA-256 qui a été signée (doit correspondre au document).',
    )
    signature_value = models.TextField(
        help_text='Signature RSA de l’empreinte, encodée en Base64.',
    )
    is_valid = models.BooleanField(
        default=False,
        help_text='Résultat de la vérification serveur avec la clé publique.',
    )
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-signed_at']
        constraints = [
            models.UniqueConstraint(
                fields=['document', 'signer'],
                name='unique_signature_per_document_signer',
            ),
        ]

    def __str__(self) -> str:
        state = 'valide' if self.is_valid else 'invalide'
        return f'{self.signer} → {self.document} ({state})'

    @property
    def matches_current_document_hash(self) -> bool:
        return self.document_sha256 == self.document.sha256
