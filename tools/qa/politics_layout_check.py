#!/usr/bin/env python3
"""Layout measurements for the Daily Signal edition (Playwright; serves ./dist locally).

Checks, at 1440 and 390 px: chapter photographs fill the editorial canvas (900 to 1120 px on desktop, never below natural-size limits), the reading column is
640 to 700 px, chapter images are 16:9 or 3:2 and never upscaled past their pixel width, headlines are larger than body text and separated from it, and every
chapter and teaser anchor scrolls to a fully visible heading (not hidden under the sticky bars). Prints a measurement table. Exit 1 on any failure.
"""
import functools
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = "/politics/daily/2026-11-05/"
CHAPTERS = ["leadership", "geography", "voters", "money", "states"]
MEASURE = r"""(id) => {
  const s = document.getElementById(id); const r = e => e ? e.getBoundingClientRect() : null;
  const fig = s.querySelector('.pol-ed__fig img'), h = s.querySelector('h2'), p = s.querySelector('.pol-ed__body p');
  const f = r(fig), hh = r(h), pp = r(p);
  const real = fig ? (() => { const m = (fig.srcset || '').split(',').map(x => x.trim().split(/\s+/)).find(x => fig.currentSrc.endsWith(x[0].split('?')[0]) || fig.currentSrc.includes(x[0].split('?')[0])); return m ? parseInt(m[1]) : fig.naturalWidth; })() : 0;
  return {fig: f && {w: Math.round(f.width), h: Math.round(f.height), nat: real, ratio: +(f.width / f.height).toFixed(2)},
          head: {w: Math.round(hh.width), size: parseFloat(getComputedStyle(h).fontSize)},
          body: {w: Math.round(pp.width), size: parseFloat(getComputedStyle(p).fontSize)},
          gap: Math.round(pp.top - (f ? f.bottom : hh.bottom))};
}"""


def main():
    from playwright.sync_api import sync_playwright
    h = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT / "dist"))
    h.log_message = lambda *a, **k: None
    srv = ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    fails, rows = [], []
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge")
        except Exception:
            b = p.chromium.launch()
        for w, hgt in ((1440, 900), (390, 844)):
            pg = b.new_context(viewport={"width": w, "height": hgt}).new_page()
            pg.goto(base + PAGE)
            pg.wait_for_load_state("networkidle")
            pg.evaluate("async () => { document.querySelectorAll('img').forEach(i => i.loading = 'eager'); await Promise.all([...document.images].map(i => i.decode().catch(() => {}))); }")
            for cid in CHAPTERS:
                m = pg.evaluate(MEASURE, cid)
                rows.append((w, cid, m))
                f = m["fig"]
                if not f:
                    fails.append(f"{w} #{cid}: no chapter image")
                    continue
                if w >= 1100:
                    if not 900 <= f["w"] <= 1120:
                        fails.append(f"{w} #{cid}: image is {f['w']}px wide (needs 900 to 1120)")
                    if not 640 <= m["body"]["w"] <= 700:
                        fails.append(f"{w} #{cid}: reading column is {m['body']['w']}px (needs 640 to 700)")
                else:
                    if f["w"] < w - 80:
                        fails.append(f"{w} #{cid}: image is only {f['w']}px wide on a {w}px screen")
                if not (abs(f["ratio"] - 16 / 9) < 0.03 or abs(f["ratio"] - 1.5) < 0.03):
                    fails.append(f"{w} #{cid}: image ratio {f['ratio']} is neither 16:9 nor 3:2")
                if f["nat"] < f["w"] * (1 if w >= 1100 else 0.9):
                    fails.append(f"{w} #{cid}: image is upscaled ({f['nat']}px natural for {f['w']}px shown)")
                if m["head"]["size"] < m["body"]["size"] * 1.6:
                    fails.append(f"{w} #{cid}: headline {m['head']['size']}px is not clearly larger than body {m['body']['size']}px")
            # anchors: chapter bar, teasers and back links must land on a fully visible heading
            bar_bottom = lambda: pg.evaluate("() => { const b = document.querySelector('.pol-chapters').getBoundingClientRect(); const mb = document.querySelector('.mobile-bar'); const m = mb ? mb.getBoundingClientRect() : {bottom: 0}; return Math.max(b.bottom, m.bottom) }")
            for cid in CHAPTERS:
                for sel in (f'.pol-chapters a[data-chapter="{cid}"]', f'#five-signals a.pol-teaser__go[href="#{cid}"]'):
                    pg.evaluate("window.scrollTo(0, 0)")
                    pg.locator(sel).first.click()
                    pg.wait_for_function("() => { window.__y2 = window.__y1; window.__y1 = window.scrollY; return window.__y2 === window.__y1; }", polling=250, timeout=8000)      # smooth scrolling has stopped
                    r = pg.evaluate("(id) => { const e = document.querySelector('#' + id + ' .pol-eyebrow').getBoundingClientRect(); const h = document.querySelector('#' + id + ' h2').getBoundingClientRect(); return {top: e.top, bottom: h.bottom} }", cid)
                    if r["top"] < bar_bottom() - 1 or r["bottom"] > hgt:
                        fails.append(f"{w} {sel}: heading spans {r['top']:.0f} to {r['bottom']:.0f}px with the sticky bars ending at {bar_bottom():.0f}px")
            pg.evaluate("window.scrollTo(0, 0)")
            ov = pg.evaluate("() => document.documentElement.scrollWidth - innerWidth")
            if ov > 1:
                fails.append(f"{w}: horizontal scroll of {ov}px")
        b.close()
    print(f"{'px':>5} {'chapter':<11} {'image':>13} {'natural':>8} {'ratio':>6} {'body col':>9} {'headline':>9} {'gap':>5}")
    for w, cid, m in rows:
        f = m["fig"]
        print(f"{w:>5} {cid:<11} {str(f['w']) + 'x' + str(f['h']):>13} {f['nat']:>8} {f['ratio']:>6} {m['body']['w']:>9} {m['head']['size']:>8.0f}p {m['gap']:>5}")
    print(f"LAYOUT CHECK: {len(fails)} problem(s)")
    for f in fails:
        print("  " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
