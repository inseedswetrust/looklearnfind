"""LookLearnFind global shell: the one persistent rail, mobile bar and Explore sheet that every generated page receives.

Build-time only (stdlib). `build.shell()` is the single place a page is written, and it calls `render()` here for every page, so
a new page of any type gets the shared navigation with no markup of its own. Nothing in a page template may copy this markup.
Design rules: docs/design/LLF_GLOBAL_SHELL.md. Enforced by `check_pages()` (strict build) and tests/test_global_shell.py.

Contract that tests rely on:
  - exactly one element with `data-llf-global-shell` and `data-llf-nav-version="1"` per page
  - exactly one rail (`id="llf-rail"`), one mobile bar and one Explore sheet inside it
  - the active LOOK / LEARN / FIND word comes from the page model (`page_mode`), never from the section being browsed
"""
import html
import re

import sidebar

NAV_VERSION = "1"
e = html.escape

# Route to mode matrix (docs/design/LLF_GLOBAL_SHELL.md). Modes are editorial state, not politics sections.
# Order matters: first match wins. "" means no word is lit (neutral pages: home, categories, topics, about, legal, search, errors).
MODE_ROUTES = (
    ("/look/", "look"), ("/u/", "look"),
    ("/find/", "find"),
    ("/learn/", "learn"), ("/elections/", "learn"),
)
# Pages where the contextual state picker is relevant. The rest of the rail is identical on every page.
STATE_CONTEXT_PREFIXES = ("/politics/", "/elections/", "/find/candidates/")
BROWSE_EXCLUDE = {"look", "find", "about"}      # modes and About are not part of the Browse list


def page_mode(path, override=None):
    if override is not None:
        return override
    for prefix, mode in MODE_ROUTES:
        if path.startswith(prefix):
            return mode
    return ""


def wants_state_picker(path, nav):
    return nav == "politics" or path.startswith(STATE_CONTEXT_PREFIXES)


def state_slug_from_path(path):
    m = re.match(r"^/elections/2026/([a-z-]+)/", path)
    return m.group(1) if m else ""


def _brand(cls="brand-large"):
    """The original logo artwork plus one masked word per mode. Word classes are prefixed (w-look) because bare `.find` and `.look` are already page-level
    class names (the homepage Find section), and a bare class here would inherit their padding and backgrounds."""
    return (f'<a class="brand {cls}" href="/" aria-label="LookLearnFind home"><img class="brand-fallback" src="/img/logo-cream.png" alt="LOOK LEARN FIND 01" width="1040" height="701">'
            '<span class="word w-look" aria-hidden="true"></span><span class="word w-learn" aria-hidden="true"></span><span class="word w-find" aria-hidden="true"></span></a>')


def _browse(site_nav, active, cls="rail-browse", label="Browse"):
    links = "".join(
        f'<a href="{e(n["href"])}"' + (' aria-current="page"' if n["key"] == active else "") + f'>{e(n["label"])}</a>'
        for n in site_nav if n["key"] not in BROWSE_EXCLUDE)
    return f'<nav class="{cls}" aria-label="{label}"><div class="eyebrow">Browse</div>{links}</nav>'


def _search(input_id):
    return (f'<form class="rail-search" action="/search/" method="get" role="search"><label class="eyebrow" for="{input_id}">Search LookLearnFind</label>'
            f'<div class="search-control"><span aria-hidden="true">&#8981;</span><input id="{input_id}" name="q" type="search" placeholder="Search stories, people" autocomplete="off"></div></form>')


def _state_picker(prefix, path, hubs, states):
    cur = state_slug_from_path(path)
    opts = '<option value="">Choose a state</option>' + "".join(
        f'<option value="{e(h["url"])}"' + (" selected" if cur and h["url"].rstrip("/").endswith("/" + cur) else "") + f'>{e(states[c])}</option>'
        for c, h in hubs.items())
    links = "".join(f'<li><a href="{e(h["url"])}">{e(states[c])}</a></li>' for c, h in hubs.items())
    return (f'<div class="state-form state-nav" data-state-nav hidden><label class="eyebrow" for="{prefix}-state-nav">Explore a state</label>'
            f'<div class="select-wrap"><select id="{prefix}-state-nav" data-state-nav-select aria-label="Choose a state election hub">{opts}</select><span aria-hidden="true">&#8964;</span></div></div>'
            f'<noscript><details class="state-fallback"><summary>State coverage</summary><ul>{links}</ul></details></noscript>')


