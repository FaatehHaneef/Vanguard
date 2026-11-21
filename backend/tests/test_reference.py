import json

from vanguard.reference.a11y_cua import collect, markdown


def test_counts_modalities_per_group(tmp_path):
    def write(rel, records):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(records))

    write(
        "BLVU/BLVU1/1/1_chrome.exe.json",
        [
            {"event": {"type": "key_press", "key": "Tab"}},
            {"event": {"type": "key_press", "key": "b"}},
            {"event": {"type": "hotkey", "key": "Ctrl"}},
        ],
    )
    write(
        "SU/SU1/1/1_chrome.exe.json",
        [{"event": "mouse_click"}, {"event": "mouse_move"}, {"event": {"type": "key_press"}}],
    )
    write("Agent-X/Screen Reader/3/1_chrome.exe.json", [{"event": "mouse_click"}])
    stats = collect(tmp_path)
    blind = stats["Blind and low-vision users"]
    assert (blind.keyboard, blind.pointer, blind.navigation_key_share) == (3, 0, 0.5)
    assert stats["Sighted users"].pointer_share == 0.5  # moves are not actions
    assert stats["Agent-X (Screen Reader)"].pointer == 1
    assert "| Sighted users | 1 | 1 | 1 | 50.0% |" in markdown(stats)
