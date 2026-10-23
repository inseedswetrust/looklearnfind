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

# ------------------------------------------------------------------ data
def _j(p, default=None):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

FL = {}
def load():
    FL["roster"] = _j(D / "FL/roster.json")
    cj = _j(D / "FL/candidates.json")
    FL["issues"], FL["cands"], FL["tip_as_of"] = cj["issues"], cj["candidates"], cj["as_of_utc"]
    FL["fec"] = _j(D / "FL/finance_fec.json")
    FL["markets"] = _j(D / "FL/markets.json")
    FL["districts"] = _j(D / "FL/districts.json")
    FL["portraits"] = _j(D / "FL/portraits.json", {})
    FL["heroes"] = _j(D / "hero_credits.json", {})
    FL["ie"] = _j(D / "FL/ie_all.json", {"candidates": {}, "captured_at_utc": ""})
    FL["by_id"] = {c["id"]: c for c in FL["cands"]}
    FL["by_race"] = {}
    for c in FL["cands"]:
        FL["by_race"].setdefault(c["race"], []).append(c)
    for r, lst in FL["by_race"].items():
        lst.sort(key=_order)
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

PLET = {"DEM": "D", "REP": "R", "LPF": "L", "NPA": "N", "WRI": "W", "IND": "I", "FFP": "F", "ASP": "A"}

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
    return f'<a href="{e(c["state_url"])}" rel="noopener">Florida Division of Elections record ↗</a>'

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
    return (f'<div class="mk"><h3>{e(title)}</h3><p class="small">Kalshi contract prices are market-implied estimates, not forecasts or vote shares.</p>'
            f'<div class="quotes">{cells}</div><p class="small">{e(m["title"])} Last trade shown. Captured {utc_stamp(FL["markets"]["captured_at_utc"])}. '
            f'<a href="{e(m["url"])}" rel="noopener">Kalshi market ↗</a></p>'
            + (f'<details class="small"><summary>Contract rule</summary>{e(rule)}.</details>' if rule else "") + "</div>")

# ------------------------------------------------------------------ candidate cards
def candidate_card(c, size="lg"):
    extra = ""
    if c["primary"] in ("Won", "Unopposed"):
        extra = f'<span class="tag">{"Won primary" if c["primary"] == "Won" else "Unopposed in primary"}</span>'
    return f'''<article class="ccard {size}" id="c-{e(c["id"])}">
<div class="cc-top">{portrait(c)}<div><div class="nm">{chip(c)}<h3>{e(c["name"])}</h3></div><div class="ds">{e(c["party"])}{(" · " + e(descr(c))) if descr(c) else ""}</div>{extra}</div></div>
{finance_line(c, compact=(size == "sm"))}
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

TIPRACE = {"governor": "2026-GOV-FL", "senate": "2026-S-FL"}

def tip_race_url(race):
    key = TIPRACE.get(race) or ("2026-H-FL-" + race.split("-")[1])
    return f"https://theissuesparty.org/races/{key}"

def race_link_span(race):
    return f'<span><a href="{tip_race_url(race)}" rel="noopener">Follow this race on TIP ↗</a></span>'

def _asof():
    return datetime.date(2026, 10, 23)

def _jsonld(name, path, crumbs):
    return ('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": "https://looklearnfind.com" + h} if h else {})} for i, (n, h) in enumerate(crumbs)]}) + "</script>")

def _toc(items):
    return ('<nav class="onpage" aria-label="On this page"><div class="uc">On this page</div><ol>' + "".join(f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in items) + "</ol></nav>")

def _wrapup(path_html, title, desc, path, crumbs, extra_js=("common", "elections")):
    API["shell"](title, desc, path, path_html, nav="politics", css=("elections",), js=extra_js, jsonld=_jsonld(title, path, crumbs))

SOURCE_NOTE = ('Sources: Florida Division of Elections candidate lists (captured {cap}); OpenFEC candidate committee totals and Schedule E ({fec}); '
               'Kalshi public market data ({mk}); TIP Issue Grades from TIP ({tip}).')

def _src_line():
    return SOURCE_NOTE.format(cap=dstr(FL["roster"]["captured_at_utc"]), fec=dstr(FL["fec"]["as_of_utc"]), mk=utc_stamp(FL["markets"]["captured_at_utc"]), tip=dstr(FL["tip_as_of"]))

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
        on = " on" if highlight == n else ""
        p = f'<path d="{v["path"]}" class="dist{on}"><title>FL-{n:02d}</title></path>'
        paths.append(f'<a href="{ST_URL}house/{n}/" aria-label="Florida district {n}">{p}</a>' if links else p)
    return f'<svg class="{cls}" viewBox="0 0 {vb[2]} {vb[3]}" role="img" aria-label="Map of Florida\'s 28 congressional districts under the 2026 plan">{"".join(paths)}</svg>'

def board_tile(title, href, cands, kicker=""):
    lis = "".join(mini_row(c) for c in cands)
    return f'<a class="btile" href="{href}"><span class="tt"><b>{e(title)}</b><em>{kicker}</em></span><ul>{lis}</ul></a>'

def state_hub():
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

def house_page():
    CUR[0] = "/elections/2026/florida/house/"
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", ST_URL), ("U.S. House", None)]
    toc = [("map", "District map"), ("districts", "All 28 districts"), ("directory", "Directory"), ("tip", "TIP issue grades"), ("sources", "Sources")]
    n = _counts()
    dek = (f'<p class="deck">All 28 districts. Every qualified candidate.</p><p class="dek">Florida\'s 2026 House races use the congressional map enacted in May 2026 (HB 1-D), which is still under legal challenge. {n["house"]} candidates qualified across the 28 districts. District descriptions below come from the official district file, not from the old map.</p>'
           f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span></p>')
    hero = f'<div class="el-hero mapheroc">{state_map()}</div>'
    body = _race_head("State of the Race / U.S. House", "Florida House Races", dek, crumbs, hero, toc)
    tiles = []
    for i in range(1, 29):
        race, cs, d = district_summary(i)
        cn = ", ".join(f"{a}" for a, p in d["counties"][:3])
        mk = (FL["markets"]["races"].get(race) or {}).get("contracts")
        q = ""
        if mk:
            top = max(mk, key=lambda x: float(x["last"] or 0))
            q = f'<span class="qmini">Kalshi: {e(top["yes_label"].split()[-1])} {cents(top["last"])}</span>'
        tot, latest, cnt = ie_total(race)
        tiles.append(f'''<a class="dcard" href="{ST_URL}house/{i}/" id="d{i}"><div class="dmap"><svg viewBox="{' '.join(map(str, FL["districts"]["viewbox"]))}" aria-hidden="true"><path d="{FL["districts"]["state_outline"]}" class="outline"/><path d="{d["path"]}" class="dist on"/></svg></div>