def _outline(toc, prefix):
    """`On this page` from real headings only. Suppressed when there is nothing to navigate."""
    if not toc or len(toc) < 2:
        return ""
    items = "".join(f'<li><a href="#{e(a)}">{e(t)}</a></li>' for a, t in toc)
    op = " open" if len(toc) <= 4 else ""
    return (f'<details class="outline" data-outline{op}><summary class="eyebrow">On this page<span class="cur" data-outline-cur></span></summary><ol>{items}</ol></details>')


def render(*, path, site_nav, active, mode, hubs, states, article=None, toc=None):
    """Return (shell_html, discovery_data_or_None).

    article = (cur_item, catalog) for a story page: the rail's context block then carries the state lens and recommendations.
    Every other page gets the contextual state picker (political pages only) and an outline built from its own headings.
    """
    data = None
    ctx_attr = ""
    if article:
        cur, cat = article
        lens = cat.default_lens(cur)
        result = cat.select(cur, lens)
        data = cat.all_results(cur)
        ctx_attr = f' data-context="{e(cur["id"])}" data-default-lens="{lens}"'
        rail_ctx = sidebar.panel(cur, result, lens, toc, "rail")
        sheet_ctx = sidebar.panel(cur, result, lens, toc, "sheet")
    else:
        pick = lambda p: _state_picker(p, path, hubs, states) if wants_state_picker(path, active) else ""
        rail_ctx = pick("rail") + _outline(toc, "rail")
        sheet_ctx = pick("sheet") + _outline(toc, "sheet")
    brand_l, brand_s = _brand(), _brand("brand-small")
    fnav, mnav = sidebar._format_nav(mode), sidebar._format_nav(mode, "format-nav mobile-formats", "Formats")
    shell = (
        f'<div class="llf-shell" data-llf-global-shell data-llf-nav-version="{NAV_VERSION}" data-mode="{e(mode)}">'
        f'<aside class="llf-rail" id="llf-rail" aria-label="LookLearnFind navigation"{ctx_attr}><div class="rail-scroll">{brand_l}{fnav}{_search("llf-site-search")}'
        f'{_browse(site_nav, active)}<div class="rail-context">{rail_ctx}</div>'
        '<div class="rail-bottom"><a href="/about/">About</a><a href="/contribute/">Contribute</a><a href="/about/corrections/">Corrections</a></div></div></aside>'
        f'<div class="mobile-bar" role="region" aria-label="LookLearnFind">{brand_s}{mnav}<button type="button" class="explore-btn" data-explore aria-haspopup="dialog">Explore</button></div>'
        '<dialog class="explore-sheet" id="explore-sheet" aria-labelledby="explore-title"><div class="dialog-top"><h2 id="explore-title">Explore</h2><button type="button" data-close-sheet>Close</button></div>'
        f'<div class="sheet-body">{_search("llf-mobile-search")}{_browse(site_nav, active, "rail-browse sheet-browse", "Browse sections")}'
        '<nav class="sheet-more" aria-label="More"><a href="/look/">Look</a><a href="/find/">Find</a><a href="/about/">About</a><a href="/account/">Sign in</a></nav>'
        f'<div class="rail-context">{sheet_ctx}</div></div></dialog></div>')
    return shell, data


def check_pages(pages):
    """Strict-build assertion: every generated HTML page carries exactly one shared shell. Returns a list of problems."""
    bad = []
    for path, h in pages.items():
        n = h.count("data-llf-global-shell")
        if n != 1:
            bad.append(f"{path}: {n} shared shell roots (expected 1)")
            continue
        if h.count(f'data-llf-nav-version="{NAV_VERSION}"') != 1:
            bad.append(f"{path}: shell version attribute missing or duplicated")
        if h.count('id="llf-rail"') != 1:
            bad.append(f"{path}: expected exactly one rail")
        if h.count('class="mobile-bar"') != 1 or h.count('id="explore-sheet"') != 1:
            bad.append(f"{path}: expected exactly one mobile bar and one Explore sheet")
        if h.count('name="q"') < 2 or 'action="/search/"' not in h:
            bad.append(f"{path}: global search missing")
    return bad
