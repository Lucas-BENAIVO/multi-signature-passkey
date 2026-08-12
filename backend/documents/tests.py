from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
import base64

from documents.models import Document, DocumentSigner

User = get_user_model()


class DocumentApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.signer = User.objects.create_user(username='signer', password='pass')
        self.stranger = User.objects.create_user(username='stranger', password='pass')
        self.owner_token = Token.objects.create(user=self.owner)
        self.signer_token = Token.objects.create(user=self.signer)
        self.stranger_token = Token.objects.create(user=self.stranger)

    def test_owner_can_upload_document(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token.key}')
        response = self.client.post(
            '/api/documents/',
            {
                'title': 'Contrat',
                'file': SimpleUploadedFile('contrat.txt', b'hello-doc'),
            },
            format='multipart',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Contrat')
        self.assertEqual(len(response.data['sha256']), 64)
        self.assertEqual(response.data['status'], Document.Status.PENDING)

    def test_assign_signers_and_visibility(self):
        document = Document.objects.create(
            title='Doc',
            file=SimpleUploadedFile('a.txt', b'data'),
            owner=self.owner,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token.key}')
        assign = self.client.post(
            f'/api/documents/{document.id}/assign/',
            {'usernames': ['signer']},
            format='json',
        )
        self.assertEqual(assign.status_code, 200)
        self.assertTrue(
            DocumentSigner.objects.filter(document=document, user=self.signer).exists()
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.signer_token.key}')
        visible = self.client.get('/api/documents/')
        self.assertEqual(visible.status_code, 200)
        self.assertEqual(len(visible.data), 1)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.stranger_token.key}')
        hidden = self.client.get('/api/documents/')
        self.assertEqual(hidden.status_code, 200)
        self.assertEqual(len(hidden.data), 0)


class DocumentSignApiTests(APITestCase):
    def setUp(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_pem = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('utf-8')

        self.owner = User.objects.create_user(username='owner', password='pass')
        self.signer = User.objects.create_user(
            username='signer',
            password='pass',
            rsa_public_key=public_pem,
        )
        self.signer_token = Token.objects.create(user=self.signer)
        self.owner_token = Token.objects.create(user=self.owner)

        self.document = Document.objects.create(
            title='Contrat',
            file=SimpleUploadedFile('contrat.txt', b'contrat-data'),
            owner=self.owner,
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

    def test_signer_can_submit_valid_signature(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.signer_token.key}')
        response = self.client.post(
            f'/api/documents/{self.document.id}/sign/',
            {
                'signature_value': self._sign(self.document.sha256),
                'document_sha256': self.document.sha256,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['signature']['is_valid'])
        self.assertEqual(
            response.data['document']['status'],
            Document.Status.FULLY_SIGNED,
        )

    def test_owner_cannot_sign_if_not_assigned(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token.key}')
        response = self.client.post(
            f'/api/documents/{self.document.id}/sign/',
            {'signature_value': self._sign(self.document.sha256)},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
