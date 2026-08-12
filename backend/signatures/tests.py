from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
import base64
import hashlib

from documents.models import Document, DocumentSigner
from signatures.services import register_signature, verify_rsa_signature


User = get_user_model()


class RsaVerificationTests(TestCase):
    def setUp(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_pem = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('utf-8')

        self.owner = User.objects.create_user(username='owner', password='x')
        self.signer = User.objects.create_user(
            username='signer',
            password='x',
            rsa_public_key=public_pem,
        )

        content = b'contrat-test'
        self.sha256 = hashlib.sha256(content).hexdigest()
        self.document = Document.objects.create(
            title='Contrat',
            file=SimpleUploadedFile('contrat.txt', content),
            owner=self.owner,
            sha256=self.sha256,
        )
        DocumentSigner.objects.create(document=self.document, user=self.signer)

    def _sign(self, sha256_hex: str) -> str:
        digest = bytes.fromhex(sha256_hex)
        signature = self.private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            Prehashed(hashes.SHA256()),
        )
        return base64.b64encode(signature).decode('ascii')

    def test_verify_valid_signature(self):
        sig_b64 = self._sign(self.sha256)
        self.assertTrue(
            verify_rsa_signature(
                public_key_pem=self.signer.rsa_public_key,
                sha256_hex=self.sha256,
                signature_b64=sig_b64,
            )
        )

    def test_register_signature_marks_document_fully_signed(self):
        sig_b64 = self._sign(self.sha256)
        signature = register_signature(
            document=self.document,
            signer=self.signer,
            signature_b64=sig_b64,
        )
        self.document.refresh_from_db()
        self.assertTrue(signature.is_valid)
        self.assertEqual(self.document.status, Document.Status.FULLY_SIGNED)
