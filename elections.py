"""LookLearnFind election pages (stdlib only). Imported by build.py.

Reads structured, verified data from data/elections/<ST>/ and renders:
  /elections/2026/florida/                 StateLanding   (the State Board)
  /elections/2026/florida/governor/        StateOfficeGuide
  /elections/2026/florida/senate/          StateOfficeGuide
  /elections/2026/florida/house/           HouseDirectory (atlas, cards and table)
  /elections/2026/florida/house/<n>/       one page per district
  /about/election-methods/                 methods, definitions, TIP grade formula
and the components used by reported articles (layout: report): MarketDeltaChart, SpendingChart, CandidateCard, TIPIssueRecord, SourcesBlock.

Nothing here invents a value. A missing value renders as an explicit "not on file" state. Charts plot only captured points.
"""
import json, re, datetime, html as _html
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).parent
D = ROOT / "data" / "elections"
API = {}
ST_URL = "/elections/2026/florida/"

# One record per state. The page builders read the active state from SX, so Florida output is unchanged and Illinois reuses the same templates.
STATES = {
    "FL": dict(code="FL", name="Florida", slug="florida", ndist=28, asof="2026-10-23", record_label="Florida Division of Elections record",
               source_note=('Sources: Florida Division of Elections candidate lists (captured {cap}); OpenFEC candidate committee totals and Schedule E ({fec}); '
                            'Kalshi public market data ({mk}); TIP Issue Grades from TIP ({tip}).'), finance=True, counties=True),
    "IL": dict(code="IL", name="Illinois", slug="illinois", ndist=17, asof="2026-10-28", record_label="Candidate listing (Green Papers)",
               source_note=('Sources: candidate listing transcribed from Green Papers on {cap} and cross-checked against OpenFEC candidate records and TIP; the Illinois State Board of Elections list could not be read '
                            '(HTTP 403), so this roster is not an official or complete list; Kalshi public market data ({mk}); TIP Issue Grades from TIP ({tip}).'), finance=False, counties=False),
}
SX = dict(STATES["FL"])
GAPS = []           # directory gaps (a listed candidate with no TIP profile) for states whose roster is not yet fully on TIP; reported, not blocking

# ------------------------------------------------------------------ data
def _j(p, default=None):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

FL = {}             # the active state's data (the name is historical: Florida was first)
def _load_state(code):
    global ST_URL
    SX.clear(); SX.update(STATES[code])
    ST_URL = f"/elections/2026/{SX['slug']}/"
    d = D / code
    FL["roster"] = _j(d / "roster.json")
    cj = _j(d / "candidates.json")
    FL["issues"], FL["cands"], FL["tip_as_of"] = cj["issues"], cj["candidates"], cj["as_of_utc"]
    FL["fec"] = _j(d / "finance_fec.json", {"as_of_utc": "", "totals": {}})
    FL["markets"] = _j(d / "markets.json")
    FL["districts"] = _j(d / "districts.json")
    FL["portraits"] = _j(d / "portraits.json", {})
    FL["heroes"] = _j(D / "hero_credits.json", {})
    FL["ie"] = _j(d / "ie_all.json", {"candidates": {}, "captured_at_utc": ""})
    FL["by_id"] = {c["id"]: c for c in FL["cands"]}
    FL["by_race"] = {}
    for c in FL["cands"]:
        FL["by_race"].setdefault(c["race"], []).append(c)
    for r, lst in FL["by_race"].items():
        lst.sort(key=_order)

def load():
    _load_state("FL")
    FL["mi"] = {
        "cands": _j(D / "MI/candidates.json")["candidates"], "fin": _j(D / "MI/finance_fec.json"),
        "d": _j(D / "MI/kalshi_SENATEMI-26-D.json"), "r": _j(D / "MI/kalshi_SENATEMI-26-R.json"),
        "portraits": _j(D / "MI/portraits.json", {}),
    }

def _last(name):
    w = [x for x in re.sub(r'["]', "", name).split() if x.lower().strip(".") not in ("jr", "sr", "ii", "iii", "iv")]
    return w[-1].lower() if w else ""

def _order(c):
    pc = c["party_code"]
    grp = 0 if pc == "REP" else 1 if pc == "DEM" else 4 if pc == "WRI" else 3 if pc == "NPA" else 2
    return (grp, c["party"] if grp == 2 else "", _last(c["name"]))

# ------------------------------------------------------------------ formatting
def money(x, exact=False):
    if x is None:
        return "—"
    x = float(x)
    if exact:
        return f"${x:,.2f}"
    if x >= 1e6:
        return f"${x/1e6:.1f}M"
    if x >= 1e3:
        return f"${x/1e3:.0f}K"
    return f"${x:,.0f}"

def cents(v):
    if v in (None, "", "None"):
        return "—"
    return f"{round(float(v) * 100)}¢"

def _fmt(d, fmt):
    """strftime with a no-zero-pad day that also works on Windows (where %-d is not supported)."""
    return d.strftime(fmt.replace("%-d", "@@D@@")).replace("@@D@@", str(d.day))

def dstr(s, fmt="%b %-d, %Y"):
    try:
        return _fmt(datetime.date.fromisoformat(str(s)[:10]), fmt)
    except Exception:
        return str(s or "")

def utc_stamp(s):
    try:
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return _fmt(d, "%b %-d, %Y, %H:%M UTC")
    except Exception:
        return s

PLET = {"DEM": "D", "REP": "R", "LPF": "L", "NPA": "N", "WRI": "W", "IND": "I", "FFP": "F", "ASP": "A", "AMC": "A", "WCP": "C"}

def chip(c):
    return f'<span class="pchip" title="{e(c["party"])}">{PLET.get(c["party_code"], "?")}</span>'

def initials(name):
    w = [x for x in re.sub(r'"[^"]*"', "", name).split() if x[0].isalpha()]
    return (w[0][0] + w[-1][0]).upper() if len(w) > 1 else name[:2].upper()

def portrait(c, cls="ph"):
    p = FL["portraits"].get(c["id"], {})
    if p.get("result") == "ok":
        return (f'<span class="{cls}"><img src="/img/elections/portraits/{e(c["id"])}.jpg" alt="Portrait of {e(c["name"])}" loading="lazy" width="240" height="300"></span>')
    return f'<span class="{cls} mono" role="img" aria-label="{e(c["name"])}: no licensed portrait on file">{e(initials(c["name"]))}</span>'

def descr(c):
    bits = []
    if c["incumbent"]:
        bits.append("Incumbent")
    if c["office"] == "governor" and c.get("running_mate"):
        bits.append(f'Running mate {c["running_mate"]}')
    if c["party_code"] == "WRI":
        bits.append("Write-in candidate")
    return " · ".join(bits)

def state_link(c):
    return f'<a href="{e(c["state_url"])}" rel="noopener">{e(SX["record_label"])} ↗</a>'

# ------------------------------------------------------------------ TIP issue record
def issue_strip(c, big=False):
    tip, items = c.get("tip"), []
    for iss in FL["issues"]:
        icon = "issue-" + iss["slug"].replace("_", "-")
        g = (tip or {}).get("grades", {}).get(iss["slug"])
        if g and g["state"] == "graded":
            lab = f'{iss["name"]}: TIP Issue Grade {g["grade"]}, {g["aligned"]} of {g["recorded"]} recorded acts aligned (computed {dstr(g["computed_at"])})'
            items.append(f'<li class="ig g" title="{e(lab)}"><svg class="ico" aria-hidden="true"><use href="/img/icons.svg#{icon}"/></svg><b>{e(g["grade"])}</b><span class="sr">{e(lab)}</span></li>')
        elif tip:
            lab = f'{iss["name"]}: not graded, no recorded congressional acts on this issue'
            items.append(f'<li class="ig n" title="{e(lab)}"><svg class="ico" aria-hidden="true"><use href="/img/icons.svg#{icon}"/></svg><b>—</b><span class="sr">{e(lab)}</span></li>')
        else:
            lab = f'{iss["name"]}: no TIP record yet for this candidate'
            items.append(f'<li class="ig x" title="{e(lab)}"><svg class="ico" aria-hidden="true"><use href="/img/icons.svg#{icon}"/></svg><b>·</b><span class="sr">{e(lab)}</span></li>')
    return f'<ul class="issue-strip{" big" if big else ""}" aria-label="TIP Issue Grades for {e(c["name"])}">' + "".join(items) + "</ul>"

def graded_count(c):
    t = c.get("tip")
    return sum(1 for g in (t or {}).get("grades", {}).values() if g["state"] == "graded") if t else 0

CUR = [""]          # page currently being built (for publishing-rule reporting)
VIOL = []           # (page, rule, detail)

def violate(rule, detail):
    item = (CUR[0], rule, detail)
    if item not in VIOL:
        VIOL.append(item)

def tip_button(c):
    t = c.get("tip")
    if t and t.get("url"):
        if t.get("grades_url"):
            return (f'<a class="btn-o" href="{e(t["grades_url"])}" rel="noopener">View congressional record on TIP →</a>'
                    f'<span class="small"><a href="{e(t["url"])}" rel="noopener">TIP governor profile ↗</a></span>')
        return f'<a class="btn-o" href="{e(t["url"])}" rel="noopener">View on TIP →</a>'
    if SX["code"] != "FL":
        item = (SX["code"], c["name"])
        if item not in GAPS:
            GAPS.append(item)
    else:
        violate("R1 no TIP profile", c["name"])
    return '<span class="btn-o off" aria-disabled="true">No TIP record yet</span>'

def tip_panel(cands=None):
    rows = "".join(
        f'<li><svg class="ico" aria-hidden="true"><use href="/img/icons.svg#issue-{i["slug"].replace("_", "-")}"/></svg><span>{e(i["name"])}'
        + (f'<small>{e(i["short"])}</small>' if i["slug"].startswith("us-") else "") + "</span></li>" for i in FL["issues"])
    n = len(cands or [])
    stat = ""
    if cands:
        g = sum(1 for c in cands if graded_count(c))
        stat = f'<p class="tip-stat"><b>{g} of {n}</b> candidates on this page have at least one TIP Issue Grade.</p>'
    return f'''<aside class="tip-panel" aria-label="TIP issue records"><div class="uc teal">TIP issue records <a href="/about/election-methods/#grades" aria-label="How grades work">?</a></div>
<ul class="issue-list">{rows}</ul>
<div class="legend"><span><b class="lg g">A+</b> TIP Issue Grade (recorded acts)</span><span><b class="lg n">—</b> Not graded: no recorded congressional acts</span><span><b class="lg x">·</b> No TIP record yet</span></div>
{stat}<p class="small"><a class="link teal" href="/about/election-methods/#grades">How we grade ↗</a></p></aside>'''

# ------------------------------------------------------------------ finance + markets + outside spending
def fec_totals(c):
    fid = c.get("fec_candidate_id")
    return (FL["fec"]["totals"].get(fid) if fid and fid[0] in "HS" and c["office"] in ("house", "senate") else None)

def finance_line(c, compact=False):
    if not SX["finance"]:
        return ""
    t = fec_totals(c)
    if not t and c["office"] == "governor":
        return '<div class="fin none"><span>Governor candidates file with the state, not the FEC. See the money section.</span></div>'
    if not t:
        txt = "No FEC candidate-committee report on file" if c["party_code"] != "WRI" else "Write-in: no FEC committee on file"
        return f'<div class="fin none"><span>{txt}</span></div>'
    per = f'{dstr(t["coverage_start_date"], "%b %-d, %Y")} – {dstr(t["coverage_end_date"], "%b %-d, %Y")}'
    cash = float(t["cash_on_hand_end_period"]) if t.get("cash_on_hand_end_period") not in (None, "") else None
    if compact:
        return f'<div class="fin"><b>{money(t["receipts"])}</b><span>raised · through {dstr(t["coverage_end_date"], "%b %-d")}</span></div>'
    return (f'<div class="fin"><b>{money(t["receipts"])}</b><span>Candidate committee receipts</span>'
            f'<small>Spent {money(t["disbursements"])} · Cash on hand {money(cash)}<br>FEC report period {per}</small></div>')

def dedupe_ie(rows):
    """One row per (committee, transaction): the 24/48-hour notice when present, since the same spending is re-reported on periodic filings."""
    best = {}
    for r in rows:
        if r.get("memo_code") == "X":      # memo entries repeat another line; FEC excludes them from totals
            continue
        k = (r.get("committee_name"), r.get("transaction_id"), r.get("expenditure_amount"), (r.get("expenditure_date") or "")[:10])
        if k not in best or (r.get("is_notice") and not best[k].get("is_notice")):
            best[k] = r
    return list(best.values())

def race_ie(race):
    """-> (rows with candidate attached, latest date) for the race."""
    out, latest = [], ""
    for c in FL["by_race"].get(race, []):
        v = FL["ie"]["candidates"].get(c.get("fec_candidate_id") or "")
        if not v:
            continue
        for r in dedupe_ie(v["transactions"]):
            amt = r.get("expenditure_amount") or 0
            if amt <= 0:
                continue
            out.append({**r, "cand": c})
            latest = max(latest, (r.get("expenditure_date") or "")[:10])
    return out, latest

def ie_total(race):
    rows, latest = race_ie(race)
    return sum(r["expenditure_amount"] for r in rows), latest, len(rows)

def market_card(race, title="What the market says"):
    m = (FL["markets"]["races"] or {}).get(race)
    if not m or "contracts" not in m:
        return (f'<div class="mk none"><h3>{e(title)}</h3><p class="small">No Kalshi contract for this race was found on the capture date '
                f'({utc_stamp(FL["markets"]["captured_at_utc"])}).</p></div>')
    cs = sorted(m["contracts"], key=lambda x: -(float(x["last"] or 0)))
    cells = "".join(
        f'<div class="q"><span class="qn">{e(c["yes_label"])}</span><span class="qp">{cents(c["last"])}</span>'
        f'<span class="qsub">bid {cents(c["yes_bid"])} · ask {cents(c["yes_ask"])}</span></div>' for c in cs)
    rule = (cs[0].get("rules") or "").split(".")[0]
    return (f'<div class="mk"><h3>{e(title)}</h3><p class="small">Party-winner contracts: each resolves on the winning party and the name shown is only a label. Prices are market-implied estimates, not forecasts or vote shares.</p>'
            f'<div class="quotes">{cells}</div><p class="small">{e(m["title"])} Last trade shown. Captured {utc_stamp(FL["markets"]["captured_at_utc"])}. '
            f'<a href="{e(m["url"])}" rel="noopener">Kalshi market ↗</a></p>'
            + (f'<details class="small"><summary>Contract rule</summary>{e(rule)}.</details>' if rule else "") + "</div>")

# ------------------------------------------------------------------ candidate cards
def candidate_card(c, size="lg", finance=True):
    extra = ""
    if c["primary"] in ("Won", "Unopposed"):
        extra = f'<span class="tag">{"Won primary" if c["primary"] == "Won" else "Unopposed in primary"}</span>'
    return f'''<article class="ccard {size}" id="c-{e(c["id"])}">
<div class="cc-top">{portrait(c)}<div><div class="nm">{chip(c)}<h3>{e(c["name"])}</h3></div><div class="ds">{e(c["party"])}{(" · " + e(descr(c))) if descr(c) else ""}</div>{extra}</div></div>
{finance_line(c, compact=(size == "sm")) if finance else ""}
{issue_strip(c)}{('<p class="small gnote">Grades come from his congressional record, shown on TIP\'s congressional profile.</p>' if (c.get("tip") or {}).get("grades_url") else "")}
<div class="cc-links">{tip_button(c)}<span class="small">{state_link(c)}</span></div></article>'''

