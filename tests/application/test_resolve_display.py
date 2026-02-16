from infotafel_project.tafelausgabe.application.display.dtos import ResolveDisplayInput
from infotafel_project.tafelausgabe.application.display.use_cases import ResolveDisplay


class DummyResolver:
    def __init__(self) -> None:
        self.last_identifier = None

    def resolve(self, monitor_identifier):
        self.last_identifier = monitor_identifier
        return {"monitor": {"identifier": monitor_identifier or "default"}}


def test_resolve_display_delegates_to_resolver() -> None:
    resolver = DummyResolver()
    use_case = ResolveDisplay(resolver=resolver)

    result = use_case.execute(ResolveDisplayInput(monitor_identifier="saal"))

    assert resolver.last_identifier == "saal"
    assert result.payload == {"monitor": {"identifier": "saal"}}


def test_resolve_display_allows_missing_identifier() -> None:
    resolver = DummyResolver()
    use_case = ResolveDisplay(resolver=resolver)

    result = use_case.execute(ResolveDisplayInput(monitor_identifier=None))

    assert resolver.last_identifier is None
    assert result.payload == {"monitor": {"identifier": "default"}}
