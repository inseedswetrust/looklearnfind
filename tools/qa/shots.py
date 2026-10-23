#!/usr/bin/env python3
"""Full-page screenshots + overflow/target checks at desktop (1440) and phone (390) widths using Playwright (Edge or Chrome).

    python3 tools/qa/shots.py <base-url> <outdir> <path> [<path> ...]

Writes <outdir>/<slug>-1440.png and -390.png and prints: horizontal overflow, console errors, small tap targets, images without alt, broken images.
"""
import sys, re, json
from pathlib import Path
from playwright.sync_api import sync_playwright
base, out, *paths = sys.argv[1:]
Path(out).mkdir(parents=True, exist_ok=True)
CHECK = """() => {
  const doc = document.documentElement;
  const over = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.right > innerWidth + 1 && getComputedStyle(e).position !== 'fixed' && !e.closest('.nav') && !e.closest('.tablewrap') && !e.closest('svg'); }).slice(0, 5).map(e => e.tagName + '.' + e.className + '#' + (e.id||'') + ' ' + Math.round(e.getBoundingClientRect().right));
  const small = [...document.querySelectorAll('a,button')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && (r.height < 24 || r.width < 24) && getComputedStyle(e).display !== 'inline'; }).length;
  const noalt = [...document.images].filter(i => !i.hasAttribute('alt')).length;
  const broken = [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src).slice(0, 5);
  return {scrollW: doc.scrollWidth, innerW: innerWidth, overflowing: over, smallTargets: small, imgNoAlt: noalt, brokenImgs: broken, h: doc.scrollHeight};
}"""
with sync_playwright() as p:
    try:
        b = p.chromium.launch(channel="msedge")
    except Exception:
        b = p.chromium.launch(channel="chrome")
    for path in paths:
        slug = path.strip("/").replace("/", "_") or "home"
        for w, h in ((1440, 900), (390, 844)):
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
            pg = ctx.new_page()
            errs = []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("response", lambda r: errs.append(f"{r.status} {r.url}") if r.status >= 400 else None)
            pg.goto(base + path, wait_until="networkidle")
            pg.screenshot(path=f"{out}/{slug}-{w}.png", full_page=True)
            res = pg.evaluate(CHECK)
            print(path, w, json.dumps({**res, "consoleErrors": errs[:3]}))
            ctx.close()
    b.close()
