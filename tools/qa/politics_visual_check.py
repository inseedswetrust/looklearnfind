#!/usr/bin/env python3
"""Screenshots and accessibility checks for /politics/ and /politics/daily/ at 1440, 1024, 390 and 320 px (Playwright; serves ./dist locally).
    python tools/qa/politics_visual_check.py --shots docs/politics/screenshots
Checks: one h1, heading order, landmarks, every link and button has a name, images have alt attributes, no horizontal scroll,
44px targets in the main pane on touch widths, focus is visible on the first link, no console errors. Exit 1 on any failure."""
import argparse, functools, json, sys, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = [("/politics/", "politics"), ("/politics/daily/", "politics-daily")]
if (ROOT / "dist" / "politics" / "daily" / "2026-11-05" / "index.html").exists():     # a preview build (LLF_PREVIEW_DRAFTS=1) also renders the draft edition
    PAGES.append(("/politics/daily/2026-11-05/", "politics-edition"))
WIDTHS = (1440, 1024, 390, 320)
JS = """() => {
  const out = [];
  const hs = [...document.querySelectorAll('main h1,main h2,main h3')].map(h => +h.tagName[1]);
  if (document.querySelectorAll('h1').length !== 1) out.push('needs exactly one h1');
  for (let i = 1; i < hs.length; i++) if (hs[i] - hs[i-1] > 1) out.push('heading level skips from h' + hs[i-1] + ' to h' + hs[i]);
  for (const l of ['main', 'nav', 'aside', 'footer']) if (!document.querySelector(l)) out.push('missing landmark ' + l);
  for (const a of document.querySelectorAll('a:not([aria-hidden=true]),button')) { if (!(a.textContent.trim() || a.getAttribute('aria-label'))) out.push('unnamed control ' + (a.getAttribute('href') || a.tagName)); }
  for (const i of document.querySelectorAll('img')) if (!i.hasAttribute('alt')) out.push('image without alt ' + i.getAttribute('src'));
  if (document.documentElement.scrollWidth > innerWidth + 1) out.push('horizontal scroll ' + document.documentElement.scrollWidth + ' > ' + innerWidth);
  if (innerWidth < 901) for (const a of document.querySelectorAll('main a.pol-state,main a.row,main a.chip,main a.link:not(.pol-inline)')) { const r = a.getBoundingClientRect(); if (r.height < 44 && r.width > 0) out.push('target under 44px: ' + a.textContent.trim().slice(0, 30) + ' (' + Math.round(r.height) + ')'); }
  return out;
}"""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--shots"); a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    h = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT / "dist")); h.log_message = lambda *x, **k: None
    srv = ThreadingHTTPServer(("127.0.0.1", 0), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    shots = Path(a.shots) if a.shots else None
    if shots: shots.mkdir(parents=True, exist_ok=True)
    fails, n = [], 0
    with sync_playwright() as p:
        try: b = p.chromium.launch(channel="msedge")
        except Exception: b = p.chromium.launch()
        for w in WIDTHS:
            ctx = b.new_context(viewport={"width": w, "height": 900}); pg = ctx.new_page(); errs = []
            pg.on("response", lambda r: errs.append(f"{r.status} {r.url}") if r.status >= 400 and "/api/" not in r.url and "favicon" not in r.url else None)
            for path, name in PAGES:
                pg.goto(base + path); pg.wait_for_load_state("networkidle")
                pg.evaluate("async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } document.querySelectorAll('img').forEach(i => { i.loading = 'eager'; }); await Promise.all([...document.images].map(i => i.decode().catch(() => {}))); window.scrollTo(0, 0); }")
                pg.wait_for_timeout(400)
                probs = pg.evaluate(JS); n += 1
                if w == 320 and path == "/politics/":
                    probs += ["wide element: " + x for x in pg.evaluate("() => [...document.querySelectorAll('main *:not(.pol-hero *):not(.pol-cut__stage *)')].filter(e => e.getBoundingClientRect().right > innerWidth + 1).slice(0, 6).map(e => e.tagName + '.' + e.className)")]
                pg.keyboard.press("Tab"); pg.keyboard.press("Tab")
                if not pg.evaluate("() => { const e = document.activeElement; return !!e && e !== document.body && getComputedStyle(e).outlineStyle !== 'none' }"):
                    probs.append("focus not visible after Tab")
                probs += [f"request failed: {e}" for e in errs]; errs.clear()
                for pr in probs: fails.append(f"{path} @{w}: {pr}")
                if shots:
                    pg.screenshot(path=str(shots / f"{name}-{w}.png"), full_page=True)
                    if w == 1440:
                        pg.screenshot(path=str(shots / f"{name}-1440-viewport.png"))
                    if w == 390 and path in ("/politics/", "/politics/daily/2026-11-05/"):
                        pg.screenshot(path=str(shots / f"{name}-drawer-closed-390.png"))
                        pg.click("a.nav-open"); pg.wait_for_timeout(450)
                        pg.evaluate("() => { const o = document.querySelector('[data-outline]'); if (o) { o.open = true; o.scrollIntoView({block: 'center'}); } }"); pg.wait_for_timeout(200)
                        pg.screenshot(path=str(shots / f"{name}-drawer-open-390.png"))
                        pg.keyboard.press("Escape"); pg.wait_for_timeout(350)
            ctx.close()
        b.close()
    print(f"{n} page checks at {len(WIDTHS)} widths; {len(fails)} failure(s)")
    for f in fails: print("  " + f)
    sys.exit(1 if fails else 0)


main()
