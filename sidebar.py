"""Look Learn Find sidebar: state registry, discovery selection and server-rendered rail markup.

Build-time only (stdlib). Selection is deterministic and runs here; the browser fetches the precomputed
per-article result (/data/discovery/<id>.json) when the reader changes the state lens, so Python and
JavaScript never disagree. Only items in data/discovery.json are eligible.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
META = json.loads((ROOT / "data" / "discovery.json").read_text(encoding="utf-8"))
CREDITS = json.loads((ROOT / "data" / "elections" / "hero_credits.json").read_text(encoding="utf-8"))
e = html.escape

STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}
FORMATS = (("look", "Look", "/look/"), ("learn", "Learn", "/learn/"), ("find", "Find", "/find/"))
HUBS = META["hubs"]
THREADS = META["threads"]
EXPIRY = "2026-11-04"  # after the general election the editorial picks must be reviewed


def validate(pages):
    """Every state code, hub URL and guide URL in the metadata must be a built page. Returns a list of problems."""
    bad = []
    for code, h in HUBS.items():
        if code not in STATES:
            bad.append(f"hub {code}: not in the state registry")
        for url in [h["url"]] + [g[1] for g in h["guides"]]:
            if url not in pages:
                bad.append(f"hub {code}: {url} is not a built page")
    for n in META["national"]:
        if n["url"] not in pages:
            bad.append(f"national {n['id']}: {n['url']} is not a built page")
    for sid, m in META["stories"].items():
        for c in m["states"]:
            if c not in STATES:
                bad.append(f"story {sid}: unknown state {c}")
        if m["thread"] not in THREADS:
            bad.append(f"story {sid}: unknown thread {m['thread']}")
        for r in m["related"]:
            if r["id"] not in META["stories"]:
                bad.append(f"story {sid}: related {r['id']} has no metadata")
    return bad


def _img(key, alt, ai=None):
    if ai is None:
        ai = bool(CREDITS.get(key, {}).get("ai")) or key.startswith("s") and key[1:2].isdigit()
    return {"image": f"/img/elections/thumb/{key}.jpg", "alt": alt, "ai": bool(ai)}


class Catalog:
    """Published politics reports plus state guides, built from the loaded STORIES."""

    def __init__(self, stories, fmt_date):
        self.items = {}
        for s in stories:
            m = META["stories"].get(s["slug"])
            if not m or s.get("layout") != "report":
                continue
            _HEROES.add(s["hero"]) if s.get("hero") else None
            im = _img(s["hero"], s.get("hero_alt", "")) if s.get("hero") else {"image": "", "alt": "", "ai": False}
            self.items[s["slug"]] = dict(
                id=s["slug"], url=s["path"], kind=s.get("format", "Report"), title=s["title"], short=m["short"],
                date=s.get("date", ""), states=m["states"], thread=m["thread"], subject=m["subject"], priority=m["priority"],
                related=m["related"], category="politics", format="learn", hero=s.get("hero", ""), **im)
        self.national = []
        for n in META["national"]:
            ik = n["image"]
            self.national.append(dict(id=n["id"], url=n["url"], kind=n["kind"], title=n["title"], short=n["short"], date="", states=[],
                                      thread="", subject="National", priority=n["priority"], related=[], category="politics", format="learn",
                                      hero="", hook=n["hook"], image=f"/img/elections/thumb/{ik}.jpg", alt=n["image_alt"], ai=False))

    # ---- coverage
    def reports(self, code):
        return [i for i in self.items.values() if code in i["states"]]

    def coverage(self, code):
        name = STATES[code]
        n = len(self.reports(code))
        hub = HUBS.get(code)
        parts = []
        if n:
            parts.append(f"{n} report{'s' if n != 1 else ''}")
        if hub:
            parts.append("a state guide")
        if not parts:
            return f"No LookLearnFind coverage of {name} yet."
        txt = f"{name}: " + " and ".join(parts)
        if not n:
            txt += ", no reporting yet"
        return txt + "."

    def hub_item(self, code):
        h = HUBS.get(code)
        if not h:
            return None
        guides = ", ".join(g[0] for g in h["guides"])
        name = STATES[code]
        im = _img(h["image"], h.get("image_alt", f"Illustration for the {name} State of the Race guide."), ai=h["image"] != "us-capitol")
        return dict(id=f"hub-{code}", url=h["url"], kind="State guide", title=f"{name}: State of the Race", short=f"{name}: every contest on the ballot",
                    hook=f"Guides: {guides}.", states=[code], **im)

    # ---- selection
    @staticmethod
    def _order(items):
        return sorted(items, key=lambda i: (-i["priority"], -int(i["date"].replace("-", "") or 0), i["id"]))

    def select(self, cur, lens):
        """Return the two-slot result for article `cur` under `lens` ('ALL' or a state code)."""
        others = [i for i in self.items.values() if i["id"] != cur["id"]]
        slots = []
        if lens == "ALL":
            related = [self.items[r["id"]] for r in cur["related"] if r["id"] in self.items]
            thread = related[0] if related else next(iter(self._order([i for i in others if i["thread"] == cur["thread"]])), None)
            if thread:
                reason = next((r["reason"] for r in cur["related"] if r["id"] == thread["id"]), f"Also in {THREADS[cur['thread']]}")
                slots.append(("Along this thread", thread, reason))
            pool = [i for i in self._order(others) if not thread or i["id"] != thread["id"]]
            # diversify: prefer a different state from the thread item and the current article
            seen = set(cur["states"]) | set((thread or {}).get("states", []))
            pick = next((i for i in pool if not set(i["states"]) & seen), pool[0] if pool else None)
            if pick:
                slots.append(("On our radar", pick, "Editor's pick" + (f" · {STATES[pick['states'][0]]}" if len(pick["states"]) == 1 else "")))
            return dict(lens="ALL", status="Suggestions: all states.", hub=None, slots=self._pack(slots), gap=False)
        pool = [i for i in others if lens in i["states"]]
        related_ids = [r["id"] for r in cur["related"]]
        thread = next((i for i in pool if i["id"] in related_ids), None)
        reason = None
        if thread:
            reason = next(r["reason"] for r in cur["related"] if r["id"] == thread["id"])
        else:
            thread = next(iter(self._order([i for i in pool if i["thread"] == cur["thread"]])), None)
            if thread:
                reason = f"Also in {THREADS[cur['thread']]}"
        if thread:
            slots.append(("Along this thread", thread, reason))
        rest = [i for i in self._order(pool) if not thread or i["id"] != thread["id"]]
        hub = self.hub_item(lens)
        if rest:
            slots.append(("On our radar", rest[0], f"Editor's pick · {STATES[lens]}"))
        elif hub:
            slots.append(("On our radar", hub, f"Where every {STATES[lens]} contest is listed"))
        gap = not slots
        if len(slots) < 2:
            nat = next(iter(self._order(self.national)), None)
            if nat:
                slots.append(("National context", nat, "National, not specific to " + STATES[lens]))
        name = STATES[lens]
        status = f"Suggestions: {name}." if not gap else f"{self.coverage(lens)} Showing national context."
        if not gap and lens not in cur["states"]:
            status += f" Reading: {', '.join(STATES[c] for c in cur['states']) or 'a national story'}."
        return dict(lens=lens, status=status, hub=HUBS[lens]["url"] if lens in HUBS else None, slots=self._pack(slots), gap=gap, coverage=self.coverage(lens))

    @staticmethod
    def _pack(slots):
        out = []
        for label, i, reason in slots:
            out.append(dict(slot=label, id=i["id"], url=i["url"], kind=i["kind"], title=i["short"], full=i["title"], image=i["image"], alt=i["alt"], ai=i["ai"], reason=reason))
        return out

    def default_lens(self, cur):
        return cur["states"][0] if len(cur["states"]) == 1 else "ALL"

    def all_results(self, cur):
        res = {"ALL": self.select(cur, "ALL")}
        for code in STATES:
            res[code] = self.select(cur, code)
        for r in res.values():
            r["lens_name"] = "All states" if r["lens"] == "ALL" else STATES[r["lens"]]
        return dict(context=cur["id"], catalog_version=META["version"], expires=EXPIRY, results=res)


# ---------------------------------------------------------------- markup
def _brand(cls="brand-large"):
    return (f'<a class="brand {cls}" href="/" aria-label="LookLearnFind home"><img class="brand-fallback" src="/img/logo-cream.png" alt="LOOK LEARN FIND 01" width="1040" height="701">'
            '<span class="word look" aria-hidden="true"></span><span class="word learn" aria-hidden="true"></span><span class="word find" aria-hidden="true"></span></a>')


def _format_nav(fmt, cls="format-nav", label="Formats"):
    return f'<nav class="{cls}" aria-label="{label}">' + "".join(
        f'<a href="{h}"' + (' aria-current="page"' if k == fmt else "") + f'>{t}</a>' for k, t, h in FORMATS) + "</nav>"


def card_html(slot):
    """One recommendation. `slot` is a packed item. The thread card is cream, the radar and national cards sit open on petrol."""
    label = slot["slot"]
    cls = "thread-card" if label == "Along this thread" else "radar-card"
    ai = '<span class="ai-tag">AI illustration</span>' if slot["ai"] else ""
    img = f'<span class="thumb"><img src="{e(slot["image"])}" alt="{e(slot["alt"])}" width="300" height="200" decoding="async">{ai}</span>' if slot["image"] else ""
    return (f'<a class="rec {cls}" href="{e(slot["url"])}" data-slot="{e(label)}">{img}<span class="rec-body"><span class="eyebrow">{e(label)}</span>'
            f'<span class="card-title">{e(slot["title"])}</span><span class="rec-kind">{e(slot["kind"])} · {e(slot["reason"])}</span></span><span class="arrow" aria-hidden="true">→</span></a>')


def recs_html(result):
    if not result["slots"]:
        return '<p class="gap">No eligible suggestions here yet.</p>'
    return "".join(card_html(s) for s in result["slots"])


def state_form(lens, prefix):
    opts = '<option value="ALL"' + (" selected" if lens == "ALL" else "") + ">All states</option>" + "".join(
        f'<option value="{c}"' + (" selected" if c == lens else "") + f">{e(n)}</option>" for c, n in STATES.items())
    return (f'<div class="state-form" data-state-form hidden><label class="eyebrow" for="{prefix}-state">Your politics lens</label>'
            f'<div class="select-wrap"><select id="{prefix}-state" name="state" data-state-select>{opts}</select><span aria-hidden="true">⌄</span></div>'
            '<p class="state-help">Choose a state to explore its coverage.</p><p class="lens-status" data-lens-status role="status" aria-live="polite"></p>'
            '<a class="coverage-link" data-coverage-link hidden></a></div>')


def noscript_states():
    links = "".join(f'<li><a href="{h["url"]}">{e(STATES[c])}</a></li>' for c, h in HUBS.items())
    return f'<noscript><details class="state-fallback"><summary>State coverage</summary><ul>{links}</ul></details></noscript>'


def outline_html(toc):
    if not toc:
        return ""
    items = "".join(f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in toc)
    # Short outlines (4 or fewer) start open. Longer ones start closed so the two recommendations stay on screen at laptop
    # heights; the script opens them on tall screens and the summary names the section being read.
    op = " open" if len(toc) <= 4 else ""
    return (f'<details class="outline" data-outline{op}><summary class="eyebrow">In this story<span class="cur" data-outline-cur></span></summary><ol>{items}</ol></details>')


def panel(cur, result, lens, toc, prefix, subject_link=True):
    sub = (f'<div class="context-nav"><a href="/politics/"><span aria-hidden="true">←</span> Politics</a><p>{e(cur["subject"])}</p></div>')
    cov = ""
    if result["hub"]:
        name = STATES.get(result["lens"], "")
        cov = f'<a class="coverage-link" data-coverage-link href="{result["hub"]}">View {e(name)} coverage <span aria-hidden="true">→</span></a>'
    form = state_form(lens, prefix).replace('<a class="coverage-link" data-coverage-link hidden></a>', cov or '<a class="coverage-link" data-coverage-link hidden></a>')
    status = result["status"] if lens != "ALL" else ""
    form = form.replace('role="status" aria-live="polite"></p>', f'role="status" aria-live="polite">{e(status)}</p>')
    return (f'{form}{noscript_states()}{sub}{outline_html(toc)}<div class="recommendations" data-recs>{recs_html(result)}</div>'
            '<a class="source-link" href="#sources"><span>Go to the source</span><span aria-hidden="true">→</span></a>')


def render(cur, cat, toc):
    """Return (rail_html, mobile_html, data_json) for one article."""
    lens = cat.default_lens(cur)
    result = cat.select(cur, lens)
    data = cat.all_results(cur)
    fmt = cur["format"]
    rail = (f'<aside class="llf-rail" id="llf-rail" aria-label="Look Learn Find sidebar" data-context="{e(cur["id"])}" data-default-lens="{lens}">'
            f'<div class="rail-scroll">{_brand()}{_format_nav(fmt)}{panel(cur, result, lens, toc, "rail")}</div></aside>')
    mobile = (f'<div class="mobile-bar" role="region" aria-label="Look Learn Find">{_brand("brand-small")}{_format_nav(fmt, "format-nav mobile-formats", "Formats")}'
              '<button type="button" class="explore-btn" data-explore aria-haspopup="dialog">Explore</button></div>'
              f'<dialog class="explore-sheet" id="explore-sheet" aria-labelledby="explore-title"><div class="dialog-top"><h2 id="explore-title">Explore</h2>'
              f'<button type="button" data-close-sheet>Close</button></div><div class="sheet-body">{panel(cur, result, lens, toc, "sheet")}</div></dialog>')
    return rail, mobile, data


def outline_from_body(body):
    return [(a, re.sub(r"<[^>]+>", "", t)) for a, t in re.findall(r'<h2 id="([a-z0-9-]+)">(.*?)</h2>', body)]


def make_thumbs(out):
    """Write 480px-wide thumbnails (full heroes are 200-370 KB each, far too heavy for a 100px rail card)."""
    from PIL import Image
    keys = {i["image"].rsplit("/", 1)[1][:-4] for i in _all_images()}
    dest = Path(out) / "img" / "elections" / "thumb"
    dest.mkdir(parents=True, exist_ok=True)
    for k in sorted(keys):
        src = Path(out) / "img" / "elections" / f"{k}.jpg"
        if not src.exists():
            raise SystemExit(f"sidebar thumbnail source missing: {src}")
        im = Image.open(src).convert("RGB")
        im.thumbnail((480, 480))
        im.save(dest / f"{k}.jpg", "JPEG", quality=78, optimize=True)


def _all_images():
    out = [dict(image=f"/img/elections/thumb/{n['image']}.jpg") for n in META["national"]]
    out += [dict(image=f"/img/elections/thumb/{h['image']}.jpg") for h in HUBS.values()]
    out += [dict(image=f"/img/elections/thumb/{r}.jpg") for r in _HEROES]
    return out


_HEROES = set()
