from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import (
    LoginSerializer,
    RsaPublicKeySerializer,
    UserSerializer,
)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RsaPublicKeyView(APIView):
    """
    Enregistre la clé publique RSA du signataire.
    La clé privée reste exclusivement sur l'appareil mobile.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = RsaPublicKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.rsa_public_key = serializer.validated_data['rsa_public_key']
        request.user.save(update_fields=['rsa_public_key'])
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
