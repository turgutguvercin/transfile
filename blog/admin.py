from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Blog

@admin.register(Blog)
class BlogAdmin(TranslatableAdmin):
    list_display = ("get_any_title", "date", "get_languages")
    search_fields = ("translations__title",)
    list_filter = ("date",)
    ordering = ("-date",)

    
    def get_queryset(self, request):
        return super().get_queryset(request).language(None)

    def get_any_title(self, obj):
        title = obj.safe_translation_getter("title", any_language=True)
        return title or "— (no translation) —"

    get_any_title.short_description = _("Title")

    def get_languages(self, obj):
        langs = obj.get_available_languages()
        return ", ".join(langs) if langs else "—"
        
    get_languages.short_description = _("Languages")
    