def mini_row(c):
    return (f'<li>{chip(c)}<span class="n">{e(c["name"])}</span>' + ('<i class="inc" title="Incumbent"></i>' if c["incumbent"] else "") + "</li>")

# ------------------------------------------------------------------ charts
def _scale(v, a, b, lo, hi):
    return lo + (v - a) * (hi - lo) / ((b - a) or 1)

def delta_chart():
    mi = FL["mi"]
    W, H, L, R, T, B = 860, 360, 52, 24, 24, 52
    def series(rows, key="close"):
        out = []
        for r in rows:
            v = r.get(key)
            if v in (None, ""):
                out.append(None)
            else:
                out.append((r["end_utc"], float(v)))
        return out
    def draw(rows, ts0, ts1, lo, hi, step_label, events, band_rows=None, tag=""):
        t0, t1 = datetime.datetime.fromisoformat(ts0.replace("Z", "+00:00")), datetime.datetime.fromisoformat(ts1.replace("Z", "+00:00"))
        X = lambda s: _scale(datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp(), t0.timestamp(), t1.timestamp(), L, W - R)
        Y = lambda v: _scale(v, lo, hi, H - B, T)
        g = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Kalshi price history for the El-Sayed contract {tag}">']
        for v in range(int(lo * 100), int(hi * 100) + 1, 5):
            y = Y(v / 100)
            g.append(f'<line x1="{L}" x2="{W-R}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/><text x="{L-8}" y="{y+4:.1f}" class="ax" text-anchor="end">{v}¢</text>')
        for s, lab in step_label:
            x = X(s)
            g.append(f'<text x="{x:.1f}" y="{H-B+20}" class="ax" text-anchor="middle">{e(lab)}</text><line x1="{x:.1f}" x2="{x:.1f}" y1="{H-B}" y2="{H-B+5}" class="tick"/>')
        if band_rows:
            top = [(X(r["end_utc"]), Y(float(r["ask_close"]))) for r in band_rows if r.get("ask_close") not in (None, "") and r.get("bid_close") not in (None, "")]
            bot = [(X(r["end_utc"]), Y(float(r["bid_close"]))) for r in band_rows if r.get("ask_close") not in (None, "") and r.get("bid_close") not in (None, "")]
            if top:
                pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in top) + " " + " ".join(f"{x:.1f},{y:.1f}" for x, y in reversed(bot))
                g.append(f'<polygon points="{pts}" class="band"/>')
        for s, lab, cls in events:
            x = X(s)
            if L <= x <= W - R:
                g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{T}" y2="{H-B}" class="ev {cls}"/><text x="{x+5:.1f}" y="{T+12}" class="evl">{e(lab)}</text>')
        run, paths = [], []
        for r in rows:
            v = r.get("close")
            if v in (None, ""):
                if run: paths.append(run); run = []
            else:
                run.append((X(r["end_utc"]), Y(float(v))))
        if run: paths.append(run)
        for p in paths:
            if len(p) > 1:
                g.append('<polyline class="line" points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in p) + '"/>')
        for p in paths:
            for x, y in p:
                g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot"/>')
        g.append("</svg>")
        return "".join(g)
    def mid(rows, delta):
        out = []
        for r in rows:
            t = datetime.datetime.fromisoformat(r["end_utc"].replace("Z", "+00:00")) - delta
            out.append({**r, "end_utc": t.strftime("%Y-%m-%dT%H:%MZ")})
        return out
    daily = mid(mi["d"]["daily"], datetime.timedelta(hours=12))          # point sits mid-way through its Eastern-time day
    ticks_d = [(r["end_utc"], dstr(r["et_day"], "%b %-d")) for r in daily if r["et_day"] in ("2026-09-21", "2026-09-28", "2026-10-05", "2026-10-12", "2026-10-19")]
    ev_d = [("2026-10-08T23:00Z", "Debate Oct 8", "a"), ("2026-10-21T23:00Z", "Debate Oct 21", "a")]
    c1 = draw(daily, "2026-09-19T16:00Z", "2026-10-23T08:00Z", 0.6, 0.78, ticks_d, ev_d, band_rows=daily, tag="daily closes September 20 to October 22 2026")
    hourly = mid([r for r in mi["d"]["hourly"] if "2026-10-07T12:00Z" <= r["end_utc"] <= "2026-10-10T12:00Z"], datetime.timedelta(minutes=30))
    ticks_h = [(f"2026-10-{d:02d}T{h:02d}:00Z", lab) for d, h, lab in ((7, 16, "Oct 7 noon ET"), (8, 4, "Oct 8 midnight"), (8, 16, "Oct 8 noon"), (9, 4, "Oct 9 midnight"), (9, 16, "Oct 9 noon"))]
    # label in ET: UTC-4. Debate began 19:00 ET Oct 8 = 23:00 UTC; ended about 20:00 ET = 00:00 UTC Oct 9.
    ticks_h = [(f"2026-10-{d:02d}T{h:02d}:00Z", lab) for d, h, lab in ((7, 16, "Oct 7 noon ET"), (8, 4, "Oct 8 12am"), (8, 16, "Oct 8 noon"), (9, 4, "Oct 9 12am"), (9, 16, "Oct 9 noon"))]
    ev_h = [("2026-10-08T23:00Z", "Debate 7pm ET", "a")]
    c2 = draw(hourly, "2026-10-07T12:00Z", "2026-10-10T12:00Z", 0.6, 0.76, ticks_h, ev_h, band_rows=hourly, tag="hourly October 7 to 10 2026")
    cap = ("Plotted points are the contract's last trade at the close of each period, exactly as Kalshi's candlestick API returned them. Shaded band: yes bid to yes ask at each period close. "
           "Daily points are the close of each Eastern-time day, drawn mid-day. Gaps mean no trade in that period; points are not connected across a gap and nothing is smoothed. Times are Eastern (EDT).")
    return f'''<figure class="chartwrap" data-tabs>
<div class="etabs" role="tablist"><button role="tab" aria-selected="true" data-t="d">Daily closes</button><button role="tab" aria-selected="false" data-t="h">Debate window, hourly</button></div>
<div class="tp" data-p="d">{c1}</div><div class="tp" data-p="h" hidden>{c2}</div>
<div class="legend2"><span><i class="sw line"></i>El-Sayed contract (Democratic win)</span><span><i class="sw band"></i>Bid–ask range</span><span><i class="sw ev"></i>Debate</span></div>
<figcaption>{cap} Source: <a href="https://kalshi.com/markets/senatemi/michigan-senate-race/senatemi-26" rel="noopener">Kalshi contract SENATEMI-26-D</a>, captured {utc_stamp(mi["d"]["captured_at_utc"])}.</figcaption></figure>'''

def spend_chart(race, label):
    rows, latest = race_ie(race)
    cs = FL["by_race"][race]
    rep = next((c for c in cs if c["party_code"] == "REP"), None)
    dem = next((c for c in cs if c["party_code"] == "DEM"), None)
    def benefits(r):
        c, so = r["cand"], r["support_oppose_indicator"]
        if c["party_code"] == "REP":
            return "r" if so == "S" else "d"
        if c["party_code"] == "DEM":
            return "d" if so == "S" else "r"
        return None
    start = datetime.date(2026, 8, 31)
    weeks = [start + datetime.timedelta(days=7 * i) for i in range(10)]
    tot = {w: {"r": 0.0, "d": 0.0} for w in weeks}
    for r in rows:
        b = benefits(r)
        d = datetime.date.fromisoformat((r.get("dissemination_date") or r["expenditure_date"])[:10])
        w = start + datetime.timedelta(days=((d - start).days // 7) * 7)
        if b and w in tot:
            tot[w][b] += r["expenditure_amount"]
    mx = max([v for t in tot.values() for v in t.values()] + [1])
    W, H, L, B, T = 760, 300, 54, 46, 16
    bw = (W - L - 16) / len(weeks)
    g = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Weekly independent expenditures reported to the FEC, {e(label)}">']
    top = (int(mx / 250000) + 1) * 250000
    for v in range(0, top + 1, 250000 if top <= 1500000 else 500000):
        y = _scale(v, 0, top, H - B, T)
        g.append(f'<line x1="{L}" x2="{W-8}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/><text x="{L-8}" y="{y+4:.1f}" class="ax" text-anchor="end">{money(v)}</text>')
    for i, w in enumerate(weeks):
        x = L + i * bw + 5
        for j, k in enumerate(("r", "d")):
            v = tot[w][k]
            y = _scale(v, 0, top, H - B, T)
            g.append(f'<rect x="{x + j * (bw/2 - 4):.1f}" y="{y:.1f}" width="{bw/2 - 6:.1f}" height="{max(H - B - y, 0):.1f}" class="bar {k}"><title>{e(_fmt(w, "Week of %b %-d"))}: {money(v, True)}</title></rect>')
        g.append(f'<text x="{L + i * bw + bw/2:.1f}" y="{H-B+18}" class="ax" text-anchor="middle">{_fmt(w, "%b %-d")}</text>')
    g.append("</svg>")
    nr = rep["name"].split()[-1] if rep else "R"
    nd = dem["name"].split()[-1] if dem else "D"
    tr = sum(v["r"] for v in tot.values()); td = sum(v["d"] for v in tot.values())
    return (f'<figure class="chartwrap"><h4>{e(label)}</h4>{"".join(g)}<div class="legend2"><span><i class="sw bar r"></i>Supports {e(nr)} or opposes {e(nd)} · {money(tr)}</span>'
            f'<span><i class="sw bar d"></i>Supports {e(nd)} or opposes {e(nr)} · {money(td)}</span></div></figure>')

def ie_table(race, limit=8):
    rows, latest = race_ie(race)
    agg = {}
    for r in rows:
        k = (r.get("committee_name") or "Committee", r["cand"]["name"], r["support_oppose_indicator"])
        a = agg.setdefault(k, [0.0, 0, ""])
        a[0] += r["expenditure_amount"]; a[1] += 1; a[2] = max(a[2], (r["expenditure_date"] or "")[:10])
    top = sorted(agg.items(), key=lambda kv: -kv[1][0])[:limit]
    body = "".join(f'<tr><td>{e(k[0])}</td><td>{"Supports" if k[2] == "S" else "Opposes"} {e(k[1])}</td><td class="num">{money(v[0], True)}</td><td class="num">{v[1]}</td><td class="num">{dstr(v[2], "%b %-d")}</td></tr>' for k, v in top)
    return (f'<div class="tablewrap"><table class="data"><thead><tr><th>Spender</th><th>Direction</th><th class="num">Amount</th><th class="num">Reports</th><th class="num">Latest</th></tr></thead><tbody>{body}</tbody></table></div>', latest)

# ------------------------------------------------------------------ page helpers
def _hero(key, alt, caption_title, caption_text):
    cr = FL["heroes"][key]
    return (f'<div class="el-hero"><img src="/img/elections/{key}.jpg" alt="{e(alt)}" width="1800" height="1200" fetchpriority="high"><div class="cap"><div class="uc">{e(caption_title)}</div><p>{e(caption_text)}</p></div>'
            f'<small class="credit">Photo: {e(cr["credit"][:60])}, <a href="{e(cr["source_page"])}" rel="noopener">{e(cr["license"])}</a></small></div>')

def _crumbs(items):
    return '<div class="breadcrumb">' + " / ".join(f'<a href="{h}">{e(l)}</a>' if h else e(l) for l, h in items) + "</div>"

def tip_race_url(race):
    code = SX["code"]
    key = {"governor": f"2026-GOV-{code}", "senate": f"2026-S-{code}"}.get(race) or (f"2026-H-{code}-" + race.split("-")[1])
    return f"https://theissuesparty.org/races/{key}"

def race_link_span(race):
    return f'<span><a href="{tip_race_url(race)}" rel="noopener">Follow this race on TIP ↗</a></span>'

def _asof():
    return datetime.date.fromisoformat(SX["asof"])

def _jsonld(name, path, crumbs):
    return ('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": "https://looklearnfind.com" + h} if h else {})} for i, (n, h) in enumerate(crumbs)]}) + "</script>")

def _toc(items):
    return ('<nav class="onpage" aria-label="On this page"><div class="uc">On this page</div><ol>' + "".join(f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in items) + "</ol></nav>")

def _wrapup(path_html, title, desc, path, crumbs, extra_js=("common", "elections")):
    API["shell"](title, desc, path, path_html, nav="politics", css=("elections",), js=extra_js, jsonld=_jsonld(title, path, crumbs))

def _src_line():
    return SX["source_note"].format(cap=dstr(FL["roster"]["captured_at_utc"]), fec=dstr(FL["fec"]["as_of_utc"]), mk=utc_stamp(FL["markets"]["captured_at_utc"]), tip=dstr(FL["tip_as_of"]))

def _counts():
    cs = FL["cands"]
    return {"cands": len(cs), "gov": len(FL["by_race"]["governor"]), "sen": len(FL["by_race"]["senate"]), "house": sum(len(v) for k, v in FL["by_race"].items() if k.startswith("house-")),
            "graded": sum(1 for c in cs if graded_count(c)), "tip": sum(1 for c in cs if c.get("tip") and c["tip"].get("url"))}

# ------------------------------------------------------------------ State landing
def state_map(highlight=None, links=True, cls="statemap"):
    d = FL["districts"]
    vb = d["viewbox"]
    paths = []
    for n, v in d["districts"].items():
        n = int(n)
        on = " on" if (highlight == n or (isinstance(highlight, (set, list, tuple)) and n in highlight)) else ""
        p = f'<path d="{v["path"]}" class="dist{on}"><title>{SX["code"]}-{n:02d}</title></path>'
        paths.append(f'<a href="{ST_URL}house/{n}/" aria-label="{SX["name"]} district {n}">{p}</a>' if links else p)
    plan = "under the 2026 plan" if SX["code"] == "FL" else "in use for the 2026 election"
    return f'<svg class="{cls}" viewBox="0 0 {vb[2]} {vb[3]}" role="img" aria-label="Map of {_poss(SX["name"])} {SX["ndist"]} congressional districts {plan}">{"".join(paths)}</svg>'

def board_tile(title, href, cands, kicker=""):
    lis = "".join(mini_row(c) for c in cands)
    return f'<a class="btile" href="{href}"><span class="tt"><b>{e(title)}</b><em>{kicker}</em></span><ul>{lis}</ul></a>'

def state_hub():
    if SX["code"] != "FL":
        return generic_hub()
    CUR[0] = ST_URL
    n = _counts()
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", None), ("Florida", None)]
    tiles = [board_tile("Governor", ST_URL + "governor/", FL["by_race"]["governor"], f'{n["gov"]} tickets'),
             board_tile("U.S. Senate", ST_URL + "senate/", FL["by_race"]["senate"], "special election")]
    for i in range(1, 29):
        tiles.append(board_tile(f"FL-{i:02d}", f"{ST_URL}house/{i}/", FL["by_race"][f"house-{i:02d}"], ", ".join(x[0] for x in FL["districts"]["districts"][str(i)]["counties"][:2])))
    board = '<div class="board">' + "".join(tiles) + "</div>"
    gov_mk = (FL["markets"]["races"]["governor"], FL["markets"]["races"]["senate"])
    mrows = ""
    for lab, m, href in (("Governor", gov_mk[0], "governor/"), ("U.S. Senate", gov_mk[1], "senate/")):
        cs = sorted(m["contracts"], key=lambda x: -float(x["last"] or 0))
        mrows += f'<tr><td><a href="{ST_URL}{href}">{lab}</a></td><td>{" · ".join(f"{e(c["yes_label"])} {cents(c["last"])}" for c in cs)}</td><td class="num">{cents(cs[0]["yes_bid"])}/{cents(cs[0]["yes_ask"])}</td></tr>'
    stories = [s for s in API["STORIES"] if s.get("state") == "FL" or s.get("race_state") == "FL"]
    cards = "".join(API["card"](s) for s in API["STORIES"] if s.get("layout") == "report")
    body = f'''<section class="page-head el-head"><div class="wrap wide"><div>{_crumbs(crumbs)}
<div class="kicker">Politics / State of the Race<i></i></div><h1 class="display">Florida: the <em>State of the Race</em></h1>
<p class="dek">Every state has a ballot. This is Florida's: {n["gov"]} governor tickets, {n["sen"]} Senate candidates and {n["house"]} House candidates in 28 districts, with the money, the market quotes and the public record behind them. Where we could not verify something, the page says so.</p>
<p class="meta"><span class="stamp">Florida 2026</span> <span>Checked {dstr(_asof().isoformat())} · {n["cands"]} candidates in 30 contests · governor, U.S. Senate and U.S. House only</span></p></div>
<div class="map-card">{state_map()}<p class="small">Florida's congressional districts under the plan enacted in May 2026 (HB 1-D). Select a district.</p></div></div></section>
<section class="band cream"><div class="wrap wide split3"><div><div class="kicker">Start with the board<i></i></div><h2 class="h2">What is actually on the ballot in Florida, and what does the record show?</h2></div>
<ol class="qs"><li><a href="#board">Who is running for governor, Senate and the House?</a></li><li><a href="#money">Where is the money and the market quoting?</a></li><li><a href="#tip">What does the congressional record show on six issues?</a></li></ol></div></section>
<section class="band" id="board"><div class="wrap wide"><div class="kicker">The State Board<i></i></div><div class="bhead"><h2 class="h2">All 30 contests, all {n["cands"]} candidates</h2>
<p class="dek">Each tile lists every candidate the Florida Division of Elections shows as Qualified or Unopposed for the November 3 general election, in LLF display order (Republican, Democratic, other parties, no party, then write-ins), not ballot order. A dot marks the sitting officeholder. <span class="pchip">W</span> marks a qualified write-in, who does not appear as a printed ballot choice.</p></div>
{board}<p class="small boardnote">District labels show the largest counties by land area inside each district, from the official 2026 district file. Candidates are listed from the state's records; spelling follows the state. Unlisted spellings and late changes: see <a href="/about/corrections/">corrections</a>.</p></div></section>
<section class="band cream" id="money"><div class="wrap wide"><div class="kicker">Money and markets<i></i></div><div class="two"><div><h2 class="h3">Kalshi quotes for the statewide races</h2>
<div class="tablewrap"><table class="data"><thead><tr><th>Race</th><th>Contract last trade</th><th class="num">Bid / ask</th></tr></thead><tbody>{mrows}</tbody></table></div>
<p class="small">Kalshi contract prices are market-implied estimates, not forecasts or vote shares. Governor and Senate contracts resolve on the party of the person sworn in. Captured {utc_stamp(FL["markets"]["captured_at_utc"])}. House district contracts are on each district page.</p></div>
<div><h2 class="h3">Where to read the money</h2><ul class="plain"><li><a href="{ST_URL}governor/#money">Governor: public matching funds, reported campaign totals</a></li><li><a href="{ST_URL}senate/#money">Senate: FEC candidate committee totals and outside spending</a></li><li><a href="{ST_URL}house/">House: every district's committee totals</a></li><li><a href="/learn/florida-house-independent-spending-october-2026/">Spending Report: FL-14 and FL-25</a></li></ul></div></div></div></section>
<section class="band" id="tip"><div class="wrap wide two"><div><div class="kicker">TIP Issue Grades<i></i></div><h2 class="h2">Six issues, graded only from recorded acts</h2>
<p class="dek">TIP grades a candidate on an issue only when there are recorded congressional acts on it. {n["graded"]} of {n["cands"]} Florida candidates have at least one grade today. Everyone else is shown as not graded, never as zero. A grade is TIP's published method applied to the record. It is not a verdict on a person.</p></div>{tip_panel()}</div></section>
<section class="band cream"><div class="wrap wide"><div class="kicker">What the record shows<i></i></div><h2 class="h3" style="margin-bottom:20px">Reported stories</h2>{cards}</div></section>
<section class="band"><div class="wrap wide"><div class="kicker">Sources and method<i></i></div><p class="small meth">{e(_src_line())} <a href="/about/election-methods/">Full methods, definitions and corrections policy ↗</a>. Last verified {dstr(_asof().isoformat())}. This guide excludes ballot measures, Cabinet offices, state legislature and judicial races by design.</p></div></section>'''
    _wrapup(body, "Florida 2026: State of the Race", f"All 30 Florida contests for governor, U.S. Senate and U.S. House: {n['cands']} candidates, money, market quotes and the TIP issue record, with sources.", ST_URL, crumbs)

# ------------------------------------------------------------------ Governor and Senate guides
GOV_ISSUES = [
    ("Property insurance and housing", "Both campaigns publish insurance plans. Donalds proposes protecting recent lawsuit reforms, trimming state fees when reserves are full, reforming My Safe Florida Home, keeping Citizens small and creating an online insurer scorecard. Jolly proposes one state-backed hurricane fund so private insurers no longer price wind risk into homeowners policies, with funding options his page lists (insurer taxes, a real estate transaction fee or existing tourist taxes) and Legislature action required.",
     [("Donalds, Affordability", "https://byrondonalds.com/issues/affordability/"), ("Jolly, Insurance Proposal Facts (Sept. 17, 2026)", "https://davidjolly.com/jolly-insurance-proposal-facts/")]),
    ("Education", "Donalds' education page proposes funding that follows the student, a goal of reading proficiency by third grade with phonics training, early screening and free tutoring. Jolly's page proposes dramatically higher teacher pay, funded in part by letting Florida's tourist development tax pay for teacher salaries and school buildings, which would need a change in law.",
     [("Donalds, Education", "https://byrondonalds.com/issues/education/"), ("Jolly, Public Education", "https://davidjolly.com/issues/public-education/")]),
    ("Taxes and executive authority", "Donalds' page says only that he would keep property taxes in check and gives no rate or measure. A governor cannot change property taxes alone: tax law runs through the Legislature, local governments and, for constitutional changes, voters. We list what each campaign has published and attribute it to the campaign.",
     [("Donalds, Affordability", "https://byrondonalds.com/issues/affordability/")]),
]

def _race_head(kicker, title, dek, crumbs, hero_html, toc):
    return f'''<section class="page-head el-head"><div class="wrap wide"><div class="hcol">{_crumbs(crumbs)}<div class="kicker">{kicker}<i></i></div><h1 class="display">{title}</h1>{dek}</div>{hero_html}{_toc(toc)}</div></section>'''

def gov_page():
    if SX["code"] != "FL":
        return generic_gov_page()
    CUR[0] = "/elections/2026/florida/governor/"
    cs = FL["by_race"]["governor"]
    major = [c for c in cs if c["party_code"] in ("REP", "DEM")]
    others = [c for c in cs if c not in major]
    for c in others:
        if not (c.get("tip") and c["tip"].get("url")):
            violate("R1 no TIP profile", c["name"])
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", ST_URL), ("Governor", None)]
    toc = [("candidates", "The candidates"), ("issues", "Key issues"), ("money", "Campaign money"), ("markets", "What the market says"), ("polls", "Polling"), ("others", "The other eight tickets"), ("sources", "Sources")]
    dek = (f'<p class="deck">The candidates, the money and what they say they will do.</p><p class="dek">Ron DeSantis is term-limited, so Florida elects a new governor on November 3. {len(cs)} tickets qualified: the Republican and Democratic nominees, five no-party tickets, one Libertarian ticket and two write-in tickets. Governor is a state office, so TIP shows the six-issue federal record only where a candidate served in Congress.</p>'
           f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span>{race_link_span("governor")}</p>')
    hero = _hero("fl-capitol", "The Old Florida State Capitol and the new Capitol tower in Tallahassee", "A governor's race", "Florida's next governor will set the state's direction on insurance, taxes and schools. Here is what is on file.")
    body = _race_head("State of the Race / Governor", "Florida Governor Race", dek, crumbs, hero, toc)
    body += f'''<section class="band" id="candidates"><div class="wrap wide cwrap"><div><div class="kicker">The candidates<i></i></div><h2 class="h2">The nominees</h2>
<p class="dek small-dek">Nominees won their party primaries. Jolly served in Congress from 2014 to 2017 as a Republican and joined the Democratic Party in April 2025. Donalds is a sitting member of Congress. Both appear below with their federal record where TIP has one.</p>
<div class="ccards two">{"".join(candidate_card(c, "xl") for c in major)}</div></div>{tip_panel(major)}</div></section>'''
    body += f'''<section class="band cream" id="issues"><div class="wrap wide"><div class="kicker">Key issues<i></i></div><h2 class="h3">What each campaign says it would do</h2><p class="small">Campaign statements, attributed to the campaign pages named. A promise is not an enacted policy.</p><div class="issuegrid">'''
    for t, txt, links in GOV_ISSUES:
        body += f'<article class="issue"><h3>{e(t)}</h3><p>{e(txt)}</p><p class="small">' + " · ".join(f'<a href="{e(u)}" rel="noopener">{e(l)} ↗</a>' for l, u in links) + "</p></article>"
    body += "</div></div></section>"
    md = [("Public matching funds, 2026 governor", [("Jolly", 3074954.60), ("Donalds", 1197766.78), ("Collins (primary, eliminated)", 199783.22)])]
    body += f'''<section class="band" id="money"><div class="wrap wide two"><div><div class="kicker">Campaign money<i></i></div><h2 class="h3">Two different kinds of money</h2>
<div class="mgrid"><div class="mbox"><span class="uc">Official · Florida Dept. of State</span><h3>Public matching funds</h3><p class="small">State matching funds distributed through {dstr("2026-10-23")} (page updated Oct. 23, 2026).</p>
<dl class="kv2"><dt>David Jolly</dt><dd>$3,074,954.60</dd><dt>Byron Donalds</dt><dd>$1,197,766.78</dd><dt>Jay Collins (eliminated in primary)</dt><dd>$199,783.22</dd><dt><b>All governor distributions</b></dt><dd><b>$4,472,504.60</b></dd></dl>
<p class="small"><a href="https://dos.fl.gov/elections/candidates-committees/campaign-finance/public-campaign-finance-matching-funds-program/public-campaign-finance-2026/" rel="noopener">Source: Florida Department of State ↗</a></p></div>
<div class="mbox"><span class="uc">Reported by the press · through Sept. 11</span><h3>Campaign accounts and committees</h3><p class="small">Attributed to the News Service of Florida (WPEC/CBS12, Sept. 21, 2026). The state's campaign finance database blocks automated access, so we could not re-pull these from filings.</p>
<dl class="kv2"><dt>Donalds campaign account</dt><dd>$13.3M raised · ~$7.4M spent</dd><dt>Friends of Byron Donalds (committee)</dt><dd>$107.6M raised · ~$70M spent</dd><dt>Jolly campaign account</dt><dd>$8.2M raised · $4.9M spent</dd><dt>Florida 2026 (committee backing Jolly)</dt><dd>$6.4M received · $3.3M spent</dd></dl>
<p class="small"><a href="https://cbs12.com/news/florida/david-jolly-florida-governors-race-2026-david-jolly-byron-daniels-public-campaign-financing-florida-democratic-party-political-donations-florida-candidates-november-election-florida-news" rel="noopener">Source: News Service of Florida via CBS12 ↗</a></p></div></div>
<p class="small">Campaign account, committee and public matching money are different things and must not be added together. Committee money can include transfers. The Sept. 11 figures are older than the Oct. 23 matching-fund figures.</p></div>
<div id="markets">{market_card("governor", "What the market says")}<p class="small">The governor contract resolves on the party of the person inaugurated: "If a representative of the Democratic party is inaugurated as the governor of Florida pursuant to the 2026 election, then the market resolves to Yes" (Jolly contract). The Republican contract is the mirror.</p></div></div></section>'''
    body += f'''<section class="band cream" id="polls"><div class="wrap wide two"><div><div class="kicker">Polling<i></i></div><h2 class="h3">What the latest poll measured</h2>
<div class="pollbox"><span class="uc">UNF Public Opinion Research Lab · Oct. 12–19, 2026</span><div class="pbar"><span class="p r" style="width:49%">Donalds 49%</span><span class="p d" style="width:47%">Jolly 47%</span></div>
<p class="small">1,471 likely midterm voters · telephone · margin of error ±2.81 points · 4% undecided. Reported by WLRN, Oct. 21, 2026, from the UNF release. In UNF's July poll Donalds led by five points. A single poll is a snapshot, not a forecast, and the gap is within about the margin of error.</p>
<p class="small"><a href="https://www.wlrn.org/government-politics/2026-10-21/republicans-donalds-moody-hold-slim-leads-in-tightening-governor-us-senate-races-unf-polls-finds" rel="noopener">Source: WLRN ↗</a></p></div></div>
<div><h2 class="h3">Read the reported feature</h2><p>The fundraising and polling story, with every number sourced and dated.</p><p><a class="btn" href="/learn/florida-governor-fundraising-polling-2026/">Read the analysis ↗</a></p></div></div></section>'''
    rows = "".join(f'<tr><td>{e(c["name"])}</td><td>{e(c["party"])}</td><td>{e(c.get("running_mate") or "—")}</td><td>{"Primary: unopposed" if c["primary"] == "Unopposed" else ("Qualified" if c["status"] == "Qualified" else e(c["status"]))}</td><td><a href="{e(c["state_url"])}" rel="noopener">State record ↗</a>{(" · " + '<a href="' + e(c["tip"]["url"]) + '" rel="noopener">TIP profile ↗</a>') if c.get("tip") and c["tip"].get("url") else ""}</td></tr>' for c in others)
    body += f'''<section class="band" id="others"><div class="wrap wide"><div class="kicker">The other eight tickets<i></i></div><h2 class="h3">Qualified governor tickets beyond the nominees</h2>
<div class="tablewrap"><table class="data"><thead><tr><th>Candidate</th><th>Ballot designation</th><th>Running mate</th><th>Status</th><th>Record</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small">Write-in candidates are qualified under Florida law but do not appear as printed ballot choices. These tickets have TIP profiles but no recorded congressional acts, so they are not graded.</p></div></section>
<section class="band cream" id="sources"><div class="wrap wide"><div class="kicker">Sources<i></i></div><p class="small meth">{e(_src_line())} Governor candidates file campaign finance with the state, not the FEC.</p>
<p class="small"><a class="link teal" href="/about/election-methods/">Methods and corrections ↗</a></p></div></section>'''
    _wrapup(body, "Florida Governor Race 2026", "Florida's governor race: all 10 qualified tickets, public matching funds, Kalshi quotes, the latest poll and each campaign's stated plans, with sources.", ST_URL + "governor/", crumbs)

def senate_page():
    if SX["code"] != "FL":
        return generic_senate_page()
    CUR[0] = "/elections/2026/florida/senate/"
    cs = FL["by_race"]["senate"]
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", ST_URL), ("U.S. Senate", None)]
    toc = [("candidates", "The candidates"), ("money", "Campaign money"), ("markets", "What the market says"), ("polls", "Polling"), ("watch", "What to watch"), ("sources", "Sources")]
    dek = ('<p class="deck">The candidates, the money and the record.</p><p class="dek">Florida elects a U.S. senator in a special election for the seat Ashley Moody holds by appointment. Three candidates qualified: the Republican incumbent, the Democratic nominee and one no-party candidate.</p>'
           f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span>{race_link_span("senate")}</p>')
    hero = _hero("us-capitol", "The dome of the United States Capitol", "A Senate seat", "One Florida seat in the U.S. Senate is on the ballot. Here is what is on file about the three candidates.")
    body = _race_head("State of the Race / U.S. Senate", "Florida U.S. Senate Race", dek, crumbs, hero, toc)
    body += f'''<section class="band" id="candidates"><div class="wrap wide cwrap"><div><div class="kicker">The candidates<i></i></div><h2 class="h2">Who qualified</h2>
<div class="ccards three">{"".join(candidate_card(c, "lg") for c in cs)}</div></div>{tip_panel(cs)}</div></section>'''
    ie_rows, latest = race_ie("senate")
    tot_ie = sum(r["expenditure_amount"] for r in ie_rows)
    tbl, _l = ie_table("senate", 8)
    body += f'''<section class="band cream" id="money"><div class="wrap wide two"><div><div class="kicker">Campaign money<i></i></div><h2 class="h3">Candidate committees and outside spending are separate</h2>
<p class="small">Candidate committee totals come from the FEC for the period shown on each card. Outside spending below is independent expenditures reported to the FEC on 24/48-hour reports through {dstr(latest)}; it is spending by other groups, not money received by a candidate.</p>
<p class="bignum"><b>{money(tot_ie)}</b><span>independent expenditures reported for this race, 2026 cycle</span></p>{tbl}</div>
<div id="markets">{market_card("senate")}<p class="small">Contract resolves on the party sworn in to the seat for the term in question.</p></div></div></section>
<section class="band" id="polls"><div class="wrap wide two"><div><div class="kicker">Polling<i></i></div><h2 class="h3">What the latest poll measured</h2><div class="pollbox"><span class="uc">UNF Public Opinion Research Lab · Oct. 12–19, 2026</span>
<div class="pbar"><span class="p r" style="width:49%">Moody 49%</span><span class="p d" style="width:45%">Nixon 45%</span></div><p class="small">1,471 likely midterm voters · telephone · margin of error ±2.81 points · 5% undecided. Reported by WLRN, Oct. 21, 2026. In UNF's July poll Moody led by eight points.</p>
<p class="small"><a href="https://www.wlrn.org/government-politics/2026-10-21/republicans-donalds-moody-hold-slim-leads-in-tightening-governor-us-senate-races-unf-polls-finds" rel="noopener">Source: WLRN ↗</a></p></div></div>
<div id="watch"><h2 class="h3">What to watch</h2><ul class="plain"><li>The next FEC pre-election and 24/48-hour reports</li><li>Whether the market quote and the polling keep diverging</li><li>Independent spending reported before Nov. 3</li></ul></div></div></section>
<section class="band cream" id="sources"><div class="wrap wide"><div class="kicker">Sources<i></i></div><p class="small meth">{e(_src_line())} <a href="/about/election-methods/">Methods ↗</a></p></div></section>'''
    _wrapup(body, "Florida U.S. Senate Race 2026", "Florida's special U.S. Senate election: the three qualified candidates, FEC money, outside spending, Kalshi quotes and polling, with sources.", ST_URL + "senate/", crumbs)

# ------------------------------------------------------------------ House
def district_summary(n):
    race = f"house-{n:02d}"
    cs = FL["by_race"][race]
    d = FL["districts"]["districts"][str(n)]
    return race, cs, d

def _poss(name):
    return name + ("'" if name.endswith("s") and name != "Florida" else "'s")

def _dl(n):
    return f'{SX["code"]}-{n:02d}'

def _seat_note(cs):
    inc = [c for c in cs if c["incumbent"]]
    return f'Incumbent: {inc[0]["name"]}' if inc else "Open seat"

def _open_seats():
    return [i for i in range(1, SX["ndist"] + 1) if not any(c["incumbent"] for c in FL["by_race"][f"house-{i:02d}"])]

def _kalshi_coverage_note():
    miss = [i for i in range(1, SX["ndist"] + 1) if not (FL["markets"]["races"].get(f"house-{i:02d}") or {}).get("contracts")]
    have = SX["ndist"] - len(miss)
    tail = (f"none was found for {' and '.join(_dl(i) for i in miss)}" if miss else "all districts have one")
    return f'Kalshi contract exists for {have} of {SX["ndist"]} districts; {tail} on {dstr(FL["markets"]["captured_at_utc"])}.'

def house_page():
    fl = SX["code"] == "FL"
    nd = SX["ndist"]
    CUR[0] = ST_URL + "house/"
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", ST_URL), ("U.S. House", None)]
    toc = [("map", "District map"), ("districts", f"All {nd} districts"), ("directory", "Directory"), ("tip", "TIP issue grades"), ("sources", "Sources")]
    n = _counts()
    if fl:
        dek = (f'<p class="deck">All 28 districts. Every qualified candidate.</p><p class="dek">Florida\'s 2026 House races use the congressional map enacted in May 2026 (HB 1-D), which is still under legal challenge. {n["house"]} candidates qualified across the 28 districts. District descriptions below come from the official district file, not from the old map.</p>'
               f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span></p>')
    else:
        oseats = _open_seats()
        dek = (f'<p class="deck">All {nd} districts. Every candidate on our roster.</p><p class="dek">{SX["name"]} elects {nd} U.S. House members on the congressional map in use since 2022. {n["house"]} candidates are on our roster across the {nd} districts, write-ins included. '
               f'{len(oseats)} seats have no incumbent on the ballot: {", ".join(_dl(i) for i in oseats[:-1])} and {_dl(oseats[-1])}. The roster comes from Green Papers because the State Board of Elections list could not be read, so it is not an official or complete list.</p>'
               f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span></p>')
    hero = f'<div class="el-hero mapheroc">{state_map()}</div>'
    body = _race_head("State of the Race / U.S. House", f"{SX['name']} House Races", dek, crumbs, hero, toc)
    tiles = []
    for i in range(1, nd + 1):
        race, cs, d = district_summary(i)
        cn = ", ".join(f"{a}" for a, p in d["counties"][:3]) if fl else _seat_note(cs)
        mk = (FL["markets"]["races"].get(race) or {}).get("contracts")
        q = ""
        if mk:
            top = max(mk, key=lambda x: float(x["last"] or 0))
            q = f'<span class="qmini">Kalshi: {e(top["yes_label"].split()[-1])} {cents(top["last"])}</span>'
        tot, latest, cnt = ie_total(race)
        tiles.append(f'''<a class="dcard" href="{ST_URL}house/{i}/" id="d{i}"><div class="dmap"><svg viewBox="{' '.join(map(str, FL["districts"]["viewbox"]))}" aria-hidden="true"><path d="{FL["districts"]["state_outline"]}" class="outline"/><path d="{d["path"]}" class="dist on"/></svg></div>
<div class="dbody"><b class="dn">{_dl(i)}</b><span class="dc">{e(cn)}</span><ul>{"".join(mini_row(c) for c in cs)}</ul><span class="dm">{q}{f'<span class="qmini">Outside spending {money(tot)}</span>' if tot else ""}</span></div></a>''')
    body += f'<section class="band" id="districts"><div class="wrap wide"><div class="kicker">All {nd} districts<i></i></div><h2 class="h2">Browse by district</h2><div class="dgrid" data-view="cards">{"".join(tiles)}</div></div></section>'
    # directory table
    rows = []
    for i in range(1, nd + 1):
        race, cs, d = district_summary(i)
        mk = (FL["markets"]["races"].get(race) or {}).get("contracts")
        q = "—"
        if mk:
            top = max(mk, key=lambda x: float(x["last"] or 0))
            q = f'{e(top["yes_label"])} {cents(top["last"])}'
        tot, latest, cnt = ie_total(race)
        who = f'{"".join(chip(c) for c in cs)} {e(", ".join(c["name"] for c in cs))}'
        if fl:
            rows.append(f'<tr><td><a href="{ST_URL}house/{i}/">{_dl(i)}</a></td><td>{e(", ".join(f"{a} ({p}%)" for a, p in d["counties"][:3]))}</td><td>{who}</td><td class="num">{sum(1 for c in cs if graded_count(c))}</td><td>{q}</td><td class="num">{money(tot) if tot else "—"}</td></tr>')
        else:
            rows.append(f'<tr><td><a href="{ST_URL}house/{i}/">{_dl(i)}</a></td><td>{e(_seat_note(cs))}</td><td>{who}</td><td class="num">{sum(1 for c in cs if graded_count(c))}</td><td>{q}</td></tr>')
    if fl:
        thead = '<tr><th>District</th><th>Largest counties (share of district area)</th><th>Candidates</th><th class="num">Graded</th><th>Kalshi last trade (higher)</th><th class="num">Outside spending</th></tr>'
        foot = (f'"Graded" counts candidates with at least one TIP Issue Grade. Kalshi contract exists for 26 of 28 districts; none was found for FL-13 and FL-23 on {dstr(FL["markets"]["captured_at_utc"])}. '
                'Outside spending is independent expenditures reported on FEC 24/48-hour reports in the 2026 cycle. County shares are land area from Census county boundaries intersected with the official district file.')
    else:
        thead = '<tr><th>District</th><th>Seat</th><th>Candidates</th><th class="num">Graded</th><th>Kalshi last trade (higher)</th></tr>'
        foot = (f'"Graded" counts candidates with at least one TIP Issue Grade. {_kalshi_coverage_note()} Seat status comes from our roster: "Open seat" means no incumbent is on the ballot. '
                'Independent expenditures and committee totals are on the FEC pages linked from each district.')
    body += f'''<section class="band cream" id="directory"><div class="wrap wide"><div class="kicker">Directory<i></i></div><h2 class="h3">District directory</h2>
<div class="tablewrap"><table class="data wide"><thead>{thead}</thead><tbody>{"".join(rows)}</tbody></table></div>
<p class="small">{foot}</p></div></section>
<section class="band" id="tip"><div class="wrap wide two"><div><div class="kicker">TIP issue grades<i></i></div><h2 class="h2">Who has a record to grade</h2><p class="dek">{sum(1 for c in FL["cands"] if c["office"] == "house" and graded_count(c))} of {n["house"]} House candidates have at least one TIP Issue Grade, because only people with recorded congressional acts can be graded. Challengers are not graded, and that is not a score of zero.</p></div>{tip_panel([c for c in FL["cands"] if c["office"] == "house"])}</div></section>
<section class="band cream" id="sources"><div class="wrap wide"><div class="kicker">Sources<i></i></div><p class="small meth">{e(_src_line())} {GEOM_NOTE[SX["code"]]} <a href="/about/election-methods/">Methods ↗</a></p></div></section>'''
    desc = ("All 28 Florida congressional districts under the 2026 map: every qualified candidate, committee totals, outside spending, Kalshi quotes and TIP issue grades." if fl else
            f"All {nd} {SX['name']} congressional districts: every candidate on our roster, Kalshi quotes and TIP issue grades, with sources and the limits of the roster.")
    _wrapup(body, f"{SX['name']} House Races 2026", desc, ST_URL + "house/", crumbs)

GEOM_NOTE = {"FL": "District geometry: Florida Legislature EDR plan EOGPCRP2026 (HB 1-D).",
             "IL": "District geometry: U.S. Census Bureau cartographic boundary file cb_2024_us_cd119_500k (119th Congress districts, in use for 2026)."}

def district_page(n):
    fl = SX["code"] == "FL"
    nd = SX["ndist"]
    CUR[0] = f"{ST_URL}house/{n}/"
    race, cs, d = district_summary(n)
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", ST_URL), ("U.S. House", ST_URL + "house/"), (_dl(n), None)]
    cn = ", ".join(f"{a} ({p}%)" for a, p in d["counties"])
    tbl, latest = ie_table(race, 6)
    tot, _l, cnt = ie_total(race)
    prev = f'<a href="{ST_URL}house/{n-1}/">← {_dl(n-1)}</a>' if n > 1 else ""
    nxt = f'<a href="{ST_URL}house/{n+1}/">{_dl(n+1)} →</a>' if n < nd else ""
    if fl:
        dek = (f'<p class="deck">{len(cs)} candidates qualified for the November 3 general election.</p><p class="dek">Largest counties by share of district area: {e(cn)}. Under the 2026 plan (HB 1-D), enacted in May 2026 and still in litigation.</p>'
               f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span>{race_link_span(race)}</p>')
    else:
        dek = (f'<p class="deck">{len(cs)} candidates on our roster for the November 3 general election.</p><p class="dek">{e(_seat_note(cs))}. The roster is transcribed from Green Papers; the State Board of Elections list could not be read, so it is not an official or complete list.</p>'
               f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span>{race_link_span(race)}</p>')
    hero = f'<div class="el-hero mapheroc one">{state_map(highlight=n, links=False)}</div>'
    body = _race_head("State of the Race / U.S. House", f"{_poss(SX['name'])} {n}{_ord(n)} Congressional District", dek, crumbs, hero,
                      [("candidates", "The candidates"), ("money", "Money"), ("market", "Market"), ("sources", "Sources")])
    if fl:
        money_html = ((f'<p class="bignum"><b>{money(tot)}</b><span>independent expenditures on FEC 24/48-hour reports, 2026 cycle, through {dstr(latest)} · {cnt} reports</span></p>{tbl}') if tot else '<p>No independent expenditures for this race were found in the FEC data pulled on ' + dstr(FL["fec"]["as_of_utc"]) + '.</p>')
        money_note = "Independent expenditures are spent by outside groups to support or oppose a candidate. They are not donations to the candidate's campaign. Candidate committee totals are on each candidate card."
    else:
        money_html = (f'<p>We have not loaded this district\'s federal filings into this page. Candidate committee totals and independent expenditures are on the FEC\'s race page: '
                      f'<a href="https://www.fec.gov/data/elections/house/{SX["code"]}/{n:02d}/2026/" rel="noopener">{_dl(n)} on FEC.gov ↗</a>. Absence here is not absence of spending.</p>')
        money_note = "Independent expenditures are spent by outside groups to support or oppose a candidate. They are not donations to the candidate's campaign."
    body += f'''<section class="band" id="candidates"><div class="wrap wide cwrap"><div><div class="kicker">The candidates<i></i></div><h2 class="h2">Who is on the ballot</h2>
<div class="ccards {"three" if len(cs) <= 3 else "four"}">{"".join(candidate_card(c, "md") for c in cs)}</div></div>{tip_panel(cs)}</div></section>
<section class="band cream" id="money"><div class="wrap wide two"><div><div class="kicker">Money<i></i></div><h2 class="h3">Outside spending in this race</h2>
{money_html}
<p class="small">{money_note}</p></div>
<div id="market">{market_card(race)}{MARKET_NOTES.get((SX["code"], race), "")}</div></div></section>
<section class="band" id="sources"><div class="wrap wide"><nav class="pn">{prev}<a href="{ST_URL}house/">All districts</a>{nxt}</nav><p class="small meth">{e(_src_line())} <a href="/about/election-methods/">Methods ↗</a></p></div></section>'''
    desc = (f"Every qualified candidate in Florida's {n}{_ord(n)} congressional district under the 2026 map, with FEC totals, outside spending, Kalshi quotes and TIP issue grades." if fl else
            f"Every candidate on our roster in {_poss(SX['name'])} {n}{_ord(n)} congressional district, with Kalshi quotes and TIP issue grades and a link to the FEC filings.")
    _wrapup(body, f"{_poss(SX['name'])} {n}{_ord(n)} Congressional District 2026", desc, f"{ST_URL}house/{n}/", crumbs)

MARKET_NOTES = {("IL", "house-04"): '<p class="small">Kalshi still lists a contract for Mayra Macías, an independent the Illinois State Board of Elections voted 8-0 on July 21, 2026 to remove from the ballot (Riverside-Brookfield Landmark, July 22). The quote is shown as the API returned it and is not an endorsement of her candidacy.</p>'}

def _ord(n):
    return "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


# ------------------------------------------------------------------ non-Florida state pages (Illinois): same modules, content from the state's own data
ROSTER_NOTE = {"IL": ('<strong>About this roster.</strong> The Illinois State Board of Elections candidate list could not be read by our tools (HTTP 403 on {cap}). '
                      'This roster is transcribed from Green Papers and cross-checked against OpenFEC and TIP. It is not an official or certified list, may omit late changes and is not claimed to be complete. '
                      'Write-in candidates are listed only where the source lists them.')}

def _roster_note():
    return f'<p class="small boardnote">{ROSTER_NOTE[SX["code"]].format(cap=dstr(FL["roster"]["captured_at_utc"]))}</p>'

def _market_rows(pairs):
    out = ""
    for lab, key, href in pairs:
        m = (FL["markets"]["races"] or {}).get(key)
        if not m or "contracts" not in m:
            continue
        cs = sorted(m["contracts"], key=lambda x: -float(x["last"] or 0))
        out += f'<tr><td><a href="{ST_URL}{href}">{lab}</a></td><td>{" · ".join(f"{e(c["yes_label"])} {cents(c["last"])}" for c in cs)}</td><td class="num">{cents(cs[0]["yes_bid"])}/{cents(cs[0]["yes_ask"])}</td></tr>'
    return out

def generic_hub():
    nd, name = SX["ndist"], SX["name"]
    CUR[0] = ST_URL
    n = _counts()
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", None), (name, None)]
    tiles = [board_tile("Governor", ST_URL + "governor/", FL["by_race"]["governor"], f'{n["gov"]} candidates'),
             board_tile("U.S. Senate", ST_URL + "senate/", FL["by_race"]["senate"], "open seat" if not any(c["incumbent"] for c in FL["by_race"]["senate"]) else "regular election")]
    for i in range(1, nd + 1):
        tiles.append(board_tile(_dl(i), f"{ST_URL}house/{i}/", FL["by_race"][f"house-{i:02d}"], _seat_note(FL["by_race"][f"house-{i:02d}"])))
    board = '<div class="board">' + "".join(tiles) + "</div>"
    mrows = _market_rows((("Governor", "governor", "governor/"), ("U.S. Senate", "senate", "senate/")))
    contests = nd + 2
    oseats = _open_seats()
    body = f'''<section class="page-head el-head"><div class="wrap wide"><div>{_crumbs(crumbs)}
<div class="kicker">Politics / State of the Race<i></i></div><h1 class="display">{name}: the <em>State of the Race</em></h1>
<p class="dek">Every state has a ballot. This is {_poss(name)}: {n["gov"]} governor candidates, {n["sen"]} Senate candidates and {n["house"]} House candidates in {nd} districts on our roster, with the market quotes and the public record behind them. Where we could not verify something, the page says so.</p>
<p class="meta"><span class="stamp">{name} 2026</span> <span>Checked {dstr(_asof().isoformat())} · {n["cands"]} candidates in {contests} contests · governor, U.S. Senate and U.S. House only</span></p></div>
<div class="map-card">{state_map()}<p class="small">{_poss(name)} {nd} congressional districts, as in use for the 2026 election. Select a district.</p></div></div></section>
<section class="band cream"><div class="wrap wide split3"><div><div class="kicker">Start with the board<i></i></div><h2 class="h2">What is on the ballot in {name}, and what does the record show?</h2></div>
<ol class="qs"><li><a href="#board">Who is running for governor, Senate and the House?</a></li><li><a href="#money">What is the market quoting?</a></li><li><a href="#tip">What does the congressional record show on six issues?</a></li></ol></div></section>
<section class="band" id="board"><div class="wrap wide"><div class="kicker">The State Board<i></i></div><div class="bhead"><h2 class="h2">All {contests} contests, {n["cands"]} candidates on our roster</h2>
<p class="dek">Each tile lists every candidate in our {name} roster for the November 3 general election, in LLF display order (Republican, Democratic, other parties, no party, then write-ins), not ballot order. A dot marks the sitting officeholder. <span class="pchip">W</span> marks a write-in, who does not appear as a printed ballot choice. {len(oseats)} House seats have no incumbent on the ballot.</p></div>
{_roster_note()}
{board}<p class="small boardnote">Candidates are listed as the source spells them. Late changes and spelling: see <a href="/about/corrections/">corrections</a>.</p></div></section>
<section class="band cream" id="money"><div class="wrap wide"><div class="kicker">Markets and money<i></i></div><div class="two"><div><h2 class="h3">Kalshi quotes for the statewide races</h2>
<div class="tablewrap"><table class="data"><thead><tr><th>Race</th><th>Contract last trade</th><th class="num">Bid / ask</th></tr></thead><tbody>{mrows}</tbody></table></div>
<p class="small">Kalshi contract prices are market-implied estimates, not forecasts or vote shares. Governor and Senate contracts resolve on the party of the person sworn in. Captured {utc_stamp(FL["markets"]["captured_at_utc"])}. House district contracts are on each district page.</p></div>
<div><h2 class="h3">Where to read the money</h2><ul class="plain"><li><a href="https://www.fec.gov/data/elections/senate/{SX["code"]}/2026/" rel="noopener">Senate: FEC candidate committee totals ↗</a></li><li><a href="{ST_URL}house/">House: every district, with its FEC page ↗</a></li><li>Governor candidates file with the state, not the FEC.</li></ul></div></div></div></section>
<section class="band" id="tip"><div class="wrap wide two"><div><div class="kicker">TIP Issue Grades<i></i></div><h2 class="h2">Six issues, graded only from recorded acts</h2>
<p class="dek">TIP grades a candidate on an issue only when there are recorded congressional acts on it. {n["graded"]} of {n["cands"]} {name} candidates have at least one grade today. Everyone else is shown as not graded, never as zero. A grade is TIP's published method applied to the record. It is not a verdict on a person.</p></div>{tip_panel()}</div></section>
<section class="band"><div class="wrap wide"><div class="kicker">Sources and method<i></i></div><p class="small meth">{e(_src_line())} <a href="/about/election-methods/">Full methods, definitions and corrections policy ↗</a>. Last verified {dstr(_asof().isoformat())}. This guide excludes ballot measures, Cabinet offices, state legislature and judicial races by design.</p></div></section>'''
    _wrapup(body, f"{name} 2026: State of the Race", f"All {contests} {name} contests for governor, U.S. Senate and U.S. House: {n['cands']} candidates on our roster, market quotes and the TIP issue record, with sources and the limits of the roster.", ST_URL, crumbs)

def _others_table(cs, note):
    for c in cs:
        if not (c.get("tip") and c["tip"].get("url")):
            tip_button(c)            # records the directory gap
    rows = "".join(f'<tr><td>{e(c["name"])}</td><td>{e(c["party"])}</td><td>{e(c.get("running_mate") or "—")}</td>'
                   f'<td>{"Write-in" if c["party_code"] == "WRI" else e(c["status"])}</td><td>{("<a href=" + chr(34) + e(c["tip"]["url"]) + chr(34) + " rel=" + chr(34) + "noopener" + chr(34) + ">TIP profile ↗</a>") if c.get("tip") and c["tip"].get("url") else "No TIP record yet"}</td></tr>' for c in cs)
    return (f'<div class="tablewrap"><table class="data"><thead><tr><th>Candidate</th><th>Ballot designation</th><th>Running mate</th><th>Status</th><th>Record</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<p class="small">{note}</p>')

def generic_gov_page():
    name = SX["name"]
    CUR[0] = ST_URL + "governor/"
    cs = FL["by_race"]["governor"]
    major = [c for c in cs if c["party_code"] in ("REP", "DEM")]
    others = [c for c in cs if c not in major]
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", ST_URL), ("Governor", None)]
    toc = [("candidates", "The candidates"), ("markets", "What the market says"), ("polls", "Polling"), ("others", "The other candidates"), ("sources", "Sources")]
    inc = next((c for c in major if c["incumbent"]), None)
    dek = (f'<p class="deck">The candidates, the market and what is on file.</p><p class="dek">{name} elects a governor on November 3. {len(cs)} candidates are on our roster: the Republican and Democratic nominees, {len([c for c in others if c["party_code"] != "WRI"])} other candidate{"s" if len([c for c in others if c["party_code"] != "WRI"]) != 1 else ""} and {len([c for c in others if c["party_code"] == "WRI"])} write-ins. '
           + (f'The incumbent, {e(inc["name"])}, was renominated. ' if inc else "") + f'Governor is a state office, so TIP shows the six-issue federal record only where a candidate served in Congress. The roster is not an official list (see below).</p>'
           f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span>{race_link_span("governor")}</p>')
    hero = _hero("il-capitol", "The Illinois State Capitol in Springfield", "A governor's race", f"{_poss(name)} next governor will be chosen on November 3. Here is what is on file.")
    body = _race_head("State of the Race / Governor", f"{name} Governor Race", dek, crumbs, hero, toc)
    body += f'''<section class="band" id="candidates"><div class="wrap wide cwrap"><div><div class="kicker">The candidates<i></i></div><h2 class="h2">The nominees</h2>
<p class="dek small-dek">Nominees won their party primaries on March 17, 2026. Neither has served in Congress, so TIP shows no graded issues for them; not graded is not a score of zero.</p>
<div class="ccards two">{"".join(candidate_card(c, "xl") for c in major)}</div></div>{tip_panel(major)}</div></section>
<section class="band cream" id="markets"><div class="wrap wide two"><div><div class="kicker">Markets<i></i></div><h2 class="h3">What the Kalshi market quotes</h2>{market_card("governor", "What the market says")}</div>
<div><p class="small">The contract resolves on the party of the person inaugurated as governor. A price is what traders were willing to pay at the capture time. It is not a forecast, a poll or a vote share.</p></div></div></section>
<section class="band" id="polls"><div class="wrap wide"><div class="kicker">Polling<i></i></div><h2 class="h3">No poll is shown</h2><p>We have not shown a poll for this race. The public polls we found as of {dstr(_asof().isoformat())} had a sponsor that was not stated or disputed, and we did not open an original release. We will add a poll when we can cite its pollster, field dates, sample and sponsor from the original.</p></div></section>
<section class="band cream" id="others"><div class="wrap wide"><div class="kicker">The other candidates<i></i></div><h2 class="h3">Everyone else on our roster</h2>
{_others_table(others, "Write-in candidates do not appear as printed ballot choices. Where a candidate has no TIP record we say so; that gap is TIP's to fill, not a statement about the candidate.")}</div></section>
<section class="band" id="sources"><div class="wrap wide"><div class="kicker">Sources<i></i></div><p class="small meth">{e(_src_line())} Governor candidates file campaign finance with the state, not the FEC.</p>{_roster_note()}
<p class="small"><a class="link teal" href="/about/election-methods/">Methods and corrections ↗</a></p></div></section>'''
    _wrapup(body, f"{name} Governor Race 2026", f"{_poss(name)} governor race: every candidate on our roster, the Kalshi quote and what is on file, with sources and the limits of the roster.", ST_URL + "governor/", crumbs)

def generic_senate_page():
    name = SX["name"]
    CUR[0] = ST_URL + "senate/"
    cs = FL["by_race"]["senate"]
    main = [c for c in cs if c["party_code"] in ("REP", "DEM")]
    rest = [c for c in cs if c not in main]
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", ST_URL), ("U.S. Senate", None)]
    toc = [("candidates", "The candidates"), ("markets", "What the market says"), ("others", "The other candidates"), ("sources", "Sources")]
    dek = (f'<p class="deck">The candidates, the market and the record.</p><p class="dek">{name} elects a U.S. senator on November 3 for the seat Dick Durbin is leaving. {len(cs)} candidates are on our roster: the Democratic nominee, the Republican nominee'
           f'{", one third-party candidate" if any(c["party_code"] == "AMC" for c in rest) else ""} and a write-in. The roster is not an official list (see below).</p>'
           f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span>{race_link_span("senate")}</p>')
    hero = _hero("us-capitol", "The dome of the United States Capitol", "A Senate seat", f"One {name} seat in the U.S. Senate is on the ballot. Here is what is on file.")
    body = _race_head("State of the Race / U.S. Senate", f"{name} U.S. Senate Race", dek, crumbs, hero, toc)
    body += f'''<section class="band" id="candidates"><div class="wrap wide cwrap"><div><div class="kicker">The candidates<i></i></div><h2 class="h2">The nominees</h2>
<p class="dek small-dek">Neither nominee has served in Congress, so TIP shows no graded issues for them; not graded is not a score of zero.</p>
<div class="ccards two">{"".join(candidate_card(c, "xl") for c in main)}</div></div>{tip_panel(main)}</div></section>
<section class="band cream" id="markets"><div class="wrap wide two"><div><div class="kicker">Markets<i></i></div><h2 class="h3">What the Kalshi market quotes</h2>{market_card("senate")}</div>
<div><p class="small">The contract resolves on the party sworn in to the seat. A price is what traders were willing to pay at the capture time. It is not a forecast, a poll or a vote share. We have not shown a poll: we found no general-election poll with an original release.</p>
<p class="small"><a href="https://www.fec.gov/data/elections/senate/{SX["code"]}/2026/" rel="noopener">Candidate committee totals on FEC.gov ↗</a></p></div></div></section>
<section class="band" id="others"><div class="wrap wide"><div class="kicker">The other candidates<i></i></div><h2 class="h3">Everyone else on our roster</h2>
{_others_table(rest, "Write-in candidates do not appear as printed ballot choices.")}</div></section>
<section class="band cream" id="sources"><div class="wrap wide"><div class="kicker">Sources<i></i></div><p class="small meth">{e(_src_line())}</p>{_roster_note()}<p class="small"><a href="/about/election-methods/">Methods ↗</a></p></div></section>'''
    _wrapup(body, f"{name} U.S. Senate Race 2026", f"{_poss(name)} U.S. Senate election: the candidates on our roster, the Kalshi quote and what is on file, with sources and the limits of the roster.", ST_URL + "senate/", crumbs)

# ------------------------------------------------------------------ Methods
def methods_page():
    crumbs = [("Home", "/"), ("About", "/about/"), ("Election methods", None)]
    rows = "".join(f'<tr><td>{e(i["name"])}</td><td>{e(i["question"])}</td></tr>' for i in FL["issues"])
    body = f'''<section class="page-head"><div class="wrap">{_crumbs(crumbs)}<div class="kicker">About<i></i></div><h1 class="display">Election <em>methods</em></h1><p class="dek">How LLF's election pages source, label and correct what they show.</p></div></section>
<section class="band cream"><div class="wrap narrow prose meth-body">
<h2 id="roster" class="h3">Who counts as a candidate</h2><p>We list every candidate the Florida Division of Elections shows as Qualified or Unopposed for the November 3, 2026 general election in the governor, U.S. Senate and U.S. House contests. Write-in candidates the state lists as qualified are labeled and are not printed ballot choices. We do not rank candidates, pick winners or recommend votes. We captured the state's candidate lists on {dstr(FL["roster"]["captured_at_utc"])} and keep the raw capture.</p>
<p>Illinois: the State Board of Elections candidate list returned HTTP 403 to our tools, so the Illinois roster is transcribed from Green Papers, cross-checked against OpenFEC and TIP, and is <b>not an official or complete list</b>. Illinois write-in candidates appear only where the source lists them. We will replace it with the Board's list when we can read it.</p>
<h2 id="districts" class="h3">District map</h2><p>House districts use the Florida Legislature's official plan EOGPCRP2026 (HB 1-D), enacted in May 2026. The map is the subject of ongoing litigation. County names on district pages are land-area shares from Census county boundaries intersected with that file. Illinois districts use the U.S. Census Bureau's cartographic boundary file cb_2024_us_cd119_500k (119th Congress), the plan in use for 2026.</p>
<h2 id="money" class="h3">Money</h2><p><b>Candidate committee totals</b> are receipts and disbursements reported to the FEC for the period shown. <b>Independent expenditures</b> are spending by other groups to support or oppose a candidate, reported on FEC Schedule E; we use 24/48-hour reports, which are the most current, and drop the same transaction when it is re-reported on a periodic filing so it is not counted twice. They are never added to candidate receipts. <b>Public matching funds</b> are state payments to governor candidates and can already be counted in campaign receipts. Governor candidates file with the state, not the FEC.</p>
<h2 id="markets" class="h3">Markets</h2><p>Kalshi prices are what traders were willing to pay for a contract at a stated time. They are market-implied estimates, not polls, vote shares or forecasts. Governor, Senate and Michigan Senate contracts resolve on the party of the winner. We show last trade, bid and ask exactly as the public API returned them with the capture time. Charts plot captured points only.</p>
<h2 id="grades" class="h3">TIP Issue Grades</h2><p>TIP tracks six issues. For each candidate and issue, TIP counts recorded congressional acts (votes, sponsorships and cosponsorships that TIP's reviewers approved and mapped to the issue) that align with TIP's position and acts that are against it. The grade is aligned divided by the total of both. An issue needs at least one recorded act to be graded. A candidate's reviewed answer to a TIP question can move one issue's score by half a point, up or down, once per issue. The score is rounded half up and mapped to a letter (A+ at 97 and above down to F- at 53 and below). Not voting, voting present and contested entries are not counted.</p>
<p><b>A grade of F- from 0 of 5 aligned acts is a real grade. A dash means not graded: no recorded acts.</b> Challengers and candidates who never served in Congress are not graded, and that is not a score of zero. Governor and state offices have different powers than Congress, so a federal grade describes a congressional record only. TIP's grades are TIP's published method, not an objective measure of a person.</p>
<div class="tablewrap"><table class="data"><thead><tr><th>Issue</th><th>The question TIP asks</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small">The sixth issue, Section 224 of the FY27 NDAA, is a single-provision record rather than a broad issue frame, and has no answer options for the reviewed-answer adjustment.</p>
<h2 id="portraits" class="h3">Portraits</h2><p>Portraits are used only where a public-domain, CC0 or openly licensed image exists. Credit and license are on file in our asset manifest. Candidates without a licensed image show a monogram. Which candidates have photos reflects what is licensed, not an editorial choice.</p>
<h2 id="corrections" class="h3">Updates and corrections</h2><p>Every page shows when it was last checked. Errors are corrected visibly and logged on the <a href="/about/corrections/">corrections page</a>. Data can change after we check it; the state, the FEC and Kalshi are the controlling sources.</p></div></section>'''
    API["shell"]("Election methods", "How LookLearnFind sources, labels and corrects election data: rosters, FEC money, Kalshi prices and TIP Issue Grades.", "/about/election-methods/", body, nav="about", css=("elections",), js=("common",), jsonld=_jsonld("Election methods", "/about/election-methods/", crumbs))


def dark_horse_status_page():
    """Coverage and freshness of the daily dark-horse monitor. Not a ranking: alphabetical by state, no scores, no odds comparison."""
    import csv as _csv
    B = D / "dark_horse"
    st = _j(B / "status.json")
    if not st or not (B / "coverage_matrix.csv").exists():
        return
    rows = list(_csv.DictReader(open(B / "coverage_matrix.csv", encoding="utf-8")))
    src = "".join(f'<tr><td>{e(k)}</td><td>{e(v.get("last_success_at") or "never")}</td><td>{"STALE" if v.get("stale") else "fresh"}</td><td>{e(v.get("last_error") or "")}</td></tr>' for k, v in st["sources"].items())
    def cl(x):
        return {"ok": "quote", "unavailable": "no market", "no_market": "no market", "not_monitored": "not monitored", "no_poll_found": "no poll found"}.get(x, x)
    body = "".join(
        f'<tr><td>{e(r["state"])} {e(r["race"])}</td><td>{e(r["candidate_name"])}</td><td>{e(r["lock_status"])}</td><td>{e(r["nov3_general_status"])}</td>'
        f'<td>{cl(r["kalshi"])}{(" · " + e(r["kalshi_contract_kind"])) if r["kalshi"] == "ok" else ""}</td><td>{cl(r["polymarket"])}</td><td>{e(str(r["polls_votehub"]))}</td><td>{cl(r["poll_status"])}</td></tr>'
        for r in rows)
    cv = st["coverage"]
    html = f'''<section class="page-head"><div class="wrap">{_crumbs([("Home", "/"), ("Politics", "/politics/"), ("Dark-horse monitor", None)])}<div class="kicker">Reporting tool<i></i></div>
<h1 class="display h1r">Dark-horse monitor: <em>coverage</em></h1><p class="dek">What the daily collector found for each watchlisted race: market quotes, polls and gaps. This is a coverage report for reporters. It does not rank or recommend candidates, and market prices are not forecasts.</p>
<p class="meta"><span>Last run {e(st["last_run_date"])}</span><span>{cv["watchlist_monitored"]} races monitored</span></p></div></section>
<section class="band cream"><div class="wrap"><h2 class="h3">Sources</h2><div class="tablewrap"><table class="data"><thead><tr><th>Source</th><th>Last success (UTC)</th><th>State</th><th>Last error</th></tr></thead><tbody>{src}</tbody></table></div>
<h2 class="h3" style="margin-top:26px">Coverage by race</h2><div class="tablewrap"><table class="data"><thead><tr><th>Race</th><th>Candidate</th><th>Evidence status</th><th>Nov 3 ballot</th><th>Kalshi</th><th>Polymarket</th><th>Polls</th><th>Poll status</th></tr></thead><tbody>{body}</tbody></table></div>
<p class="small">Kalshi contracts for House and Senate races resolve on the party of the person sworn in and are labeled with the candidate's name; they are not named-candidate contracts. Polymarket contracts shown are individual-winner contracts. Polls come from VoteHub's API (beta) with the original poll link and sponsor; absence of a poll is "no poll found", not zero. Status "verified" means a documented criterion has a cited source; "partial", "unverified" and "background" rows are research leads. Nothing here is a ranking.</p></div></section>'''
    API["shell"]("Dark-horse monitor coverage", "Coverage and freshness of the daily market and poll collection for watchlisted races.", "/elections/2026/dark-horse/status/", html, nav="politics",
                css=("elections",), js=("common",), noindex=True, sitemap=False)

# ------------------------------------------------------------------ build + report layout
def build(api):
    API.update(api)
    load()
    for st in API["STORIES"]:
        if st.get("layout") == "report":
            for k in ("title", "dek"):
                st[k] = expand_values(st.get(k, ""))
    state_hub(); gov_page(); senate_page(); house_page(); methods_page(); dark_horse_status_page()
    for i in range(1, 29):
        district_page(i)
    _load_state("IL")
    state_hub(); gov_page(); senate_page(); house_page()
    for i in range(1, SX["ndist"] + 1):
        district_page(i)
    load()          # report articles read the Florida data

def macro_html(name):
    return MACROS[name]()

def _mi_card(c):
    p = FL["mi"]["portraits"].get(c["id"], {})
    img = f'<img src="/img/elections/portraits/{c["id"]}.jpg" alt="Portrait of {e(c["name"])}" loading="lazy" width="240" height="300">' if p.get("result") == "ok" else f'<span class="mono">{e(initials(c["name"]))}</span>'
    link = f'<a class="btn-o" href="{e(c["tip_url"])}" rel="noopener">View on TIP →</a>' if c.get("tip_url") else ""
    return f'<div class="mic"><span class="ph">{img}</span><span class="pchip">{PLET[c["party_code"]]}</span><b>{e(c["name"])}</b><small>{e(c["party"])}</small>{link}</div>'

def mi_aside():
    mi = FL["mi"]
    d = {r["end_utc"][:10]: r for r in mi["d"]["daily"]}
    last = mi["d"]["daily"][-1]
    cands = mi["cands"]
    fin = mi["fin"]["totals"]
    frows = "".join(f'<dt>{e(c["name"])}</dt><dd>{money(fin[c["id"]]["receipts"])} <small>through {dstr(fin[c["id"]]["coverage_end_date"], "%b %-d")}</small></dd>' for c in cands)
    return f'''<aside class="relrail"><div class="rb"><div class="uc teal"><a href="https://theissuesparty.org/races/2026-S-MI" rel="noopener">Michigan Senate race on TIP ↗</a></div><div class="mics">{"".join(_mi_card(c) for c in cands)}</div></div>
<div class="rb"><div class="uc teal">Quick stats (Kalshi)</div><dl class="kv2"><dt>El-Sayed contract, last daily close ({dstr(last["et_day"], "%b %-d")})</dt><dd>{cents(last["close"])}</dd><dt>Bid / ask at close</dt><dd>{cents(last["bid_close"])} / {cents(last["ask_close"])}</dd><dt>Contract</dt><dd>SENATEMI-26-D</dd></dl></div>
<div class="rb"><div class="uc teal">Latest poll (Marist)</div><dl class="kv2"><dt>El-Sayed (likely voters)</dt><dd>50%</dd><dt>Rogers (likely voters)</dt><dd>48%</dd><dt>Margin of error</dt><dd>±4.3</dd><dt>Field dates</dt><dd>Oct 15–18</dd></dl><p class="small">Registered voters: El-Sayed +7 (±4.0).</p></div>
<div class="rb"><div class="uc teal">Candidate committee receipts (FEC)</div><dl class="kv2">{frows}</dl><p class="small">Different report periods; do not compare directly.</p></div></aside>'''

def spend_aside():
    cs = [c for c in FL["cands"] if c["race"] in ("house-14", "house-25")]
    tot14, l14, n14 = ie_total("house-14"); tot25, l25, n25 = ie_total("house-25")
    return f'''<aside class="relrail"><div class="rb"><div class="uc teal">Independent expenditures, 2026 cycle</div><dl class="kv2"><dt>FL-14</dt><dd>{money(tot14)}</dd><dt>FL-25</dt><dd>{money(tot25)}</dd></dl><p class="small">FEC 24/48-hour reports through {dstr(max(l14, l25))}. Duplicates removed.</p></div>
<div class="rb"><div class="uc teal">Candidates</div><ul class="plain">{"".join(f'<li>{chip(c)} <a href="{ST_URL}house/{c["race"].split("-")[1]}/#c-{e(c["id"])}">{e(c["name"])}</a> <small>FL-{c["race"].split("-")[1]}</small></li>' for c in cs if c["party_code"] in ("REP", "DEM"))}</ul></div></aside>'''

def gov_aside():
    cs = [c for c in FL["by_race"]["governor"] if c["party_code"] in ("REP", "DEM")]
    return f'''<aside class="relrail"><div class="rb"><div class="uc teal">Quick comparison</div><dl class="kv2"><dt>Donalds (R)</dt><dd>Running mate Bryan Avila</dd><dt>Jolly (D)</dt><dd>Running mate Gwen Graham</dd></dl></div>
<div class="rb"><div class="uc teal">Latest poll (UNF)</div><dl class="kv2"><dt>Donalds</dt><dd>49%</dd><dt>Jolly</dt><dd>47%</dd><dt>Likely voters</dt><dd>1,471</dd><dt>Field dates</dt><dd>Oct 12–19</dd><dt>Margin of error</dt><dd>±2.81</dd></dl></div>
<div class="rb"><div class="uc teal">Kalshi governor contract</div><dl class="kv2">{"".join(f'<dt>{e(c["yes_label"])}</dt><dd>{cents(c["last"])}</dd>' for c in sorted(FL["markets"]["races"]["governor"]["contracts"], key=lambda x: -float(x["last"])))}</dl><p class="small">Captured {utc_stamp(FL["markets"]["captured_at_utc"])}.</p></div></aside>'''

ASIDES = {"delta": mi_aside, "spend": spend_aside, "gov": gov_aside}

def gov_cands():
    return '<div class="ccards two">' + "".join(candidate_card(c, "xl") for c in FL["by_race"]["governor"] if c["party_code"] in ("REP", "DEM")) + "</div>" + tip_panel([c for c in FL["by_race"]["governor"] if c["party_code"] in ("REP", "DEM")])

def gov_others():
    others = [c for c in FL["by_race"]["governor"] if c["party_code"] not in ("REP", "DEM")]
    for c in others:
        if not (c.get("tip") and c["tip"].get("url")):
            violate("R1 no TIP profile", c["name"])
    rows = "".join(f'<tr><td>{('<a href="' + e(c["tip"]["url"]) + '" rel="noopener">' + e(c["name"]) + "</a>") if c.get("tip") and c["tip"].get("url") else e(c["name"])}</td><td>{e(c["party"])}</td><td>{e(c.get("running_mate") or "—")}</td></tr>' for c in others)
    return f'<div class="tablewrap"><table class="data"><thead><tr><th>Candidate</th><th>Designation</th><th>Running mate</th></tr></thead><tbody>{rows}</tbody></table></div>'

def stats_delta():
    daily = {r["et_day"]: r for r in FL["mi"]["d"]["daily"]}
    pick = [("2026-10-05", "close, Oct 5", "before the slide"), ("2026-10-07", "close, Oct 7", "the day before the debate"), ("2026-10-09", "close, Oct 9", "the day after the debate, the low"), ("2026-10-22", "close, Oct 22", "latest full day")]
    expect = {"2026-10-05": "73¢", "2026-10-07": "71¢", "2026-10-09": "67¢", "2026-10-22": "69¢"}
    for k, v in expect.items():   # copy in the article was written from these numbers; fail the build if the data changes
        assert cents(daily[k]["close"]) == v, (k, daily[k]["close"], v)
    return '<div class="statrow">' + "".join(f'<div><b>{cents(daily[k]["close"])}</b><span>{a}</span><small>{c}</small></div>' for k, a, c in pick) + "</div>"

def stats_gov():
    return ('<div class="statrow"><div><b>10</b><span>qualified tickets</span><small>Florida Division of Elections</small></div>'
            '<div><b>49–47</b><span>Donalds–Jolly, UNF poll</span><small>likely voters, Oct 12–19</small></div>'
            '<div><b>$4.47M</b><span>state matching funds paid to governor candidates</span><small>through Oct 23</small></div>'
            f'<div><b>{cents(max(FL["markets"]["races"]["governor"]["contracts"], key=lambda x: float(x["last"]))["last"])}</b><span>Kalshi last trade, Republican contract</span><small>{utc_stamp(FL["markets"]["captured_at_utc"])}</small></div></div>')

def spend_tables():
    out = ""
    for race, lab in (("house-14", "FL-14: Castor (D) and Beltran (R)"), ("house-25", "FL-25: Moskowitz (D) and Singer (R)")):
        tbl, latest = ie_table(race, 8)
        tot, _l, cnt = ie_total(race)
        out += f'<h3 class="sub">{e(lab)}</h3><p class="bignum"><b>{money(tot)}</b><span>reported, 2026 cycle, through {dstr(latest)} · {cnt} reports after removing duplicates</span></p>{tbl}'
    return out

MACROS = {
    "delta_chart": delta_chart,
    "spend14": lambda: spend_chart("house-14", "FL-14: weekly independent expenditures"),
    "spend25": lambda: spend_chart("house-25", "FL-25: weekly independent expenditures"),
    "spend_tables": spend_tables,
    "gov_cands": gov_cands,
    "gov_others": gov_others,
    "stats_delta": stats_delta,
    "stats_gov": stats_gov,
}

def _ie_week(race, d0, d1):
    rows, _l = race_ie(race)
    return sum(r["expenditure_amount"] for r in rows if d0 <= (r.get("dissemination_date") or r["expenditure_date"])[:10] <= d1)

def _ie_dir(race):
    rows, _l = race_ie(race)
    out = {"R": 0.0, "D": 0.0}
    for r in rows:
        c, so = r["cand"], r["support_oppose_indicator"]
        if c["party_code"] in ("REP", "DEM"):
            out["R" if (c["party_code"] == "REP") == (so == "S") else "D"] += r["expenditure_amount"]
    return out

def _est_share(race):
    rows, _l = race_ie(race)
    tot = sum(r["expenditure_amount"] for r in rows)
    est = sum(r["expenditure_amount"] for r in rows if "ESTIMATE" in (r.get("expenditure_description") or "").upper())
    return round(100 * est / tot) if tot else 0

def _cand(name):
    return next(c for c in FL["cands"] if c["name"] == name)

def _rcpt(name):
    t = fec_totals(_cand(name))
    return money(t["receipts"]), dstr(t["coverage_end_date"], "%b %-d")

def values():
    t14, l14, n14 = ie_total("house-14"); t25, l25, n25 = ie_total("house-25")
    d14, d25 = _ie_dir("house-14"), _ie_dir("house-25")
    V = {"ie14": money(t14), "ie25": money(t25), "ie_both": money(t14 + t25), "ie14_exact": money(t14, True), "ie25_exact": money(t25, True),
         "n14": str(n14), "n25": str(n25), "l14": dstr(l14, "%b %-d"), "l25": dstr(l25, "%b %-d"),
         "wk14": money(_ie_week("house-14", "2026-09-30", "2026-10-06")), "wk25": money(_ie_week("house-25", "2026-09-30", "2026-10-06")),
         "wk14b": money(_ie_week("house-14", "2026-10-14", "2026-10-20")), "wk25b": money(_ie_week("house-25", "2026-10-14", "2026-10-20")),
         "r14": money(d14["R"]), "d14": money(d14["D"]), "r25": money(d25["R"]), "d25": money(d25["D"]),
         "est14": str(_est_share("house-14")), "est25": str(_est_share("house-25")),
         "castor": _rcpt("Kathy Castor")[0], "castor_d": _rcpt("Kathy Castor")[1], "beltran": _rcpt("Mike Beltran")[0], "beltran_d": _rcpt("Mike Beltran")[1],
         "moskowitz": _rcpt("Jared Moskowitz")[0], "moskowitz_d": _rcpt("Jared Moskowitz")[1], "singer": _rcpt("Scott Singer")[0], "singer_d": _rcpt("Scott Singer")[1]}
    return V

def _alias_table():
    """name -> (regex of aliases, profile url or None, landing page for the candidate on LLF)."""
    t = {}
    def add(name, aliases, url, page):
        t[name] = (aliases, url, page)
    for c in FL["cands"]:
        if c["name"] in ("Byron Donalds", "David Jolly", "Kathy Castor", "Mike Beltran", "Jared Moskowitz", "Scott Singer", "Ashley Moody", "Angie Nixon"):
            last = c["name"].split()[-1]
            race = c["race"]
            page = ST_URL + ("governor/" if race == "governor" else "senate/" if race == "senate" else f"house/{int(race.split('-')[1])}/")
            tip = c.get("tip") or {}
            add(c["name"], [c["name"], last], tip.get("grades_url") or tip.get("url"), page + "#c-" + c["id"])
    add("Jay Collins", ["Jay Collins", "Collins"], "https://theissuesparty.org/candidates/GOV-FL-COLLINS", ST_URL + "governor/")
    for c in FL["mi"]["cands"]:
        add(c["name"], [c["name"], c["name"].split()[-1]], c.get("tip_url"), "/learn/michigan-senate-delta-october-2026/")
    return t

RACE_PATTERNS = [
    (r"FL-(\d{1,2})", lambda m: (f"race:fl-{int(m.group(1))}", f"{ST_URL}house/{int(m.group(1))}/")),
    (r"Florida(?:'s)? governor(?:'s)? race|governor(?:'s)? race|governor race", lambda m: ("race:governor", ST_URL + "governor/")),
    (r"Florida(?:'s)? (?:U\.S\. )?Senate race", lambda m: ("race:senate", ST_URL + "senate/")),
    (r"Michigan(?:'s)? (?:U\.S\. )?Senate race", lambda m: ("race:mi-senate", "https://theissuesparty.org/races/2026-S-MI")),
]

def autolink(body, story_path):
    """Publishing rules R1 and R2: first mention of every featured candidate links to their TIP profile (R1); first mention of every race links to that race (R2).
    Candidates with no TIP profile link to their LLF race page and are reported as R1 violations."""
    table = _alias_table()
    alts = []
    for name, (aliases, url, page) in table.items():
        for a in aliases:
            alts.append((a, name))
    alts.sort(key=lambda x: -len(x[0]))
    name_re = "|".join(r"\b" + re.escape(a) + r"\b" for a, _ in alts)
    race_re = "|".join("(?:" + pat + ")" for pat, _ in RACE_PATTERNS)
    big = re.compile("(" + race_re + "|" + name_re + ")")
    seen = set()
    SKIP = {"a", "h1", "h2", "h3", "h4", "h5", "h6", "script", "style", "svg", "figure", "figcaption", "table", "button", "title", "aside"}
    stack, out = [], []
    for tok in re.split(r"(<[^>]+>)", body):
        if tok.startswith("<"):
            m = re.match(r"<(/?)([a-zA-Z0-9]+)", tok)
            if m and not tok.endswith("/>"):
                tag = m.group(2).lower()
                if tag in SKIP:
                    if m.group(1):
                        if tag in stack:
                            stack.remove(tag)
                    else:
                        stack.append(tag)
            out.append(tok)
            continue
        if stack:
            out.append(tok)
            continue
        def rep(m):
            txt = m.group(0)
            for pat, fn in RACE_PATTERNS:
                mm = re.fullmatch(pat, txt)
                if mm:
                    key, href = fn(mm)
                    if key in seen:
                        return txt
                    seen.add(key)
                    ext = ' rel="noopener"' if href.startswith("http") else ""
                    return f'<a class="plink" href="{href}"{ext}>{txt}</a>'
            for a, name in alts:
                if a == txt:
                    key = "cand:" + name
                    if key in seen:
                        return txt
                    seen.add(key)
                    aliases, url, page = table[name]
                    if url:
                        return f'<a class="plink" href="{e(url)}" rel="noopener">{txt}</a>'
                    violate("R1 no TIP profile", name)
                    return f'<a class="plink" href="{page}">{txt}</a>'
            return txt
        out.append(big.sub(rep, tok))
    return "".join(out)

def rules_report():
    n = len(VIOL)
    lines = [f"PUBLISHING RULES: {n} violation(s)"] + [f"  {r}: {d} on {p}" for p, r, d in VIOL]
    if GAPS:
        lines.append(f"DIRECTORY GAPS (not blocking, resolve before an Illinois page is published): {len(GAPS)} listed candidates have no TIP profile: " + ", ".join(nm for _s, nm in GAPS))
    return n, "\n".join(lines)

def expand_values(text):
    V = values()
    return re.sub(r"\[\[v:([a-z0-9_]+)\]\]", lambda m: V[m.group(1)], text or "")

def expand_macros(body):
    body = re.sub(r"\[\[el:([a-z0-9_]+)\]\]", lambda m: MACROS[m.group(1)](), body)
    V = values()
    return re.sub(r"\[\[v:([a-z0-9_]+)\]\]", lambda m: V[m.group(1)], body)

def render_report(s):
    """ReportedArticle: story body + rail + sources, using the shared story contract (openfile, sources, corrections blocks)."""
    A = API
    CUR[0] = s["path"]
    body = s["_body"]
    openfile, body = A["take_block"](body, "openfile")
    sources_raw, body = A["take_block"](body, "sources")
    corr_raw, body = A["take_block"](body, "corrections")
    openfile = expand_values(openfile) if openfile else openfile
    srcs = []
    for line in (sources_raw or "").splitlines():
        p = [x.strip() for x in line.split("|")]
        if len(p) >= 6 and p[0].isdigit():
            srcs.append(dict(n=int(p[0]), title=p[1], pub=p[2], date=p[3], url=p[4], why=p[5]))
    body = expand_macros(body)
    body = autolink(body, s["path"])
    body = re.sub(r"\[\[s:(\d+)\]\]", lambda m: f'<a class="fn" id="ref-{m.group(1)}" href="#source-{m.group(1)}" aria-label="Source {m.group(1)}">SOURCE {int(m.group(1)):02d}</a>', body)
    of = ""
    if openfile:
        d = A["kv_block"](openfile)
        rows = [("The question", "question"), ("What we checked", "checked"), ("What the sources support", "supported"), ("Other views", "other"), ("What remains open", "open")]
        of = '<div class="open-file"><h3>Open file</h3><dl>' + "".join(f"<dt>{l}</dt><dd>{d[k]}</dd>" for l, k in rows if d.get(k)) + "</dl></div>"
    src_html = '<div class="sources" id="sources"><h2>Sources</h2>' + "".join(
        f'<div class="src" id="source-{x["n"]}"><span class="k">SOURCE {x["n"]:02d}</span><div><span class="ti"><a href="{e(x["url"])}" rel="noopener">{e(x["title"])}</a></span>{e(x["pub"])} · {e(x["date"])}<div class="why"><b>Why it matters:</b> {e(x["why"])}</div></div></div>' for x in srcs) + "</div>"
    if corr_raw:
        corr = '<div class="corrections"><b>Updates and corrections.</b><br>' + "<br>".join(f"{e(dstr(l.split('|')[0].strip()))} — {e(l.split('|', 1)[1].strip())}" for l in corr_raw.splitlines() if "|" in l) + "</div>"
    else:
        corr = '<div class="corrections"><b>Updates and corrections.</b> None so far. Corrections are logged on the <a href="/about/corrections/">corrections page</a>.</div>'
    toc_items = re.findall(r'<h2 id="([a-z0-9-]+)">(.*?)</h2>', body)
    toc = ('<nav class="onpage" aria-label="In this article"><div class="uc">In this article</div><ol>' + "".join(f'<li><a href="#{a}">{re.sub("<[^>]+>", "", t)}</a></li>' for a, t in toc_items) + "</ol></nav>") if toc_items else ""
    hero_key = s.get("hero", "")
    hero = _hero(hero_key, s.get("hero_alt", ""), s.get("hero_title", ""), s.get("hero_text", "")) if hero_key else ""
    rail = ASIDES[s["aside"]]() if s.get("aside") else ""
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    mins = max(3, round(words / 220))
    byline = (f'<div class="byline"><span><b>By</b> {e(s.get("author", "LookLearnFind"))}</span><span><b>Published</b> {e(A["fmt_date"](s.get("date", "")))}</span>'
              f'<span><b>Updated</b> {e(A["fmt_date"](s.get("updated", s.get("date", ""))))}</span><span><b>Read</b> {mins} min</span><span><b>Series</b> {e(s.get("format", ""))}</span></div>')
    crumbs = [("Home", "/"), ("Politics", "/politics/"), (s.get("format", "Report"), None)]
    html = f'''<article class="report"><section class="page-head el-head rep"><div class="wrap wide"><div class="hcol">{_crumbs(crumbs)}<div class="kicker">{e(s.get("format", ""))}<i></i></div><h1 class="display h1r">{e(s["title"])}</h1><p class="dek">{e(s.get("dek", ""))}</p>{byline}</div>{hero}</div></section>
<div class="wrap wide rgrid"><div class="rmain story-body">{of}{body.strip()}{src_html}{corr}</div><div class="rside">{toc}{rail}</div></div>
<section class="band cream"><div class="wrap wide"><div class="kicker">Explore the record<i></i></div><ul class="explore"><li><a href="{ST_URL}">Florida State of the Race: all 30 contests ↗</a></li><li><a href="{ST_URL}governor/">Governor race guide ↗</a></li><li><a href="{ST_URL}senate/">U.S. Senate race guide ↗</a></li><li><a href="{ST_URL}house/">House districts ↗</a></li><li><a href="/about/election-methods/">Methods, definitions and corrections ↗</a></li></ul></div></section>
</article>'''
    ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "NewsArticle", "headline": s["title"], "description": s.get("dek", ""),
          "datePublished": s.get("date", ""), "dateModified": s.get("updated", s.get("date", "")), "author": {"@type": "Organization", "name": "LookLearnFind"},
          "publisher": {"@type": "Organization", "name": "LookLearnFind"}, **({"image": "https://looklearnfind.com" + s["og"]} if s.get("og") else {}), "mainEntityOfPage": "https://looklearnfind.com" + s["path"]}) + "</script>"
    API["shell"](s["title"], s.get("dek", ""), s["path"], html, nav="politics", css=("elections",), js=("common", "elections"), jsonld=ld, og=(s.get("og") or None))


# ------------------------------------------------------------------ Florida Senate and House articles (2026-10-24)
# Components for the two long-form articles. Every number comes from data/elections/FL/story_data.json (with its source) or from the captured Kalshi/TIP data.
_SD = {}
def _sd():
    if not _SD:
        _SD.update(_j(D / "FL/story_data.json", {}))
    return _SD

def _bar_row(y, label, pct, scale, fill, note=""):
    w = max(2, round(pct / scale * 430))
    return (f'<text x="0" y="{y + 18}" class="rl">{e(label)}</text><rect x="190" y="{y}" width="{w}" height="26" fill="{fill}"/>'
            f'<text x="{190 + w + 8}" y="{y + 19}" class="rv">{pct:g}%</text>' + (f'<text x="190" y="{y + 42}" class="rn">{e(note)}</text>' if note else ""))

def poll_unf():
    u = _sd()["unf_oct"]
    rows = (_bar_row(8, "Ashley Moody (R)", u["moody"], 60, "#1c1d1b") + _bar_row(50, "Angie Nixon (D)", u["nixon"], 60, "#145b5d") + _bar_row(92, "Undecided", u["undecided"], 60, "#aeb8ad"))
    alt = f'UNF poll, {u["field_start"]} to {u["field_end"]}: Moody {u["moody"]} percent, Nixon {u["nixon"]} percent, undecided {u["undecided"]} percent, {u["n"]:,} likely voters, margin of error plus or minus {u["moe"]}.'
    return (f'<figure class="chartwrap pollcard"><h4>UNF poll, Florida U.S. Senate</h4><svg class="chart" viewBox="0 0 680 140" role="img" aria-label="{e(alt)}">{rows}</svg>'
            f'<figcaption>{e(u["pollster"])}, fielded Oct 12–19 by telephone among {u["n"]:,} {e(u["population"])}; margin of error ±{u["moe"]} points overall. Published Oct 21. Reported by '
            f'<a href="{e(u["sources"][0])}" rel="noopener">WLRN</a> and <a href="{e(u["sources"][1])}" rel="noopener">Action News Jax</a>. A poll is a snapshot, not a forecast.</figcaption></figure>')

def sept_polls():
    sd = _sd()
    rows = "".join(f'<tr><td>{e(p["pollster"])}</td><td>{e(p["sponsor"])}</td><td>{e(p["field"])}</td><td class="num">{p["n"]:,}</td><td class="num">±{p["moe"]}</td>'
                   f'<td class="num">{p["moody"]:g}</td><td class="num">{p["nixon"]:g}</td></tr>' for p in sd["sept_polls"])
    return ('<div class="tablewrap"><table class="data"><caption class="sr">September polls of Florida likely voters</caption><thead><tr><th>Pollster</th><th>Sponsor</th><th>Fielded</th>'
            '<th class="num">Sample</th><th class="num">Margin</th><th class="num">Moody</th><th class="num">Nixon</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
            f'<p class="small">All three polled likely Florida voters in September 2026. Listing as published by <a href="{e(sd["sept_source"])}" rel="noopener">Newsweek</a>; we have not opened the pollsters\' own releases.</p>')

def _sen_pair():
    return [_cand("Ashley Moody"), _cand("Angie Nixon")]

def sen_cards():
    return '<div class="ccards two">' + "".join(candidate_card(c, "xl", finance=False) for c in _sen_pair()) + "</div>" + tip_panel(_sen_pair())

def mk_sen():
    return market_card("senate", "What the Kalshi market shows")

def stats_sen():
    u = _sd()["unf_oct"]
    r = next(c for c in FL["markets"]["races"]["senate"]["contracts"] if c["ticker"].endswith("-R"))
    return ('<div class="statrow">'
            f'<div><b>{u["moody"]}–{u["nixon"]}</b><span>Moody–Nixon, UNF poll</span><small>likely voters, Oct 12–19</small></div>'
            f'<div><b>{u["n"]:,}</b><span>likely voters polled</span><small>margin of error ±{u["moe"]}</small></div>'
            f'<div><b>{cents(r["last"])}</b><span>Kalshi last trade, Republican party contract</span><small>{utc_stamp(FL["markets"]["captured_at_utc"])}</small></div>'
            '<div><b>3</b><span>candidates on the ballot</span><small>Florida Division of Elections</small></div></div>')

def sen_aside():
    u = _sd()["unf_oct"]
    cs = _sen_pair()
    def img(c):
        if FL["portraits"].get(c["id"], {}).get("result") == "ok":
            return f'<img src="/img/elections/portraits/{c["id"]}.jpg" alt="Portrait of {e(c["name"])}" loading="lazy" width="240" height="300">'
        return f'<span class="mono">{e(initials(c["name"]))}</span>'
    mics = "".join(f'<div class="mic"><span class="ph">{img(c)}</span><span class="pchip">{PLET[c["party_code"]]}</span><b>{e(c["name"])}</b><small>{e(c["party"])}</small>'
                   f'<a class="btn-o" href="{e(c["tip"]["url"])}" rel="noopener">View on TIP →</a></div>' for c in cs)
    return (f'<aside class="relrail"><div class="rb"><div class="uc teal"><a href="https://theissuesparty.org/races/2026-S-FL" rel="noopener">Florida Senate race on TIP ↗</a></div><div class="mics">{mics}</div></div>'
            f'<div class="rb"><div class="uc teal">Latest poll (UNF)</div><dl class="kv2"><dt>Moody</dt><dd>{u["moody"]}%</dd><dt>Nixon</dt><dd>{u["nixon"]}%</dd><dt>Undecided</dt><dd>{u["undecided"]}%</dd>'
            f'<dt>Likely voters</dt><dd>{u["n"]:,}</dd><dt>Field dates</dt><dd>Oct 12–19</dd><dt>Margin of error</dt><dd>±{u["moe"]}</dd></dl></div></aside>')

def map_story():
    d = FL["districts"]
    vb = d["viewbox"]
    hl = [14, 9, 20, 6, 25]
    paths = "".join(f'<path d="{v["path"]}" class="dist{" on" if int(n) in hl else ""}"><title>FL-{int(n):02d}</title></path>' for n, v in d["districts"].items())
    off = {20: (-70, -34), 25: (-62, 38)}          # districts 20 and 25 sit side by side on the coast; pull their pins apart with leader lines
    pins = ""
    for n in hl:
        x, y = d["districts"][str(n)]["label_xy"]
        dx, dy = off.get(n, (0, 0))
        lead = f'<line x1="{x}" y1="{y}" x2="{x + dx}" y2="{y + dy}"/>' if dx or dy else ""
        pins += f'<g class="pin">{lead}<circle cx="{x + dx}" cy="{y + dy}" r="24"/><text x="{x + dx}" y="{y + dy + 8}" text-anchor="middle">{n}</text></g>'
    alt = "Map of Florida's 28 congressional districts under the 2026 plan with districts 6, 9, 14, 20 and 25 marked"
    return (f'<figure class="chartwrap mapstory"><h4>Where the story happens: five districts under the 2026 plan</h4><svg class="statemap" viewBox="0 0 {vb[2]} {vb[3]}" role="img" aria-label="{e(alt)}">{paths}{pins}</svg>'
            f'<figcaption>Districts 6, 9, 14, 20 and 25 marked. Boundaries: Florida Legislature plan EOGPCRP2026 (HB 1-D). Each district has its own page: <a href="{ST_URL}house/14/">FL-14</a>, '
            f'<a href="{ST_URL}house/9/">FL-9</a>, <a href="{ST_URL}house/6/">FL-6</a>, <a href="{ST_URL}house/20/">FL-20</a>, <a href="{ST_URL}house/25/">FL-25</a>.</figcaption></figure>')

def trump_bars():
    t = _sd()["trump_2024"]
    def row(y, lab, tr, ha, who):
        wt, wh = round(tr / 100 * 430), round(ha / 100 * 430)
        return (f'<text x="0" y="{y + 18}" class="rl">{e(lab)}</text><text x="0" y="{y + 36}" class="rn">{e(who)}</text><rect x="150" y="{y}" width="{wt}" height="26" fill="#1c1d1b"/>'
                f'<text x="158" y="{y + 19}" class="rv inv">Trump {tr}</text><rect x="{150 + wt}" y="{y}" width="{wh}" height="26" fill="#145b5d"/><text x="{158 + wt}" y="{y + 19}" class="rv inv">Harris {ha}</text>')
    alt = f'Reported 2024 presidential vote on the new lines: FL-14 Trump {t["fl14"]["trump"]}, Harris {t["fl14"]["harris"]}; FL-9 Trump {t["fl09"]["trump"]}, Harris {t["fl09"]["harris"]}.'
    return (f'<figure class="chartwrap"><h4>2024 presidential vote on the new district lines (reported)</h4><svg class="chart" viewBox="0 0 640 110" role="img" aria-label="{e(alt)}">'
            + row(6, "FL-14", t["fl14"]["trump"], t["fl14"]["harris"], "Castor (D) district") + row(56, "FL-9", t["fl09"]["trump"], t["fl09"]["harris"], "Soto (D) district")
            + f'</svg><figcaption>Reported by <a href="{e(t["source"])}" rel="noopener">WLRN</a> on May 5, 2026, for the redrawn lines. LLF has not recomputed them. Minor candidates are left out of the reported margins.</figcaption></figure>')

def result_bars():
    r = _sd()["primary_results"]
    rows = (_bar_row(8, "FL-6 · Fine (R)", r["fl06"]["winner_pct"], 70, "#145b5d", f'beat Bilzerian ({r["fl06"]["runner_up_pct"]:g}%) in the Republican primary')
            + _bar_row(62, "FL-25 · Moskowitz (D)", r["fl25"]["winner_pct"], 70, "#145b5d", "beat DSA-backed Larkin (share not reported)")
            + _bar_row(116, "FL-20 · Wasserman Schultz (D)", r["fl20"]["winner_pct"], 70, "#145b5d", "won a crowded field (other shares not reported)"))
    alt = f'Reported Aug 18 primary results: Fine {r["fl06"]["winner_pct"]} percent in FL-6, Moskowitz {r["fl25"]["winner_pct"]} percent in FL-25, Wasserman Schultz {r["fl20"]["winner_pct"]} percent in FL-20.'
    return (f'<figure class="chartwrap"><h4>August 18 primaries: winners\' reported shares</h4><svg class="chart" viewBox="0 0 680 170" role="img" aria-label="{e(alt)}">{rows}</svg>'
            f'<figcaption>Shares as reported by <a href="{e(r["source"])}" rel="noopener">Algemeiner</a> on Aug 19; {e(r["caveat"])}. The Division of Elections roster records all three as winners.</figcaption></figure>')

def house_cards_a():
    cs = [_cand("Kathy Castor"), _cand("Darren Soto")]
    return '<div class="ccards two">' + "".join(candidate_card(c, "xl", finance=False) for c in cs) + "</div>" + tip_panel(cs)

def house_cards_b():
    cs = [_cand("Jared Moskowitz"), _cand("Randy Fine"), _cand("Debbie Wasserman Schultz")]
    return '<div class="ccards three">' + "".join(candidate_card(c, "lg", finance=False) for c in cs) + "</div>"

def mk_h14():
    return market_card("house-14", "FL-14: what the Kalshi market shows")

def mk_h25():
    return market_card("house-25", "FL-25: what the Kalshi market shows")

def stats_house():
    sd = _sd()
    n = sum(1 for c in FL["cands"] if c["office"] == "house")
    t = sd["trump_2024"]
    return ('<div class="statrow">'
            f'<div><b>{sd["map"]["districts_reworked"]} of {sd["map"]["districts_total"]}</b><span>districts reworked in 2026</span><small>districts {sd["map"]["unchanged"]} unchanged</small></div>'
            f'<div><b>{t["fl14"]["trump"]}–{t["fl14"]["harris"]}</b><span>2024 vote, new FL-14 (reported)</span><small>Trump–Harris</small></div>'
            f'<div><b>{t["fl09"]["trump"]}–{t["fl09"]["harris"]}</b><span>2024 vote, new FL-9 (reported)</span><small>Trump–Harris</small></div>'
            f'<div><b>{n}</b><span>House candidates on the November ballot</span><small>Florida Division of Elections</small></div></div>')

def house_aside():
    links = "".join(f'<li><a href="{ST_URL}house/{n}/">FL-{n:02d} district page</a> · <a href="https://theissuesparty.org/races/2026-H-FL-{n:02d}" rel="noopener">on TIP ↗</a></li>' for n in (6, 9, 14, 20, 25))
    return (f'<aside class="relrail"><div class="rb"><div class="uc teal">The five districts</div><ul class="plain">{links}</ul></div>'
            '<div class="rb"><div class="uc teal">The map</div><dl class="kv2"><dt>Plan</dt><dd>EOGPCRP2026</dd><dt>Bill</dt><dd>HB 1-D</dd><dt>Reworked</dt><dd>21 of 28</dd><dt>Unchanged</dt><dd>1 to 7</dd></dl></div></aside>')

MACROS.update({"poll_unf": poll_unf, "sept_polls": sept_polls, "sen_cards": sen_cards, "mk_sen": mk_sen, "stats_sen": stats_sen, "map_story": map_story, "trump_bars": trump_bars,
               "result_bars": result_bars, "house_cards_a": house_cards_a, "house_cards_b": house_cards_b, "mk_h14": mk_h14, "mk_h25": mk_h25, "stats_house": stats_house})
ASIDES.update({"sen": sen_aside, "house": house_aside})

_values_base = values
def values():
    V = _values_base()
    sd = _sd()
    u = sd["unf_oct"]
    rs = next(c for c in FL["markets"]["races"]["senate"]["contracts"] if c["ticker"].endswith("-R"))
    V.update({"sen_moody": str(u["moody"]), "sen_nixon": str(u["nixon"]), "sen_undec": str(u["undecided"]), "sen_n": f'{u["n"]:,}', "sen_moe": str(u["moe"]), "sen_july": str(u["july_moody_lead"]),
              "vindman_raised": f'${sd["vindman_raised_through_june_musd"]} million', "fine_pct": f'{sd["primary_results"]["fl06"]["winner_pct"]:g}', "bilz_pct": f'{sd["primary_results"]["fl06"]["runner_up_pct"]:g}',
              "mosk_pct": f'{sd["primary_results"]["fl25"]["winner_pct"]:g}', "dws_pct": f'{sd["primary_results"]["fl20"]["winner_pct"]:g}',
              "t14": f'{sd["trump_2024"]["fl14"]["trump"]} to {sd["trump_2024"]["fl14"]["harris"]}', "t09": f'{sd["trump_2024"]["fl09"]["trump"]} to {sd["trump_2024"]["fl09"]["harris"]}',
              "sen_r_last": cents(rs["last"]), "gov_r_last": cents(next(c for c in FL["markets"]["races"]["governor"]["contracts"] if c["ticker"].endswith("-R"))["last"]), "gov_d_last": cents(next(c for c in FL["markets"]["races"]["governor"]["contracts"] if c["ticker"].endswith("-D"))["last"]), "sen_r_bid": cents(rs["yes_bid"]), "sen_r_ask": cents(rs["yes_ask"]), "mk_stamp": utc_stamp(FL["markets"]["captured_at_utc"])})
    return V


# ------------------------------------------------------------------ internal links to the long-form articles (audit fix: new reports were not linked from the guides)
_ART_SEN = ("Florida's Senate race tightens in the newest poll as Moody skips the debate", "/learn/florida-senate-special-election-poll-debate-october-2026/")
_ART_HOU = ("Florida redrew 21 House districts. Here is what changed and what the primaries showed", "/learn/florida-house-new-map-primaries-october-2026/")
_REPORTING = {ST_URL + "senate/": [_ART_SEN], ST_URL + "house/": [_ART_HOU], ST_URL: [_ART_SEN, _ART_HOU]}
_wrapup_base = _wrapup

def _wrapup(path_html, title, desc, path, crumbs, extra_js=("common", "elections")):
    arts = _REPORTING.get(path)
    if arts:
        path_html += ('<section class="band cream"><div class="wrap wide"><div class="kicker">Latest reporting<i></i></div><ul class="explore">'
                      + "".join(f'<li><a href="{h}">{e(t)} ↗</a></li>' for t, h in arts) + "</ul></div></section>")
    return _wrapup_base(path_html, title, desc, path, crumbs, extra_js)
