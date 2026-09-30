#!/usr/bin/env python3
"""LookLearnFind static site builder. Stdlib only.

    python3 build.py          # writes ./dist
    python3 build.py --zip    # also writes release/looklearnfind-site.zip

Sources
  content/*.html         plain pages          (front matter: title, description, path, nav)
  content/learn/*.html   stories  (kind: story)   -> /learn/<slug>/
  content/find/*.html    finds    (kind: find)    -> /find/<type>/<slug>/
  data/site.json         nav, categories, topics, find types
  data/threads.json      curated threads (editors edit this file; proposals live in the database)
  static/                copied as-is (css, js, img, api/ PHP backend, .htaccess)
See docs/ for the brand guide, sitemap and nexus design.
"""
import json, re, shutil, sys, datetime
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent
OUT = ROOT / "dist"
CFG = json.loads((ROOT / "config.json").read_text())
SITE = json.loads((ROOT / "data" / "site.json").read_text())
THREADS = json.loads((ROOT / "data" / "threads.json").read_text())

CATS = {c["slug"]: c for c in SITE["categories"]}
TOPICS = {t["slug"]: t for t in SITE["topics"]}
TOPIC_ORDER = [t["slug"] for t in SITE["topics"]]
TTYPES = {t["slug"]: t for t in SITE["find_types"]}
TTYPE_BY_TYPE = {t["type"]: t for t in SITE["find_types"]}
TH = {t["slug"]: t for t in THREADS}
VERB = {"candidate": "vote", "business": "visit", "guide": "try", "product": "buy", "place": "visit"}
IMG = {
    "politics-forum": "/img/politics-forum.jpg", "politics-vote": "/img/politics-vote.jpg",
    "economy-shop": "/img/economy-shop.jpg", "everyday-cooking": "/img/everyday-cooking.jpg",
    "everyday-home": "/img/everyday-home.jpg", "everyday-workout": "/img/everyday-workout.jpg",
}
e = lambda s: escape(str(s), quote=True)


# ---------------------------------------------------------------- parsing
def split_front(text, path):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2)


def lst(v):
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def take_block(body, name):
    m = re.search(r"<!--" + name + r"\n(.*?)\n-->", body, re.S)
    if not m:
        return None, body
    return m.group(1), body.replace(m.group(0), "")


