from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class ContentItemType(models.TextChoices):
    SONG = "song", "Lied"
    BIBLE = "bible", "Bibel"


class ContentItem(models.Model):
    """Zentrale Einheit fuer Inhalte, die auf allen Monitoren ausgespielt werden."""

    item_type = models.CharField(max_length=20, choices=ContentItemType.choices)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    language = models.CharField(max_length=10, blank=True, help_text="z. B. de, en")
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_content_items",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_content_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ("title",)
        verbose_name = "Inhalt"
        verbose_name_plural = "Inhalte"

    def save(self, *args, **kwargs) -> None:  # pragma: no cover - helper
        if not self.slug:
            base_slug = slugify(self.title) or "content"
            candidate = base_slug
            suffix = 2
            while ContentItem.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - admin display
        return self.title


class ContentSlide(models.Model):
    """Einzelne Folie innerhalb eines Inhalts."""

    item = models.ForeignKey(ContentItem, related_name="slides", on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    label = models.CharField(max_length=50, blank=True)
    text = models.TextField(blank=True)
    chords = models.TextField(blank=True, help_text="Akkorde fuer Musiker")
    notes = models.TextField(blank=True, help_text="Interne Hinweise")
    display_options = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("position", "id")
        unique_together = ("item", "position")
        verbose_name = "Folie"
        verbose_name_plural = "Folien"

    def __str__(self) -> str:  # pragma: no cover - admin display
        label = self.label or f"Slide {self.position}"
        return f"{self.item.title} - {label}"


class BibleReference(models.Model):
    """Verknuepft einen Inhalt des Typs Bibel mit einer konkreten Bibelstelle."""

    item = models.OneToOneField(
        ContentItem,
        related_name="bible_reference",
        on_delete=models.CASCADE,
    )
    book = models.CharField(max_length=60)
    chapter = models.PositiveIntegerField()
    verse_start = models.PositiveIntegerField()
    verse_end = models.PositiveIntegerField()
    translation = models.CharField(max_length=30, default="LUT")
    text = models.TextField(help_text="Text der Bibelstelle in der gewaehlten Uebersetzung")

    class Meta:
        verbose_name = "Bibelstelle"
        verbose_name_plural = "Bibelstellen"

    def __str__(self) -> str:  # pragma: no cover - admin display
        reference = f"{self.book} {self.chapter}:{self.verse_start}"
        if self.verse_end != self.verse_start:
            reference = f"{reference}-{self.verse_end}"
        return f"{reference} ({self.translation})"


class Setlist(models.Model):
    """Repraesentiert einen Ablaufplan oder Gottesdienst."""

    name = models.CharField(max_length=200)
    event_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_setlists",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_template = models.BooleanField(default=False)

    class Meta:
        ordering = ("-event_date", "-created_at")
        verbose_name = "Setliste"
        verbose_name_plural = "Setlisten"

    def __str__(self) -> str:  # pragma: no cover - admin display
        if self.event_date:
            return f"{self.name} ({self.event_date:%d.%m.%Y})"
        return self.name


class SetlistItem(models.Model):
    """Verknuepft Inhalte mit einer Setliste und definiert die Reihenfolge."""

    setlist = models.ForeignKey(Setlist, related_name="items", on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    content_item = models.ForeignKey(
        ContentItem,
        related_name="setlist_items",
        on_delete=models.CASCADE,
    )
    notes = models.CharField(max_length=255, blank=True)
    is_optional = models.BooleanField(default=False)

    class Meta:
        ordering = ("position", "id")
        unique_together = ("setlist", "position")
        verbose_name = "Setlisteneintrag"
        verbose_name_plural = "Setlisteneintraege"

    def __str__(self) -> str:  # pragma: no cover - admin display
        return f"{self.setlist.name}: {self.content_item.title}"


class MonitorRole(models.TextChoices):
    FRONT = "front", "Publikum"
    STAGE = "stage", "Buehne"
    STREAM = "stream", "Livestream"
    CONTROL = "control", "Regie"


def default_layer_config() -> dict[str, Any]:
    return {
        "lyrics": True,
        "voices": True,
        "bible_reference": True,
        "notes": False,
        "next_slide": False,
    }


class Monitor(models.Model):
    """Virtueller Monitor mit eigener Layer-Konfiguration."""

    identifier = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=MonitorRole.choices, default=MonitorRole.FRONT)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "name")
        verbose_name = "Monitor"
        verbose_name_plural = "Monitore"

    def __str__(self) -> str:  # pragma: no cover - admin display
        return self.name


class MonitorLayerConfig(models.Model):
    """Standard-Layer pro Monitor."""

    monitor = models.OneToOneField(Monitor, related_name="layer_config", on_delete=models.CASCADE)
    layers = models.JSONField(default=default_layer_config)

    class Meta:
        verbose_name = "Monitor-Layer"
        verbose_name_plural = "Monitor-Layer"

    def __str__(self) -> str:  # pragma: no cover - admin display
        return f"Layer fuer {self.monitor.name}"


class MonitorContentOverride(models.Model):
    """Ueberschreibt Layer fuer einen spezifischen Inhalt und Monitor."""

    monitor = models.ForeignKey(Monitor, related_name="content_overrides", on_delete=models.CASCADE)
    content_item = models.ForeignKey(
        ContentItem,
        related_name="monitor_overrides",
        on_delete=models.CASCADE,
    )
    layers = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("monitor", "content_item")
        verbose_name = "Monitor-Override"
        verbose_name_plural = "Monitor-Overrides"

    def __str__(self) -> str:  # pragma: no cover - admin display
        return f"Override {self.monitor.name} / {self.content_item.title}"


class DisplayState(models.Model):
    """Aktueller globaler Live-Zustand."""

    singleton_key = models.CharField(max_length=20, unique=True, default="live", editable=False)
    current_item = models.ForeignKey(
        ContentItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="display_states",
    )
    current_slide = models.ForeignKey(
        ContentSlide,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="display_states",
    )
    visibility_overrides = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Anzeigestatus"
        verbose_name_plural = "Anzeigestatus"

    def __str__(self) -> str:  # pragma: no cover - admin display
        if self.current_item:
            return f"Live: {self.current_item.title}"
        return "Live: (kein Inhalt)"


class Eintrag(models.Model):
    """Bestehender Legacy-Eintrag fuer die aktuelle Anzeige."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eintraege"
    )
    text = models.TextField(blank=True)
    sopran = models.BooleanField(default=False)
    alt = models.BooleanField(default=False)
    tenor = models.BooleanField(default=False)
    bass = models.BooleanField(default=False)
    monitor = models.ForeignKey(
        Monitor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="legacy_entries",
    )
    expire = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Legacy-Eintrag"
        verbose_name_plural = "Legacy-Eintraege"

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.created:%Y-%m-%d %H:%M} - {self.text[:20]}"
