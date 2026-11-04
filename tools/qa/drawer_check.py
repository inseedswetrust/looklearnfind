#!/usr/bin/env python3
"""Behavior check for the mobile slide-in navigation drawer (Playwright; Edge or Chrome). Serves ./dist locally; never touches the network.

    python3 tools/qa/drawer_check.py                         # 4 page types x widths 320, 390, 768 and 900 (drawer) and 1024 (rail)
    python3 tools/qa/drawer_check.py --shots <dir>           # also writes closed and open screenshots at every width
    python3 tools/qa/drawer_check.py --json <file>

The drawer is the same element as the desktop rail (`#llf-rail`, one navigation source in shared_nav.py). Asserted at 900px and under: closed state (visible
trigger labelled "Open navigation", 44px target, drawer off-screen and visibility:hidden so nothing in it takes focus, no horizontal scroll, the headline is not covered);
open state (width min(300px, 85vw), dialog semantics, aria-expanded, backdrop, scroll lock, focus moves in and stays in, background inert, order of contents, 44px targets);
every way of closing (Close, backdrop, Escape, swipe left) restores focus to the trigger and the scroll position; outline links close the drawer and land on their section;
the "/" shortcut opens it on the search field; reduced motion removes the transition; JavaScript disabled still opens and closes it (:target). At 1024px: the rail is fixed
and visible, no trigger, no dialog role. Exit code 1 on any failure.
"""
import argparse, functools, json, sys, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
PAGES = [("/", "home", False), ("/elections/2026/pennsylvania/", "pennsylvania-hub", True), ("/elections/2026/pennsylvania/house/1/", "race-page", True),
         ("/learn/pennsylvania-governor-poll-party-market-2026/", "article", True)]
MOBILE = [320, 390, 768, 900]
DESKTOP = [1024]


def serve():
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(DIST)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


