from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

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
