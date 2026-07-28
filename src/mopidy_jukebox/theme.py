"""Colour schemes for the kiosk UI.

Each theme is a small set of anchor colours; the UI's CSS custom properties are
set from these at load time. Keeping them here rather than in the HTML means a
cabinet can be re-themed with a config edit and a restart, and every client --
wall unit and phones -- agrees.

Names describe the cabinet, not the palette: someone choosing a theme is
looking at a physical machine, not a swatch book.
"""

THEMES = {
    # The default. Wurlitzer oxblood, marquee-bulb amber, typed-paper cream.
    "oxblood": {
        "night": "#150e10", "night2": "#1f1519", "night3": "#2a1d22",
        "deep": "#4a1622", "deepLo": "#33101a",
        "accent": "#f0a830", "accentHot": "#ffd166",
        "paper": "#f2e8d5", "paper2": "#e4d7bd", "ink": "#2b2118",
        "chrome": "#8a9199", "chromeLo": "#565d63",
    },
    # Cool blue chrome, closer to a 1950s Seeburg.
    "seeburg": {
        "night": "#0c1018", "night2": "#141b26", "night3": "#1d2634",
        "deep": "#16324a", "deepLo": "#0f2436",
        "accent": "#4fc3f7", "accentHot": "#9fe4ff",
        "paper": "#eef3f7", "paper2": "#dbe4ec", "ink": "#16202b",
        "chrome": "#8fa3b5", "chromeLo": "#59697a",
    },
    # Neon diner: hot pink on near-black.
    "diner": {
        "night": "#120a12", "night2": "#1c101c", "night3": "#281826",
        "deep": "#4a1140", "deepLo": "#330b2c",
        "accent": "#ff4fa3", "accentHot": "#ff8ec6",
        "paper": "#f7e9f2", "paper2": "#e8d4e0", "ink": "#2b1824",
        "chrome": "#a58fa0", "chromeLo": "#6b5a66",
    },
    # Green CRT, for a machine that should look like equipment.
    "phosphor": {
        "night": "#080d0a", "night2": "#0f1712", "night3": "#16211a",
        "deep": "#12341f", "deepLo": "#0b2415",
        "accent": "#4ade80", "accentHot": "#a7f3c0",
        "paper": "#e6f2ea", "paper2": "#cfe0d5", "ink": "#101d15",
        "chrome": "#88a394", "chromeLo": "#546a5e",
    },
    # No hue at all. Reads as an appliance rather than a toy.
    "mono": {
        "night": "#101010", "night2": "#181818", "night3": "#222222",
        "deep": "#2e2e2e", "deepLo": "#1e1e1e",
        "accent": "#e8e8e8", "accentHot": "#ffffff",
        "paper": "#efefef", "paper2": "#dcdcdc", "ink": "#1a1a1a",
        "chrome": "#9a9a9a", "chromeLo": "#606060",
    },
}

DEFAULT = "oxblood"


def _clean_hex(value):
    """Return '#rrggbb' or None. Accepts '#abc', 'abc', '#aabbcc', 'aabbcc'."""
    if not value:
        return None
    h = str(value).strip().lstrip("#").lower()
    if len(h) == 3 and all(c in "0123456789abcdef" for c in h):
        h = "".join(c * 2 for c in h)
    if len(h) == 6 and all(c in "0123456789abcdef" for c in h):
        return "#" + h
    return None


def _lighten(hex_color, amount=0.35):
    """Move a colour toward white. Used to derive the 'hot' variant of a
    custom accent so a single config value is enough."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (round(c + (255 - c) * amount) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def resolve(theme_name, accent_override=None):
    """Build the palette a client should apply."""
    palette = dict(THEMES.get(theme_name, THEMES[DEFAULT]))
    accent = _clean_hex(accent_override)
    if accent:
        palette["accent"] = accent
        palette["accentHot"] = _lighten(accent)
    return palette
