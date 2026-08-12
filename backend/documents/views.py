from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from documents.models import Document, DocumentSigner
from documents.serializers import (
    AssignSignersSerializer,
    DocumentCreateSerializer,
    DocumentSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API documents :
    - dépôt (owner)
    - consultation (owner ou signataire affecté)
    - affectation de signataires (owner)
    """

    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    http_method_names = ('get', 'post', 'head', 'options')

    def get_queryset(self):
        user = self.request.user
        return (
            Document.objects.filter(Q(owner=user) | Q(signers__user=user))
            .distinct()
            .select_related('owner')
            .prefetch_related('signers__user', 'signatures')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentCreateSerializer
        return DocumentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        output = DocumentSerializer(document, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        document = self.get_object()
        if document.owner_id != request.user.id:
            return Response(
                {'detail': 'Seul le propriétaire peut affecter des signataires.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssignSignersSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        users = serializer.context['resolved_users']
        is_required = serializer.validated_data['is_required']

        created = []
        for user in users:
            signer, was_created = DocumentSigner.objects.get_or_create(
                document=document,
                user=user,
                defaults={'is_required': is_required},
            )
            if was_created:
                created.append(user.username)

        output = DocumentSerializer(document, context={'request': request})
        return Response(
            {
                'assigned_now': created,
                'document': output.data,
            },
            status=status.HTTP_200_OK,
        )
