from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Utilisateur applicatif.
    La clé privée RSA reste sur le mobile ; seule la clé publique est stockée ici.
    """

    rsa_public_key = models.TextField(
        blank=True,
        help_text='Clé publique RSA PEM (jamais la clé privée).',
    )

    class Meta:
        ordering = ['username']

    def __str__(self) -> str:
        return self.username

    @property
    def has_rsa_public_key(self) -> bool:
        return bool(self.rsa_public_key.strip())
