#!/usr/bin/env python3
"""Render-level regression check for the global shell (Playwright; Edge or Chrome). Serves ./dist locally, never touches the network.

    python3 tools/qa/shell_check.py                      # checks every page type at 1440, 1280, 1024, 900, 390 and 320 px
    python3 tools/qa/shell_check.py --quick              # 1440, 900 and 390 only
    python3 tools/qa/shell_check.py --shots docs/design/screenshots   # also writes the delivery screenshots

Asserts per page and width (docs/design/LLF_GLOBAL_SHELL.md): one rail in the DOM, visible and fixed on desktop (>=901px) and hidden on mobile; one mobile bar,
fixed and visible on mobile only; the page content is offset by the rail (no overlap); no horizontal scroll; the lit LOOK / LEARN / FIND word matches the route
matrix; global search present and reachable; "/" focuses search but not while typing in a field; the Explore sheet opens and Escape closes it; no console errors.
Exit code 1 on any failure. Needs `python3 build.py` to have produced dist/.
"""
import argparse, json, subprocess, sys, threading, time, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
WIDTHS = [1440, 1280, 1024, 900, 390, 320]
# (path, expected lit mode, label). Mode matrix: docs/design/LLF_GLOBAL_SHELL.md
PAGES = [
    ("/", "", "home"),
    ("/politics/", "", "politics section"),
    ("/economy/", "", "economy section"),
    ("/topics/", "", "topics index"),
    ("/topics/politics/", "", "topic"),
    ("/threads/midterms-2026/", "", "thread"),
    ("/latest/", "", "latest"),
    ("/learn/", "learn", "learn index"),
    ("/learn/pennsylvania-governor-poll-party-market-2026/", "learn", "article"),
    ("/learn/what-was-tartary/", "learn", "sample article"),
    ("/find/", "find", "find"),
    ("/find/candidates/", "find", "candidate directory"),
    ("/look/", "look", "look ledger"),
    ("/elections/2026/pennsylvania/", "learn", "state hub"),
    ("/elections/2026/pennsylvania/governor/", "learn", "governor page"),
    ("/elections/2026/pennsylvania/house/", "learn", "house index"),
    ("/elections/2026/pennsylvania/house/1/", "learn", "race page"),
    ("/elections/2026/florida/", "learn", "Florida hub (separate generator)"),
    ("/elections/2026/florida/house/1/", "learn", "Florida district"),
    ("/search/", "", "search"),
    ("/about/", "", "about"),
    ("/privacy/", "", "legal"),
    ("/404.html", "", "404"),
]
SHOTS = [("/", "homepage"), ("/elections/2026/pennsylvania/", "pennsylvania-hub"), ("/elections/2026/pennsylvania/house/1/", "race-page"),
         ("/learn/pennsylvania-governor-poll-party-market-2026/", "article")]


