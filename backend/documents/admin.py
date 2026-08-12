from django.contrib import admin

from .models import Document, DocumentSigner


class DocumentSignerInline(admin.TabularInline):
    model = DocumentSigner
    extra = 1
    autocomplete_fields = ('user',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'status', 'owner', 'sha256_short', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'sha256', 'owner__username')
    readonly_fields = ('sha256', 'created_at', 'updated_at')
    autocomplete_fields = ('owner',)
    inlines = (DocumentSignerInline,)

    @admin.display(description='SHA-256')
    def sha256_short(self, obj: Document) -> str:
        if not obj.sha256:
            return '—'
        return f'{obj.sha256[:12]}…'


@admin.register(DocumentSigner)
class DocumentSignerAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'is_required', 'assigned_at')
    list_filter = ('is_required',)
    search_fields = ('document__title', 'user__username')
    autocomplete_fields = ('document', 'user')
