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


def toc_from_body(body):
    """Outline entries for the rail, from the page's own navigation. Prefers the page's in-content `On this page` list (so the rail can replace it),
    then real `<h2 id>` headings. Returns [(anchor, text)]; empty when there is nothing to navigate."""
    m = re.search(r'<nav class="onpage"[^>]*>(.*?)</nav>', body, re.S)
    if m:
        items = [(a, re.sub(r"<[^>]+>", "", t).strip()) for a, t in re.findall(r'<a href="#([A-Za-z0-9_-]+)"[^>]*>(.*?)</a>', m.group(1), re.S)]
        if len(items) >= 2:
            return items
    found = []
    for attrs, inner in re.findall(r"<h2([^>]*)>(.*?)</h2>", body, re.S):
        m = re.search(r'\sid="([A-Za-z0-9_-]+)"', attrs)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", inner)).strip()
        if m and text and m.group(1) not in ("explore-title",):
            found.append((m.group(1), text))
    return found


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
            f'<div class="search-control"><span aria-hidden="true">&#8981;</span><input id="{input_id}" name="q" type="search" placeholder="Search the archive" autocomplete="off"></div></form>')


def _state_picker(prefix, path, hubs, states):
    cur = state_slug_from_path(path)
    opts = '<option value="">Choose a state</option>' + "".join(
        f'<option value="{e(h["url"])}"' + (" selected" if cur and h["url"].rstrip("/").endswith("/" + cur) else "") + f'>{e(states[c])}</option>'
        for c, h in hubs.items())
    links = "".join(f'<li><a href="{e(h["url"])}">{e(states[c])}</a></li>' for c, h in hubs.items())
    return (f'<div class="state-form state-nav" data-state-nav hidden><label class="eyebrow" for="{prefix}-state-nav">Explore a state</label>'
            f'<div class="select-wrap"><select id="{prefix}-state-nav" data-state-nav-select aria-label="Choose a state election hub">{opts}</select><span aria-hidden="true">&#8964;</span></div></div>'
            f'<noscript><details class="state-fallback"><summary>State coverage</summary><ul>{links}</ul></details></noscript>')


def _outline(toc, prefix, is_open=False):
    """`On this page` from real headings only. Suppressed when there is nothing to navigate."""
    if not toc or len(toc) < 2:
        return ""
    items = "".join(f'<li><a href="#{e(a)}">{e(t)}</a></li>' for a, t in toc)
    op = " open" if (is_open or len(toc) <= 4) else ""
    return (f'<details class="outline" data-outline{op}><summary class="eyebrow">On this page<span class="cur" data-outline-cur></span></summary><ol>{items}</ol></details>')


def ensure_heading_ids(body):
    """Stable section ids from the page generators: every `<h2>` without an id gets one from its text (lowercase words joined by hyphens, at most 48 characters,
    unique on the page). Ids already present are never changed. Used for election pages so the rail outline always has anchors."""
    used = set(re.findall(r'\sid="([^"]+)"', body))

    def add(m):
        attrs, inner = m.group(1), m.group(2)
        if re.search(r'\sid="', attrs):
            return m.group(0)
        words = re.findall(r"[a-z0-9]+", re.sub(r"<[^>]+>", " ", html.unescape(inner)).lower())
        slug = "-".join(words)[:48].rstrip("-") or "section"
        base, n = slug, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        return f'<h2{attrs} id="{slug}">{inner}</h2>'
    return re.sub(r"<h2([^>]*)>(.*?)</h2>", add, body, flags=re.S)


def _story_context(cur, toc):
    """Context block for a story when no recommendation is current: parent link and subject, state picker, outline, source link. No suggestions are shown."""
    sub = f'<div class="context-nav"><a href="/politics/"><span aria-hidden="true">&#8592;</span> Politics</a><p>{e(cur["subject"])}</p></div>'
    return sub


