"""Politics landing (/politics/) and Daily Signal pages (/politics/daily/, /politics/daily/YYYY-MM-DD/).

Authority: docs/politics/brand/ (Politics Creative Lock: 01 visual identity, 02 copy spec, edition-001 integration contract and mockup) on top of
docs/politics/INDEX.md. Driven by data/politics_home.json, data/discovery.json and approved records in data/politics_daily/. Pages are written only through
build.shell(); this module contains no navigation markup. It never states a result, margin, call or position: a module without verified content shows its
approved explanatory copy only, and a call to action is rendered only when its destination exists in the built site (gated otherwise).

A Daily Signal record is public only when its status is "approved" and its fact check has passed. A "draft" record is built only for local review
(LLF_PREVIEW_DRAFTS=1): noindex, labelled as a draft, absent from the sitemap and search, and never zipped.

Reusable components (CSS in static/css/politics.css, tokens --llf-*): hero_duochrome, daily_strip, five_signals, accountability_feature (newspaper-cutout
composition), tile, state_bar, signals_tile, reporting_list, evidence_band, render_edition.
"""
import json
import pathlib
import re
from html import escape as e

ROOT = pathlib.Path(__file__).parent
HOME_FILE = ROOT / "data" / "politics_home.json"
DAILY_DIR = ROOT / "data" / "politics_daily"
REQUIRED_DAILY = ("story_id", "date", "title", "dek", "sources", "author", "editor", "update_log", "status")
GATED = []          # (module, label, route) for every call to action that was not shown; read by the build report and tests


def load_home():
    return json.loads(HOME_FILE.read_text(encoding="utf-8"))


