"""HTTP endpoints for the jukebox.

Mopidy lists every registered app on its root page, so this app needs
something at its own root rather than a dead link. The index doubles as a
status page: it shows the settings every client is actually running with,
which is the first thing you want when the credit rules look wrong.

Routes (mounted by Mopidy under /jukeboxapi/):
    /                 human-readable status page
    /config.json      the same values as JSON, which the UI fetches
"""

import json

import tornado.web

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jukebox &middot; status</title>
<style>
  :root{{--night:#150e10;--night2:#1f1519;--amber:#f0a830;--amber2:#ffd166;
        --paper:#f2e8d5;--chrome:#8a9199;--chrome2:#565d63}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--night);color:var(--paper);min-height:100vh;padding:6vh 5vw;
       font:16px/1.6 "Liberation Sans Narrow","DejaVu Sans Condensed",
       "Arial Narrow",system-ui,sans-serif}}
  .wrap{{max-width:660px;margin:0 auto}}
  h1{{font-size:clamp(22px,4vw,34px);letter-spacing:.2em;text-transform:uppercase;
     color:var(--amber);font-weight:700;margin-bottom:.15em}}
  .sub{{color:var(--chrome);letter-spacing:.14em;text-transform:uppercase;
       font-size:13px;margin-bottom:2.2em}}
  .cta{{display:inline-block;background:linear-gradient(180deg,var(--amber2),var(--amber));
       color:#2b2118;padding:16px 30px;font-weight:700;letter-spacing:.16em;
       text-transform:uppercase;text-decoration:none;box-shadow:0 4px 0 #96601a;
       margin-bottom:2.4em}}
  .cta:active{{transform:translateY(3px);box-shadow:0 1px 0 #96601a}}
  h2{{font-size:12px;letter-spacing:.3em;text-transform:uppercase;
     color:var(--chrome2);margin:2em 0 .7em}}
  table{{width:100%;border-collapse:collapse;
        font-family:"DejaVu Sans Mono","Liberation Mono",monospace;font-size:14px}}
  td{{padding:9px 12px;border-bottom:1px solid #2a1d22}}
  td:first-child{{color:var(--chrome)}}
  td:last-child{{text-align:right;color:var(--amber2);font-weight:700}}
  code{{background:var(--night2);padding:2px 7px;color:var(--paper)}}
  p{{color:var(--chrome);font-size:14px}}
  a{{color:var(--amber)}}
</style>
</head>
<body><div class="wrap">
  <h1>{title}</h1>
  <div class="sub">Mopidy-Jukebox &middot; status</div>

  <a class="cta" href="/jukebox/">Open the jukebox &rarr;</a>

  <h2>Live settings</h2>
  <table>{rows}</table>

  <h2>Changing these</h2>
  <p>Edit the <code>[jukebox]</code> section of <code>mopidy.conf</code> and
     restart Mopidy. Every client &mdash; the cabinet and every phone &mdash;
     reads these from <a href="config.json">config.json</a>, so one edit
     applies everywhere.</p>
</div></body>
</html>
"""

_LABELS = [
    ("startCredits", "Starting credits"),
    ("maxCredits", "Maximum credits"),
    ("refillEvery", "Refill interval"),
    ("costPerSong", "Cost per song"),
    ("attractAfter", "Attract screen after"),
    ("pageSize", "Rows per bank"),
]


def _human(key, value):
    if key in ("refillEvery", "attractAfter"):
        secs = value // 1000
        if secs >= 60 and secs % 60 == 0:
            return f"{secs // 60} min"
        return f"{secs} s"
    return str(value)


class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, cfg):
        self.cfg = cfg

    def get(self):
        rows = "".join(
            f"<tr><td>{label}</td><td>{_human(key, self.cfg[key])}</td></tr>"
            for key, label in _LABELS
            if key in self.cfg
        )
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.write(_PAGE.format(title=self.cfg.get("title", "Jukebox"), rows=rows))


class ConfigHandler(tornado.web.RequestHandler):
    def initialize(self, cfg):
        self.cfg = cfg

    def get(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.write(json.dumps(self.cfg))


def app_factory(config, core):
    c = config["jukebox"]
    payload = {
        "startCredits": c["start_credits"],
        "maxCredits": c["max_credits"],
        "refillEvery": c["refill_seconds"] * 1000,
        "costPerSong": c["cost_per_song"],
        "attractAfter": c["attract_seconds"] * 1000,
        "pageSize": c["page_size"],
        "title": c["title"],
    }
    return [
        (r"/", IndexHandler, {"cfg": payload}),
        (r"/config.json", ConfigHandler, {"cfg": payload}),
    ]