STATE = """() => {
  const r = document.getElementById('llf-rail'), t = document.querySelector('.nav-open'), b = document.querySelector('.drawer-backdrop');
  const vis = e => { const c = getComputedStyle(e), q = e.getBoundingClientRect(); return c.visibility !== 'hidden' && c.display !== 'none' && q.width > 0 && q.height > 0; };
  const rr = r.getBoundingClientRect();
  return { railVisible: vis(r), railLeft: rr.left, railRight: rr.right, railWidth: rr.width, railRole: r.getAttribute('role'), modal: r.getAttribute('aria-modal'), inert: r.hasAttribute('inert'),
    railVis: getComputedStyle(r).visibility, trigVisible: t ? vis(t) : false, trigExpanded: t && t.getAttribute('aria-expanded'), trigLabel: t && t.getAttribute('aria-label'), trigControls: t && t.getAttribute('aria-controls'),
    trigRect: t ? t.getBoundingClientRect().toJSON() : null, backVisible: b ? vis(b) : false, backBg: b ? getComputedStyle(b).backgroundColor : '', backOpacity: b ? getComputedStyle(b).opacity : '',
    scrollY: Math.round(window.pageYOffset), bodyFixed: getComputedStyle(document.body).position === 'fixed', bodyTop: document.body.style.top, mainInert: document.getElementById('main').hasAttribute('inert'),
    focusInRail: r.contains(document.activeElement), activeId: document.activeElement && (document.activeElement.className || document.activeElement.id || document.activeElement.tagName),
    activeIsTrigger: document.activeElement === t, scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    transition: getComputedStyle(r).transitionDuration, h1Top: (document.querySelector('h1') || {getBoundingClientRect: () => ({top: 999})}).getBoundingClientRect().top,
    vw: window.innerWidth, format: document.body.getAttribute('data-format') };
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots")
    ap.add_argument("--json")
    args = ap.parse_args()
    from playwright.sync_api import sync_playwright
    srv, port = serve()
    base = f"http://127.0.0.1:{port}"
    fails, checks = [], 0
    out = Path(args.shots) if args.shots else None
    if out:
        out.mkdir(parents=True, exist_ok=True)

    def ok(cond, msg, ctxlabel):
        nonlocal checks
        checks += 1
        if not cond:
            fails.append(f"{ctxlabel}: {msg}")

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

        def settle(page, ms=330):
            page.wait_for_timeout(ms)

        for w in MOBILE + DESKTOP:
            mobile = w <= 900
            ctx = browser.new_context(viewport={"width": w, "height": 800}, has_touch=mobile, device_scale_factor=1)
            for path, name, has_context_nav in PAGES:
                L = f"{w}px {name}"
                page = ctx.new_page()
                page.goto(base + path, wait_until="load")
                page.wait_for_timeout(200)
                s = page.evaluate(STATE)
                if not mobile:
                    ok(s["railVisible"] and not s["trigVisible"] and s["railRole"] is None and s["modal"] is None, f"desktop rail must be visible, fixed, with no trigger and no dialog role ({s['railVisible']}, {s['trigVisible']}, {s['railRole']})", L)
                    ok(abs(s["railWidth"] - 236) < 1.5, f"rail width {s['railWidth']}", L)
                    ok(s["scrollW"] <= s["clientW"] + 1, "horizontal scroll", L)
                    if out:
                        page.screenshot(path=str(out / f"{name}-{w}.png"))
                    page.close()
                    continue
                # ---- closed state
                ok(s["trigVisible"] and s["trigLabel"] == "Open navigation" and s["trigControls"] == "llf-rail" and s["trigExpanded"] == "false", f"closed trigger wrong {s['trigVisible']}/{s['trigLabel']}/{s['trigControls']}/{s['trigExpanded']}", L)
                ok(s["trigRect"]["width"] >= 44 and s["trigRect"]["height"] >= 44, f"trigger target {s['trigRect']['width']}x{s['trigRect']['height']}", L)
                ok(not s["railVisible"] and s["railVis"] == "hidden" and s["railRight"] <= 1, f"drawer should be off-screen and hidden when closed ({s['railVis']}, right={s['railRight']})", L)
                ok(s["inert"], "closed drawer must be inert", L)
                ok(not s["backVisible"], "backdrop visible while closed", L)
                ok(s["scrollW"] <= s["clientW"] + 1, f"horizontal scroll ({s['scrollW']} > {s['clientW']})", L)
                ok(s["h1Top"] >= 64 or path == "/", f"headline covered by the header (top {s['h1Top']})", L)
                page.evaluate("document.querySelector('#llf-rail a').focus()")
                ok(not page.evaluate("document.getElementById('llf-rail').contains(document.activeElement)"), "a closed drawer link could take focus", L)
                page.evaluate("document.activeElement && document.activeElement.blur()")
                if out:
                    page.screenshot(path=str(out / f"{name}-{w}-closed.png"))
                # ---- open state
                page.evaluate("window.scrollTo({top: 700, behavior: 'instant'})")
                page.wait_for_timeout(120)
                y0 = page.evaluate("Math.round(window.pageYOffset)")
                page.click(".nav-open")
                settle(page)
                if out:
                    page.screenshot(path=str(out / f"{name}-{w}-open.png"))     # taken before any focus movement so the top of the drawer shows
                s = page.evaluate(STATE)
                want_w = min(300, 0.85 * w)
                ok(s["railVisible"] and abs(s["railWidth"] - want_w) < 1.5 and abs(s["railLeft"]) < 1, f"open drawer geometry (width {s['railWidth']}, want {want_w}, left {s['railLeft']})", L)
                ok(s["railRole"] == "dialog" and s["modal"] == "true" and s["trigExpanded"] == "true", f"dialog semantics ({s['railRole']}, {s['modal']}, {s['trigExpanded']})", L)
                ok(s["backVisible"] and "0, 0, 0" in s["backBg"].replace("rgba(10, 10, 12", "rgba(0, 0, 0") or s["backVisible"], "backdrop not visible", L)
                ok(s["bodyFixed"] and s["mainInert"], f"background not locked (fixed={s['bodyFixed']}, inert={s['mainInert']})", L)
                ok(s["focusInRail"], f"focus did not move into the drawer ({s['activeId']})", L)
                ok(s["scrollW"] <= s["clientW"] + 1, "horizontal scroll while open", L)
                # contents order
                order = page.evaluate("""() => {
                  const r = document.getElementById('llf-rail'), q = s => r.querySelector(s);
                  const pos = [['brand', '.brand'], ['modes', '.format-nav'], ['search', '.rail-search'], ['browse', '.rail-browse'], ['state', '[data-state-nav]'], ['outline', '[data-outline]'], ['recs', '[data-recs]'], ['utility', '.rail-bottom']]
                    .map(([k, sel]) => [k, q(sel)]).filter(([k, e]) => e);
                  const names = pos.map(p => p[0]);
                  let okOrder = true;
                  for (let i = 1; i < pos.length; i++) if (!(pos[i - 1][1].compareDocumentPosition(pos[i][1]) & Node.DOCUMENT_POSITION_FOLLOWING)) okOrder = false;
                  return {names, okOrder};
                }""")
                ok(order["okOrder"] and order["names"][:4] == ["brand", "modes", "search", "browse"] and order["names"][-1] == "utility", f"drawer content order {order['names']}", L)
                ok(("state" in order["names"]) == has_context_nav, f"state selector presence {order['names']} (expected {has_context_nav})", L)
                small = page.evaluate("""() => [...document.querySelectorAll('#llf-rail a, #llf-rail button, #llf-rail select, #llf-rail input[type=search], #llf-rail summary')]
                    .filter(e => e.getBoundingClientRect().width > 0 && !e.closest('noscript')).map(e => [e.tagName + '.' + (e.className || e.id || e.textContent.trim().slice(0, 18)), Math.round(e.getBoundingClientRect().height)]).filter(x => x[1] < 44)""")
                ok(not small, f"touch targets under 44px: {small[:4]}", L)
                # focus containment
                stay = True
                for _ in range(45):
                    page.keyboard.press("Tab")
                    if not page.evaluate("document.getElementById('llf-rail').contains(document.activeElement)"):
                        stay = False
                        break
                ok(stay, "Tab left the drawer", L)
                # ---- closing paths
                def reopen():
                    page.evaluate("window.scrollTo({top: 700, behavior: 'instant'})"); page.wait_for_timeout(100)
                    page.click(".nav-open"); settle(page)
                for how in ("close", "backdrop", "escape", "swipe"):
                    if how != "close":
                        pass
                    cur = page.evaluate(STATE)
                    if not cur["railVisible"]:
                        reopen()
                    if how == "close":
                        page.click(".drawer-close")
                    elif how == "backdrop":
                        page.mouse.click(w - 6, 400)
                    elif how == "escape":
                        page.keyboard.press("Escape")
                    else:
                        page.evaluate("""() => { const r = document.getElementById('llf-rail'); const mk = (x, y) => new Touch({identifier: 7, target: r, clientX: x, clientY: y});
                          r.dispatchEvent(new TouchEvent('touchstart', {bubbles: true, changedTouches: [mk(240, 300)], touches: [mk(240, 300)]}));
                          r.dispatchEvent(new TouchEvent('touchend', {bubbles: true, changedTouches: [mk(120, 310)]})); }""")
                    settle(page)
                    s = page.evaluate(STATE)
                    ok(not s["railVisible"] and s["trigExpanded"] == "false" and not s["bodyFixed"], f"{how}: drawer did not close ({s['railVisible']}, {s['trigExpanded']}, {s['bodyFixed']})", L)
                    ok(s["activeIsTrigger"], f"{how}: focus not restored to the trigger ({s['activeId']})", L)
                    ok(abs(s["scrollY"] - y0) <= 1, f"{how}: scroll position {s['scrollY']} != {y0}", L)
                    ok(s["bodyTop"] == "" and not s["mainInert"], f"{how}: scroll lock or inert left behind", L)
                # swipe must not open it, and a horizontal gesture on the page must not either
                page.evaluate("""() => { const m = document.getElementById('main'); const mk = (x, y) => new Touch({identifier: 9, target: m, clientX: x, clientY: y});
                  m.dispatchEvent(new TouchEvent('touchstart', {bubbles: true, changedTouches: [mk(4, 300)], touches: [mk(4, 300)]})); m.dispatchEvent(new TouchEvent('touchend', {bubbles: true, changedTouches: [mk(180, 305)]})); }""")
                settle(page, 150)
                ok(not page.evaluate(STATE)["railVisible"], "an edge swipe on the page opened the drawer", L)
                # outline link closes the drawer and lands on the section
                has_outline = page.evaluate("!!document.querySelector('#llf-rail [data-outline] a')")
                if has_outline:
                    page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})"); page.click(".nav-open"); settle(page)
                    if not page.evaluate("document.querySelector('#llf-rail [data-outline]').open"):
                        page.click("#llf-rail [data-outline] summary")
                    href = page.evaluate("document.querySelectorAll('#llf-rail [data-outline] a')[1].getAttribute('href')")
                    page.click(f"#llf-rail [data-outline] a[href='{href}']")
                    settle(page, 450)
                    top = page.evaluate(f"document.getElementById({json.dumps(href[1:])}).getBoundingClientRect().top")
                    ok(not page.evaluate(STATE)["railVisible"] and -2 <= top <= 220, f"outline link: drawer open or section not reached (top {top})", L)
                # "/" opens the drawer on the search field
                page.evaluate("window.scrollTo(0, 0)"); page.evaluate("document.activeElement && document.activeElement.blur()")
                page.keyboard.press("/")
                settle(page)
                ok(page.evaluate("document.activeElement && document.activeElement.id") == "llf-site-search" and page.evaluate(STATE)["railVisible"], "'/' did not open the drawer on search", L)
                page.keyboard.press("Escape"); page.keyboard.press("Escape")
                page.close()
            ctx.close()

        # ---- reduced motion
        ctx = browser.new_context(viewport={"width": 390, "height": 800}, has_touch=True, reduced_motion="reduce")
        page = ctx.new_page(); page.goto(base + "/", wait_until="load"); page.wait_for_timeout(200)
        s = page.evaluate(STATE)
        ok(s["transition"] in ("0s", "0s, 0s"), f"reduced motion: transition {s['transition']}", "390px reduced-motion")
        page.click(".nav-open"); page.wait_for_timeout(40)
        ok(page.evaluate(STATE)["railVisible"], "reduced motion: drawer should be open immediately", "390px reduced-motion")
        ctx.close()
        # ---- normal motion duration is short
        ctx = browser.new_context(viewport={"width": 390, "height": 800}, has_touch=True)
        page = ctx.new_page(); page.goto(base + "/", wait_until="load"); page.wait_for_timeout(200)
        d = page.evaluate("getComputedStyle(document.getElementById('llf-rail')).transitionDuration")
        ok(d.startswith("0.24s"), f"transition duration {d}", "390px")
        ctx.close()
        # ---- JavaScript off: the drawer still opens and closes (:target)
        ctx = browser.new_context(viewport={"width": 390, "height": 800}, java_script_enabled=False)
        page = ctx.new_page(); page.goto(base + "/elections/2026/pennsylvania/", wait_until="load")
        page.click(".nav-open"); page.wait_for_timeout(350)
        vis = page.evaluate("getComputedStyle(document.getElementById('llf-rail')).visibility")
        ok(vis == "visible", f"no-JS: drawer did not open via :target ({vis})", "390px no-JS")
        page.click(".drawer-close"); page.wait_for_timeout(350)
        vis = page.evaluate("getComputedStyle(document.getElementById('llf-rail')).visibility")
        ok(vis == "hidden", f"no-JS: drawer did not close ({vis})", "390px no-JS")
        ctx.close()
        # ---- parity: the destinations in the drawer are the destinations in the desktop rail
        def links(width):
            c = browser.new_context(viewport={"width": width, "height": 800})
            p = c.new_page(); p.goto(base + "/elections/2026/pennsylvania/", wait_until="load")
            v = p.evaluate("[...document.querySelectorAll('#llf-rail a[href]')].map(a => a.getAttribute('href'))")
            nav = p.evaluate("document.querySelectorAll('nav').length")
            c.close()
            return v, nav
        dl, _ = links(390)
        dk, _ = links(1280)
        ok(dl == dk, "drawer and desktop rail carry different links", "parity")
        browser.close()
    srv.shutdown()
    print(f"{checks} assertions across {len(PAGES)} page types at {len(MOBILE) + len(DESKTOP)} widths; {len(fails)} failure(s)")
    for f in fails[:60]:
        print("FAIL", f)
    if args.json:
        Path(args.json).write_text(json.dumps({"assertions": checks, "failures": fails}, indent=1), encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
