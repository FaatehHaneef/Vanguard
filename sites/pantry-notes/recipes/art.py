"""Illustrations drawn for the site: one small SVG per kind of dish. Decorative only;
the recipe title next to each says what the dish is."""

_PLATE = '<ellipse cx="160" cy="132" rx="118" ry="34" fill="#fff" stroke="#e4d6c3" stroke-width="4"/>'
_BOWL = '<path d="M70 104h180a90 70 0 0 1-180 0z" fill="#fff" stroke="#e4d6c3" stroke-width="4"/>'


def _svg(background: str, body: str) -> str:
    return (
        '<svg viewBox="0 0 320 240" preserveAspectRatio="xMidYMid slice" aria-hidden="true" '
        f'focusable="false"><rect width="320" height="240" fill="{background}"/>{body}</svg>'
    )


ART = {
    "curry": _svg(
        "#fcefd6",
        _BOWL
        + '<ellipse cx="160" cy="106" rx="86" ry="18" fill="#e9a23b"/>'
        + '<g fill="#3e7a45"><circle cx="130" cy="102" r="6"/><circle cx="178" cy="108" r="5"/>'
        + '<circle cx="200" cy="100" r="4"/></g>',
    ),
    "tray": _svg(
        "#fbe3dc",
        '<rect x="50" y="80" width="220" height="110" rx="14" fill="#5b4d42"/>'
        + '<g fill="#c8442b"><circle cx="100" cy="120" r="18"/><circle cx="170" cy="150" r="16"/></g>'
        + '<g fill="#e9a23b"><circle cx="220" cy="120" r="16"/><circle cx="130" cy="160" r="12"/></g>'
        + '<circle cx="210" cy="165" r="10" fill="#3e7a45"/>',
    ),
    "greens": _svg(
        "#e1f0df",
        _BOWL
        + '<ellipse cx="160" cy="106" rx="86" ry="18" fill="#3e7a45"/>'
        + '<g fill="#fdf8f1"><rect x="120" y="96" width="16" height="14" rx="3"/>'
        + '<rect x="160" y="100" width="16" height="14" rx="3"/><rect x="196" y="94" width="16" height="14" rx="3"/></g>',
    ),
    "risotto": _svg(
        "#f4ebdd",
        _PLATE
        + '<ellipse cx="160" cy="126" rx="80" ry="22" fill="#f3dfa8"/>'
        + '<g fill="#3e7a45"><circle cx="140" cy="120" r="4"/><circle cx="170" cy="128" r="4"/>'
        + '<circle cx="190" cy="118" r="4"/></g><circle cx="215" cy="112" r="10" fill="#f2d14a"/>',
    ),
    "pasta": _svg(
        "#fbe3dc",
        _PLATE
        + '<g fill="none" stroke="#f0c46a" stroke-width="6" stroke-linecap="round">'
        + '<path d="M100 128c30-20 60 20 120-6"/><path d="M110 138c40-16 70 14 100-4"/>'
        + '<path d="M120 118c30-14 50 14 80 0"/></g>'
        + '<g fill="#c8442b"><circle cx="140" cy="122" r="7"/><circle cx="185" cy="132" r="7"/></g>'
        + '<g fill="#2a211b"><circle cx="160" cy="118" r="4"/><circle cx="205" cy="124" r="4"/></g>',
    ),
    "lasagne": _svg(
        "#fcefd6",
        '<rect x="70" y="80" width="180" height="100" rx="10" fill="#c8442b"/>'
        + '<g fill="#f3dfa8"><rect x="70" y="100" width="180" height="12"/>'
        + '<rect x="70" y="130" width="180" height="12"/><rect x="70" y="160" width="180" height="12"/></g>'
        + '<rect x="70" y="80" width="180" height="20" rx="10" fill="#e9a23b"/>',
    ),
    "soup": _svg(
        "#e1f0df",
        _BOWL
        + '<ellipse cx="160" cy="106" rx="86" ry="18" fill="#c8442b"/>'
        + '<g fill="#e9a23b"><rect x="130" y="100" width="12" height="8" rx="2"/>'
        + '<rect x="176" y="104" width="12" height="8" rx="2"/></g>'
        + '<g fill="#3e7a45"><circle cx="156" cy="102" r="5"/><circle cx="200" cy="100" r="4"/></g>',
    ),
    "taco": _svg(
        "#fcefd6",
        '<path d="M70 170a90 90 0 0 1 180 0z" fill="#f0c46a"/>'
        + '<path d="M90 160c20-40 120-40 140 0" fill="#2a211b"/>'
        + '<g fill="#6b3f69"><rect x="110" y="132" width="20" height="8" rx="3"/>'
        + '<rect x="170" y="128" width="22" height="8" rx="3"/></g>'
        + '<g fill="#3e7a45"><circle cx="150" cy="126" r="6"/><circle cx="200" cy="140" r="6"/></g>',
    ),
    "aubergine": _svg(
        "#ede2f0",
        _PLATE
        + '<ellipse cx="135" cy="124" rx="52" ry="20" fill="#6b3f69" transform="rotate(-12 135 124)"/>'
        + '<ellipse cx="195" cy="128" rx="52" ry="20" fill="#6b3f69" transform="rotate(10 195 128)"/>'
        + '<g fill="#e9a23b" opacity="0.9">'
        + '<ellipse cx="135" cy="121" rx="40" ry="11" transform="rotate(-12 135 121)"/>'
        + '<ellipse cx="195" cy="125" rx="40" ry="11" transform="rotate(10 195 125)"/></g>',
    ),
    "katsu": _svg(
        "#fcefd6",
        _PLATE
        + '<ellipse cx="135" cy="128" rx="55" ry="18" fill="#fff8e7"/>'
        + '<g fill="#c9822a"><rect x="160" y="108" width="20" height="34" rx="4"/>'
        + '<rect x="184" y="108" width="20" height="34" rx="4"/><rect x="208" y="108" width="20" height="34" rx="4"/></g>'
        + '<path d="M100 132c20 8 60 8 80 0" stroke="#b5651d" stroke-width="10" fill="none"/>',
    ),
    "bowl": _svg(
        "#e8f1f4",
        _BOWL
        + '<ellipse cx="160" cy="106" rx="86" ry="18" fill="#fff8e7"/>'
        + '<rect x="128" y="94" width="60" height="18" rx="6" fill="#e87d5a"/>'
        + '<g fill="#3e7a45"><circle cx="208" cy="104" r="6"/><circle cx="222" cy="100" r="6"/></g>'
        + '<circle cx="110" cy="104" r="7" fill="#a8d28f"/>',
    ),
    "pan": _svg(
        "#fbe3dc",
        '<circle cx="160" cy="130" r="90" fill="#2a211b"/><circle cx="160" cy="130" r="78" fill="#c8442b"/>'
        + '<circle cx="130" cy="110" r="16" fill="#fff"/><circle cx="130" cy="110" r="7" fill="#e9a23b"/>'
        + '<circle cx="190" cy="150" r="16" fill="#fff"/><circle cx="190" cy="150" r="7" fill="#e9a23b"/>'
        + '<rect x="250" y="122" width="60" height="16" rx="8" fill="#2a211b"/>',
    ),
    "wrap": _svg(
        "#fcefd6",
        '<path d="M90 190l70-150 70 150z" fill="#f3dfa8"/>'
        + '<g fill="#8a5a2b"><circle cx="150" cy="110" r="12"/><circle cx="172" cy="130" r="12"/></g>'
        + '<g fill="#3e7a45"><circle cx="140" cy="140" r="7"/><circle cx="180" cy="104" r="6"/></g>'
        + '<circle cx="160" cy="160" r="6" fill="#c8442b"/>',
    ),
    "skewer": _svg(
        "#f4ebdd",
        _PLATE
        + '<path d="M70 130h190" stroke="#8a6a4a" stroke-width="4"/>'
        + '<g fill="#8a4a2b"><rect x="95" y="118" width="40" height="24" rx="12"/>'
        + '<rect x="145" y="118" width="40" height="24" rx="12"/><rect x="195" y="118" width="40" height="24" rx="12"/></g>',
    ),
    "pie": _svg(
        "#fcefd6",
        '<ellipse cx="160" cy="150" rx="110" ry="40" fill="#5b4d42"/>'
        + '<ellipse cx="160" cy="135" rx="100" ry="36" fill="#f0c46a"/>'
        + '<g stroke="#c9822a" stroke-width="4" fill="none"><path d="M100 130c20-10 40 10 60 0s40 10 60 0"/>'
        + '<path d="M110 145c20-10 40 10 60 0s30 10 40 0"/></g>',
    ),
    "crumble": _svg(
        "#ede2f0",
        '<rect x="70" y="90" width="180" height="90" rx="14" fill="#6b3f69"/>'
        + '<rect x="70" y="90" width="180" height="40" rx="14" fill="#d9a35b"/>'
        + '<g fill="#b97d3a"><circle cx="100" cy="104" r="6"/><circle cx="140" cy="112" r="5"/>'
        + '<circle cx="180" cy="102" r="6"/><circle cx="220" cy="110" r="5"/></g>',
    ),
    "noodles": _svg(
        "#fcefd6",
        _BOWL
        + '<g fill="none" stroke="#f3dfa8" stroke-width="7" stroke-linecap="round">'
        + '<path d="M100 104c20-10 40 10 60 0s40 10 60 0"/><path d="M110 112c20-8 40 8 60 0s30 8 40 0"/></g>'
        + '<g fill="#e87d5a"><path d="M130 96a10 10 0 0 1 16 8"/><path d="M180 96a10 10 0 0 1 16 8"/></g>'
        + '<circle cx="210" cy="102" r="5" fill="#3e7a45"/>',
    ),
    "salad": _svg(
        "#e1f0df",
        _BOWL
        + '<ellipse cx="160" cy="106" rx="86" ry="18" fill="#a8d28f"/>'
        + '<g fill="#c8442b"><circle cx="130" cy="100" r="9"/><circle cx="190" cy="104" r="9"/></g>'
        + '<rect x="150" y="96" width="16" height="12" fill="#fff"/>'
        + '<g fill="#2a211b"><circle cx="210" cy="96" r="5"/><circle cx="112" cy="104" r="5"/></g>',
    ),
}
