from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import (
    ContentItem,
    ContentItemType,
    ContentSlide,
    DisplayState,
    Monitor,
    MonitorLayerConfig,
    MonitorRole,
)

User = get_user_model()


def _default_data_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parents[4] / "Infotafel" / "htdocs" / "data",
        Path(__file__).resolve().parents[4] / "infotafel" / "htdocs" / "data",
        Path(__file__).resolve().parents[3] / "infotafel" / "htdocs" / "data",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


class Command(BaseCommand):
    """Importiert bestehende JSON-Daten aus dem PHP-System in das neue Modell."""

    help = "Importiert Monitore und Anzeigen aus infotafel/htdocs/data/*.json"

    def add_arguments(self, parser):
        default_base_dir = _default_data_dir()
        parser.add_argument(
            "--base-dir",
            default=str(default_base_dir),
            help=f"Basisverzeichnis der JSON-Dateien (Standard: {default_base_dir})",
        )
        parser.add_argument(
            "--user",
            default=None,
            help="Optionaler Benutzername, der als Ersteller fuer ContentItems gesetzt wird.",
        )
        parser.add_argument(
            "--skip-monitors",
            action="store_true",
            help="Monitore nicht importieren.",
        )
        parser.add_argument(
            "--skip-content",
            action="store_true",
            help="Anzeigeinhalte nicht importieren.",
        )

    def handle(self, *args, **options):
        base_dir = Path(options["base_dir"]).expanduser().resolve()
        if not base_dir.exists():
            fallback = _default_data_dir()
            if fallback.exists() and fallback != base_dir:
                base_dir = fallback
            else:
                raise CommandError(
                    "Basisverzeichnis "
                    f"{base_dir} wurde nicht gefunden. Nutzen Sie --base-dir, "
                    "um den Pfad vorzugeben."
                )

        user = None
        username = options.get("user")
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist as err:
                raise CommandError(f"Benutzer {username} wurde nicht gefunden.") from err

        monitors_data = self._load_json(base_dir / "monitors.json", default=[])
        settings_data = self._load_json(base_dir / "einstellungen.json", default={})
        display_data = self._load_json(base_dir / "anzeige.json", default={})

        with transaction.atomic():
            if not options["skip_monitors"]:
                self._import_monitors(monitors_data, settings_data)
            if not options["skip_content"]:
                self._import_content(display_data, user)
            self._ensure_display_state()

        self.stdout.write(self.style.SUCCESS("Import abgeschlossen."))

    def _load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Datei {path} konnte nicht gelesen werden: {exc}") from exc

    def _import_monitors(
        self, monitors: Iterable[dict[str, Any]], settings: dict[str, Any]
    ) -> None:
        for entry in monitors:
            identifier = str(entry.get("id") or entry.get("identifier") or "").strip()
            if not identifier:
                continue
            monitor, created = Monitor.objects.get_or_create(
                identifier=identifier,
                defaults={
                    "name": entry.get("name") or identifier,
                    "role": MonitorRole.FRONT,
                    "description": "",
                    "order": Monitor.objects.count(),
                    "is_active": True,
                },
            )
            if not created:
                monitor.name = entry.get("name") or monitor.name
                monitor.save(update_fields=["name"])
            duration = None
            duration_entry = settings.get(identifier)
            if isinstance(duration_entry, dict):
                duration = duration_entry.get("anzeigedauer")
            layer_defaults = (
                monitor.layer_config.layers if getattr(monitor, "layer_config", None) else None
            )
            if not layer_defaults:
                MonitorLayerConfig.objects.get_or_create(
                    monitor=monitor,
                    defaults={
                        "layers": {
                            "lyrics": True,
                            "voices": True,
                            "bible_reference": True,
                            "notes": False,
                            "next_slide": False,
                            "duration": duration,
                        }
                    },
                )
            else:
                if duration is not None:
                    layer_defaults["duration"] = duration
                    monitor.layer_config.layers = layer_defaults
                    monitor.layer_config.save(update_fields=["layers"])
        if not monitors:
            self.stdout.write("Keine Monitore in monitors.json gefunden.")

    def _import_content(self, display_data: dict[str, Any], user: User | None) -> None:
        # Importiert jeden Monitor-Eintrag als ContentItem + Slide
        for monitor_id, payload in display_data.items():
            if not isinstance(payload, dict):
                continue
            text = (payload.get("text") or "").strip()
            if not text:
                continue
            item, created = ContentItem.objects.get_or_create(
                slug=f"legacy-{monitor_id}",
                defaults={
                    "item_type": ContentItemType.SONG,
                    "title": f"Legacy {monitor_id}",
                    "subtitle": "Imported",
                    "language": "de",
                    "metadata": {
                        "voices": {
                            "sopran": bool(payload.get("sopran")),
                            "alt": bool(payload.get("alt")),
                            "tenor": bool(payload.get("tenor")),
                            "bass": bool(payload.get("bass")),
                        }
                    },
                    "created_by": user,
                    "updated_by": user,
                },
            )
            if not created:
                item.metadata = item.metadata or {}
                item.metadata["voices"] = {
                    "sopran": bool(payload.get("sopran")),
                    "alt": bool(payload.get("alt")),
                    "tenor": bool(payload.get("tenor")),
                    "bass": bool(payload.get("bass")),
                }
                if user:
                    item.updated_by = user
                item.save()
            ContentSlide.objects.update_or_create(
                item=item,
                position=1,
                defaults={
                    "text": text,
                    "label": "Legacy",
                },
            )
        if not display_data:
            self.stdout.write("Keine Inhalte in anzeige.json gefunden.")

    def _ensure_display_state(self) -> None:
        DisplayState.objects.get_or_create(singleton_key="live")
