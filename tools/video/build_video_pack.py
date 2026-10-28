#!/usr/bin/env python3
"""Build and check the whole video pack for one state from ONE spec file. An agent runs this with no other direction.

    python3 tools/video/build_video_pack.py <spec.json> [--check] [--no-render] [--out release/video/<id>]

--check      validate only (exit 2 on any problem)
--no-render  skip the Playwright frame render of still frames (still writes the documents)
--render-video --authorization "<the owner's own words requesting a rendered video>"
             the ONLY way to ask for a rendered video. Without it this tool is assets-only and never writes a video file. No renderer ships in this repo:
             the flag records the request in the workflow ledger and stops (exit 3). See docs/production/03_VIDEO_SKILL_AND_SHOT_CONTRACT.md.
LEGACY: this builder and its fixed 18 x 5-second spec are the Florida example. New states use tools/video/scene_pack.py (script-led timing, SCENES.csv).
Writes: <out>/frames/segNN.png and segNN_alpha.png (layer-1 deterministic frames, 1080x1920), cover.png, storyboard.html,
        docs/video/<ID>_STORYBOARD.md, _FACT_SHEET.md, fl_video_prompts.csv, fl_video_animations.csv (via visual direction builder),
        and the script table inside docs/video/FLORIDA_VIDEO_SCRIPT_AND_PITCH.md between its markers.
The validator is what makes this repeatable: it refuses a pack whose narration is too long, whose spoken or on-screen numbers are not in the fact sheet,
whose plate prompts could generate people or text, or that still contains <fill> placeholders.
"""
import base64, csv, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
ONES = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
ORD = r"(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|[a-z]+teenth|[a-z]+ieth)"
FORBIDDEN_IN_PLATES = ["person", "people", "face", "faces", "portrait", "hand", "hands", "text", "letter", "letters", "number", "numbers", "logo", "logos", "flag", "flags", "red", "blue", "candidate", "ballot", "crowd"]
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:\s*[–-]\s*\d{1,2})?"


def seg_secs(spec, s):
    """Seconds for one segment: its own `seconds` if set, else the spec default. (The fixed 5-second rule is the Florida example, not a requirement.)"""
    return s.get("seconds", spec.get("segment_seconds", 5))


def seg_start(spec, n):
    return sum(seg_secs(spec, x) for x in spec["segments"] if x["n"] < n)


def spoken_numbers(text):
    """Cardinal numbers spoken in a line, as floats ('one hundred seven million' -> 107, 'six point four' -> 6.4, 'fourteen and a half million' -> 14.5). Ordinals are ignored."""
    t = re.sub(rf"\b[a-z]+-{ORD}\b", " ", text.lower())
    t = re.sub(rf"\b{ORD}\b", " ", t)
    words = re.findall(r"[a-z]+", t)
    out, cur, have, i = [], 0, False, 0
    def flush():
        nonlocal cur, have
        if have:
            out.append(float(cur))
        cur, have = 0, False
    while i < len(words):
        w = words[i]
        if w in ONES:
            cur += ONES[w]; have = True
        elif w in TENS:
            cur += TENS[w]; have = True
        elif w == "hundred" and have:
            cur = (cur or 1) * 100
        elif w == "point" and have:
            dec, j = "", i + 1
            while j < len(words) and words[j] in ONES and ONES[words[j]] < 10:
                dec += str(ONES[words[j]]); j += 1
            cur = float(f"{cur}.{dec}") if dec else cur
            i = j - 1
        elif w == "and" and i + 2 < len(words) and words[i + 1] == "a" and words[i + 2] == "half" and have:
            cur += 0.5; i += 2
        elif w in ("million", "billion", "thousand"):
            flush()
        else:
            flush()
        i += 1
    flush()
    return out


