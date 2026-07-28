"""Tests for the extension definition.

Mopidy validates an extension's shipped defaults against its own schema at
startup, so the most valuable test here is that those two agree -- a mismatch
means the extension silently refuses to load on a user's machine.
"""

import configparser
from unittest import mock

import mopidy_jukebox


def test_get_default_config():
    ext = mopidy_jukebox.Extension()
    cfg = ext.get_default_config()
    assert "[jukebox]" in cfg
    assert "enabled = true" in cfg
    assert "start_credits" in cfg
    assert "page_size" in cfg


def test_get_config_schema():
    schema = mopidy_jukebox.Extension().get_config_schema()
    for key in ("start_credits", "max_credits", "refill_seconds",
                "cost_per_song", "attract_seconds", "page_size", "title"):
        assert key in schema


def test_defaults_satisfy_schema():
    ext = mopidy_jukebox.Extension()
    parser = configparser.RawConfigParser()
    parser.read_string(ext.get_default_config())
    values, errors = ext.get_config_schema().deserialize(dict(parser["jukebox"]))
    assert errors == {}
    assert values["start_credits"] >= 0
    assert values["max_credits"] >= values["cost_per_song"]


def test_setup_registers_static_and_app():
    registry = mock.Mock()
    mopidy_jukebox.Extension().setup(registry)
    kinds = [c[0][0] for c in registry.add.call_args_list]
    assert "http:static" in kinds
    assert "http:app" in kinds


def test_static_dir_contains_the_ui():
    import pathlib
    index = pathlib.Path(mopidy_jukebox.__file__).parent / "static" / "index.html"
    assert index.is_file()
    assert "jukebox" in index.read_text().lower()
