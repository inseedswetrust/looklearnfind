#!/usr/bin/env python3
"""Render the share images for the Florida Senate and House articles from the same data the pages use.

    python3 tools/social/render_cards.py [outdir]        default: static/img/elections/social

Writes OG images (1200x630 JPG) and 4:5 social cards (1080x1350 PNG): poll card, map card and TIP grade cards. Cards are plain HTML rendered with Playwright, so type, color and
numbers follow the site's tokens and the data files. Nothing is invented: every number is read from story_data.json, candidates.json or districts.json.
Portraits are public domain (credits in fl_assets.csv); a candidate without a licensed portrait gets a monogram.
"""
import base64, json, sys, html
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "static/img/elections/social"
OUT.mkdir(parents=True, exist_ok=True)
J = lambda p: json.loads((ROOT / p).read_text(encoding="utf-8"))
SD, CAND, DIST, PORT = J("data/elections/FL/story_data.json"), J("data/elections/FL/candidates.json"), J("data/elections/FL/districts.json"), J("data/elections/FL/portraits.json")
ISS = CAND["issues"]
by = {c["name"]: c for c in CAND["candidates"]}
e = html.escape
CSS = """*{box-sizing:border-box;margin:0}body{background:#f5f2eb;color:#1c1d1b;font-family:Georgia,'Times New Roman',serif}
.sans{font-family:Arial,Helvetica,sans-serif}.k{font:700 22px Arial;letter-spacing:.14em;text-transform:uppercase;color:#145b5d}
.card{position:relative;overflow:hidden;padding:56px 60px;display:flex;flex-direction:column}
h1{font-weight:400;letter-spacing:-.02em;line-height:1.02}.foot{position:absolute;left:60px;right:60px;bottom:40px;display:flex;justify-content:space-between;font:700 20px Arial;letter-spacing:.08em;color:#5d6a61;text-transform:uppercase}
.foot b{color:#145b5d}.bar{height:84px;display:flex;align-items:center;padding-left:14px;color:#fff;font:700 26px Arial}.lab{font:700 40px Arial;margin:26px 0 10px}
.ph{width:150px;height:188px;object-fit:cover;object-position:center 20%;border:2px solid #c9c4b9}.mono{width:150px;height:188px;display:grid;place-items:center;font-size:54px;color:#145b5d;background:#eee9df;border:2px solid #c9c4b9}
.note{font:20px/1.4 Arial;color:#5d6a61}.hl{background:#dfca00;color:#1c1d1b;padding:0 8px}
.ig{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:10px}.ig div{border:2px solid #c9c4b9;background:#fffdf8;padding:10px 0;text-align:center;font:700 34px Arial;color:#145b5d}.ig div.n{color:#aeb8ad}
.ig small{display:block;font:11px Arial;color:#5d6a61;margin-top:4px;padding:0 3px;line-height:1.15}.row{display:flex;gap:22px;align-items:center;border-top:2px solid #c9c4b9;padding:20px 0}
"""

def img(c, cls="ph"):
    p = PORT.get(c["id"], {})
    f = ROOT / f"static/img/elections/portraits/{c['id']}.jpg"
    if p.get("result") == "ok" and f.exists():
        return f'<img class="{cls}" src="data:image/jpeg;base64,{base64.b64encode(f.read_bytes()).decode()}" alt="">'
    ini = "".join(w[0] for w in c["name"].split()[:1] + c["name"].split()[-1:]).upper()
    return f'<div class="mono">{e(ini)}</div>'

def short(i):
    return {"data_bill_of_rights": "Data rights", "war_crime_accountability": "War crimes", "congressional_stock_trading_ban": "Stock ban", "citizens_united_reform": "Citizens United", "universal_healthcare": "Healthcare", "us-israel-military-merger": "US-Israel merger"}[i["slug"]]

def strip(c):
    t = (c.get("tip") or {}).get("grades", {})
    out = ""
    for i in ISS:
        g = t.get(i["slug"], {})
        ok = g.get("state") == "graded"
        out += f'<div class="{"" if ok else "n"}">{e(g["grade"]) if ok else "—"}<small>{e(short(i))}</small></div>'
    return f'<div class="ig">{out}</div>'