def render(*, path, site_nav, active, mode, hubs, states, article=None, toc=None):
    """Return (shell_html, discovery_data_or_None).

    One element is both the desktop rail and the mobile drawer (`#llf-rail`): the same markup, links and context, restyled by CSS and opened by the menu trigger on
    small screens. There is no second navigation structure.
    article = (cur_item, catalog) for a story page. While `sidebar.recommendations_current()` is false the story gets the state picker and outline only (no
    suggestions); when it is true the context block carries the state lens and the current recommendations.
    """
    data = None
    ctx_attr = ""
    picker = _state_picker("rail", path, hubs, states) if wants_state_picker(path, active) else ""
    if article:
        cur, cat = article
        data = cat.all_results(cur)
        if sidebar.recommendations_current():
            lens = cat.default_lens(cur)
            result = cat.select(cur, lens)
            ctx_attr = f' data-context="{e(cur["id"])}" data-default-lens="{lens}"'
            ctx = sidebar.panel(cur, result, lens, toc, "rail").replace('<details class="outline" data-outline>', '<details class="outline" data-outline open>')
        else:
            ctx = (picker + _story_context(cur, toc) + _outline(toc, "rail", is_open=True)
                   + '<a class="source-link" href="#sources"><span>Go to the source</span><span aria-hidden="true">&#8594;</span></a>')
    else:
        ctx = picker + _outline(toc, "rail", is_open=True)
    brand_l, brand_s = _brand(), _brand("brand-small")
    fnav = sidebar._format_nav(mode)
    shell = (
        f'<div class="llf-shell" data-llf-global-shell data-llf-nav-version="{NAV_VERSION}" data-mode="{e(mode)}">'
        f'<aside class="llf-rail" id="llf-rail" aria-label="LookLearnFind navigation"{ctx_attr}><div class="rail-scroll">'
        f'<div class="rail-head">{brand_l}<a class="drawer-close" href="#main" aria-label="Close navigation"><span aria-hidden="true">&#215;</span><span class="dc-label">Close</span></a></div>'
        f'{fnav}{_search("llf-site-search")}{_browse(site_nav, active)}<div class="rail-context">{ctx}</div>'
        '<div class="rail-bottom"><a href="/about/">About</a><a href="/contribute/">Contribute</a><a href="/about/corrections/">Corrections</a><a class="only-mobile" href="/account/">Sign in</a></div>'
        '</div></aside>'
        '<a class="drawer-backdrop" href="#main" tabindex="-1" aria-hidden="true"></a>'
        f'<div class="mobile-bar" role="region" aria-label="LookLearnFind">{brand_s}'
        '<a class="nav-open" href="#llf-rail" role="button" aria-controls="llf-rail" aria-expanded="false" aria-label="Open navigation"><span class="burger" aria-hidden="true"></span></a></div></div>')
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
            bad.append(f"{path}: expected exactly one rail/drawer")
        if h.count('class="mobile-bar"') != 1 or h.count('class="nav-open"') != 1 or 'aria-controls="llf-rail"' not in h:
            bad.append(f"{path}: expected exactly one mobile bar with a menu trigger that controls the rail")
        if 'id="explore-sheet"' in h or "<dialog" in h.split("</header>")[0]:
            bad.append(f"{path}: the old Explore sheet must not be rendered (the rail is the drawer)")
        if h.count('type="search"') < 1 or 'action="/search/"' not in h or 'id="llf-site-search"' not in h:
            bad.append(f"{path}: global search missing")
        mast = re.search(r'<header class="mast[^"]*">.*?</header>', h, re.S)
        if not mast or 'class="menu-btn"' in mast.group(0) or re.findall(r'href="([^"]+)"', re.search(r'<nav class="nav".*?</nav>', mast.group(0), re.S).group(0)) != ["/search/", "/account/"]:
            bad.append(f"{path}: the mast must carry only search and account (the rail is the primary navigation)")
    return bad
