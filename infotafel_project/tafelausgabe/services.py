from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from django.db.models import Q
from django.utils import timezone

from .models import (
    ContentItemType,
    DisplayState,
    Eintrag,
    Monitor,
    MonitorContentOverride,
    MonitorRole,
    default_layer_config,
)


@dataclass
class DisplayContext:
    monitor: dict[str, Any]
    layers: dict[str, bool]
    content: dict[str, Any]
    generated_at: Any


VOICE_KEYS = ("sopran", "alt", "tenor", "bass")


def _resolve_monitor(identifier: str | None) -> Monitor | None:
    base_qs = Monitor.objects.filter(is_active=True)
    if identifier:
        monitor = base_qs.filter(identifier=identifier).first()
        if monitor:
            return monitor
    return base_qs.order_by("order", "id").first() or Monitor(
        identifier="default",
        name="Hauptanzeige",
        role=MonitorRole.FRONT,
        is_active=True,
    )


def _base_layers_for_monitor(monitor: Monitor | None) -> dict[str, bool]:
    layers = default_layer_config().copy()
    if monitor and getattr(monitor, "layer_config", None):
        config_layers = monitor.layer_config.layers or {}
        layers.update({key: bool(value) for key, value in config_layers.items()})
    return layers


def _apply_specific_overrides(
    layers: dict[str, bool],
    monitor: Monitor | None,
    display_state: DisplayState | None,
    content_item_id: int | None,
) -> None:
    """Mutiert das Layer-Dict entsprechend Monitor- und Laufzeit-Overrides."""

    if monitor and monitor.pk and content_item_id:
        override = (
            MonitorContentOverride.objects.filter(monitor=monitor, content_item_id=content_item_id)
            .order_by("-updated_at")
            .first()
        )
        if override and override.layers:
            layers.update({key: bool(value) for key, value in (override.layers or {}).items()})

    if display_state and display_state.visibility_overrides:
        state_overrides = display_state.visibility_overrides.get(
            (monitor.identifier if monitor else "default"), {}
        )
        if isinstance(state_overrides, dict):
            layers.update({key: bool(value) for key, value in state_overrides.items()})


def _voices_from_payload(payload: dict[str, Any] | None) -> dict[str, bool]:
    voices = {key: False for key in VOICE_KEYS}
    if not isinstance(payload, dict):
        return voices
    for key in VOICE_KEYS:
        voices[key] = bool(payload.get(key))
    return voices


def _build_content_from_state(
    display_state: DisplayState | None,
    monitor: Monitor | None,
) -> dict[str, Any]:
    if not display_state or not display_state.current_item:
        return {}

    item = display_state.current_item
    slide = display_state.current_slide
    if slide and slide.item_id != item.id:
        slide = None
    if slide is None:
        slide = item.slides.order_by("position", "id").first()

    voices_payload: dict[str, Any] = {}
    if slide and isinstance(slide.display_options, dict):
        voices_payload = slide.display_options.get("voices", {})
    if not voices_payload and isinstance(item.metadata, dict):
        voices_payload = item.metadata.get("voices", {})

    voices = _voices_from_payload(voices_payload)
    text = (slide.text if slide else "") or ""
    text = text.strip()

    bible_reference_payload = None
    if item.item_type == ContentItemType.BIBLE and hasattr(item, "bible_reference"):
        reference = item.bible_reference
        bible_reference_payload = {
            "book": reference.book,
            "chapter": reference.chapter,
            "verse_start": reference.verse_start,
            "verse_end": reference.verse_end,
            "translation": reference.translation,
            "reference": _format_bible_reference(
                reference.book,
                reference.chapter,
                reference.verse_start,
                reference.verse_end,
            ),
            "text": reference.text,
        }
        if not text:
            text = reference.text.strip()

    notes = ""
    if slide and slide.notes:
        notes = slide.notes.strip()
    elif isinstance(item.metadata, dict):
        notes = str(item.metadata.get("notes", "")).strip()

    chords = ""
    if slide and slide.chords:
        chords = slide.chords.strip()

    return {
        "id": item.id,
        "type": item.item_type,
        "title": item.title,
        "subtitle": item.subtitle,
        "text": text,
        "voices": voices,
        "notes": notes,
        "chords": chords,
        "bible_reference": bible_reference_payload,
        "updated_at": display_state.updated_at,
        "slide": {
            "id": slide.id if slide else None,
            "position": slide.position if slide else None,
            "label": slide.label if slide else None,
        },
    }


