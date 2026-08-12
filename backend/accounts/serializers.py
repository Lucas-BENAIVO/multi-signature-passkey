from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    has_rsa_public_key = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'has_rsa_public_key',
            'rsa_public_key',
        )
        read_only_fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'has_rsa_public_key',
            'rsa_public_key',
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        user = authenticate(
            username=attrs['username'],
            password=attrs['password'],
        )
        if user is None:
            raise serializers.ValidationError('Identifiants invalides.')
        if not user.is_active:
            raise serializers.ValidationError('Compte désactivé.')
        attrs['user'] = user
        return attrs


class RsaPublicKeySerializer(serializers.Serializer):
    rsa_public_key = serializers.CharField(
        help_text='Clé publique RSA au format PEM. Jamais la clé privée.',
    )

    def validate_rsa_public_key(self, value: str) -> str:
        pem = value.strip()
        if 'PRIVATE KEY' in pem:
            raise serializers.ValidationError(
                'Une clé privée a été détectée. Envoyez uniquement la clé publique.',
            )
        try:
            key = serialization.load_pem_public_key(pem.encode('utf-8'))
        except ValueError as exc:
            raise serializers.ValidationError(
                'PEM de clé publique RSA invalide.',
            ) from exc

        if not isinstance(key, rsa.RSAPublicKey):
            raise serializers.ValidationError('La clé doit être une clé publique RSA.')

        if key.key_size < 2048:
            raise serializers.ValidationError('La clé RSA doit faire au moins 2048 bits.')

        # Normalize to a canonical PEM SubjectPublicKeyInfo
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('utf-8')