def map_svg(hl, size=600, pins=True):
    vb = DIST["viewbox"]
    paths = "".join(f'<path d="{v["path"]}" fill="{"#145b5d" if int(n) in hl else "#d8e2dc"}" stroke="#f5f2eb" stroke-width="1.6"/>' for n, v in DIST["districts"].items())
    off = {20: (-70, -34), 25: (-62, 38)}
    pin = ""
    if pins:
        for n in hl:
            x, y = DIST["districts"][str(n)]["label_xy"]
            dx, dy = off.get(n, (0, 0))
            pin += (f'<line x1="{x}" y1="{y}" x2="{x + dx}" y2="{y + dy}" stroke="#1c1d1b" stroke-width="2"/>' if dx or dy else "") + f'<circle cx="{x + dx}" cy="{y + dy}" r="26" fill="#dfca00" stroke="#1c1d1b" stroke-width="2"/><text x="{x + dx}" y="{y + dy + 9}" text-anchor="middle" font="" style="font:700 26px Arial">{n}</text>'
    return f'<svg width="{size}" viewBox="0 0 {vb[2]} {vb[3]}">{paths}{pin}</svg>'

u = SD["unf_oct"]
moody, nixon = by["Ashley Moody"], by["Angie Nixon"]
cards = {}
cards["og-fl-senate"] = (1200, 630, f'''<div class="card" style="width:1200px;height:630px"><div class="k">State of the race · Florida U.S. Senate</div>
<div style="display:flex;gap:40px;margin-top:26px"><div style="flex:1"><h1 style="font-size:74px">Florida's Senate race tightens in the newest poll</h1>
<p class="sans" style="font-size:26px;margin-top:22px;line-height:1.35">UNF: Moody <b>{u["moody"]}</b>, Nixon <b>{u["nixon"]}</b> · {u["n"]:,} likely voters · Oct 12–19 · ±{u["moe"]}</p></div>
<div style="display:flex;gap:16px;zoom:1.35">{img(moody)}{img(nixon)}</div></div><div class="foot"><span><b>LookLearnFind</b> · LLF</span><span>Issue grades on <b>TIP</b></span></div></div>''')
cards["ig-fl-senate-poll"] = (1080, 1350, f'''<div class="card" style="width:1080px;height:1350px"><div class="k">Florida U.S. Senate · special election</div>
<h1 style="font-size:88px;margin-top:20px">Moody 49, Nixon 45 in the newest poll</h1><p class="note" style="margin-top:14px;font-size:24px">University of North Florida · {u["n"]:,} likely voters · Oct 12–19 · margin of error ±{u["moe"]}</p>
<div style="display:flex;gap:30px;margin-top:40px;align-items:flex-end;transform-origin:left;"><div style="zoom:1.5;display:flex;gap:20px">{img(moody)}{img(nixon)}</div></div>
<div class="lab">Ashley Moody (R) {u["moody"]}%</div><div class="bar" style="width:{u["moody"]/60*100:.0f}%;background:#1c1d1b"></div>
<div class="lab">Angie Nixon (D) {u["nixon"]}%</div><div class="bar" style="width:{u["nixon"]/60*100:.0f}%;background:#145b5d"></div>
<div class="lab">Undecided {u["undecided"]}%</div><div class="bar" style="width:{u["undecided"]/60*100:.0f}%;background:#aeb8ad"></div>
<p class="note" style="margin-top:34px">WLRN reports the July UNF poll had Moody ahead by {u["july_moody_lead"]}. A poll is a snapshot, not a forecast.</p>
<div class="foot"><span><b>LookLearnFind</b> · WLRN, Action News Jax</span><span>looklearnfind.com</span></div></div>''')
rows = "".join(f'<div class="row">{img(c)}<div style="flex:1"><div style="font-size:42px">{e(c["name"])}</div><div class="note">{e(c["party"])} · {e(sub)}</div>{strip(c)}</div></div>' for c, sub in
               ((moody, "U.S. Senate · 2 of 6 issues graded"), (nixon, "State legislator · no congressional record, none graded")))
