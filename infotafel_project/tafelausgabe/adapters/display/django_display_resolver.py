from typing import Any

from ...services import resolve_display_for_monitor, serialize_display_context


class DjangoDisplayResolver:
    """Adapter that resolves display state via existing Django-backed services."""

    def resolve(self, monitor_identifier: str | None) -> dict[str, Any]:
        context = resolve_display_for_monitor(monitor_identifier)
        return serialize_display_context(context)
