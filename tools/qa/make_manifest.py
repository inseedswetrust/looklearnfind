#!/usr/bin/env python3
"""Write docs/election-build/ASSET_MANIFEST.csv from the credit tables and data folders (stdlib only)."""
import json, csv, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
rows = []

def sha(p):
    p = ROOT / p
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else ""

hc = json.loads((ROOT / "data/elections/hero_credits.json").read_text(encoding="utf-8"))
for k, v in hc.items():
    rows.append(dict(asset_id=f"IMG-HERO-{k}", type="hero_photo", source=v["source_page"], license=v["license"], path=f"static/img/elections/{k}.jpg",
                     reference_design="01,02,03,06,07,08 hero", usage="page hero", credit=v["credit"][:80], sha256_16=sha(f"static/img/elections/{k}.jpg"), notes=v["file"]))
for st in ("FL", "MI"):
    pj = json.loads((ROOT / f"data/elections/{st}/portraits.json").read_text(encoding="utf-8"))
    for cid, v in pj.items():
        if v.get("result") == "ok":
            rows.append(dict(asset_id=f"IMG-PORTRAIT-{cid}", type="portrait", source=v["source_page"], license=v["license"], path=f"static/img/elections/portraits/{cid}.jpg",
                             reference_design="02,03,06 candidate cards", usage=f"candidate card: {v['name']}", credit=v["credit"][:80],
                             sha256_16=sha(f"static/img/elections/portraits/{cid}.jpg"), notes=f"Wikipedia match: {v['wikipedia']}; file {v['file']}"))
for f in sorted((ROOT / "assets/icons").glob("issue-*.svg")):
    rel = f.relative_to(ROOT).as_posix()
    rows.append(dict(asset_id=f"ICON-{f.stem}", type="icon", source="created for LLF in this build", license="LLF original", path=rel, reference_design="TIP issue key (02,03)",
                     usage="six-issue key and chips", credit="LookLearnFind", sha256_16=sha(rel), notes="64x64 line icon, one yellow dot, currentColor"))
data = [("DATA-ROSTER", "Florida Division of Elections candidate lists (governor; federal)", "public record", "data/elections/FL/roster.json; captures/fl_*.html", "state captures with SHA-256 in roster.json"),
        ("DATA-DISTRICTS", "Florida Legislature EDR plan EOGPCRP2026 (HB 1-D) shapefile; Census cb_2024_us_county_500k for county names", "public record (government data)", "data/elections/FL/districts.json; captures/EOGPCRP2026.zip", "simplified to 0.004 degrees; SVG paths"),
        ("DATA-FEC", "OpenFEC candidate totals and Schedule E", "public record", "data/elections/FL/finance_fec.json, ie_all.json; data/elections/MI/senate_delta/finance_fec.json", "raw API captures in captures/"),
        ("DATA-KALSHI", "Kalshi public market API quotes and candlesticks", "Kalshi public data, shown with attribution and timestamp", "data/elections/FL/markets.json; data/elections/MI/kalshi_SENATEMI-26-D.json", "raw captures in captures/"),
        ("DATA-TIP", "TIP candidate pages and Issue Grades (read-only production export)", "owner data", "data/elections/FL/candidates.json", "link status checked live; no credentials stored")]
for a, s, l, p, n in data:
    rows.append(dict(asset_id=a, type="dataset", source=s, license=l, path=p, reference_design="all", usage="structured data behind pages and charts", credit="", sha256_16="", notes=n))
for n in ("01_state_of_race_landing", "02_governor_race_guide", "03_senate_race_guide", "04_house_race_guide_grid", "05_house_race_guide_directory",
          "06_delta_report_article", "07_spending_report_article", "08_governor_long_form_article"):
    rows.append(dict(asset_id=f"REF-{n[:2]}", type="design_reference", source="owner-approved AI mockup (handoff zip)", license="not for publication", path="(not shipped)", reference_design=n,
                     usage="layout reference only; people, numbers, maps and labels in the mockups were not used", credit="", sha256_16="", notes="AI-generated faces, amounts and geography discarded"))
cols = ["asset_id", "type", "source", "license", "path", "reference_design", "usage", "credit", "sha256_16", "notes"]
with open(ROOT / "docs/election-build/ASSET_MANIFEST.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows")
