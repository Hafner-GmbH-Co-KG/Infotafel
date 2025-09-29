from __future__ import annotations

from typing import Optional

from django import forms
from django.db.models import Max
from django.utils.text import slugify

from .models import Monitor, MonitorLayerConfig, MonitorRole, default_layer_config


class MonitorCreateForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    identifier = forms.CharField(
        label="Kurzname",
        max_length=60,
        required=False,
        help_text="Wird fuer die URL benutzt; bleibt leer, um ihn automatisch zu erzeugen.",
    )
    role = forms.ChoiceField(label="Rolle", choices=MonitorRole.choices, initial=MonitorRole.FRONT)
    description = forms.CharField(
        label="Beschreibung",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    is_active = forms.BooleanField(label="Aktiv", required=False, initial=True)

    _resolved_identifier: Optional[str] = None

    def clean_identifier(self) -> str:
        identifier = self.cleaned_data.get("identifier", "").strip()
        if identifier:
            identifier = slugify(identifier)
        return identifier

    def clean(self):  # type: ignore[override]
        cleaned = super().clean()
        if self.errors:
            return cleaned
        name = cleaned.get("name", "").strip()
        identifier = cleaned.get("identifier", "")
        base = identifier or slugify(name)
        if not base:
            self.add_error("name", "Es konnte kein URL-Kurzname erzeugt werden.")
            return cleaned
        candidate = base
        suffix = 2
        while Monitor.objects.filter(identifier=candidate).exists():
            candidate = f"{base}-{suffix}"
            suffix += 1
        cleaned["identifier"] = candidate
        self._resolved_identifier = candidate
        return cleaned

    def save(self) -> Monitor:
        if self._resolved_identifier is None:
            raise ValueError("Form must be validated before calling save().")
        max_order = Monitor.objects.aggregate(Max("order"))
        next_order = (max_order["order__max"] or 0) + 10
        monitor = Monitor.objects.create(
            identifier=self._resolved_identifier,
            name=self.cleaned_data["name"].strip(),
            role=self.cleaned_data["role"],
            description=self.cleaned_data.get("description", ""),
            order=next_order,
            is_active=bool(self.cleaned_data.get("is_active", True)),
        )
        MonitorLayerConfig.objects.get_or_create(
            monitor=monitor,
            defaults={"layers": default_layer_config()},
        )
        return monitor


class MonitorDeleteForm(forms.Form):
    monitor_id = forms.IntegerField(widget=forms.HiddenInput)

    _monitor: Optional[Monitor] = None

    def clean_monitor_id(self) -> int:
        monitor_id = self.cleaned_data["monitor_id"]
        try:
            monitor = Monitor.objects.get(pk=monitor_id)
        except Monitor.DoesNotExist as exc:  # pragma: no cover - defensive
            raise forms.ValidationError("Monitor wurde nicht gefunden.") from exc
        if Monitor.objects.count() <= 1:
            raise forms.ValidationError("Der letzte Monitor kann nicht geloescht werden.")
        self._monitor = monitor
        return monitor_id

    def delete(self) -> Monitor:
        if self._monitor is None:
            raise ValueError("Form must be validated before calling delete().")
        monitor = self._monitor
        monitor.delete()
        return monitor
