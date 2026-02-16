from django.contrib import admin

from .models import (
    BibleReference,
    ContentItem,
    ContentSlide,
    DisplayState,
    Eintrag,
    Monitor,
    MonitorContentOverride,
    MonitorLayerConfig,
    Setlist,
    SetlistItem,
)


class ContentSlideInline(admin.TabularInline):
    model = ContentSlide
    extra = 1
    ordering = ("position",)


class BibleReferenceInline(admin.StackedInline):
    model = BibleReference
    extra = 0
    max_num = 1


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ("title", "item_type", "language", "updated_at", "is_archived")
    list_filter = ("item_type", "language", "is_archived")
    search_fields = ("title", "subtitle", "metadata")
    inlines = [ContentSlideInline, BibleReferenceInline]


class SetlistItemInline(admin.TabularInline):
    model = SetlistItem
    extra = 1
    ordering = ("position",)


@admin.register(Setlist)
class SetlistAdmin(admin.ModelAdmin):
    list_display = ("name", "event_date", "is_template", "updated_at")
    list_filter = ("event_date", "is_template")
    search_fields = ("name", "description")
    inlines = [SetlistItemInline]


class MonitorLayerConfigInline(admin.StackedInline):
    model = MonitorLayerConfig
    extra = 0
    max_num = 1


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ("name", "identifier", "role", "order", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("name", "identifier")
    inlines = [MonitorLayerConfigInline]


@admin.register(MonitorContentOverride)
class MonitorContentOverrideAdmin(admin.ModelAdmin):
    list_display = ("monitor", "content_item", "updated_at")
    list_filter = ("monitor", "content_item")
    search_fields = ("monitor__name", "content_item__title")


@admin.register(DisplayState)
class DisplayStateAdmin(admin.ModelAdmin):
    list_display = ("singleton_key", "current_item", "current_slide", "updated_at")
    readonly_fields = ("singleton_key", "updated_at")


@admin.register(Eintrag)
class EintragAdmin(admin.ModelAdmin):
    list_display = ("created", "user", "text")
    list_filter = ("user", "created")
    search_fields = ("text",)
