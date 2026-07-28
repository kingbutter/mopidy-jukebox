"""The HTTP app.

Mounted under /jukeboxapi/ by Mopidy, which prefixes every route with the app
name. These tests mount the routes the same way so the paths under test are
the paths that will exist at runtime.
"""

import json
from unittest import mock

import pytest
import tornado.web
from tornado.testing import AsyncHTTPTestCase

from mopidy_jukebox.web import _human, app_factory

CONFIG = {
    "jukebox": {
        "start_credits": 4,
        "max_credits": 8,
        "refill_seconds": 600,
        "cost_per_song": 1,
        "attract_seconds": 90,
        "page_size": 10,
        "title": "Basement Jukebox",
        "theme": "oxblood",
        "accent_color": "",
    }
}


def routes():
    return app_factory(CONFIG, mock.Mock())


# ── route wiring ──────────────────────────────────────────────────────────
def test_registers_index_and_config_routes():
    paths = [r[0] for r in routes()]
    assert r"/" in paths
    assert r"/config.json" in paths


def test_seconds_are_converted_to_milliseconds():
    # mopidy.conf is friendlier in seconds; the browser works in ms.
    payload = routes()[0][2]["cfg"]
    assert payload["refillEvery"] == 600_000
    assert payload["attractAfter"] == 90_000


@pytest.mark.parametrize("key,value,expected", [
    ("refillEvery", 600_000, "10 min"),
    ("refillEvery", 90_000, "90 s"),
    ("attractAfter", 60_000, "1 min"),
    ("startCredits", 4, "4"),
])
def test_human_formatting(key, value, expected):
    assert _human(key, value) == expected


# ── served over HTTP, mounted as Mopidy mounts it ─────────────────────────
class TestApp(AsyncHTTPTestCase):
    def get_app(self):
        # Mopidy does: handler[0] = f"/{app['name']}{handler[0]}"
        prefixed = []
        for path, handler, kwargs in routes():
            prefixed.append((f"/jukeboxapi{path}", handler, kwargs))
        return tornado.web.Application(prefixed)

    def test_index_returns_a_page_not_a_404(self):
        r = self.fetch("/jukeboxapi/")
        assert r.code == 200
        assert "text/html" in r.headers["Content-Type"]

    def test_index_shows_the_configured_title_and_values(self):
        body = self.fetch("/jukeboxapi/").body.decode()
        assert "Basement Jukebox" in body
        assert "10 min" in body          # refill interval, humanised
        assert ">4<" in body             # starting credits

    def test_index_links_to_the_jukebox_itself(self):
        body = self.fetch("/jukeboxapi/").body.decode()
        assert 'href="/jukebox/"' in body

    def test_config_json_is_valid_json(self):
        r = self.fetch("/jukeboxapi/config.json")
        assert r.code == 200
        assert "application/json" in r.headers["Content-Type"]
        data = json.loads(r.body)
        assert data["startCredits"] == 4
        assert data["refillEvery"] == 600_000
        assert data["title"] == "Basement Jukebox"

    def test_config_json_is_not_cached(self):
        # A stale config would silently give guests the wrong credit rules.
        r = self.fetch("/jukeboxapi/config.json")
        assert r.headers["Cache-Control"] == "no-store"


# ── theming ───────────────────────────────────────────────────────────────
from mopidy_jukebox.theme import DEFAULT, THEMES, _clean_hex, resolve  # noqa: E402

PALETTE_KEYS = {"night","night2","night3","deep","deepLo","accent","accentHot",
                "paper","paper2","ink","chrome","chromeLo"}


def test_every_theme_defines_the_full_palette():
    # A missing key means that CSS variable keeps the previous theme's value,
    # which shows up as one stray colour rather than an obvious failure.
    for name, pal in THEMES.items():
        assert set(pal) == PALETTE_KEYS, f"{name} is missing {PALETTE_KEYS - set(pal)}"


def test_every_theme_colour_is_a_hex_triplet():
    import re
    for name, pal in THEMES.items():
        for key, value in pal.items():
            assert re.fullmatch(r"#[0-9a-f]{6}", value), f"{name}.{key} = {value}"


def test_unknown_theme_falls_back_to_the_default():
    assert resolve("does-not-exist") == THEMES[DEFAULT]


@pytest.mark.parametrize("raw,expected", [
    ("#f0a830", "#f0a830"),
    ("f0a830", "#f0a830"),
    ("#FA3", "#ffaa33"),
    ("fa3", "#ffaa33"),
    ("banana", None),
    ("", None),
    (None, None),
    ("#12345", None),
])
def test_clean_hex(raw, expected):
    assert _clean_hex(raw) == expected


def test_accent_override_also_derives_the_hot_variant():
    pal = resolve("oxblood", "#00b4ff")
    assert pal["accent"] == "#00b4ff"
    assert pal["accentHot"] != pal["accent"]      # lighter, not identical
    assert pal["night"] == THEMES["oxblood"]["night"]   # rest untouched


def test_bad_accent_override_is_ignored():
    assert resolve("oxblood", "banana")["accent"] == THEMES["oxblood"]["accent"]


def test_config_json_carries_the_palette():
    cfg = {"jukebox": dict(CONFIG["jukebox"], theme="diner", accent_color="")}
    payload = app_factory(cfg, mock.Mock())[0][2]["cfg"]
    assert payload["theme"] == "diner"
    assert payload["palette"]["accent"] == THEMES["diner"]["accent"]
