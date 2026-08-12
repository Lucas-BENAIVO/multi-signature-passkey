from django.contrib import admin

from .models import Signature


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = (
        'document',
        'signer',
        'is_valid',
        'matches_hash',
        'signed_at',
    )
    list_filter = ('is_valid', 'signed_at')
    search_fields = (
        'document__title',
        'signer__username',
        'document_sha256',
    )
    readonly_fields = ('signed_at',)
    autocomplete_fields = ('document', 'signer')

    @admin.display(boolean=True, description='Hash OK')
    def matches_hash(self, obj: Signature) -> bool:
        return obj.matches_current_document_hash
