from django.contrib.auth import get_user_model
from rest_framework import serializers

from documents.models import Document, DocumentSigner

User = get_user_model()


class DocumentSignerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = DocumentSigner
        fields = ('id', 'user_id', 'username', 'is_required', 'assigned_at')
        read_only_fields = fields


class DocumentSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    signers = DocumentSignerSerializer(many=True, read_only=True)
    signatures_count = serializers.SerializerMethodField()
    valid_signatures_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id',
            'title',
            'file',
            'owner',
            'owner_username',
            'version',
            'sha256',
            'status',
            'signers',
            'signatures_count',
            'valid_signatures_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'owner',
            'owner_username',
            'version',
            'sha256',
            'status',
            'signers',
            'signatures_count',
            'valid_signatures_count',
            'created_at',
            'updated_at',
        )

    def get_signatures_count(self, obj: Document) -> int:
        return obj.signatures.count()

    def get_valid_signatures_count(self, obj: Document) -> int:
        return obj.signatures.filter(is_valid=True, document_sha256=obj.sha256).count()

    def create(self, validated_data):
        request = self.context['request']
        return Document.objects.create(owner=request.user, **validated_data)


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('title', 'file')

    def create(self, validated_data):
        request = self.context['request']
        return Document.objects.create(owner=request.user, **validated_data)


class AssignSignersSerializer(serializers.Serializer):
    usernames = serializers.ListField(
        child=serializers.CharField(max_length=150),
        allow_empty=False,
        help_text='Liste des noms d’utilisateurs à affecter comme signataires.',
    )
    is_required = serializers.BooleanField(default=True)

    def validate_usernames(self, usernames):
        normalized = [name.strip() for name in usernames if name.strip()]
        if not normalized:
            raise serializers.ValidationError('Au moins un nom d’utilisateur est requis.')

        users = list(User.objects.filter(username__in=normalized))
        found = {user.username for user in users}
        missing = sorted(set(normalized) - found)
        if missing:
            raise serializers.ValidationError(
                f'Utilisateurs introuvables : {", ".join(missing)}',
            )
        self.context['resolved_users'] = users
        return normalized