<div class="dbody"><b class="dn">FL-{i:02d}</b><span class="dc">{e(cn)}</span><ul>{"".join(mini_row(c) for c in cs)}</ul><span class="dm">{q}{f'<span class="qmini">Outside spending {money(tot)}</span>' if tot else ""}</span></div></a>''')
    body += f'<section class="band" id="districts"><div class="wrap wide"><div class="kicker">All 28 districts<i></i></div><h2 class="h2">Browse by district</h2><div class="dgrid" data-view="cards">{"".join(tiles)}</div></div></section>'
    # directory table
    rows = []
    for i in range(1, 29):
        race, cs, d = district_summary(i)
        mk = (FL["markets"]["races"].get(race) or {}).get("contracts")
        q = "—"
        if mk:
            top = max(mk, key=lambda x: float(x["last"] or 0))
            q = f'{e(top["yes_label"])} {cents(top["last"])}'
        tot, latest, cnt = ie_total(race)
        rows.append(f'<tr><td><a href="{ST_URL}house/{i}/">FL-{i:02d}</a></td><td>{e(", ".join(f"{a} ({p}%)" for a, p in d["counties"][:3]))}</td><td>{"".join(chip(c) for c in cs)} {e(", ".join(c["name"] for c in cs))}</td><td class="num">{sum(1 for c in cs if graded_count(c))}</td><td>{q}</td><td class="num">{money(tot) if tot else "—"}</td></tr>')
    body += f'''<section class="band cream" id="directory"><div class="wrap wide"><div class="kicker">Directory<i></i></div><h2 class="h3">District directory</h2>
