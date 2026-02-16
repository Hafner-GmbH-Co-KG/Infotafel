from .dtos import ResolveDisplayInput, ResolveDisplayOutput
from .ports import DisplayResolverPort


class ResolveDisplay:
    """Use-case for resolving display data for a monitor."""

    def __init__(self, resolver: DisplayResolverPort) -> None:
        self._resolver = resolver

    def execute(self, request: ResolveDisplayInput) -> ResolveDisplayOutput:
        payload = self._resolver.resolve(request.monitor_identifier)
        return ResolveDisplayOutput(payload=payload)