cards["ig-fl-senate-tip"] = (1080, 1350, f'''<div class="card" style="width:1080px;height:1350px"><div class="k">TIP issue grades · Florida U.S. Senate</div><h1 style="font-size:70px;margin:18px 0 10px">Six issues. Two graded. Four are not.</h1>
<p class="note">A dash means not graded: no recorded congressional acts. It is not a zero and not a position.</p>{rows}
<p class="note" style="margin-top:20px">Grades computed Oct 21, 2026 from recorded congressional acts. How they work: looklearnfind.com/about/election-methods/</p>
<div class="foot"><span><b>The Issues Party</b> × <b>LookLearnFind</b></span><span>theissuesparty.org</span></div></div>''')
hl = [14, 9, 20, 6, 25]
cards["og-fl-house"] = (1200, 630, f'''<div class="card" style="width:1200px;height:630px"><div class="k">State of the race · Florida U.S. House</div>
<div style="display:flex;gap:30px;margin-top:20px"><div style="flex:1"><h1 style="font-size:72px">Florida redrew 21 House districts</h1>
<p class="sans" style="font-size:25px;margin-top:20px;line-height:1.35">What the 2026 map changed and what three August primaries showed.</p></div><div style="margin-top:-10px">{map_svg(hl, 400)}</div></div>
<div class="foot"><span><b>LookLearnFind</b> · LLF</span><span>Issue grades on <b>TIP</b></span></div></div>''')
t = SD["trump_2024"]
cards["ig-fl-house-map"] = (1080, 1350, f'''<div class="card" style="width:1080px;height:1350px"><div class="k">Florida U.S. House · the 2026 map</div><h1 style="font-size:78px;margin-top:16px">21 of 28 districts were redrawn</h1>
<div style="display:flex;gap:10px;margin-top:20px"><div style="margin-left:-30px">{map_svg(hl, 640)}</div><div class="sans" style="font-size:26px;line-height:1.4;padding-top:40px">
<p><b>14</b> Castor (D): reported 2024 vote on the new lines, Trump {t["fl14"]["trump"]}, Harris {t["fl14"]["harris"]}</p><p style="margin-top:18px"><b>9</b> Soto (D): Trump {t["fl09"]["trump"]}, Harris {t["fl09"]["harris"]}</p>
<p style="margin-top:18px"><b>20</b> Wasserman Schultz (D) moved here and won the primary</p><p style="margin-top:18px"><b>25</b> Moskowitz (D) won his primary</p><p style="margin-top:18px"><b>6</b> Fine (R) won his primary</p></div></div>
<p class="note" style="margin-top:20px">Districts 1 to 7 were not changed. Margins are reporters' figures (WLRN, May 5); LLF has not recomputed them.</p>
<div class="foot"><span><b>LookLearnFind</b> · plan EOGPCRP2026</span><span>looklearnfind.com</span></div></div>''')
names = ("Kathy Castor", "Darren Soto", "Jared Moskowitz", "Randy Fine", "Debbie Wasserman Schultz")
rows = "".join(f'<div class="row" style="padding:12px 0">{img(by[n])}<div style="flex:1"><div style="font-size:34px">{e(n)} <span class="note">· FL-{by[n]["race"].split("-")[1]}</span></div>{strip(by[n])}</div></div>' for n in names)
cards["ig-fl-house-tip"] = (1080, 1350, f'''<div class="card" style="width:1080px;height:1350px;padding-top:40px"><div class="k">TIP issue grades · five Florida House members</div>{rows}
<p class="note" style="margin-top:6px">A dash means not graded: no recorded congressional acts on that issue. Computed Oct 21, 2026.</p>
<div class="foot"><span><b>The Issues Party</b> × <b>LookLearnFind</b></span><span>theissuesparty.org</span></div></div>''')

with sync_playwright() as p:
    try:
        b = p.chromium.launch(channel="msedge")
    except Exception:
        b = p.chromium.launch(channel="chrome")
    for name, (w, h, body) in cards.items():
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.set_content(f"<style>{CSS}</style>{body}")
        png = OUT / f"{name}.png"
        pg.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": w, "height": h})
        if name.startswith("og-"):
            Image.open(png).convert("RGB").save(OUT / f"{name}.jpg", quality=88)
            png.unlink()
        pg.close()
    b.close()
print(sorted(x.name for x in OUT.iterdir()))