def _build_content_from_legacy(monitor: Monitor | None) -> dict[str, Any]:
    now = timezone.now()
    queryset = Eintrag.objects.filter(Q(expire__isnull=True) | Q(expire__gt=now)).order_by(
        "-created"
    )
    entry = None
    if monitor and getattr(monitor, "pk", None):
        entry = queryset.filter(monitor=monitor).first()
    if not entry:
        entry = queryset.filter(monitor__isnull=True).first()
    if not entry:
        entry = queryset.first()
    if not entry:
        return {}
    return {
        "id": entry.id,
        "type": "legacy",
        "title": "Legacy",
        "subtitle": "",
        "text": entry.text.strip(),
        "voices": {
            "sopran": entry.sopran,
            "alt": entry.alt,
            "tenor": entry.tenor,
            "bass": entry.bass,
        },
        "notes": "",
        "chords": "",
        "bible_reference": None,
        "updated_at": entry.created,
        "expires_at": entry.expire,
    }


def _format_bible_reference(book: str, chapter: int, verse_start: int, verse_end: int) -> str:
    if verse_start == verse_end:
        return f"{book} {chapter}:{verse_start}"
    return f"{book} {chapter}:{verse_start}-{verse_end}"


def resolve_display_for_monitor(identifier: str | None = None) -> DisplayContext:
    monitor = _resolve_monitor(identifier)
    display_state = (
        DisplayState.objects.select_related("current_item", "current_slide")
        .order_by("pk")
        .filter(singleton_key="live")
        .first()
    )

    layers = _base_layers_for_monitor(monitor)
    content = _build_content_from_state(display_state, monitor)

    if not content:
        content = _build_content_from_legacy(monitor)

    if not content:
        content = {
            "id": None,
            "type": "empty",
            "title": "",
            "subtitle": "",
            "text": "",
            "voices": _voices_from_payload({}),
            "notes": "",
            "chords": "",
            "bible_reference": None,
            "updated_at": None,
        }

    content_item_id = content.get("id") if isinstance(content, dict) else None
    _apply_specific_overrides(layers, monitor, display_state, content_item_id)

    if "voices" not in content or not isinstance(content["voices"], dict):
        content["voices"] = _voices_from_payload({})

    generated_at = timezone.now()

    monitor_payload = {
        "identifier": monitor.identifier if monitor else "default",
        "name": monitor.name if monitor else "Hauptanzeige",
        "role": monitor.role if monitor else MonitorRole.FRONT,
    }

    return DisplayContext(
        monitor=monitor_payload,
        layers=layers,
        content=content,
        generated_at=generated_at,
    )


def serialize_display_context(context: DisplayContext) -> dict[str, Any]:
    """Bereitet den Display-Kontext fuer API/Frontend auf."""
    payload = asdict(context)
    generated_at = payload.get("generated_at")
    if hasattr(generated_at, "isoformat"):
        payload["generated_at"] = generated_at.isoformat()
    content_payload = payload.get("content") or {}
    updated_at = content_payload.get("updated_at")
    if hasattr(updated_at, "isoformat"):
        content_payload["updated_at"] = updated_at.isoformat()
    expires_at = content_payload.get("expires_at")
    if hasattr(expires_at, "isoformat"):
        content_payload["expires_at"] = expires_at.isoformat()
    payload["content"] = content_payload
    return payload
