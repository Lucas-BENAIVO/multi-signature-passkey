import hashlib

from django.conf import settings
from django.db import models


class Document(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente de signature'
        PARTIALLY_SIGNED = 'partially_signed', 'Partiellement signé'
        FULLY_SIGNED = 'fully_signed', 'Complètement signé'

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%Y/%m/')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_documents',
    )
    version = models.PositiveIntegerField(default=1)
    sha256 = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
        help_text='Empreinte SHA-256 du fichier (hex).',
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.title} (v{self.version})'

    def compute_sha256(self) -> str:
        digest = hashlib.sha256()
        self.file.open('rb')
        try:
            for chunk in self.file.chunks():
                digest.update(chunk)
        finally:
            self.file.close()
        return digest.hexdigest()

    def save(self, *args, **kwargs):
        if self.file and not self.sha256:
            self.sha256 = self.compute_sha256()
        super().save(*args, **kwargs)


class DocumentSigner(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='signers',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_assignments',
    )
    is_required = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['assigned_at']
        constraints = [
            models.UniqueConstraint(
                fields=['document', 'user'],
                name='unique_document_signer',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} → {self.document}'