<div class="tablewrap"><table class="data wide"><thead><tr><th>District</th><th>Largest counties (share of district area)</th><th>Candidates</th><th class="num">Graded</th><th>Kalshi last trade (higher)</th><th class="num">Outside spending</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<p class="small">"Graded" counts candidates with at least one TIP Issue Grade. Kalshi contract exists for 26 of 28 districts; none was found for FL-13 and FL-23 on {dstr(FL["markets"]["captured_at_utc"])}. Outside spending is independent expenditures reported on FEC 24/48-hour reports in the 2026 cycle. County shares are land area from Census county boundaries intersected with the official district file.</p></div></section>
<section class="band" id="tip"><div class="wrap wide two"><div><div class="kicker">TIP issue grades<i></i></div><h2 class="h2">Who has a record to grade</h2><p class="dek">{sum(1 for c in FL["cands"] if c["office"] == "house" and graded_count(c))} of {n["house"]} House candidates have at least one TIP Issue Grade, because only people with recorded congressional acts can be graded. Challengers are not graded, and that is not a score of zero.</p></div>{tip_panel([c for c in FL["cands"] if c["office"] == "house"])}</div></section>
<section class="band cream" id="sources"><div class="wrap wide"><div class="kicker">Sources<i></i></div><p class="small meth">{e(_src_line())} District geometry: Florida Legislature EDR plan EOGPCRP2026 (HB 1-D). <a href="/about/election-methods/">Methods ↗</a></p></div></section>'''
    _wrapup(body, "Florida House Races 2026", "All 28 Florida congressional districts under the 2026 map: every qualified candidate, committee totals, outside spending, Kalshi quotes and TIP issue grades.", ST_URL + "house/", crumbs)

def district_page(n):
    CUR[0] = f"{ST_URL}house/{n}/"
    race, cs, d = district_summary(n)
    crumbs = [("Home", "/"), ("Politics", "/politics/"), ("State of the Race", ST_URL), ("U.S. House", ST_URL + "house/"), (f"FL-{n:02d}", None)]
    cn = ", ".join(f"{a} ({p}%)" for a, p in d["counties"])
    tbl, latest = ie_table(race, 6)
    tot, _l, cnt = ie_total(race)
    prev = f'<a href="{ST_URL}house/{n-1}/">← FL-{n-1:02d}</a>' if n > 1 else ""
    nxt = f'<a href="{ST_URL}house/{n+1}/">FL-{n+1:02d} →</a>' if n < 28 else ""
    dek = (f'<p class="deck">{len(cs)} candidates qualified for the November 3 general election.</p><p class="dek">Largest counties by share of district area: {e(cn)}. Under the 2026 plan (HB 1-D), enacted in May 2026 and still in litigation.</p>'
           f'<p class="meta"><span>Checked {dstr(_asof().isoformat())}</span>{race_link_span(race)}</p>')
    hero = f'<div class="el-hero mapheroc one">{state_map(highlight=n, links=False)}</div>'
    body = _race_head("State of the Race / U.S. House", f"Florida's {n}{_ord(n)} Congressional District", dek, crumbs, hero,
                      [("candidates", "The candidates"), ("money", "Money"), ("market", "Market"), ("sources", "Sources")])
    body += f'''<section class="band" id="candidates"><div class="wrap wide cwrap"><div><div class="kicker">The candidates<i></i></div><h2 class="h2">Who is on the ballot</h2>
<div class="ccards {"three" if len(cs) <= 3 else "four"}">{"".join(candidate_card(c, "md") for c in cs)}</div></div>{tip_panel(cs)}</div></section>
<section class="band cream" id="money"><div class="wrap wide two"><div><div class="kicker">Money<i></i></div><h2 class="h3">Outside spending in this race</h2>
{(f'<p class="bignum"><b>{money(tot)}</b><span>independent expenditures on FEC 24/48-hour reports, 2026 cycle, through {dstr(latest)} · {cnt} reports</span></p>{tbl}') if tot else '<p>No independent expenditures for this race were found in the FEC data pulled on ' + dstr(FL["fec"]["as_of_utc"]) + '.</p>'}
<p class="small">Independent expenditures are spent by outside groups to support or oppose a candidate. They are not donations to the candidate's campaign. Candidate committee totals are on each candidate card.</p></div>
<div id="market">{market_card(race)}</div></div></section>
<section class="band" id="sources"><div class="wrap wide"><nav class="pn">{prev}<a href="{ST_URL}house/">All districts</a>{nxt}</nav><p class="small meth">{e(_src_line())} <a href="/about/election-methods/">Methods ↗</a></p></div></section>'''
    _wrapup(body, f"Florida's {n}{_ord(n)} Congressional District 2026", f"Every qualified candidate in Florida's {n}{_ord(n)} congressional district under the 2026 map, with FEC totals, outside spending, Kalshi quotes and TIP issue grades.", f"{ST_URL}house/{n}/", crumbs)

def _ord(n):
    return "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")

# ------------------------------------------------------------------ Methods
def methods_page():
    crumbs = [("Home", "/"), ("About", "/about/"), ("Election methods", None)]
    rows = "".join(f'<tr><td>{e(i["name"])}</td><td>{e(i["question"])}</td></tr>' for i in FL["issues"])
    body = f'''<section class="page-head"><div class="wrap">{_crumbs(crumbs)}<div class="kicker">About<i></i></div><h1 class="display">Election <em>methods</em></h1><p class="dek">How LLF's election pages source, label and correct what they show.</p></div></section>
