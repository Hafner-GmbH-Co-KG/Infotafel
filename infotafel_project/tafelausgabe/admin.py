from django.contrib import admin

from .models import Eintrag


@admin.register(Eintrag)
class EintragAdmin(admin.ModelAdmin):
    list_display = ("created", "user", "text")
    list_filter = ("user", "created")
