# Mopidy-Jukebox

[![PyPI](https://img.shields.io/pypi/v/Mopidy-Jukebox)](https://pypi.org/project/Mopidy-Jukebox/)
[![CI](https://github.com/kingbutter/mopidy-jukebox/actions/workflows/ci.yml/badge.svg)](https://github.com/kingbutter/mopidy-jukebox/actions)

A [Mopidy](https://mopidy.com/) extension that turns a touchscreen into a
TouchTunes-style jukebox. Guests browse album art, spend free credits, and
queue the next song — from the cabinet itself or from their phone.

Built for an actual 1990s TouchTunes Allegro cabinet with a resistive Elo
panel, so the UI assumes single-touch, no hover, and no keyboard.

## What it does

- **Art-first browsing.** Categories come from whatever your backends expose;
  albums and artists render as tiles, with drill-down to track lists.
- **Dialable selection codes.** Track lists page into banks — A1–A10, then
  B1–B10 — and an on-screen keypad lets you punch in a code, the way the
  mechanical machines worked.
- **Credits.** Free, but rationed: a starting balance and a slow refill, so
  one person can't own the night.
- **No transport controls for guests.** No pause, no skip, no volume. An
  admin panel hides behind five taps on the credits counter.
- **Attract mode** built from album art already in the cache.
- **Phone and kiosk layouts** from one page, with the device's own keyboard
  on phones and a built-in QWERTY on the wall unit.

Served from Mopidy's own web server, so the page and the JSON-RPC endpoint
share an origin — there is no CORS configuration to get wrong.

## Installation

```sh
python3 -m pip install Mopidy-Jukebox
```

Then open `http://<your-host>:6680/jukebox/`.

## Configuration

Defaults are usable as-is. To change them, add a `[jukebox]` section to your
`mopidy.conf`:

```ini
[jukebox]
enabled = true
start_credits = 4        # credits a guest starts with
max_credits = 8          # ceiling, so credits don't stockpile
refill_seconds = 600     # one more credit every N seconds
cost_per_song = 1
attract_seconds = 90     # idle time before the attract screen
page_size = 10           # rows per selection bank (A1..A10)
title = Jukebox
```

Every client reads these from `/jukeboxapi/config.json`, so a change here
applies to the wall unit and every phone at once.

## Project resources

- [Source code](https://github.com/kingbutter/mopidy-jukebox)
- [Issue tracker](https://github.com/kingbutter/mopidy-jukebox/issues)

## Credits

- Original author: [King Butter](https://github.com/kingbutter)
- Current maintainer: [King Butter](https://github.com/kingbutter)