def serve():
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass
    handler = functools.partial(Quiet, directory=str(DIST))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--shots")
    ap.add_argument("--json")
    args = ap.parse_args()
    from playwright.sync_api import sync_playwright
    widths = [1440, 900, 390] if args.quick else WIDTHS
    srv, port = serve()
    base = f"http://127.0.0.1:{port}"
    fails, checks = [], 0
    with sync_playwright() as pw:
        browser = None
        for ch in ("msedge", "chrome", None):
            try:
                browser = pw.chromium.launch(channel=ch) if ch else pw.chromium.launch()
                break
            except Exception:
                continue
        if not browser:
            print("no Playwright browser available"); return 2
        for w in widths:
            h = 900 if w >= 901 else 800
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
            for path, mode, label in PAGES:
                page = ctx.new_page()
                errs = []
                # a static server has no PHP backend: /api/ requests are expected to fail here and are not shell defects
                page.on("response", lambda r: errs.append(f"{r.status} {r.url.replace(base, '')}") if r.status >= 400 and "/api/" not in r.url and not r.url.endswith("/404.html") else None)
                page.on("console", lambda m: errs.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
                page.on("pageerror", lambda e: errs.append(str(e)))
                resp = page.goto(base + path, wait_until="load")
                page.wait_for_timeout(150)
                def fail(msg):
                    fails.append(f"{w}px {path} ({label}): {msg}")
                info = page.evaluate("""() => {
                    const q = s => document.querySelectorAll(s);
                    const vis = el => { if (!el) return false; const r = el.getBoundingClientRect(), cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; };
                    const rail = document.getElementById('llf-rail'), bar = document.querySelector('.mobile-bar'), main = document.getElementById('main');
                    const lit = [...q('.format-nav a[aria-current=page]')].map(a => a.textContent.trim().toLowerCase());
                    const word = document.body.getAttribute('data-format');
                    return {
                      roots: q('[data-llf-global-shell]').length, rails: q('#llf-rail').length, bars: q('.mobile-bar').length, sheets: q('#explore-sheet').length,
                      railVisible: vis(rail), railPos: rail ? getComputedStyle(rail).position : '', railRect: rail ? rail.getBoundingClientRect().toJSON() : null,
                      barVisible: vis(bar), barPos: bar ? getComputedStyle(bar).position : '',
                      mainLeft: main ? main.getBoundingClientRect().left : null, bodyPad: parseFloat(getComputedStyle(document.body).paddingLeft),
                      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
                      lit, word, search: q('input[name=q][type=search]').length, searchForm: !!document.querySelector('form[action="/search/"]'),
                      oldRail: q('.llf-rail').length, h1: q('h1').length
                    };
                }""")
                if resp is None or (resp.status >= 400 and path != "/404.html"):
                    fail(f"HTTP {resp.status if resp else 'none'}")
                if info["roots"] != 1: fail(f"{info['roots']} shell roots")
                if info["rails"] != 1: fail(f"{info['rails']} rails")
                if info["bars"] != 1 or info["sheets"] != 1: fail(f"{info['bars']} mobile bars, {info['sheets']} sheets")
                if info["oldRail"] != 1: fail(f"{info['oldRail']} elements with class llf-rail (a second rail?)")
                if info["search"] < 2 or not info["searchForm"]: fail("global search missing")
                if w >= 901:
                    if not info["railVisible"] or info["railPos"] != "fixed": fail(f"desktop rail not visible and fixed (visible={info['railVisible']}, position={info['railPos']})")
                    if info["barVisible"]: fail("mobile bar visible on desktop")
                    if info["railRect"] and abs(info["railRect"]["width"] - 236) > 1: fail(f"rail width {info['railRect']['width']}")
                    if info["mainLeft"] is not None and info["mainLeft"] < 235: fail(f"content overlaps the rail (main left {info['mainLeft']})")
                else:
                    if info["railVisible"]: fail("rail visible on mobile")
                    if not info["barVisible"] or info["barPos"] != "fixed": fail("mobile bar not visible and fixed")
                if info["scrollW"] > info["clientW"] + 1: fail(f"horizontal scroll ({info['scrollW']} > {info['clientW']})")
                want = [mode.capitalize().lower()] if mode else []
                lit = sorted(set(info["lit"]))
                if lit != want: fail(f"lit mode {lit}, expected {want}")
                if info["word"] != mode: fail(f"body data-format {info['word']!r}, expected {mode!r}")
                # fixed on scroll (desktop) and mobile bar stays on screen
                page.evaluate("window.scrollTo(0, 800)")
                page.wait_for_timeout(80)
                sel = "#llf-rail" if w >= 901 else ".mobile-bar"
                top = page.evaluate("s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.top, r.left]; }", sel)
                if abs(top[0]) > 1: fail(f"shell moved on scroll (top {top[0]})")
                page.evaluate("window.scrollTo(0, 0)")
                if errs: fail("console errors: " + "; ".join(errs[:3]))
                checks += 1
                if w in (1440, 390) and args.shots and any(path == p for p, _ in SHOTS):
                    out = Path(args.shots); out.mkdir(parents=True, exist_ok=True)
                    name = dict(SHOTS)[path]
                    kind = "desktop" if w >= 901 else "mobile"
                    page.screenshot(path=str(out / f"{name}-{kind}.png"))
                    page.screenshot(path=str(out / f"{name}-{kind}-full.png"), full_page=True)
                page.close()
            # interaction checks once per width on the article
            page = ctx.new_page()
            page.goto(base + "/learn/pennsylvania-governor-poll-party-market-2026/", wait_until="load")
            page.wait_for_timeout(150)
            page.keyboard.press("/")
            focused = page.evaluate("document.activeElement && document.activeElement.id")
            want = "llf-site-search" if w >= 901 else "llf-mobile-search"
            if focused != want: fails.append(f"{w}px: '/' focused {focused!r}, expected {want!r}")
            page.keyboard.type("/x")
            val = page.evaluate("document.activeElement.value")
            if val != "/x": fails.append(f"{w}px: '/' was captured while typing in a field (value {val!r})")
            if w < 901:
                if not page.evaluate("document.getElementById('explore-sheet').open"): fails.append(f"{w}px: Explore sheet did not open with '/'")
                page.keyboard.press("Escape")          # first Escape clears a search field in most browsers; the next closes the dialog
                if page.evaluate("document.getElementById('explore-sheet').open"): page.keyboard.press("Escape")
                if page.evaluate("document.getElementById('explore-sheet').open"): fails.append(f"{w}px: Escape did not close the Explore sheet")
            page.close()
            ctx.close()
        browser.close()
    srv.shutdown()
    print(f"{checks} page checks at {len(widths)} widths; {len(fails)} failure(s)")
    for f in fails[:80]:
        print("FAIL", f)
    if args.json:
        Path(args.json).write_text(json.dumps({"checks": checks, "widths": widths, "failures": fails}, indent=1), encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
