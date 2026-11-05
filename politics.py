"""Politics landing (/politics/) and Daily Signal index (/politics/daily/).

Driven by data/politics_home.json, data/discovery.json and approved records in data/politics_daily/.
Policy: docs/politics/INDEX.md. Pages are written only through build.shell(); this module has no navigation markup.
Never states a result, margin or call: empty modules show an intentional empty state.
"""
import json
import pathlib
from html import escape as e

ROOT = pathlib.Path(__file__).parent
HOME_FILE = ROOT / "data" / "politics_home.json"
DAILY_DIR = ROOT / "data" / "politics_daily"
REQUIRED_DAILY = ("story_id", "date", "title", "dek", "sources", "author", "editor", "update_log", "status")


def load_home():
    return json.loads(HOME_FILE.read_text(encoding="utf-8"))


def load_daily(directory=None):
    """Approved daily records only, newest first. A record missing a required field is skipped and reported."""
    out, bad = [], []
    for f in sorted((directory or DAILY_DIR).glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        miss = [k for k in REQUIRED_DAILY if not r.get(k)]
        if miss:
            bad.append(f"{f.name}: missing {', '.join(miss)}")
            continue
        if r["status"] == "approved":
            out.append(r)
    out.sort(key=lambda r: r["date"], reverse=True)
    return out, bad


def _module(cls, lab, heading, inner, intro=""):
    i = f'<p class="small pol-intro">{e(intro)}</p>' if intro else ""
    return (f'<section class="pol-mod {cls}" id="{cls}"><div class="wrap"><div class="lab">{e(lab)}</div>'
            f'<h2>{e(heading)}</h2>{i}{inner}</div></section>')


def _empty(msg):
    return f'<div class="empty pol-empty"><b>{e(msg)}</b></div>'


def daily_card(r, fmt_date):
    return (f'<a class="card pol-daily" href="/politics/daily/{e(r["date"])}/"><div class="eyebrow">Daily Signal / {e(fmt_date(r["date"]))}</div>'
            f'<h3>{e(r["title"])}</h3><p>{e(r["dek"])}</p><div class="kindline">{e(r["story_id"])}</div></a>')


def render_daily_record(r, fmt_date):
    src = "".join(f'<li><a href="{e(s["url"])}" rel="noopener">{e(s["label"])}</a>, {e(fmt_date(s.get("date", "")))}</li>' for s in r["sources"])
    log = "".join(f'<li>{e(fmt_date(u["date"]))}: {e(u["note"])}</li>' for u in r["update_log"])
    body = r.get("body_html", "")
    return (f'<section class="page-head"><div class="wrap"><div class="breadcrumb"><a href="/">Home</a> / <a href="/politics/">Politics</a> / '
            f'<a href="/politics/daily/">Daily Signal</a> / {e(fmt_date(r["date"]))}</div><div class="kicker">DAILY SIGNAL<i></i></div>'
            f'<h1 class="display">{e(r["title"])}</h1><p class="dek">{e(r["dek"])}</p>'
            f'<p class="small">Story ID {e(r["story_id"])}. By {e(r["author"])}. Edited by {e(r["editor"])}.</p></div></section>'
            f'<section class="pol-mod"><div class="wrap">{body}<h2 id="sources">Sources</h2><ul class="pol-list">{src}</ul>'
            f'<h2 id="updates">Update log</h2><ul class="pol-list">{log}</ul></div></section>')


def build(api):
    """api: dict with shell, STORIES, cards, fmt_date, page_head, contribute_band, CANDS, DISCOVERY."""
    shell, STORIES, cards, fmt_date = api["shell"], api["STORIES"], api["cards"], api["fmt_date"]
    page_head, contribute_band = api["page_head"], api["contribute_band"]
    home = load_home()
    daily, _bad = load_daily()
    disc = json.loads((ROOT / "data" / "discovery.json").read_text(encoding="utf-8"))

    # Hero: phase statement first, so no module can read as a result.
    banner = f'<div class="pol-phase" role="note"><b>Status.</b> {e(home["phase_note"])}</div>'
    head = page_head(e(home["eyebrow"]), e(home["headline"]), e(home["dek"]), crumbs=[("Home", "/"), ("Politics", None)], extra=banner)

    d = home["daily"]
    d_inner = ('<div class="cards">' + "".join(daily_card(r, fmt_date) for r in daily[: d["limit"]]) + "</div>"
               + '<p><a class="link teal" href="/politics/daily/">All Daily Signals ↗</a></p>') if daily else _empty(d["empty"])
    daily_mod = _module("daily-signal", "Daily Signal", d["heading"], d_inner, d["intro"] if daily else d["intro"])

    fs = home["follow_story"]
    stories = [s for s in STORIES if disc["stories"].get(s["path"].strip("/").split("/")[-1], {}).get("thread") == fs["thread"]][: fs["limit"]]
    f_inner = (f'<p class="pol-label">{e(fs["label"])}</p>' + cards(stories)) if stories else _empty("No stories to follow yet.")
    follow_mod = _module("follow-the-story", "Follow the story", fs["heading"], f_inner)

    st = home["states"]
    hubs = disc["hubs"]
    tiles = "".join(
        f'<a class="pol-state" href="{e(hubs[s["code"]]["url"])}"><span class="code">{e(s["code"])}</span><span class="nm">{e(s["name"])}</span>'
        f'<span class="sub">Governor, Senate, House</span></a>' for s in st["list"] if s["code"] in hubs)
    states_mod = _module("explore-a-state", "Explore a state", st["heading"], f'<div class="pol-states">{tiles}</div>', st["intro"])

    rc = home["record"]
    n_tip = sum(1 for c in api["CANDS"] if c["tip"]["url"])
    vals = {"stories": str(len([s for s in STORIES if s.get("category") == "politics"])), "candidates": str(n_tip)}
    items = "".join(f'<div class="pol-stat"><div class="v">{e(i["value"].format(**vals))}</div><div class="l">{e(i["label"])}</div>'
                    f'<div class="n">{e(i["note"])}</div></div>' for i in rc["items"])
    record_mod = _module("the-record", "The Record", rc["heading"], f'<div class="pol-stats">{items}</div>', rc["intro"])

    site = api["SITE"]
    th = [x for x in api["THREADS"] if x["category"] == "politics"]
    rows = "".join(f'<a class="row" href="/threads/{e(x["slug"])}/"><span class="n">{i:02d}</span><span class="t">{e(x["title"])}</span>'
                   f'<span class="d">{e(x["summary"])}</span><span class="ar">↗</span></a>' for i, x in enumerate(th, 1))
    chips = "".join(f'<a class="chip" href="/topics/{e(x["slug"])}/">{e(x["label"])} ↗</a>' for x in site["topics"] if x["category"] == "politics")
    threads_mod = _module("threads", "Threads", "Follow a thread", f'<div class="rows">{rows}</div><div class="chips pol-chips">{chips}</div>')

    ra = home["radar"]
    radar_mod = _module("on-our-radar", "On our radar", ra["heading"], _empty(ra["empty"]))

    v = home["verify"]
    links = "".join(f'<a class="row" href="{e(l["href"])}"><span class="n">→</span><span class="t">{e(l["label"])}</span>'
                    f'<span class="d">{e(l["note"])}</span><span class="ar">↗</span></a>' for l in v["links"])
    verify_mod = _module("watch-read-verify", "Verify", v["heading"], f'<div class="rows">{links}</div>')

    a = home["action"]
    action = (f'<section class="pol-mod pol-action"><div class="wrap"><p><b>{e(a["label"])}</b> '
              f'<a class="link teal" href="{e(a["href"])}" rel="noopener">theissuesparty.org ↗</a></p><p class="small">{e(a["note"])}</p></div></section>')

    body = head + daily_mod + follow_mod + states_mod + record_mod + threads_mod + radar_mod + verify_mod + action + contribute_band()
    shell("Politics: the public record", home["dek"][:155], "/politics/", body, nav="politics", css=("politics",), js=("common",))

    # Daily index
    di = (f'<div class="cards">{"".join(daily_card(r, fmt_date) for r in daily)}</div>' if daily else _empty(home["daily"]["empty"]))
    dhead = page_head("DAILY SIGNAL", "One sourced item a day", home["daily"]["intro"],
                      crumbs=[("Home", "/"), ("Politics", "/politics/"), ("Daily Signal", None)])
    shell("Daily Signal", home["daily"]["intro"][:155], "/politics/daily/", dhead + f'<section class="pol-mod"><div class="wrap">{di}</div></section>',
          nav="politics", css=("politics",), js=("common",))
    for r in daily:
        shell(r["title"], r["dek"][:155], f'/politics/daily/{r["date"]}/', render_daily_record(r, fmt_date), nav="politics", css=("politics",), js=("common",))
