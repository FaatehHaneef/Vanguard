from vanguard import catalog
from vanguard.contracts import PersonaStatus


def test_five_personas_load():
    assert set(catalog.personas()) == {
        "keyboard-only",
        "screen-reader",
        "magnifier",
        "first-time",
        "unrestricted",
    }


def test_full_and_preview_split():
    status = {pid: spec.status for pid, spec in catalog.personas().items()}
    full = {pid for pid, value in status.items() if value is PersonaStatus.FULL}
    assert full == {"keyboard-only", "unrestricted"}


def test_exactly_one_control():
    controls = [spec for spec in catalog.personas().values() if spec.is_control]
    assert [spec.id for spec in controls] == ["unrestricted"]


def test_tasks_refer_to_known_sites():
    assert {task.site_id for task in catalog.tasks().values()} <= set(catalog.sites())
    assert "buy-two" in catalog.tasks()