def screen_numbers(lines):
    s = " ".join(lines)
    s = re.sub(MONTH, " ", s)
    s = re.sub(r"FL-\d+", " ", s)
    s = re.sub(r"\b(?:2024|2026)\b", " ", s)
    return [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*\.?\d*", s) if x.strip(",.")]


def close(a, b):
    return abs(a - b) <= max(0.011 * abs(b), 1e-9)


def validate(spec):
    P = []
    segs, trans = spec["segments"], spec["transitions"]
    total = sum(seg_secs(spec, s) for s in segs)
    if total != spec["duration_seconds"]:
        P.append(f"segments add up to {total}s, not {spec['duration_seconds']}s")
    if [s["n"] for s in segs] != list(range(1, len(segs) + 1)):
        P.append("segment numbers are not 1..N in order")
    if [(t["from"], t["to"]) for t in trans] != [(i, i + 1) for i in range(1, len(segs))]:
        P.append("transitions do not link consecutive segments")
    facts = {f["id"]: f for f in spec["facts"]}
    for f in spec["facts"]:
        if f["status"] not in ("VERIFIED", "ATTRIBUTED"):
            P.append(f"{f['id']}: status must be VERIFIED or ATTRIBUTED, not {f['status']}")
        if not f.get("source") or "<fill>" in json.dumps(f):
            P.append(f"{f['id']}: missing source or placeholder")
    ids = set()
    for s in segs:
        n = s["n"]
        words = len(s["vo"].split())
        cap = spec["voice"].get("max_words_per_segment")
        if cap is None:
            cap = int(seg_secs(spec, s) * spec["voice"]["words_per_second"]) + 1      # pacing follows the scene length when no fixed cap is set
        if words > cap:
            P.append(f"segment {n}: narration is {words} words (max {cap})")
        if not s["facts"]:
            P.append(f"segment {n}: no fact IDs")
        for fid in s["facts"]:
            if fid not in facts:
                P.append(f"segment {n}: unknown fact {fid}")
        allowed = [float(x.replace(",", "")) for fid in s["facts"] if fid in facts for x in facts[fid]["numbers"]] + [float(x) for x in s.get("structural", [])]
        for v in spoken_numbers(s["vo"]):
            if not any(close(v, a) for a in allowed):
                P.append(f"segment {n}: narration says {v:g}, which is not in its facts {s['facts']}")
        for v in screen_numbers(s["on_screen"]):
            if not any(close(v, a) for a in allowed):
                P.append(f"segment {n}: on-screen number {v:g} is not in its facts {s['facts']}")
        for a in s["animations"]:
            if a["start"] + a["duration"] > seg_secs(spec, s) + 1e-9:
                P.append(f"segment {n}: animation '{a['element']}' runs past the segment")
        pl = s["plate"]
        if pl["id"] in ids:
            P.append(f"duplicate plate id {pl['id']}")
        ids.add(pl["id"])
        low = pl["desc"].lower()
        for w in FORBIDDEN_IN_PLATES:
            if re.search(rf"\b{w}\b", low):
                P.append(f"plate {pl['id']}: prompt contains '{w}' (generated plates must carry no people, text, numbers, logos, flags or party colors)")
        if re.search(r"\d", pl["desc"]):
            P.append(f"plate {pl['id']}: prompt contains a digit")
        if "<fill>" in json.dumps(s):
            P.append(f"segment {n}: unfilled placeholder")
        if "portrait_px" in s.get("params", {}) and "left" in s["params"] and "right" in s["params"]:
            pass   # one size value serves both sides, so equal treatment is structural
    for t in trans:
        low = t["motion"].lower()
        for w in ("person", "people", "face", "text", "number", "logo", "flag"):
            if re.search(rf"\b{w}\b", low):
                P.append(f"transition {t['id']}: motion prompt contains '{w}'")
    if not spec.get("disclosures") or not spec.get("credits"):
        P.append("disclosures and credits are required")
    return P


# ---------------------------------------------------------------- frame rendering (layer 1: deterministic)
INK, TEAL, PAPER, YEL, MUT = "#1c1d1b", "#145b5d", "#f5f2eb", "#dfca00", "#5d6a61"
CSS = f"""*{{box-sizing:border-box;margin:0}}html,body{{width:1080px;height:1920px}}body{{font-family:Georgia,'Times New Roman',serif;color:{INK};overflow:hidden}}
.f{{position:relative;width:1080px;height:1920px;padding:260px 70px 350px}}.sans{{font-family:Arial,Helvetica,sans-serif}}
.k{{font:700 30px Arial;letter-spacing:.14em;text-transform:uppercase;color:{TEAL}}}h1{{font-weight:400;letter-spacing:-.02em;line-height:1.02}}
.cap{{font:26px/1.35 Arial;color:{MUT};margin-top:22px}}.big{{font-weight:400;letter-spacing:-.03em}}
.chip{{display:inline-block;background:{YEL};color:{INK};font:700 30px Arial;padding:10px 18px}}.ph{{object-fit:cover;object-position:center 20%;border:3px solid #c9c4b9;display:block}}
.nm{{font:700 34px Arial;margin-top:10px}}.pl{{font:26px Arial;color:{MUT}}}.bar{{height:92px;display:flex;align-items:center;padding-left:18px;color:#fff;font:700 34px Arial}}
.lab{{font:700 38px Arial;margin:26px 0 10px}}.slot{{border:3px solid #c9c4b9;background:#fffdf8;text-align:center;padding:22px 0 12px;font:700 56px Arial;color:{TEAL}}}.slot.n{{color:#aeb8ad}}
.slot small{{display:block;font:15px Arial;color:{MUT};margin-top:6px}}.card{{border:3px solid {INK};background:#fffdf8;padding:36px;margin-bottom:30px}}.tile{{border:2px solid #c9c4b9;background:#fffdf8;padding:8px;font:15px/1.25 Arial;height:236px;overflow:hidden}}
.tile b{{display:block;font:700 22px Arial;color:{TEAL};margin-bottom:6px}}.tile.y{{background:{YEL}}}.tile i{{font-style:normal;color:{MUT}}}"""
_cache = {}
def J(p):
    if p not in _cache:
        _cache[p] = json.loads((ROOT / p).read_text(encoding="utf-8"))
    return _cache[p]
def cands(): return {c["name"]: c for c in J("data/elections/FL/candidates.json")["candidates"]}
def portraits(): return J("data/elections/FL/portraits.json")
e = html.escape

def img(name, px):
    c = cands()[name]
    f = ROOT / f"static/img/elections/portraits/{c['id']}.jpg"
    if portraits().get(c["id"], {}).get("result") == "ok" and f.exists():
        return f'<img class="ph" style="width:{px}px;height:{round(px * 1.25)}px" src="data:image/jpeg;base64,{base64.b64encode(f.read_bytes()).decode()}" alt="">'
    ini = "".join(w[0] for w in name.split()[:1] + name.split()[-1:])
    return f'<div class="ph" style="width:{px}px;height:{round(px * 1.25)}px;display:grid;place-items:center;font-size:{px // 3}px;background:#eee9df;color:{TEAL}">{ini}</div>'

def short(i):
    return {"data_bill_of_rights": "Data rights", "war_crime_accountability": "War crimes", "congressional_stock_trading_ban": "Stock ban", "citizens_united_reform": "Citizens United", "universal_healthcare": "Healthcare", "us-israel-military-merger": "US-Israel merger"}.get(i["slug"], i["name"])

def strip(name):
    t = (cands()[name].get("tip") or {}).get("grades", {})
    out = ""
    for i in J("data/elections/FL/candidates.json")["issues"]:
        g = t.get(i["slug"], {})
        ok = g.get("state") == "graded"
        out += f'<div class="slot {"" if ok else "n"}">{e(g["grade"]) if ok else "—"}<small>{e(short(i))}</small></div>'
    return f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:8px">{out}</div>'

def map_svg(fill_set, width, pins=None):
    d = J("data/elections/FL/districts.json")
    vb = d["viewbox"]
    paths = "".join(f'<path d="{v["path"]}" fill="{TEAL if int(n) in fill_set else "#d8e2dc"}" stroke="{PAPER}" stroke-width="1.6"/>' for n, v in d["districts"].items())
    pin = ""
    off = {20: (-70, -34), 25: (-62, 38)}
    for n in pins or []:
        x, y = d["districts"][str(n)]["label_xy"]
        dx, dy = off.get(n, (0, 0))
        pin += (f'<line x1="{x}" y1="{y}" x2="{x + dx}" y2="{y + dy}" stroke="{INK}" stroke-width="2"/>' if dx or dy else "") + f'<circle cx="{x + dx}" cy="{y + dy}" r="26" fill="{YEL}" stroke="{INK}" stroke-width="2"/><text x="{x + dx}" y="{y + dy + 9}" text-anchor="middle" style="font:700 26px Arial">{n}</text>'
    return f'<svg width="{width}" viewBox="0 0 {vb[2]} {vb[3]}">{paths}{pin}</svg>'

def bars(rows, scale, width=900):
    col = {"ink": INK, "teal": TEAL}
    return "".join(f'<div class="lab">{e(r["label"])} {r["v"]:g}%</div><div class="bar" style="width:{r["v"] / scale * width:.0f}px;background:{col[r.get("color", "teal")]}"></div>' for r in rows)

def rng(s):
    a, b = s.split("-"); return set(range(int(a), int(b) + 1))

def frame_html(seg, spec):
    t, p, os_ = seg["frame"], seg["params"], seg["on_screen"]
    if t == "hero_title":
        ph = base64.b64encode((ROOT / p["photo"]).read_bytes()).decode()
        return (f'<div class="f" style="background:linear-gradient(rgba(245,242,235,.0),rgba(28,29,27,.55)),url(data:image/jpeg;base64,{ph}) center/cover"><span class="chip">{e(os_[0])}</span>'
                f'<h1 style="font-size:110px;color:#fffdf8;position:absolute;left:70px;right:70px;bottom:420px;text-shadow:0 2px 12px rgba(0,0,0,.45)">{e(os_[1])}</h1></div>')
    if t == "board":
        c = list(cands().values())
        def nm(race):
            rows = [x for x in c if x["race"] == race and x["party_code"] in ("DEM", "REP", "NPA") and x["status"] in ("Qualified", "Unopposed")]
            rows.sort(key=lambda x: {"REP": 0, "DEM": 1}.get(x["party_code"], 2))
            return "".join(f'{e(x["name"].split()[-1])} <i>{x["party_code"][0]}</i><br>' for x in rows[:3])
        tiles = f'<div class="tile y"><b>GOV</b>{nm("governor")}</div><div class="tile y"><b>SEN</b>{nm("senate")}</div>' + "".join(f'<div class="tile"><b>FL-{n}</b>{nm(f"house-{n:02d}")}</div>' for n in range(1, 29))
        return f'<div class="f" style="background:{PAPER};padding:250px 40px 340px"><div class="k" style="margin-left:30px;margin-bottom:18px">{e(os_[0])}</div><div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px">{tiles}</div></div>'
    if t == "map":
        return f'<div class="f" style="background:{PAPER}"><div style="margin-left:-40px">{map_svg(rng(p["filled"]), 1000)}</div><div class="chip" style="font-size:44px;margin-top:20px">{e(os_[0])}</div></div>'
    if t == "map_bars":
        b = "".join(f'<div class="lab">{e(r["label"])}: Trump {r["a"]} · Harris {r["b"]}</div><div style="display:flex;width:900px;height:84px"><div class="bar" style="width:{r["a"]}%;background:{INK}"></div><div class="bar" style="width:{r["b"]}%;background:{TEAL}"></div></div>' for r in p["bars"])
        return f'<div class="f" style="background:{PAPER}"><div style="margin-left:-40px;margin-top:-50px">{map_svg(set(rng("8-28")), 640)}</div>{b}<p class="cap">{e(os_[2])}<br>{e(os_[3])}</p></div>'
    if t == "portraits_pins":
        ppl = "".join(f'<div>{img(n, 250)}<div class="nm">{e(" ".join(n.split()[1:]))}</div></div>' for n in p["people"])
        return f'<div class="f" style="background:{PAPER}"><div style="margin-left:-60px;margin-top:-60px">{map_svg(rng("8-28"), 860, p["pins"])}</div><div style="display:flex;gap:30px;justify-content:center;margin-top:10px">{ppl}</div><p class="cap" style="text-align:center">{e(os_[3])}</p></div>'
    if t == "issue_strip":
        n = p["person"]
        return f'<div class="f" style="background:{PAPER}"><div class="k">{e(os_[0])}</div><div style="display:flex;gap:30px;margin:30px 0">{img(n, 320)}<div><h1 style="font-size:64px">{e(n)}</h1><div class="pl">TIP issue grades · computed Oct 21</div></div></div>{strip(n)}<p class="cap" style="font-size:34px;margin-top:40px">{e(os_[1])}</p></div>'
    if t == "split_portraits":
        L, R = p["left"], p["right"]
        return (f'<div class="f" style="background:linear-gradient(90deg,{INK} 50%,{TEAL} 50%);color:#fffdf8"><div class="k" style="color:{YEL}">{e(os_[0])}</div>'
                f'<div style="display:flex;gap:40px;margin-top:70px;justify-content:center">{img(L, 400)}{img(R, 400)}</div><div style="display:flex;justify-content:space-around;margin-top:20px;font:700 40px Arial"><span>{e(L)} (R)</span><span>{e(R)} (D)</span></div>'
                f'<div style="display:flex;gap:30px;justify-content:center;margin-top:120px">' + "".join(f'<div style="width:150px;height:150px;border-radius:50%;border:5px solid {YEL}"></div>' for _ in range(3)) + f'</div><p class="cap" style="color:#e9e6dc;text-align:center;font-size:40px">{e(os_[2])}</p></div>')
    if t == "poll_bars":
        return f'<div class="f" style="background:{PAPER}"><div class="k">{e(p["title"])}</div><h1 style="font-size:96px;margin:20px 0 30px">Close, not a lead</h1>{bars(p["rows"], 60)}<p class="cap">{e(p["caption"])}</p></div>'
    if t == "market_chip":
        m = [c for c in J("data/elections/FL/markets.json")["races"][p["race"]]["contracts"] if c["ticker"].endswith(p["ticker_suffix"])][0]
        cents = f'{round(float(m["last"]) * 100)}¢'
        return f'<div class="f" style="background:{PAPER};text-align:center"><div class="k">{e(os_[1])}</div><div class="big" style="font-size:420px;line-height:1;margin-top:120px;color:{TEAL}">{cents}</div><div class="chip" style="font-size:40px;margin-top:40px">{e(os_[2])}</div><p class="cap">Captured {e(J("data/elections/FL/markets.json")["captured_at_utc"])}</p></div>'
    if t == "two_bars":
        mx = max(r["v"] for r in p["rows"])
        cols = "".join(f'<div style="text-align:center;width:360px"><div class="big" style="font-size:76px">{e(r["text"])}</div><div style="height:{max(14, round(r["v"] / mx * 760))}px;background:{[INK, TEAL][i]};margin-top:10px"></div><div class="lab" style="font-size:28px">{e(r["label"])}</div></div>' for i, r in enumerate(p["rows"]))
        return f'<div class="f" style="background:{PAPER}"><div style="display:flex;gap:80px;align-items:flex-end;justify-content:center;height:1000px">{cols}</div><p class="cap">{e(p["caption"])}</p></div>'
    if t == "three_stamps":
        st = "".join(f'<div style="text-align:center"><div style="width:280px;height:280px;border-radius:50%;border:8px solid {TEAL};display:grid;place-items:center;font:700 44px Arial;color:{TEAL}">{e(s["top"])}</div><div class="nm" style="font-size:30px">{e(s["bottom"])}</div></div>' for s in p["stamps"])
        return f'<div class="f" style="background:{PAPER}"><div style="display:flex;gap:30px;justify-content:center;margin-top:200px">{st}</div><h1 style="font-size:90px;text-align:center;margin-top:160px">{e(p["footer"])}</h1></div>'
    if t == "senate_card":
        px = p["portrait_px"]
        return (f'<div class="f" style="background:{PAPER}"><div class="k" style="text-align:center">{e(os_[0])}</div><div style="display:flex;gap:60px;justify-content:center;margin-top:120px">'
                f'<div>{img(p["left"], px)}<div class="nm">{e(p["left"])}</div><div class="pl">Republican · appointed Jan 2025</div></div><div>{img(p["right"], px)}<div class="nm">{e(p["right"])}</div><div class="pl">Democrat · state representative</div></div></div></div>')
    if t == "portrait_spotlight":
        return (f'<div class="f" style="background:radial-gradient(circle at 50% 38%,#fffbe0,{PAPER} 60%)"><div class="k">{e(os_[0])}</div><div style="margin:40px auto 0;width:520px">{img(p["person"], 520)}</div>'
                f'<div class="card" style="margin-top:60px"><div class="nm" style="margin:0">{e(p["card"])}</div><p class="cap" style="margin-top:12px">{e(p["money"])}</p></div></div>')
    if t == "poll_bars_portraits":
        px = p["portrait_px"] // 2
        return f'<div class="f" style="background:{PAPER}"><div style="display:flex;gap:30px;justify-content:center">{img(p["left"], px)}{img(p["right"], px)}</div>{bars(p["rows"], 60)}<p class="cap">{e(p["caption"])}</p></div>'
    if t == "gap_marker":
        def x(v): return 90 + v * 90
        return (f'<div class="f" style="background:{PAPER}"><div class="k">Moody lead over Nixon, in points</div><svg width="940" height="420" style="margin-top:80px"><line x1="40" y1="200" x2="900" y2="200" stroke="{INK}" stroke-width="6"/>'
                f'<circle cx="{x(p["from"]) - 40}" cy="200" r="30" fill="#aeb8ad"/><text x="{x(p["from"]) - 40}" y="130" text-anchor="middle" style="font:700 56px Arial">{p["from"]}</text><text x="{x(p["from"]) - 40}" y="300" text-anchor="middle" style="font:24px Arial">July (one report)</text>'
                f'<circle cx="{x(p["to"]) - 40}" cy="200" r="38" fill="{YEL}" stroke="{INK}" stroke-width="4"/><text x="{x(p["to"]) - 40}" y="130" text-anchor="middle" style="font:700 72px Arial">{p["to"]}</text><text x="{x(p["to"]) - 40}" y="300" text-anchor="middle" style="font:24px Arial">Now (UNF)</text></svg><p class="cap">{e(p["caption"])}</p></div>')
    if t == "quote_cards":
        cs = "".join(f'<div class="card"><div class="k">{e(c["head"])}</div><h1 style="font-size:64px;margin:16px 0">{e(c["body"])}</h1><div class="pl">{e(c["source"])}</div></div>' for c in p["cards"])
        return f'<div class="f" style="background:{PAPER}"><div style="margin-top:180px">{cs}</div></div>'
    if t == "closing_line":
        px = p["portrait_px"] // 2
        ln = "".join(f'<h1 style="font-size:{[92, 120, 70][i % 3]}px;margin-top:34px">{e(s)}</h1>' for i, s in enumerate(p["lines"]))
        return f'<div class="f" style="background:linear-gradient({PAPER},#fbf3c9)"><div style="display:flex;gap:30px;justify-content:center">{img(p["left"], px)}{img(p["right"], px)}</div><div style="margin-top:80px">{ln}</div></div>'
    if t == "end_card":
        return (f'<div class="f" style="background:linear-gradient({PAPER},#d8e2dc)"><h1 style="font-size:78px;margin-top:140px;white-space:nowrap">{e(os_[0])}</h1><div class="k" style="font-size:40px;margin-top:20px">{e(os_[1])}</div>'
                f'<p style="font:700 40px Arial;margin-top:90px">{e(os_[2])}</p><p class="cap" style="margin-top:90px">{e(" · ".join(spec["credits"]))}<br><br>{e(" ".join(spec["disclosures"]))}</p></div>')
    raise ValueError("unknown frame type " + t)


def render(spec, out):
    from playwright.sync_api import sync_playwright
    fr = out / "frames"
    fr.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge")
        except Exception:
            b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        jobs = [(f"seg{s['n']:02d}", frame_html(s, spec)) for s in spec["segments"]]
        cover = {"n": 0, "frame": "hero_title", "params": {"photo": "static/img/elections/fl-capitol.jpg"}, "on_screen": ["49–47 · 83¢ · $107.6M vs $6.4M", "THREE NUMBERS. THEY DO NOT AGREE."]}
        jobs.append(("cover", frame_html(cover, spec)))
        for name, body in jobs:
            for alpha in (False, True):
                bg = "transparent" if alpha else PAPER
                pg.set_content(f"<style>{CSS}body{{background:{bg}}}</style>{body}")
                if alpha:                                   # transparent version keeps content, drops the paper background
                    pg.evaluate("document.querySelectorAll('.f').forEach(e=>{if(!e.style.background.includes('url'))e.style.background='transparent'})")
                pg.screenshot(path=str(fr / (f"{name}_alpha.png" if alpha else f"{name}.png")), omit_background=alpha)
        b.close()
    return sorted(x.name for x in fr.iterdir())


# ---------------------------------------------------------------- documents
def script_table(spec):
    rows = ["| # | Time | On screen | Narrator (synthetic) | SFX and music | Facts |", "|---|---|---|---|---|---|"]
    for s in spec["segments"]:
        a = seg_start(spec, s["n"])
        t = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
        rows.append(f"| {s['n']} | {t(a)} to {t(a + seg_secs(spec, s))} | {'; '.join(s['on_screen'])} | \"{s['vo']}\" | {s['sfx']} | {', '.join(s['facts'])} |")
    words = sum(len(s["vo"].split()) for s in spec["segments"])
    rows.append("")
    rows.append(f"Total spoken words: {words}. Read time at {spec['voice']['words_per_second']} words a second: {words / spec['voice']['words_per_second']:.0f} seconds of {spec['duration_seconds']}. Every segment is {spec['voice']['max_words_per_segment']} words or fewer.")
    return "\n".join(rows)

def vo_read(spec):
    return " ".join(s["vo"] for s in spec["segments"])

def fill_markers(path, name, text):
    s = path.read_text(encoding="utf-8")
    a, b = f"<!--{name}-->", f"<!--/{name}-->"
    if a in s and b in s:
        s = re.sub(re.escape(a) + r".*?" + re.escape(b), lambda m: a + "\n" + text + "\n" + b, s, flags=re.S)
        path.write_text(s, encoding="utf-8")
        return True
    return False

def fact_sheet(spec):
    r = [f"# Fact sheet for {spec['id']} (generated from the spec; do not edit by hand)", "", f"As of {spec['as_of']}. Everything the video may state. VERIFIED = read in a primary source or two independent sources; ATTRIBUTED = always said as 'according to ...'. REFRESH = re-read on the day of publication.", "",
         "| ID | Fact | Numbers | Source | Status | Never say | Refresh |", "|---|---|---|---|---|---|---|"]
    for f in spec["facts"]:
        r.append(f"| {f['id']} | {f['statement']} | {', '.join(f['numbers']) or '—'} | {f['source']} | {f['status']} | {f['never_say'] or '—'} | {'yes' if f['refresh'] else 'no'} |")
    return "\n".join(r) + "\n"

def storyboard_md(spec, frames=True):
    r = [f"# Storyboard: {spec['id']} (generated from the spec)", "", f"{spec['duration_seconds']} s, {spec['format']['aspect']}, {spec['format']['width']}x{spec['format']['height']}, {spec['format']['fps']} fps. Layer-1 frames are in `release/video/{spec['id']}/frames/` (`segNN.png` on paper, `segNN_alpha.png` transparent).", ""]
    tr = {t["from"]: t for t in spec["transitions"]}
    for s in spec["segments"]:
        a = seg_start(spec, s["n"])
        r += [f"## Segment {s['n']} · {a}-{a + seg_secs(spec, s)} s · `{s['frame']}`", f"- Frame: `seg{s['n']:02d}.png`", f"- On screen: {' / '.join(s['on_screen'])}", f"- Narrator: \"{s['vo']}\"", f"- SFX and music: {s['sfx']}", f"- Facts: {', '.join(s['facts'])}",
              f"- Plate {s['plate']['id']} ({s['plate']['role']}): see `fl_video_prompts.csv`",
              "- Animations (deterministic layer): " + "; ".join(f"{x['element']}: {x['action']} at {x['start']}s for {x['duration']}s ({x['easing']})" for x in s["animations"])]
        if s["n"] in tr:
            t = tr[s["n"]]
            r.append(f"- Transition out {t['id']} ({t['seconds']} s): {t['motion']} Fallback: {t['fallback']}.")
        r.append("")
    return "\n".join(r)

def contact_sheet(spec, out):
    cells = "".join(f'<figure style="margin:0;width:250px"><img src="frames/seg{s["n"]:02d}.png" style="width:250px;border:1px solid #ccc"><figcaption style="font:12px Arial"><b>{s["n"]}</b> {html.escape(s["vo"])}</figcaption></figure>' for s in spec["segments"])
    (out / "storyboard.html").write_text(f'<!doctype html><meta charset="utf-8"><title>{spec["id"]} storyboard</title><body style="margin:20px;background:#fff"><div style="display:flex;flex-wrap:wrap;gap:14px">{cells}</div>', encoding="utf-8")


def main():
    a = sys.argv[1:]
    spec = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    probs = validate(spec)
    for p in probs:
        print("PROBLEM:", p)
    if probs:
        print(len(probs), "problem(s)")
        return 2
    print("spec valid:", len(spec["segments"]), "segments,", len(spec["facts"]), "facts,", len(spec["transitions"]), "transitions")
    if "--render-video" in a:                        # the only door to a rendered video, and it needs the owner's own words
        auth = a[a.index("--authorization") + 1].strip() if "--authorization" in a and a.index("--authorization") + 1 < len(a) else ""
        if len(auth) < 15:
            print("REFUSED: a rendered video needs --authorization with the owner's explicit request in their own words. A script, storyboard, image or transition request is not one.")
            return 2
        import datetime
        log = ROOT / "docs/production/RENDER_REQUESTS.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} {spec['id']} authorization: {auth}\n")
        print("VIDEO_RENDER_REQUESTED recorded in docs/production/RENDER_REQUESTS.log. No renderer is installed in this repository (editing is done in Premiere Pro from the asset pack); nothing was rendered.")
        return 3
    if "--check" in a:
        return 0
    if spec.get("state") != "FL":
        print("REFUSED: this builder and its fixed 18 x 5-second layout are the Florida example. Use `python3 tools/video/scene_pack.py init <ST>` (script-led timing, SCENES.csv, ASSETS.csv, TRANSITIONS.csv).")
        return 2
    out = Path(a[a.index("--out") + 1]) if "--out" in a else ROOT / "release/video" / spec["id"]
    out.mkdir(parents=True, exist_ok=True)
    docs = ROOT / "docs/video"
    (docs / "FLORIDA_VIDEO_FACT_SHEET.md").write_text(fact_sheet(spec), encoding="utf-8")
    (docs / "FLORIDA_VIDEO_STORYBOARD.md").write_text(storyboard_md(spec), encoding="utf-8")
    pitch = docs / "FLORIDA_VIDEO_SCRIPT_AND_PITCH.md"
    if pitch.exists():
        fill_markers(pitch, "script-table", script_table(spec))
        fill_markers(pitch, "vo-read", vo_read(spec))
    import build_visual_direction as bvd
    bvd.build(spec)
    if "--no-render" not in a:
        names = render(spec, out)
        contact_sheet(spec, out)
        print("rendered", len(names), "still frames to", out)
    vids = [x for x in out.rglob("*") if x.suffix.lower() in VIDEO_EXT]
    if vids:                                          # assets-only guard: this tool must never leave a video behind
        print("FAIL: a video file exists in the output:", [str(v) for v in vids])
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
