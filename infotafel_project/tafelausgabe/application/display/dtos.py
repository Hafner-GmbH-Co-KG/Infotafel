from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResolveDisplayInput:
    """Input DTO for resolving display data."""

    monitor_identifier: str | None


@dataclass(frozen=True)
class ResolveDisplayOutput:
    """Output DTO for display payload returned to inbound adapters."""

    payload: dict[str, Any]
