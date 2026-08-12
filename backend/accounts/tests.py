from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

User = get_user_model()


class AuthApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='secret123')

    def test_login_returns_token(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'alice', 'password': 'secret123'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'alice')
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_me_requires_auth(self):
        response = self.client.get('/api/auth/me/')
        self.assertIn(response.status_code, (401, 403))

        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        me = self.client.get('/api/auth/me/')
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data['username'], 'alice')
        self.assertFalse(me.data['has_rsa_public_key'])

    def test_register_rsa_public_key(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('utf-8')
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode('utf-8')

        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        rejected = self.client.post(
            '/api/auth/rsa-public-key/',
            {'rsa_public_key': private_pem},
            format='json',
        )
        self.assertEqual(rejected.status_code, 400)

        accepted = self.client.post(
            '/api/auth/rsa-public-key/',
            {'rsa_public_key': public_pem},
            format='json',
        )
        self.assertEqual(accepted.status_code, 200)
        self.assertTrue(accepted.data['has_rsa_public_key'])
        self.user.refresh_from_db()
        self.assertIn('BEGIN PUBLIC KEY', self.user.rsa_public_key)
