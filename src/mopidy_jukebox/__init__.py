"""Mopidy-Jukebox -- serves the TouchTunes-style kiosk UI from Mopidy itself.

Serving the UI from Mopidy's own web server rather than a separate static
server means the page and the JSON-RPC endpoint share an origin, which
removes the CORS configuration entirely -- no allowed_origins, no separate
systemd unit, no port to remember.

    http://jukebox.local:6680/jukebox/
"""

import pathlib
from importlib.metadata import PackageNotFoundError, version

from mopidy import config, ext

# Single source of truth: the git tag becomes the package version via
# setuptools-scm, and Mopidy requires Extension.version to match what is on
# PyPI. Reading it back from the installed metadata keeps them in step.
try:
    __version__ = version("Mopidy-Jukebox")
except PackageNotFoundError:  # running from a source tree
    __version__ = "0.0.0"


class Extension(ext.Extension):
    dist_name = "Mopidy-Jukebox"
    ext_name = "jukebox"
    version = __version__

    def get_default_config(self):
        # Read the file directly rather than via config.read(): the helper has
        # moved between Mopidy versions, and this only needs to return text.
        return (pathlib.Path(__file__).parent / "ext.conf").read_text()

    def get_config_schema(self):
        schema = super().get_config_schema()
        # Guests never get transport controls; these are the knobs that shape
        # what they *can* do. The UI reads them from /jukebox/config.json.
        schema["start_credits"] = config.Integer(minimum=0, maximum=99)
        schema["max_credits"] = config.Integer(minimum=1, maximum=99)
        schema["refill_seconds"] = config.Integer(minimum=10)
        schema["cost_per_song"] = config.Integer(minimum=0, maximum=99)
        schema["attract_seconds"] = config.Integer(minimum=5)
        schema["page_size"] = config.Integer(minimum=4, maximum=26)
        schema["title"] = config.String()
        from .theme import THEMES
        schema["theme"] = config.String(choices=sorted(THEMES))
        # Blank means "use the theme's own accent". Any hex works.
        schema["accent_color"] = config.String(optional=True)
        return schema

    def setup(self, registry):
        registry.add(
            "http:static",
            {
                "name": self.ext_name,
                "path": str(pathlib.Path(__file__).parent / "static"),
            },
        )
        from .web import app_factory

        registry.add(
            "http:app",
            {"name": self.ext_name + "api", "factory": app_factory},
        )