def load_daily(directory=None, include_drafts=False):
    """Public records (approved and fact-checked), newest first. Drafts only for local preview. Incomplete records are skipped and reported."""
    out, bad = [], []
    for f in sorted((directory or DAILY_DIR).glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        miss = [k for k in REQUIRED_DAILY if not r.get(k)]
        if miss:
            bad.append(f"{f.name}: missing {', '.join(miss)}")
            continue
        if r["status"] == "approved" and (r.get("fact_check") or {"state": "passed"}).get("state") != "passed":
            bad.append(f"{f.name}: approved without a passed fact check")
            continue
        if r["status"] == "approved" or (include_drafts and r["status"] == "draft"):
            out.append(r)
    out.sort(key=lambda r: (r["date"], -int(r.get("order", 99))), reverse=True)
    return out, bad


def briefings(records):
    """Group records by date: {date: [records in order]}. Several story IDs may share one briefing date; an edition record leads its date."""
    g = {}
    for r in sorted(records, key=lambda r: (0 if r.get("blocks") else 1, int(r.get("order", 99)), r["story_id"])):
        g.setdefault(r["date"], []).append(r)
    return dict(sorted(g.items(), reverse=True))


def read_minutes(r):
    b = r.get("blocks") or {}
    texts = list(b.get("opening", {}).get("paras", [])) + list(b.get("opening", {}).get("glance", []))
    for s in b.get("sections", []):
        texts += s.get("paras", [])
    words = len(re.sub(r"<[^>]+>", " ", " ".join(texts)).split())
    return max(1, round(words / 220))


# ---------------------------------------------------------------- helpers
def _ok(api, route):
    return route in api["PAGES_OUT"]


def _cta(api, module, c, cls="pol-cta", fallback_href=None):
    """A call to action is shown only when its internal destination was built. `fallback_href` is another real destination used when the route is not built."""
    if not c:
        return ""
    if c.get("route"):
        if _ok(api, c["route"]):
            href = c["route"]
        elif fallback_href:
            href = fallback_href
        else:
            GATED.append((module, c["label"], c["route"]))
            return ""
        return f'<a class="{cls}" href="{e(href)}">{e(c["label"])}<span aria-hidden="true"> ↗</span></a>'
    if c.get("href") and c.get("approved", True):
        return f'<a class="{cls}" href="{e(c["href"])}" rel="noopener">{e(c["label"])}<span aria-hidden="true"> ↗</span></a>'
    GATED.append((module, c["label"], c.get("href") or ""))
    return ""


def _edition_href(api, anchor=""):
    ed = api.get("_edition")
    return f'/politics/daily/{ed["date"]}/{("#" + anchor) if anchor else ""}' if ed else None


def _fallback(api, c):
    """Resolve a fallback hint: `edition#id` (the visible Daily Signal edition), `#anchor` (same page) or None."""
    f = c.get("fallback")
    if not f:
        return None
    if f.startswith("edition"):
        return _edition_href(api, f.split("#", 1)[1] if "#" in f else "")
    return f


def credit_line(api, key):
    c = api["HERO_CREDITS"].get(key)
    if not c:
        return "AI illustration" if key[:1] == "s" and key[1:2].isdigit() else ""
    if str(c.get("license", "")).startswith("AI"):
        return "AI illustration"
    return f'Photo: {c.get("credit", "")}, {c.get("license", "")}'


def _story(api, sid):
    for s in api["STORIES"]:
        if s["path"].strip("/").split("/")[-1] == sid:
            return s
    return None


def _fmt(api, s):
    return api["fmt_date"](s.get("date", ""))


def _img(key):
    return f"/img/elections/{key}.jpg"


def _head(m, mid=None, tag="h2"):
    i = f' id="{mid}"' if mid else ""
    return f'<div class="pol-eyebrow">{e(m["eyebrow"])}</div><{tag}{i}>{e(m["h2"])}</{tag}>'


# ---------------------------------------------------------------- components
def hero_duochrome(h):
    art = h["art"]
    lines = "<br>".join(e(x) for x in h["h1"])
    return (f'<section class="pol-hero" aria-labelledby="pol-h1"><div class="pol-hero__in">'
            f'<div class="pol-hero__text"><div class="breadcrumb"><a href="/">Home</a> / Politics</div>'
            f'<div class="pol-eyebrow pol-eyebrow--rule">{e(h["eyebrow"])}</div><h1 id="pol-h1">{lines}</h1><p class="pol-hero__deck">{e(h["deck"])}</p></div>'
            f'<figure class="pol-duo" data-asset="{e(art["asset_id"])}"><span class="pol-duo__plane" aria-hidden="true"></span>'
            f'<img class="pol-duo__img" src="{e(art["src"])}" width="{art["width"]}" height="{art["height"]}" alt="{e(art["alt"])}" fetchpriority="high">'
            f'<figcaption>{e(art["credit"])}</figcaption></figure></div></section>')


def daily_strip(api, d, groups):
    """Left: yellow field with the series title. Right: the live headline, date and read time, one link. Fallback: approved sentence plus the latest dated feature."""
    ed = api.get("_edition")
    draft = ' <span class="pol-draft">DRAFT PREVIEW</span>' if ed and ed["status"] != "approved" else ""
    left = f'<div class="pol-daily__title"><span class="pol-tab">{e(d["eyebrow"])}</span><h2 id="pol-daily-h">{e(d["h2"])}</h2></div>'
    if groups:
        date, recs = next(iter(groups.items()))
        lead = recs[0]
        label = api["fmt_date"](date).upper() + (f' / EDITION {e(lead["edition"])}' if lead.get("edition") else "")
        mins = f' / {read_minutes(lead)} MIN READ' if lead.get("blocks") else ""
        more = f' <span class="pol-daily__count">{len(recs)} stories</span>' if len(recs) > 1 and not lead.get("blocks") else ""
        right = (f'<p class="pol-daily__lead">{e(lead["title"])}</p><p class="pol-daily__meta">{label}{mins}{more}{draft}</p>'
                 f'<p class="pol-daily__links"><a class="pol-cta" href="/politics/daily/{e(date)}/">{e(d["cta"])}<span aria-hidden="true"> →</span></a>'
                 f'<a class="pol-cta pol-cta--quiet" href="/politics/daily/">{e(d["past"])}</a></p>')
    else:
        s = api["STORIES"][0] if api["STORIES"] else None
        feat = (f'<p class="pol-daily__feature"><span class="pol-daily__fl">{e(d["fallback_label"])}</span> '
                f'<a href="{e(s["path"])}">{e(s["title"])}</a> <span class="pol-daily__date">{e(_fmt(api, s))}</span></p>') if s else ""
        right = (f'<p class="pol-daily__lead">{e(d["standfirst"])}</p><p class="pol-daily__note">{e(d["empty"])}</p>{feat}'
                 f'<p class="pol-daily__links"><a class="pol-cta pol-cta--quiet" href="/politics/daily/">{e(d["past"])}</a></p>')
    five = five_signals(api, d) if groups and next(iter(groups.values()))[0].get("blocks") else ""
    return (f'<section class="pol-daily" id="daily-signal" aria-labelledby="pol-daily-h"><div class="pol-daily__in">{left}<div class="pol-daily__body">{right}</div></div>{five}</section>')


def five_signals(api, d):
    ed = api["_edition"]
    items = "".join(
        f'<li><a href="/politics/daily/{e(ed["date"])}/#{e(i["target"])}"><span class="pol-five__n">{e(i["n"])}</span><span class="pol-five__t">{e(i["title"])}</span></a></li>'
        for i in ed["blocks"]["signals"]["items"])
    return f'<nav class="pol-five" aria-label="{e(d["five_label"])}"><p class="pol-five__lab">{e(d["five_label"])}</p><ol>{items}</ol></nav>'


def accountability_feature(api, a):
    art = a["art"]
    prim = _cta(api, "accountability", a["cta_primary"], fallback_href=_fallback(api, a["cta_primary"]))
    ctas = prim + _cta(api, "accountability", a["cta_secondary"], "pol-cta pol-cta--quiet")
    tip = _cta(api, "accountability", a.get("tip"), "pol-cta pol-cta--quiet") if a.get("tip") else ""
    labels = "".join(f"<li>{e(s)}</li>" for s in a["statuses"])
    return (f'<section class="pol-acc" id="accountability-desk" aria-labelledby="pol-acc-h">'
            f'<figure class="pol-cut" data-assets="{e(art["a"]["asset_id"])} {e(art["b"]["asset_id"])}">'
            f'<span class="pol-cut__plane" aria-hidden="true"></span>'
            f'<img class="pol-cut__ghost" src="/img/politics/capitol-cut.png" alt="" width="999" height="740" loading="lazy">'
            f'<img class="pol-cut__a" src="{e(art["a"]["src"])}" width="{art["a"]["width"]}" height="{art["a"]["height"]}" alt="{e(art["a"]["alt"])}" loading="lazy">'
            f'<img class="pol-cut__b" src="{e(art["b"]["src"])}" width="{art["b"]["width"]}" height="{art["b"]["height"]}" alt="{e(art["b"]["alt"])}" loading="lazy">'
            f'<figcaption>{e(art["caption"])}</figcaption></figure>'
            f'<div class="pol-acc__text">{_head(a, "pol-acc-h")}<p class="pol-deck">{e(a["deck"])}</p><p class="pol-acc__ctas">{ctas}{tip}</p>'
            f'<div class="pol-nodata"><h3>{e(a["live_title"])}</h3><p>{e(a["no_data"])}</p>'
            f'<ul class="pol-status" aria-label="How we label a public position">{labels}</ul></div></div></section>')


def tile(api, mid, m, cta_html, extra=""):
    """A topic tile: text on the paper side, a photograph on the other side cut by a diagonal edge. Natural colour or monochrome, never a blanket filter."""
    im = m["image"]
    cr = credit_line(api, im["key"])
    return (f'<article class="pol-tile" id="{mid}" aria-labelledby="{mid}-h"><div class="pol-tile__t">{_head(m, mid + "-h")}<p class="pol-tile__d">{e(m["deck"])}</p>{cta_html}{extra}</div>'
            f'<div class="pol-tile__pic"><img class="pol-img--{e(im["treatment"])}" src="{_img(im["key"])}" alt="" loading="lazy" width="1200" height="800">'
            f'<span class="pol-credit">{e(cr)}</span></div></article>')


def _round_cta(label, href):
    return f'<a class="pol-round" href="{e(href)}" aria-label="{e(label)}"><span aria-hidden="true">→</span></a>'


def election_tile(api, m, hubs):
    href = m["cta"]["route"] if _ok(api, m["cta"]["route"]) else m["cta"]["fallback"]
    return tile(api, "election-2026", m, _round_cta(m["cta"]["label"], href))


def state_bar(api, m, hubs):
    states = [s for s in m["states"] if s["code"] in hubs and hubs[s["code"]]["url"] in api["PAGES_OUT"]]
    states.sort(key=lambda s: (0 if s["code"] == m.get("lead") else 1, s["name"]))
    opts = "".join(f'<option value="{e(hubs[s["code"]]["url"])}">{e(s["name"])}</option>' for s in states)
    links = "".join(f'<a href="{e(hubs[s["code"]]["url"])}"><span class="c">{e(s["code"])}</span>{e(s["name"])}</a>' for s in states)
    sel = (f'<form class="pol-select" data-pol-state-jump><label for="pol-state-sel">{e(m["selector_label"])}</label>'
           f'<select id="pol-state-sel"><option value="">{e(m["selector_label"])}</option>{opts}</select></form>')
    return (f'<nav class="pol-statebar" id="state-reports" aria-label="Election 2026 state reports"><p class="pol-statebar__lab">{e(m["states_label"])}</p>'
            f'<div class="pol-statebar__links">{links}</div>{sel}</nav>')


def money_tile(api, m):
    story = _story(api, m["cta"].get("fallback_story", ""))
    href = m["cta"]["route"] if _ok(api, m["cta"]["route"]) else (story["path"] if story else None)
    if not href:
        GATED.append(("money", m["cta"]["label"], m["cta"]["route"]))
        return tile(api, "follow-the-money", m, "")
    if href != m["cta"]["route"]:
        GATED.append(("money", m["cta"]["label"] + " (route not built; links to the lead report)", m["cta"]["route"]))
    return tile(api, "follow-the-money", m, _round_cta(m["cta"]["label"], href))


def record_tile(api, m):
    href = m["cta"]["route"] if _ok(api, m["cta"]["route"]) else None
    if not href:
        GATED.append(("record", m["cta"]["label"], m["cta"]["route"]))
    return tile(api, "state-of-the-record", m, _round_cta(m["cta"]["label"], href) if href else "")


def signals_tile(api, m):
    im = m["image"]
    cr = credit_line(api, im["key"])
    items = [i for i in (m.get("items") or []) if i.get("status") == "approved"]
    body = "".join(f'<li><b>{e(i["headline"])}</b> {e(i["stat_or_comparison"])} <span class="pol-credit">Verified {e(i["verified_at"])} by {e(i["reviewer"])}. {e(i["method_note"])}</span></li>' for i in items)
    none = "" if items else f'<p class="pol-signals__none">{e(m["no_signal"])}</p>'
    prim = _cta(api, "signals", m["cta"], fallback_href=_fallback(api, m["cta"]))
    links = prim + _cta(api, "signals", m["method"], "pol-cta pol-cta--quiet")
    return (f'<article class="pol-signals" id="election-signals" aria-labelledby="pol-sig-h"><div class="pol-signals__t">{_head(m, "pol-sig-h")}<p class="pol-tile__d">{e(m["deck"])}</p>'
            f'{("<ul class=pol-sigl>" + body + "</ul>") if items else ""}{none}<p class="pol-signals__links">{links}</p></div>'
            f'<div class="pol-signals__pic"><img class="pol-img--{e(im["treatment"])}" src="{_img(im["key"])}" alt="" loading="lazy" width="1200" height="800">'
            f'<span class="pol-signals__plane" aria-hidden="true"></span><span class="pol-credit">{e(cr)}</span></div></article>')


def reporting_list(api, m, site, threads):
    lst = [s for s in (_story(api, i) for i in m["list_ids"]) if s]
    rows = "".join(
        f'<li><a href="{e(s["path"])}"><span class="pol-ruled__t">{e(s["title"])}</span><span class="pol-ruled__arrow" aria-hidden="true">→</span></a>'
        f'<span class="pol-ruled__m">{e(_fmt(api, s))}<span class="pol-badge">{e(m["context_badge"])}</span></span></li>' for s in lst)
    tl = " ".join(f'<a href="/threads/{e(t["slug"])}/">{e(t["title"])}</a>' for t in threads if t["category"] == "politics")
    chips = " ".join(f'<a href="/topics/{e(t["slug"])}/">{e(t["label"])}</a>' for t in site["topics"] if t["category"] == "politics")
    return (f'<section class="pol-reporting" id="current-reporting" aria-labelledby="pol-rep-h">{_head(m, "pol-rep-h")}<ul class="pol-ruled">{rows}</ul>'
            f'<p class="pol-reporting__more">{_cta(api, "reporting", m["cta"])}</p>'
            f'<p class="pol-threadlinks"><span>{e(m["threads_label"])}</span> {tl} {chips}</p></section>')


def evidence_band(api, m):
    rows = ""
    for l in m["links"]:
        c = _cta(api, "source", l, "pol-ev__link") if (l.get("route") or l.get("href")) else ""
        if c:
            rows += f"<li>{c}</li>"
    return (f'<section class="pol-evidence" id="go-to-the-source" aria-labelledby="pol-src-h"><div class="pol-evidence__in">'
            f'<div class="pol-evidence__t"><h2 id="pol-src-h"><span class="pol-paper">{e(m["label"])}</span></h2><span class="pol-sr">{e(m["h2"])}</span></div>'
            f'<div class="pol-evidence__b"><p class="pol-evidence__deck">{e(m["deck"])}</p><ul class="pol-ev">{rows}</ul><p class="pol-method">{e(m["method_line"])}</p></div>'
            f'</div></section>')


# ---------------------------------------------------------------- Daily Signal pages
def render_edition(r, fmt_date, preview=False):
    """The long-form briefing: opening, five jump-linked signals, five deep sections, what we are watching, numbered sources. One shared shell, one rail."""
    b = r["blocks"]
    op, sg = b["opening"], b["signals"]
    draft = ('<p class="pol-draftbar" role="note"><b>Draft for review.</b> Not approved or published. The independent fact check is pending, '
             'so figures, calls and control claims below are unverified.</p>') if r["status"] != "approved" else ""
    outline = "".join(f'<li><a href="#{e(x["id"])}">{e(x["label"])}</a></li>' for x in r["rail"]) + '<li><a href="#sources">Go to the source</a></li>'
    glance = "".join(f"<li>{x}</li>" for x in op["glance"])
    teasers = "".join(
        f'<li><a class="pol-sig__a" href="#{e(i["target"])}"><span class="pol-sig__n">{e(i["n"])} / {e(i["label"])}</span><span class="pol-sig__t">{e(i["title"])}</span></a>'
        f'<p>{i["teaser"]}</p></li>' for i in sg["items"])
    secs = ""
    for s in b["sections"]:
        paras = "".join(f"<p>{p}</p>" for p in s["paras"])
        secs += (f'<section class="pol-ed__sec" id="{e(s["id"])}"><div class="pol-eyebrow">{e(s["n"])} / {e(next((x["label"] for x in r["rail"] if x["id"] == s["id"]), ""))}</div>'
                 f'<h2>{e(s["h2"])}</h2>{paras}<p class="pol-ed__src">{s["source_review"]}</p><p class="pol-ed__back"><a href="#five-signals">Back to today\'s signals</a></p></section>')
    w = b["watching"]
    watch = "".join(f"<li>{x}</li>" for x in w["items"])
    src = "".join(f'<li><a href="{e(s["url"])}" rel="noopener">{e(s["label"])}</a>, {e(fmt_date(s["date"]))}</li>' for s in r["sources"])
    log = "".join(f'<li>{e(fmt_date(u["date"]))}: {e(u["note"])}</li>' for u in r["update_log"])
    return (f'<article class="pol-ed" data-outline-label="On this briefing" data-story-id="{e(r["story_id"])}">'
            f'<header class="pol-ed__head"><div class="breadcrumb"><a href="/">Home</a> / <a href="/politics/">Politics</a> / <a href="/politics/daily/">The Daily Signal</a> / {e(fmt_date(r["date"]))}</div>'
            f'<div class="pol-eyebrow">THE DAILY SIGNAL / EDITION {e(r["edition"])}</div><h1>{e(r["title"])}</h1><p class="pol-ed__dek">{e(r["dek"])}</p>'
            f'<p class="pol-credit">{e(fmt_date(r["date"]))} / {read_minutes(r)} min read. Story ID {e(r["story_id"])}. By {e(r["author"])}. {("Edited by " + e(r["editor"])) if not r["editor"].lower().startswith("not yet") else "Editor not yet assigned"}. Source cutoff {e(fmt_date(r["source_cutoff"]))}.</p>{draft}</header>'
            f'<nav class="onpage" aria-label="On this briefing"><ol>{outline}</ol></nav>'
            f'<section class="pol-ed__sec" id="{e(op["id"])}"><h2>{e(op["h2"])}</h2>{"".join(f"<p>{p}</p>" for p in op["paras"])}'
            f'<div class="pol-glance"><h3>At a glance</h3><ul>{glance}</ul></div><p class="pol-ed__src">{op["source_note"]}</p></section>'
            f'<section class="pol-ed__sec pol-ed__signals" id="{e(sg["id"])}"><h2>{e(sg["h2"])}</h2><p>{sg["intro"]}</p><ol class="pol-sig">{teasers}</ol></section>'
            f'{secs}'
            f'<section class="pol-ed__sec" id="{e(w["id"])}"><h2>{e(w["h2"])}</h2><ul class="pol-list">{watch}</ul><p class="pol-ed__close">{w["closing"]}</p></section>'
            f'<section class="pol-ed__sec" id="sources"><h2>Go to the source</h2><p>{b["sources_intro"]}</p><ol class="pol-list">{src}</ol>'
            f'<h3>Update log</h3><ul class="pol-list">{log}</ul></section></article>')


def render_daily_briefing(date, recs, fmt_date):
    flat = [r for r in recs if not r.get("blocks")]
    ed = next((r for r in recs if r.get("blocks")), None)
    crumbs = (f'<div class="breadcrumb"><a href="/">Home</a> / <a href="/politics/">Politics</a> / <a href="/politics/daily/">The Daily Signal</a> / {e(fmt_date(date))}</div>')
    sections = ""
    for r in flat:
        src = "".join(f'<li><a href="{e(s["url"])}" rel="noopener">{e(s["label"])}</a>, {e(fmt_date(s.get("date", "")))}</li>' for s in r["sources"])
        log = "".join(f'<li>{e(fmt_date(u["date"]))}: {e(u["note"])}</li>' for u in r["update_log"])
        sections += (f'<article class="pol-story" id="{e(r["story_id"])}"><h2>{e(r["title"])}</h2><p class="pol-deck">{e(r["dek"])}</p>'
                     f'<p class="pol-credit">Story ID {e(r["story_id"])}. By {e(r["author"])}. Edited by {e(r["editor"])}.</p>{r.get("body_html", "")}'
                     f'<h3>Sources</h3><ul class="pol-list">{src}</ul><h3>Update log</h3><ul class="pol-list">{log}</ul></article>')
    if ed:
        return render_edition(ed, fmt_date) + (f'<section class="pol-page"><div class="pol-page__in">{sections}</div></section>' if sections else "")
    toc = "".join(f'<li><a href="#{e(r["story_id"])}">{e(r["title"])}</a></li>' for r in flat) if len(flat) > 1 else ""
    return (f'<section class="pol-page"><div class="pol-page__in">{crumbs}<div class="pol-eyebrow">THE DAILY SIGNAL</div><h1>{e(fmt_date(date))}</h1>'
            f'{("<ul class=pol-list>" + toc + "</ul>") if toc else ""}{sections}</div></section>')


def build(api):
    """api: shell, STORIES, cards, fmt_date, CANDS, SITE, THREADS, PAGES_OUT, HERO_CREDITS, PREVIEW. Call after every other generator has run."""
    GATED.clear()
    shell, fmt_date = api["shell"], api["fmt_date"]
    preview = bool(api.get("PREVIEW"))
    home = load_home()
    daily, _bad = load_daily(include_drafts=preview)
    groups = briefings(daily)
    ed_rec = next((rs[0] for rs in groups.values() if rs[0].get("blocks")), None)
    api = dict(api, _edition=ed_rec)
    disc = json.loads((ROOT / "data" / "discovery.json").read_text(encoding="utf-8"))
    hubs = disc["hubs"]

    # Daily pages are written first so the landing's links to them resolve against the built routes.
    d = home["daily"]
    for dt, rs in groups.items():
        is_draft = any(r["status"] != "approved" for r in rs)
        page = render_daily_briefing(dt, rs, fmt_date)
        shell(rs[0]["title"], rs[0]["dek"][:155], f"/politics/daily/{dt}/", page, nav="politics", css=("politics",), js=("common",), bodyclass="pol-home",
              noindex=is_draft, sitemap=not is_draft)
        api["PAGES_OUT"].setdefault(f"/politics/daily/{dt}/", "")
    if groups:
        items = "".join(
            f'<li><a href="/politics/daily/{e(dt)}/"><span class="pol-ruled__t">{e(fmt_date(dt))}: {e(rs[0]["title"])}</span><span class="pol-ruled__arrow" aria-hidden="true">→</span></a>'
            f'<span class="pol-ruled__m">{len(rs)} {"story" if len(rs) == 1 else "stories"}{" / DRAFT PREVIEW" if rs[0]["status"] != "approved" else ""}</span></li>' for dt, rs in groups.items())
        inner = f'<ul class="pol-ruled">{items}</ul>'
    else:
        inner = f'<p class="pol-daily__note">{e(d["empty"])}</p>'
    idx = (f'<section class="pol-page"><div class="pol-page__in"><div class="breadcrumb"><a href="/">Home</a> / <a href="/politics/">Politics</a> / The Daily Signal</div>'
           f'<div class="pol-eyebrow">{e(d["eyebrow"])}</div><h1>{e(d["h2"])}</h1><p class="pol-deck">{e(d["standfirst"])}</p>{inner}</div></section>')
    shell("The Daily Signal", d["standfirst"][:155], "/politics/daily/", idx, nav="politics", css=("politics",), js=("common",), bodyclass="pol-home")

    body = (hero_duochrome(home["hero"]) + daily_strip(api, d, groups) + accountability_feature(api, home["accountability"])
            + f'<div class="pol-tiles">{election_tile(api, home["election"], hubs)}{money_tile(api, home["money"])}{record_tile(api, home["record"])}</div>'
            + state_bar(api, home["election"], hubs)
            + f'<div class="pol-duo-row">{signals_tile(api, home["signals"])}{reporting_list(api, home["reporting"], api["SITE"], api["THREADS"])}</div>'
            + evidence_band(api, home["source"]))
    shell(home["meta"]["title"], home["meta"]["description"], "/politics/", body, nav="politics", css=("politics",), js=("common", "politics"), bodyclass="pol-home")
    return list(GATED)
