from typing import Any, Protocol


class DisplayResolverPort(Protocol):
    """Port for resolving a serialized display payload."""

    def resolve(self, monitor_identifier: str | None) -> dict[str, Any]: ...
