"""Capture the real site panels the Florida infographics embed (unedited screenshots, 2x).

Writes under assets/video/florida-2026/infographics/captures/:
  tip_moody_where_they_stand.png, tip_nixon_where_they_stand.png  (TIP record panels, live site)
  llf_florida_hero.png                                              (LLF Florida page hero)
  capture_log.json                                                  (url, time, viewport, clip)
Usage: PYTHONUTF8=1 python tools/video/capture_florida_sites.py
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[2] / "assets/video/florida-2026/infographics/captures"
JOBS = [
    ("tip_moody_where_they_stand", "https://theissuesparty.org/candidates/S6FL00640", {"x": 805, "y": 148, "width": 263, "height": 475}),
    ("tip_nixon_where_they_stand", "https://theissuesparty.org/candidates/S6FL00830", {"x": 805, "y": 148, "width": 263, "height": 475}),
    ("llf_florida_hero", "https://looklearnfind.com/elections/2026/florida/", {"x": 40, "y": 125, "width": 1000, "height": 540}),
]

with sync_playwright() as p:
    try:
        b = p.chromium.launch(channel="msedge")
    except Exception:
        b = p.chromium.launch(channel="chrome")
    log = []
    for name, url, clip in JOBS:
        pg = b.new_page(viewport={"width": 1080, "height": 1500}, device_scale_factor=2)
        pg.goto(url, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(1500)
        pg.screenshot(path=str(OUT / f"{name}.png"), clip=clip)
        log.append({"file": f"{name}.png", "url": url, "title": pg.title(), "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "viewport": "1080x1500 @2x", "clip": clip})
        pg.close()
    b.close()
(OUT / "capture_log.json").write_text(json.dumps(log, indent=1), encoding="utf8")
print("ok", len(log))