def kv_block(text):
    d = {}
    for line in (text or "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def bullets(text):
    return [l[1:].strip() for l in (text or "").splitlines() if l.strip().startswith("-")]


def fmt_date(s):
    try:
        return datetime.date.fromisoformat(s).strftime("%b %-d, %Y")
    except Exception:
        return s or ""


# ---------------------------------------------------------------- content model
STORIES, FINDS, PAGES = [], [], []


def load_content():
    for src in sorted((ROOT / "content").rglob("*.html")):
        meta, body = split_front(src.read_text(), src)
        kind = meta.get("kind", "page")
        meta["_src"] = src
        if kind == "story":
            meta["slug"] = src.stem
            meta["path"] = f"/learn/{src.stem}/"
            meta["threads"] = lst(meta.get("threads"))
            meta["topics"] = lst(meta.get("topics"))
            meta["_body"] = body
            STORIES.append(meta)
        elif kind == "find":
            meta["slug"] = src.stem
            t = TTYPE_BY_TYPE[meta["type"]]
            meta["path"] = f"/find/{t['slug']}/{src.stem}/"
            meta["threads"] = lst(meta.get("threads"))
            meta["topics"] = lst(meta.get("topics"))
            meta["_body"] = body
            FINDS.append(meta)
        else:
            meta["_body"] = body
            PAGES.append(meta)
    STORIES.sort(key=lambda m: m.get("date", ""), reverse=True)
    FINDS.sort(key=lambda m: m.get("added", ""), reverse=True)
    for t in THREADS:
        for k in ("aliases", "topics", "related"):
            t.setdefault(k, [])


STORY_BY = {}
FIND_BY = {}


def index_content():
    for s in STORIES:
        STORY_BY[s["slug"]] = s
    for f in FINDS:
        FIND_BY[f["slug"]] = f
    # find <- story backrefs from [[find:slug]] macros and "finds:" front matter
    for f in FINDS:
        f["came_from"] = []
    for s in STORIES:
        refs = lst(s.get("finds")) + re.findall(r"\[\[find:([a-z0-9-]+)\]\]", s["_body"])
        s["_finds"] = list(dict.fromkeys(r for r in refs if r in FIND_BY))
        for r in s["_finds"]:
            FIND_BY[r]["came_from"].append(s["slug"])


# ---------------------------------------------------------------- html helpers
def icon(slug):
    return f'<svg aria-hidden="true" focusable="false"><use href="/img/topic-icons.svg#{slug}"/></svg>'


def thread_chip(slug):
    t = TH.get(slug)
    return f'<a class="thread-chip" href="/threads/{e(slug)}/">{e(t["title"] if t else slug)}</a>'


def thread_chips(slugs):
    slugs = [s for s in slugs if s in TH]
    if not slugs:
        return ""
    return '<div class="thread-chips" aria-label="Threads">' + "".join(thread_chip(s) for s in slugs) + "</div>"


def cat_label(slug):
    return CATS[slug]["label"] if slug in CATS else ""


def kind_label(item):
    if item.get("kind") == "story":
        return item.get("format", "Story")
    return TTYPE_BY_TYPE[item["type"]]["label"][:-1] if item.get("kind") == "find" else ""


def card(item, plain=False):
    if item["kind"] == "story":
        eyebrow = " / ".join(x for x in [cat_label(item.get("category", "")), item.get("format", "Story")] if x)
    else:
        eyebrow = f"Find / {TTYPE_BY_TYPE[item['type']]['label'][:-1]}"
    img = IMG.get(item.get("image", ""), "")
    pic = f'<div class="pic" style="background-image:url({img})" role="img" aria-label="{e(item.get("image_alt", ""))}"></div>' if img and not plain else ""
    ill = '<div class="kindline">Illustrative sample</div>' if item.get("illustrative") == "yes" else ""
    return (f'<a class="card" href="{item["path"]}">{pic}<div class="eyebrow">{e(eyebrow)}</div>'
            f'<h3>{e(item["title"])}</h3><p>{e(item.get("dek", ""))}</p>{ill}</a>')


def cards(items, cls="", plain=False):
    return f'<div class="cards {cls}">' + "".join(card(i, plain) for i in items) + "</div>"


def find_rows(items):
    out = []
    for i, f in enumerate(items, 1):
        out.append(f'<a class="row" href="{f["path"]}"><span class="n">{i:02d}</span><span class="t">{e(f["title"])}</span>'
                   f'<span class="d">{e(f.get("dek", ""))}</span><span class="ar">↗</span></a>')
    return '<div class="rows">' + "".join(out) + "</div>"


def look_shelf(params, heading="What people are saving", lab="Look", note=""):
    """Live Ledger shelf, filled by /js/shelf.js from /api/ledger/list. Falls back to an honest empty state."""
    attrs = " ".join(f'data-{k}="{e(v)}"' for k, v in params.items())
    return f'''<section class="shelf look" data-look-shelf {attrs}>
<div class="wrap"><div class="shelf-head"><div><div class="lab">{e(lab)} · Ledger</div><h2>{e(heading)}</h2></div>
<a class="link teal" href="/look/?{"&".join(f"{k}={e(v)}" for k, v in params.items())}">Open in the Ledger ↗</a></div>
<p class="small" style="max-width:640px;margin:-8px 0 22px">Short videos kept by readers and editors. A save is a recommendation to look, not a verification. {e(note)}</p>
<div data-shelf-body><div class="empty">Loading saved videos…</div></div></div></section>'''


def learn_shelf(stories, heading="What the record shows", empty_q="this"):
    body = cards(stories, "c2" if len(stories) == 2 else "") if stories else (
        f'<div class="empty"><b>We have not looked into {e(empty_q)} yet.</b> If you have an original source, a record, or a question worth chasing, '
        f'<a href="/contribute/">send it to us</a>.</div>')
    return f'''<section class="shelf"><div class="wrap"><div class="shelf-head"><div><div class="lab">Learn · Reported</div><h2>{e(heading)}</h2></div>
<a class="link teal" href="/learn/">All stories ↗</a></div>{body}</div></section>'''


def find_shelf(finds, heading="Where to try it"):
    body = find_rows(finds) if finds else ('<div class="empty"><b>No real-world Finds for this yet.</b> Know a person, place, or guide that holds up? '
                                            '<a href="/contribute/">Tell us why</a>.</div>')
    return f'''<section class="shelf"><div class="wrap"><div class="shelf-head"><div><div class="lab">Find · Real world</div><h2>{e(heading)}</h2></div>
<a class="link teal" href="/find/">All Finds ↗</a></div>{body}</div></section>'''


def illus_bar():
    return ('<div class="illus"><div class="wrap">Illustrative sample · The text, people and sources on this page are placeholders that show how this page type works. '
            'They are not reporting.</div></div>')


# ---------------------------------------------------------------- page shell
PAGES_OUT = {}     # path -> (html)
SITEMAP = []
SEARCH = []


def nav_html(active):
    out = []
    for n in SITE["nav"]:
        cur = ' aria-current="page"' if n["key"] == active else ""
        out.append(f'<a href="{n["href"]}"{cur}>{e(n["label"])}</a>')
    out.append('<span class="sep"></span><a class="mag" href="/search/" aria-label="Search">⌕</a>')
    out.append('<a class="acct" href="/account/" data-acct>Sign in</a>')
    return "".join(out)


def shell(title, desc, path, body, nav="", css=(), js=(), og=None, noindex=False, illustrative=False, bodyclass="", lead="", sitemap=True, jsonld=""):
    canonical = CFG["url"] + path
    full_title = title if "LookLearnFind" in title else f"{title} | LookLearnFind"
    og_img = CFG["url"] + (og or "/img/og-default.jpg")
    links = "".join(f'<link rel="stylesheet" href="/css/{c}.css?v={CFG["updated"]}">' for c in ("site",) + tuple(css))
    scripts = "".join(f'<script src="/js/{j}.js?v={CFG["updated"]}" defer></script>' for j in ("site",) + tuple(js))
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    foot_nav = "".join(f'<a href="{n["href"]}">{e(n["label"])}</a>' for n in SITE["nav"])
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#1d1d1d">
{robots}
<meta property="og:type" content="website"><meta property="og:site_name" content="LookLearnFind">
<meta property="og:title" content="{e(title.split("|")[0].strip())}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
{links}
{jsonld}
</head>
<body class="{bodyclass}">
<a class="skip" href="#main">Skip to content</a>
<header class="mast"><div class="wrap">
<a class="logo" href="/" aria-label="LookLearnFind home"><img src="/img/logo-01.png" alt="LOOK LEARN FIND 01" width="171" height="126"></a>
<button class="menu-btn" aria-expanded="false" aria-controls="nav">Menu</button>
<nav class="nav" id="nav" aria-label="Main">{nav_html(nav)}</nav>
</div></header>
{illus_bar() if illustrative else ""}
<main id="main">
{body}
</main>
<section class="signup" aria-label="Newsletter"><div class="wrap">
<div><h2>Keep looking.</h2><p>New questions, useful finds, and the sources that made us look twice.</p></div>
<form data-newsletter><label class="sr" for="nl-email">Email</label><input id="nl-email" type="email" name="email" placeholder="Your email" required autocomplete="email"><button type="submit">Sign up ↗</button></form>
<div class="msg" data-newsletter-msg aria-live="polite"></div></div></section>
<footer class="foot"><div class="wrap">
<div class="top"><a class="logo" href="/" aria-label="LookLearnFind home"><img src="/img/logo-01.png" alt="LOOK LEARN FIND 01" width="171" height="126"></a><nav aria-label="Footer">{foot_nav}</nav></div>
<div class="fine"><div><a href="/contribute/">Contribute</a><a href="/about/standards/">Standards</a><a href="/about/corrections/">Corrections</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="/contact/">Contact</a></div>
<div>© LookLearnFind. Interesting ideas. Open receipts.</div></div>
</div></footer>
{scripts}
</body>
</html>
'''
    PAGES_OUT[path] = html
    if sitemap and not noindex:
        SITEMAP.append(path)


def page_head(kicker, title_html, dek="", crumbs=None, extra=""):
    bc = ""
    if crumbs:
        bc = '<div class="breadcrumb">' + " / ".join(f'<a href="{h}">{e(l)}</a>' if h else e(l) for l, h in crumbs) + "</div>"
    d = f'<p class="dek">{dek}</p>' if dek else ""
    return f'<section class="page-head"><div class="wrap">{bc}<div class="kicker">{kicker}<i></i></div><h1 class="display">{title_html}</h1>{d}{extra}</div></section>'


def contribute_band(msg="Bring a question. Bring a source. Tell us what held up."):
    return f'''<section class="band warm"><div class="wrap split"><div><div class="kicker">Contribute<i></i></div><h2 class="h2">{e(msg)}</h2></div>
<div><p class="dek">Send a question, an original source, a video worth keeping, or a report from trying a Find. We credit contributors and explain corrections.</p>
<p style="margin-top:20px"><a class="btn" href="/contribute/">Send something ↗</a></p></div></div></section>'''


# ---------------------------------------------------------------- story + find renderers
def render_story(s):
    body = s["_body"]
    openfile, body = take_block(body, "openfile")
    sources_raw, body = take_block(body, "sources")
    corr_raw, body = take_block(body, "corrections")
    sources = []
    for line in (sources_raw or "").splitlines():
        p = [x.strip() for x in line.split("|")]
        if len(p) >= 6 and p[0].isdigit():
            sources.append(dict(n=int(p[0]), title=p[1], pub=p[2], date=p[3], url=p[4], why=p[5]))
    finds_seen = []

    def fn(m):
        n = int(m.group(1))
        return f'<a class="fn" id="ref-{n}" href="#source-{n}" aria-label="Source {n}">SOURCE {n:02d}</a>'

    def fm(m):
        slug = m.group(1)
        if slug not in FIND_BY:
            return ""
        if slug not in finds_seen:
            finds_seen.append(slug)
        i = finds_seen.index(slug) + 1
        return f'<a class="find-mark" href="{FIND_BY[slug]["path"]}" title="{e(FIND_BY[slug]["title"])}">FIND {i:02d} ↗</a>'

    body = re.sub(r"\[\[s:(\d+)\]\]", fn, body)
    body = re.sub(r"\[\[find:([a-z0-9-]+)\]\]", fm, body)
    of = ""
    if openfile:
        d = kv_block(openfile)
        rows = [("The question", "question"), ("What we checked", "checked"), ("What the sources support", "supported"),
                ("Other views", "other"), ("What remains open", "open")]
        of = '<div class="open-file"><h3>Open file</h3><dl>' + "".join(
            f"<dt>{l}</dt><dd>{d[k]}</dd>" for l, k in rows if d.get(k)) + "</dl></div>"
    src_html = ""
    if sources:
        src_html = '<div class="sources" id="sources"><h2>Sources</h2>' + "".join(
            f'<div class="src" id="source-{x["n"]}"><span class="k">SOURCE {x["n"]:02d}</span><div>'
            f'<span class="ti">' + (f'<a href="{e(x["url"])}" rel="noopener">{e(x["title"])}</a>' if x["url"].startswith("http") else e(x["title"])) +
            ('<span class="ph">Placeholder</span>' if x["url"] in ("-", "") else "") +
            f'</span>{e(x["pub"])} · {e(x["date"])}<div class="why"><b>Why it matters:</b> {e(x["why"])}</div></div></div>'
            for x in sources) + "</div>"
    corr = ""
    if corr_raw:
        corr = '<div class="corrections"><b>Updates and corrections.</b><br>' + "<br>".join(
            f"{e(fmt_date(l.split('|')[0].strip()))} — {e(l.split('|', 1)[1].strip())}" for l in corr_raw.splitlines() if "|" in l) + "</div>"
    else:
        corr = '<div class="corrections"><b>Updates and corrections.</b> None so far. Corrections are logged on the <a href="/about/corrections/">corrections page</a>.</div>'
    finds = [FIND_BY[x] for x in s["_finds"]]
    hero = IMG.get(s.get("image", ""), "")
    hero_html = f'<div class="wrap"><div class="story-hero" style="background-image:url({hero})" role="img" aria-label="{e(s.get("image_alt", ""))}"></div></div>' if hero else ""
    side_finds = ""
    if finds:
        side_finds = '<div class="blk"><h4>Find in the world</h4><ol>' + "".join(
            f'<li><a href="{f["path"]}">{e(f["title"])} ↗</a></li>' for f in finds) + "</ol></div>"
    src_side = ""
    if sources:
        src_side = '<div class="blk"><h4>Sources</h4><ol>' + "".join(
            f'<li><a href="#source-{x["n"]}">SOURCE {x["n"]:02d}</a> — {e(x["title"][:60])}</li>' for x in sources) + "</ol></div>"
    threads_side = ""
    if s["threads"]:
        threads_side = '<div class="blk"><h4>Threads</h4>' + thread_chips(s["threads"]) + "</div>"
    find_mod = ""
    if finds:
        find_mod = f'''<section class="find-module"><div class="wrap"><div class="kicker">Find<i></i></div>
<h2>Try it. Visit it. Meet them.</h2>{find_rows(finds)}
<p class="small" style="color:#b9bdb5;margin-top:18px">Each Find shows why it is listed, what we checked, and any commercial relationship.</p></div></section>'''
    look = ""
    if s["threads"]:
        look = look_shelf({"thread": s["threads"][0]}, "Short videos on this thread", "Look")
    byline = (f'<div class="byline"><span><b>By</b> {e(s.get("author", "LookLearnFind"))}</span><span><b>Published</b> {e(fmt_date(s.get("date", "")))}</span>'
              f'<span><b>Updated</b> {e(fmt_date(s.get("updated", s.get("date", ""))))}</span>'
              + (f'<span><b>Disclosure</b> {e(s["disclosure"])}</span>' if s.get("disclosure") else '<span><b>Disclosure</b> None for this story.</span>') + "</div>")
    html = f'''<article>
<section class="story-head"><div class="wrap narrow" style="max-width:1160px"><div class="breadcrumb"><a href="/learn/">Learn</a> / <a href="/{s.get("category", "")}/">{e(cat_label(s.get("category", "")))}</a></div>
<div class="kicker">{e(s.get("format", "Story"))}<i></i></div><h1>{e(s["title"])}</h1><p class="dek">{e(s.get("dek", ""))}</p>{byline}{thread_chips(s["threads"])}</div></section>
{hero_html}
<div class="story"><div class="story-body">{of}{body.strip()}{src_html}{corr}</div>
<aside class="story-aside" aria-label="Story notes">{src_side}{side_finds}{threads_side}</aside></div>
</article>{find_mod}{look}{contribute_band()}'''
    jsonld = ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "Article", "headline": s["title"], "description": s.get("dek", ""),
        "datePublished": s.get("date", ""), "dateModified": s.get("updated", s.get("date", "")),
        "author": {"@type": "Organization", "name": s.get("author", "LookLearnFind")}}) + "</script>") if s.get("illustrative") != "yes" else ""
    shell(s["title"], s.get("dek", ""), s["path"], html, nav=s.get("category", ""), js=("shelf",), illustrative=s.get("illustrative") == "yes",
          og=None, jsonld=jsonld)


def render_find(f):
    body = f["_body"]
    why, body = take_block(body, "why")
    checked, body = take_block(body, "checked")
    know, body = take_block(body, "know")
    limits, body = take_block(body, "limits")
    t = TTYPE_BY_TYPE[f["type"]]
    verb = VERB.get(f["type"], "try")
    secs = []
    if why:
        secs.append(f'<section class="shelf" style="border:0;padding:30px 0 0"><div class="lab uc" style="color:var(--teal)">Why it made the list</div><div class="prose" style="font-size:20px;line-height:1.55;margin-top:8px">{why}</div></section>')
    if checked:
        secs.append('<section style="margin-top:34px"><div class="lab uc" style="color:var(--teal)">What we checked</div><ul class="checklist">' + "".join(f"<li>{b}</li>" for b in bullets(checked)) + "</ul></section>")
    if limits:
        secs.append('<section style="margin-top:34px"><div class="lab uc" style="color:var(--teal)">Limits</div><ul class="checklist">' + "".join(f"<li>{b}</li>" for b in bullets(limits)) + "</ul></section>")
    if know:
        secs.append(f'<section style="margin-top:34px"><div class="lab uc" style="color:var(--teal)">What to know before you {verb}</div><ul class="checklist">' + "".join(f"<li>{b}</li>" for b in bullets(know)) + "</ul></section>")
    disc = f'<div class="disclosure"><b>Disclosure</b>{e(f.get("disclosure", "No commercial relationship."))}</div>'
    cf = [STORY_BY[x] for x in f.get("came_from", [])]
    cf_html = ""
    if cf:
        cf_html = '<div class="blk" style="margin-top:30px"><div class="lab uc" style="color:var(--teal)">Came from</div>' + "".join(
            f'<p style="margin:6px 0"><a class="link teal" href="{s["path"]}">{e(s["title"])} ↗</a></p>' for s in cf) + "</div>"
    hero = IMG.get(f.get("image", ""), "")
    hero_html = f'<div class="story-hero" style="background-image:url({hero});aspect-ratio:16/7;margin:24px 0 0" role="img" aria-label="{e(f.get("image_alt", ""))}"></div>' if hero else ""
    facts = [("Type", t["label"][:-1])]
    if f.get("place"):
        facts.append(("Place", f["place"]))
    facts.append(("Last checked", fmt_date(f.get("checked", f.get("added", "")))))
    facts.append(("Category", cat_label(f.get("category", ""))))
    kv = '<dl class="kv" style="margin-top:22px">' + "".join(f"<dt>{e(a)}</dt><dd>{e(b)}</dd>" for a, b in facts if b) + "</dl>"
    look = look_shelf({"thread": f["threads"][0]}, "Short videos on this thread") if f["threads"] else ""
    html = f'''<article><section class="story-head"><div class="wrap" style="max-width:1160px">
<div class="breadcrumb"><a href="/find/">Find</a> / <a href="/find/{t["slug"]}/">{e(t["label"])}</a></div>
<div class="kicker">Find / {e(t["label"][:-1])}<i></i></div><h1>{e(f["title"])}</h1><p class="dek">{e(f.get("dek", ""))}</p>{kv}{thread_chips(f["threads"])}</div></section>
<div class="wrap">{hero_html}</div>
<div class="wrap" style="max-width:820px;padding-bottom:70px">{"".join(secs)}{disc}{cf_html}
<p class="small" style="margin-top:26px">Being listed here is a judgment with stated criteria, not a guarantee. <a href="/about/standards/">How we choose</a>.</p></div></article>{look}{contribute_band("Tried it? Tell us what held up.")}'''
    shell(f["title"], f.get("dek", ""), f["path"], html, nav="find", js=("shelf",), illustrative=f.get("illustrative") == "yes")


# ---------------------------------------------------------------- generated pages
def by_thread(slug):
    return [s for s in STORIES if slug in s["threads"]], [f for f in FINDS if slug in f["threads"]]


def gen_threads():
    body = page_head("Threads", "Follow a <em>thread.</em>",
                     "A thread is one subject, followed across short videos, reported stories, and real-world places. Every thread page keeps those three apart, so you can see who said what and what was checked.",
                     crumbs=[("Home", "/"), ("Threads", None)])
    groups = {}
    for t in sorted(THREADS, key=lambda x: x["title"].lower()):
        groups.setdefault(t["category"], []).append(t)
    body += '<section class="band cream"><div class="wrap">'
    for c in SITE["categories"]:
        ts = groups.get(c["slug"], [])
        if not ts:
            continue
        body += f'<h2 class="h3" style="margin:0 0 14px">{e(c["label"])}</h2><div class="rows">'
        for i, t in enumerate(ts, 1):
            ss, ff = by_thread(t["slug"])
            body += (f'<a class="row" href="/threads/{t["slug"]}/"><span class="n">{i:02d}</span><span class="t">{e(t["title"])}</span>'
                     f'<span class="d">{e(t["summary"])}</span><span class="ar">↗</span></a>')
        body += '</div><div style="height:34px"></div>'
    body += '<div id="more-threads" data-more-threads></div></div></section>'
    body += contribute_band("Propose a thread. Bring a source.")
    shell("Threads", "Follow a subject across short videos, reported stories, and real-world Finds.", "/threads/", body, nav="topics", js=("threads",))

    for t in THREADS:
        ss, ff = by_thread(t["slug"])
        rel = [TH[r] for r in t["related"] if r in TH]
        topics = [TOPICS[x] for x in t["topics"] if x in TOPICS]
        alias = f'<p class="small" style="margin-top:14px">Also searched as: {e(", ".join(t["aliases"]))}</p>' if t["aliases"] else ""
        relhtml = ""
        if rel or topics:
            relhtml = ('<div class="rail"><div class="chips">' + "".join(f'<a class="chip" href="/threads/{r["slug"]}/">Related: {e(r["title"])}</a>' for r in rel)
                       + "".join(f'<a class="chip" href="/topics/{x["slug"]}/">Topic: {e(x["label"])}</a>' for x in topics) + "</div></div>")
        head = page_head(f'Thread / {e(cat_label(t["category"]))}', e(t["title"]), e(t["summary"]),
                         crumbs=[("Home", "/"), ("Threads", "/threads/"), (t["title"], None)], extra=alias + relhtml)
        shelves = (look_shelf({"thread": t["slug"]}, "What people are saving", "Look",
                              "Reader-added and editor-added labels say who selected each clip.")
                   + learn_shelf(ss, "What the record shows", t["title"]) + find_shelf(ff))
        shell(f'{t["title"]} — a thread', t["summary"], f'/threads/{t["slug"]}/', head + shelves + contribute_band(), nav="topics", js=("shelf",))


def gen_topics():
    grid = '<div class="topic-grid">' + "".join(
        f'<a class="topic" href="/topics/{t["slug"]}/"><span class="n">{i:02d} / 12</span>{icon(t["slug"])}<span class="t"><span>{e(t["label"])}</span><span>↗</span></span></a>'
        for i, t in enumerate(SITE["topics"], 1)) + "</div>"
    body = page_head("Topics", "Choose a <em>thread.</em>",
                     "Twelve ways in. Follow one question, then another. Each subject connects back to people, perspectives, practical choices, and original sources.",
                     crumbs=[("Home", "/"), ("Topics", None)])
    body += f'<section class="band cream" style="padding-top:20px"><div class="wrap">{grid}<p class="small" style="margin-top:12px">Money is the one added topic: it gives the Economy section a clear practical home alongside Businesses.</p></div></section>'
    body += '<section class="band"><div class="wrap split"><div><div class="kicker">Narrower<i></i></div><h2 class="h2">Looking for something more specific?</h2></div><div><p class="dek">Threads follow one subject across videos, stories, and places.</p><p style="margin-top:18px"><a class="btn" href="/threads/">Browse all threads ↗</a></p></div></div></section>'
    shell("Topics", "Twelve topics across politics, economy, society and everyday life.", "/topics/", body, nav="topics")
    for i, t in enumerate(SITE["topics"], 1):
        ss = [s for s in STORIES if t["slug"] in s["topics"]]
        ff = [f for f in FINDS if t["slug"] in f["topics"]]
        ths = [x for x in THREADS if t["slug"] in x["topics"]]
        thr = ('<div class="thread-chips">' + "".join(thread_chip(x["slug"]) for x in ths) + "</div>") if ths else ""
        head = page_head(f'Topic {i:02d} / 12 · {e(cat_label(t["category"]))}', e(t["label"]), e(t["q"]),
                         crumbs=[("Home", "/"), ("Topics", "/topics/"), (t["label"], None)], extra=thr)
        body = (head + learn_shelf(ss, "What the record shows", t["label"].lower()) + find_shelf(ff, "Where to try it")
                + look_shelf({"topic": t["slug"]}, "What people are saving") + contribute_band())
        shell(t["label"], t["q"], f'/topics/{t["slug"]}/', body, nav="topics", js=("shelf",))


def gen_categories():
    tile_imgs = {"politics": ["politics-forum", "politics-vote"], "economy": ["economy-shop"], "society": [], "everyday-life": ["everyday-home", "everyday-cooking", "everyday-workout"]}
    for c in SITE["categories"]:
        ss = [s for s in STORIES if s.get("category") == c["slug"]]
        ff = [f for f in FINDS if f.get("category") == c["slug"]]
        ts = [t for t in SITE["topics"] if t["category"] == c["slug"]]
        chips = '<div class="chips" style="display:flex;gap:8px;flex-wrap:wrap">' + "".join(f'<a class="chip" href="/topics/{t["slug"]}/">{e(t["label"])} ↗</a>' for t in ts) + "</div>"
        head = page_head(f'{c["num"]} / {e(c["label"])}', e(c["headline"]), e(c["dek"]), crumbs=[("Home", "/"), (c["label"], None)], extra=f'<div style="margin-top:26px">{chips}</div>')
        body = (head + learn_shelf(ss, f'Worth a closer look in {c["label"]}', c["label"].lower()) + find_shelf(ff, "Real-world Finds")
                + look_shelf({"category": c["slug"]}, "What people are saving") + contribute_band())
        shell(c["label"], c["dek"], f'/{c["slug"]}/', body, nav=c["slug"], js=("shelf",))


def gen_learn_latest_find():
    head = page_head("Learn", "Reported, <em>with receipts.</em>",
                     "Long-form stories and deep dives. Every claim that can be traced points to the original record at the footnote.", crumbs=[("Home", "/"), ("Learn", None)])
    body = head + '<section class="band cream" style="padding-top:20px"><div class="wrap">' + (cards(STORIES) if STORIES else "<p>No stories yet.</p>") + "</div></section>" + contribute_band()
    shell("Learn", "Reported stories with numbered footnotes to original material.", "/learn/", body, nav="latest")

    items = sorted(STORIES + FINDS, key=lambda m: m.get("date", m.get("added", "")), reverse=True)
    body = page_head("Latest", "Worth a <em>closer look.</em>", "The newest stories and Finds. Short videos live in the Look Ledger, in newest-added order.", crumbs=[("Home", "/"), ("Latest", None)])
    body += '<section class="band cream" style="padding-top:20px"><div class="wrap">' + cards(items) + '</div></section>'
    body += look_shelf({"sort": "added", "limit": "4"}, "Newest in the Ledger", "Look")
    shell("Latest", "The newest stories, Finds, and saved videos.", "/latest/", body, nav="latest", js=("shelf",))

    # find hub
    head = page_head("Find", "Find what <em>holds up.</em>", "People, places, products, and practical paths. Each result shows why it is here and where the information came from.", crumbs=[("Home", "/"), ("Find", None)])
    hub = '<section class="band dark"><div class="wrap"><div class="rows">' + "".join(
        f'<a class="row" href="/find/{t["slug"]}/"><span class="n">{i:02d}</span><span class="t">{e(t["label"])}</span><span class="d">{e(t["blurb"])}</span><span class="ar">↗</span></a>'
        for i, t in enumerate(SITE["find_types"], 1)) + "</div></div></section>"
    ledger = f'''<section class="band"><div class="wrap split"><div><div class="kicker">Look<i></i></div><h2 class="h2">Short videos, kept on purpose.</h2></div>
<div><p class="dek">The Look Ledger is a searchable, human-curated index of short videos. Filter by subject, follow people whose eye you trust, and open the original.</p><p style="margin-top:18px"><a class="btn" href="/look/">Open the Ledger ↗</a></p></div></div></section>'''
    shell("Find", "People, places, products, and practical paths that hold up.", "/find/", head + f'<section class="band cream" style="padding:10px 0 0"><div class="wrap"><div class="cards">{"".join(card(f) for f in FINDS[:3])}</div></div></section>' + hub + ledger + contribute_band(), nav="find")
    for t in SITE["find_types"]:
        ff = [f for f in FINDS if f["type"] == t["type"]]
        body = page_head(f'Find / {e(t["label"])}', e(t["label"]), e(t["blurb"]), crumbs=[("Home", "/"), ("Find", "/find/"), (t["label"], None)])
        body += '<section class="band cream" style="padding-top:20px"><div class="wrap">' + (cards(ff) if ff else f'<div class="empty" style="border:1px dashed var(--rule2);padding:26px;font:14px var(--sans)"><b>No {e(t["label"].lower())} listed yet.</b> Every listing shows why it is here, what we checked, and any commercial relationship before it appears. <a href="/contribute/">Suggest one</a>.</div>') + "</div></section>" + contribute_band()
        shell(t["label"], t["blurb"], f'/find/{t["slug"]}/', body, nav="find")


def gen_home():
    def T(href, img, eyebrow, title, p="", cls=""):
        st = f' style="background-image:url({IMG[img]})"' if img else ""
        pp = f"<p>{e(p)}</p>" if p else ""
        return f'<a class="tile {cls}" href="{href}"{st}><div class="eyebrow">{e(eyebrow)}</div><h3>{e(title)}</h3>{pp}</a>'

    def head(c, side_link, side_text=None):
        return (f'<div class="chapter-head"><div><div class="kicker">{c["num"]} / {e(c["label"]).upper()}<i></i></div><h2 class="display" style="font-size:clamp(42px,6vw,76px)">{e(c["headline"])}</h2></div>'
                f'<div class="side"><p>{e(c["dek"])}</p><a class="link" href="{side_link[0]}">{e(side_link[1])} ↗</a></div></div>')
    C = CATS
    latest = (STORIES[:3])
    topics = '<div class="topic-grid">' + "".join(
        f'<a class="topic" href="/topics/{t["slug"]}/"><span class="n">{i:02d} / 12</span>{icon(t["slug"])}<span class="t"><span>{e(t["label"])}</span><span>↗</span></span></a>'
        for i, t in enumerate(SITE["topics"], 1)) + "</div>"
    finds = '<div class="rows">' + "".join(
        f'<a class="row" href="/find/{t["slug"]}/"><span class="n">{i:02d}</span><span class="t">{e(t["label"])}</span><span class="d">{e(t["blurb"])}</span><span class="ar">↗</span></a>'
        for i, t in enumerate(SITE["find_types"][:4], 1)) + "</div>"
    body = f'''<section class="hero-art" role="img" aria-label="Two overlapping portraits joined by a yellow overlap and a SOURCE 01 annotation"></section>
<div class="hero-mobile-text display">where signal meets source</div>
<div class="hero-strip"><div class="wrap"><span>Look closer / 2026 midterms</span><a href="/politics/">Politics is the opening file ↓</a></div></div>

<section class="band" id="politics"><div class="wrap">{head(C["politics"], ("/politics/", "The midterms file"))}
<div class="feature-card"><div class="copy"><div class="eyebrow">The opening file · Election 2026</div><h3>The midterms, in the open.</h3>
<p>What matters in your race? Who is asking for your vote? What does the record show? One place to begin asking better questions.</p>
<a class="link" href="/threads/midterms-2026/">See the starting sources ↗</a><div class="small" style="margin-top:14px;text-transform:uppercase;letter-spacing:.1em;font-weight:700;font-size:9px">A living guide · Editorial concept</div></div>
<div class="pic" style="background-image:url({IMG["politics-vote"]})" role="img" aria-label="Neighbors walking into a polling place on an autumn day"><span class="badge">01 / The ballot</span></div></div>
<div class="tiles t2">{T("/threads/candidate-forums/", "politics-forum", "02 / The people", "Hear the answer. Check the record.", "Candidate forums, positions, votes, and the questions still unanswered.")}
{T("/topics/candidates/", "", "03 / The receipts", "Read past the claim.", "Original documents, campaign money, and context that changes the picture.", "type")}</div>
<div class="rail"><span class="uc">Start with original material →</span><div class="chips"><a class="chip" href="/threads/midterms-2026/">Midterm basics ↗</a><a class="chip" href="/topics/politics/">Your ballot ↗</a><a class="chip" href="/topics/money/">Campaign finance ↗</a></div></div></div></section>

<section class="band warm" id="economy"><div class="wrap">{head(C["economy"], ("/economy/", "Explore economy"))}
<div class="tiles t3">{T("/topics/businesses/", "economy-shop", "01 / Small business", "Who builds it, who owns it, who benefits?", "The choices and pressures behind a local counter.", "tall")}
{T("/threads/grocery-prices/", "economy-shop", "02 / Prices", "What a price actually tells you.", "", "tall")}
{T("/topics/money/", "", "03 / Work", "The people behind the product.", "", "tall type")}</div>
<div class="rail"><span>Business decisions are also questions about ownership, labor, value, and where your money goes.</span><a class="link" href="/topics/businesses/">Business and money topics ↗</a></div></div></section>

<section class="band teal" id="society"><div class="wrap">{head(C["society"], ("/society/", "Explore society"))}
<div class="tiles t3b">{T("/society/", "", "02 / Conversation", "Listen past the label.", "", "type tall")}
{T("/society/", "", "03 / Public space", "Where ideas meet people.", "", "type tall")}
{T("/threads/tartaria/", "", "01 / Common ground", "A table with room for another perspective.", "The messy, interesting work of understanding each other.", "type tall")}</div>
<div class="rail"><span>Give a question enough room to be complicated. Then show what can actually be checked.</span><a class="link" href="/about/">Our approach ↗</a></div></div></section>

<section class="band tint" id="everyday-life"><div class="wrap">{head(C["everyday-life"], ("/everyday-life/", "Explore everyday life"))}
<div class="tiles t3">{T("/topics/home-improvement/", "everyday-home", "01 / Home", "Know what you are making before you start.", "Good questions save materials, time, and money.", "tall")}
{T("/topics/cooking/", "everyday-cooking", "02 / Kitchen", "Cook with curiosity.", "", "tall")}
{T("/topics/working-out/", "everyday-workout", "03 / Body", "Find a rhythm that lasts.", "", "tall")}</div>
<div class="rail"><span>From a supplement claim to a renovation quote, the useful detail is often the one someone helps you notice.</span><a class="link" href="/topics/">Browse the practical topics ↗</a></div></div></section>

<section class="band" id="topics"><div class="wrap"><div class="chapter-head"><div><div class="kicker">05 / Topics<i></i></div><h2 class="display" style="font-size:clamp(42px,6vw,76px)">Choose a thread.</h2></div>
<div class="side"><p>Twelve ways in. Follow one question, then another. Each subject connects back to people, perspectives, practical choices, and original sources.</p></div></div>
{topics}<p class="small" style="margin-top:12px">Money is the one added topic: it gives the Economy section a clear practical home alongside Businesses.</p></div></section>

<section class="band warm" id="latest"><div class="wrap"><div class="chapter-head"><div><div class="kicker">06 / Latest<i></i></div><h2 class="display" style="font-size:clamp(42px,6vw,76px)">Worth a closer look.</h2></div>
<div class="side"><a class="link" href="/latest/">Latest ↗</a></div></div>{cards(latest)}</div></section>

<section class="band" id="look" style="background:var(--paper2)"><div class="wrap"><div class="chapter-head"><div><div class="kicker">07 / Look<i></i></div><h2 class="display" style="font-size:clamp(42px,6vw,76px)">A feed you can steer.</h2></div>
<div class="side"><p>Short videos worth keeping, with the notes that explain why. Search the subjects. Follow people whose eye you trust.</p><a class="link" href="/look/">Open the Ledger ↗</a></div></div>
<div data-look-shelf data-sort="added" data-limit="3"><div data-shelf-body></div></div></div></section>

<section class="band dark" id="find"><div class="wrap"><div class="chapter-head"><div><div class="kicker">08 / Find<i></i></div><h2 class="display" style="font-size:clamp(42px,6vw,76px)">Find what holds up.</h2></div>
<div class="side"><p>People, places, products, and practical paths. Each result should show why it is here and where the information came from.</p></div></div>{finds}</div></section>

<section class="band teal" id="about"><div class="wrap split"><div><div class="kicker">09 / About<i></i></div><h2 class="display" style="font-size:clamp(42px,6vw,76px)">Interesting ideas. Open receipts.</h2>
<p class="dek" style="margin:26px 0">LookLearnFind is for people who like looking again. We make room for perspective, show the material behind a claim, and keep the pleasure of discovery in the process.</p>
<a class="link" href="/about/">About us ↗</a></div>
<div class="open-panel"><h4>A story, opened up</h4><div class="r"><b>LOOK</b><span>What is the real question?</span></div><div class="r"><b>LEARN</b><span>What do the sources show? What might we be missing?</span></div><div class="r"><b>FIND</b><span>What is worth exploring next?</span></div><div class="src">Source 01 — Original material ↗</div></div></div></section>'''
    shell("LookLearnFind — where signal meets source", "Short posts to catch your eye, reported deep dives with receipts, and real-world finds worth a visit. Curiosity should lead somewhere.",
          "/", body, nav="", js=("shelf",), bodyclass="home")


def gen_search_shell():
    body = page_head("Search", "Follow a <em>thread.</em>", "", crumbs=[("Home", "/"), ("Search", None)])
    body += '''<section class="band cream" style="padding-top:10px"><div class="wrap narrow" style="max-width:900px">
<form class="searchbar" data-search-form role="search"><label class="sr" for="q">What are you looking into?</label><input id="q" name="q" type="search" placeholder="What are you looking into?" autocomplete="off"><button class="btn" type="submit">Search</button></form>
<p class="small" style="margin:6px 0 18px">Try “candidate forum,” “kitchen project,” or “skincare claim.”</p>
<div class="tabs" role="tablist" data-search-tabs></div><div data-search-results aria-live="polite"></div></div></section>'''
    shell("Search", "Search stories, Finds, threads, topics and saved videos.", "/search/", body, nav="", js=("search",), sitemap=False)


def gen_look_shells():
    hero = '''<section class="hero" style="padding:44px 0 36px"><div class="wrap wide"><div class="hero-head"><div><div class="kicker">Look <i></i> The Ledger</div>
<h1 class="display">A feed you<br>can <em>steer.</em></h1></div><div class="hero-right"><p>Short videos worth keeping, with the notes that explain why. Search the subjects. Follow people whose eye you trust. Open the original when something catches yours.</p><div class="minor">Human saves &nbsp;/&nbsp; Your filters &nbsp;/&nbsp; No hidden ranking</div></div></div></div></section>'''
    app = '''<div id="ledger-app"><noscript><div class="wrap wide"><p class="notice">The Ledger needs JavaScript to filter and save. You can still <a href="/threads/">browse threads</a>.</p></div></noscript></div>
<section class="lfoot"><div class="wrap wide"><div><h2>Good finds have a way of traveling.</h2><p>Keep your own Ledger. Follow the people who see what you might have missed.</p></div><a data-start-ledger href="/account/?mode=signup">Start your Ledger ↗</a></div></section>'''
    shell("The Look Ledger — a feed you can steer", "A searchable, human-curated index of short videos. Filter by subject, follow people whose eye you trust, and open the original.",
          "/look/", hero + app, nav="look", css=("ledger",), js=("ledger",), bodyclass="ledger-page")
    shell("Add a post", "Put one in the Ledger. Paste the link, tell us what made you stop.", "/look/add/",
          '<div id="add-app" class="wrap" style="padding-top:54px;padding-bottom:70px"></div>', nav="look", css=("ledger",), js=("add",), noindex=True, sitemap=False)
    shell("Ledger entry", "A saved short video in the Look Ledger.", "/look/entry/",
          '<div id="entry-app" class="wrap wide" style="padding-top:40px;padding-bottom:70px"></div>', nav="look", css=("ledger",), js=("entry",), sitemap=False)
    shell("Account", "Sign in or create a profile to save videos and follow other people's finds.", "/account/",
          '<div id="account-app" class="wrap" style="padding-top:54px;padding-bottom:70px"></div>', nav="look", css=("ledger",), js=("account",), noindex=True, sitemap=False)
    shell("Profile", "A public Ledger profile.", "/u/", '<div id="profile-app" class="wrap wide" style="padding-top:40px;padding-bottom:70px"></div>', nav="look", css=("ledger",), js=("profile",), sitemap=False)
    shell("Editors", "Ledger review queue.", "/admin/", '<div id="admin-app" class="wrap wide" style="padding-top:40px;padding-bottom:70px"></div>', nav="", css=("ledger",), js=("admin",), noindex=True, sitemap=False)
    shell("Thread", "A thread on LookLearnFind.", "/threads/t/", '<div id="thread-app"></div>', nav="topics", css=("ledger",), js=("threadpage", "shelf"), noindex=True, sitemap=False)


def gen_pages():
    for p in PAGES:
        path = p["path"]
        body = p["_body"].strip()
        illus = p.get("illustrative") == "yes"
        shell(p["title"], p["description"], path, body, nav=p.get("nav", ""), js=tuple(lst(p.get("js"))), css=tuple(lst(p.get("css"))),
              noindex=p.get("noindex") == "yes", illustrative=illus, sitemap=p.get("sitemap", "yes") != "no")


def write_search_index():
    idx = []
    strip = lambda h: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))[:600]
    for s in STORIES:
        idx.append(dict(t="story", title=s["title"], url=s["path"], dek=s.get("dek", ""), cat=s.get("category", ""), topics=s["topics"], threads=s["threads"], text=strip(s["_body"]), ill=s.get("illustrative") == "yes"))
    for f in FINDS:
        idx.append(dict(t="find", title=f["title"], url=f["path"], dek=f.get("dek", ""), cat=f.get("category", ""), topics=f["topics"], threads=f["threads"], text=strip(f["_body"]), ill=f.get("illustrative") == "yes"))
    for t in THREADS:
        idx.append(dict(t="thread", title=t["title"], url=f'/threads/{t["slug"]}/', dek=t["summary"], cat=t["category"], topics=t["topics"], threads=[], text=" ".join(t["aliases"])))
    for t in SITE["topics"]:
        idx.append(dict(t="topic", title=t["label"], url=f'/topics/{t["slug"]}/', dek=t["q"], cat=t["category"], topics=[], threads=[], text=""))
    for p in PAGES:
        if p.get("sitemap", "yes") != "no" and p.get("noindex") != "yes" and p["path"] not in ("/",):
            idx.append(dict(t="page", title=p["title"].split("|")[0].strip(), url=p["path"], dek=p["description"], cat="", topics=[], threads=[], text=""))
    (OUT / "search-index.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    (OUT / "threads.json").write_text(json.dumps([{k: t[k] for k in ("slug", "title", "aliases", "category", "topics", "summary")} for t in THREADS], ensure_ascii=False, separators=(",", ":")))
    (OUT / "site-data.json").write_text(json.dumps({"categories": SITE["categories"], "topics": [{"slug": t["slug"], "label": t["label"], "category": t["category"]} for t in SITE["topics"]], "kinds": SITE["kinds"], "platforms": SITE["platforms"]}, ensure_ascii=False, separators=(",", ":")))


def main():
    load_content()
    index_content()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(ROOT / "static", OUT, dirs_exist_ok=True)
    for s in STORIES:
        render_story(s)
    for f in FINDS:
        render_find(f)
    gen_pages(); gen_home(); gen_topics(); gen_categories(); gen_threads(); gen_learn_latest_find(); gen_search_shell(); gen_look_shells()
    for path, html in PAGES_OUT.items():
        dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        if path.endswith(".html"):
            dest = OUT / path.lstrip("/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html)
    write_search_index()
    lm = CFG["updated"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in sorted(set(SITEMAP)):
        sm.append(f"  <url><loc>{CFG['url']}{u}</loc><lastmod>{lm}</lastmod></url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n")
    print(f"Built {len(PAGES_OUT)} pages to {OUT}")
    if "--zip" in sys.argv:
        import zipfile
        rel = ROOT / "release"
        rel.mkdir(exist_ok=True)
        zpath = rel / "looklearnfind-site.zip"
        if zpath.exists():
            zpath.unlink()
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(OUT.rglob("*")):
                if f.is_file() and "_data" not in f.parts and not f.name.endswith(".sqlite"):
                    z.write(f, f.relative_to(OUT).as_posix())
        print(f"Wrote {zpath} ({zpath.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