<section class="band cream"><div class="wrap narrow prose meth-body">
<h2 id="roster" class="h3">Who counts as a candidate</h2><p>We list every candidate the Florida Division of Elections shows as Qualified or Unopposed for the November 3, 2026 general election in the governor, U.S. Senate and U.S. House contests. Write-in candidates the state lists as qualified are labeled and are not printed ballot choices. We do not rank candidates, pick winners or recommend votes. We captured the state's candidate lists on {dstr(FL["roster"]["captured_at_utc"])} and keep the raw capture.</p>
<h2 id="districts" class="h3">District map</h2><p>House districts use the Florida Legislature's official plan EOGPCRP2026 (HB 1-D), enacted in May 2026. The map is the subject of ongoing litigation. County names on district pages are land-area shares from Census county boundaries intersected with that file.</p>
<h2 id="money" class="h3">Money</h2><p><b>Candidate committee totals</b> are receipts and disbursements reported to the FEC for the period shown. <b>Independent expenditures</b> are spending by other groups to support or oppose a candidate, reported on FEC Schedule E; we use 24/48-hour reports, which are the most current, and drop the same transaction when it is re-reported on a periodic filing so it is not counted twice. They are never added to candidate receipts. <b>Public matching funds</b> are state payments to governor candidates and can already be counted in campaign receipts. Governor candidates file with the state, not the FEC.</p>
<h2 id="markets" class="h3">Markets</h2><p>Kalshi prices are what traders were willing to pay for a contract at a stated time. They are market-implied estimates, not polls, vote shares or forecasts. Governor, Senate and Michigan Senate contracts resolve on the party of the winner. We show last trade, bid and ask exactly as the public API returned them with the capture time. Charts plot captured points only.</p>
<h2 id="grades" class="h3">TIP Issue Grades</h2><p>TIP tracks six issues. For each candidate and issue, TIP counts recorded congressional acts (votes, sponsorships and cosponsorships that TIP's reviewers approved and mapped to the issue) that align with TIP's position and acts that are against it. The grade is aligned divided by the total of both. An issue needs at least one recorded act to be graded. A candidate's reviewed answer to a TIP question can move one issue's score by half a point, up or down, once per issue. The score is rounded half up and mapped to a letter (A+ at 97 and above down to F- at 53 and below). Not voting, voting present and contested entries are not counted.</p>
<p><b>A grade of F- from 0 of 5 aligned acts is a real grade. A dash means not graded: no recorded acts.</b> Challengers and candidates who never served in Congress are not graded, and that is not a score of zero. Governor and state offices have different powers than Congress, so a federal grade describes a congressional record only. TIP's grades are TIP's published method, not an objective measure of a person.</p>
<div class="tablewrap"><table class="data"><thead><tr><th>Issue</th><th>The question TIP asks</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small">The sixth issue, Section 224 of the FY27 NDAA, is a single-provision record rather than a broad issue frame, and has no answer options for the reviewed-answer adjustment.</p>
<h2 id="portraits" class="h3">Portraits</h2><p>Portraits are used only where a public-domain, CC0 or openly licensed image exists. Credit and license are on file in our asset manifest. Candidates without a licensed image show a monogram. Which candidates have photos reflects what is licensed, not an editorial choice.</p>
<h2 id="corrections" class="h3">Updates and corrections</h2><p>Every page shows when it was last checked. Errors are corrected visibly and logged on the <a href="/about/corrections/">corrections page</a>. Data can change after we check it; the state, the FEC and Kalshi are the controlling sources.</p></div></section>'''
    API["shell"]("Election methods", "How LookLearnFind sources, labels and corrects election data: rosters, FEC money, Kalshi prices and TIP Issue Grades.", "/about/election-methods/", body, nav="about", css=("elections",), js=("common",), jsonld=_jsonld("Election methods", "/about/election-methods/", crumbs))

# ------------------------------------------------------------------ build + report layout
def build(api):
    API.update(api)
    load()
    for st in API["STORIES"]:
        if st.get("layout") == "report":
            for k in ("title", "dek"):
                st[k] = expand_values(st.get(k, ""))
    state_hub(); gov_page(); senate_page(); house_page(); methods_page()
    for i in range(1, 29):
        district_page(i)

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
          "publisher": {"@type": "Organization", "name": "LookLearnFind"}}) + "</script>"
    API["shell"](s["title"], s.get("dek", ""), s["path"], html, nav="politics", css=("elections",), js=("common", "elections"), jsonld=ld)
