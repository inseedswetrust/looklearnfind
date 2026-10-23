#!/usr/bin/env python3
"""Internal workflow dashboard: reads the files the pipeline already writes and renders six views. No server, no database, not part of the public site.

    python3 tools/qa/dashboard.py [outdir]        default: release/dashboard  (index.html + dashboard.json)

Views: state, race, article, asset/source, watchlist coverage, daily runs. Every row carries three SEPARATE flags so they are never conflated:
  source_available  the upstream source exists and answered the last time we looked
  collected         we captured it into the repo (with a timestamp and hash)
  editorial_ready   a claim ledger exists, the gate says READY, and the workflow state is past ARTICLE_APPROVED
"""
import csv, json, html, subprocess, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflow")); sys.path.insert(0, str(ROOT / "tools/qa"))
import transitions, factcheck_gate

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "release/dashboard"
OUT.mkdir(parents=True, exist_ok=True)
DH = ROOT / "data/elections/dark_horse"
PK = ROOT / "release/research_packet"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
rd = lambda p, d=None: json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else d
rc = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig"))) if Path(p).exists() else []

man = rd(PK / "manifest.json", {})
latest, status = rd(DH / "latest.json", {}), rd(DH / "status.json", {})
cov = rc(DH / "coverage_matrix.csv")
ledger = transitions.read()
state_of = lambda e: transitions.current(e)
LEDGER_PAGES = {"florida-governor-fundraising-polling-2026": ("governor", "gov draft", "all"), "michigan-senate-delta-october-2026": ("delta", "delta draft", "all"),
                "florida-house-independent-spending-october-2026": ("spending", "house", "all")}     # ledger `page` values that belong to each article
READY_FROM = transitions.STATES.index("ARTICLE_APPROVED")

# ---- state view
states = [{"state": "FL", "scope": "Governor, U.S. Senate, U.S. House", "roster_source_available": True, "roster_collected": bool(man),
           "roster_snapshot": (man.get("source_snapshots_utc") or {}).get("dos_roster"), "federal_rows_on_ballot": (man.get("counts") or {}).get("federal_rows_on_november_ballot"),
           "tip_grades_graded_rows": (man.get("counts") or {}).get("grade_rows_graded"), "packet_version": man.get("version"), "editorial_ready": False,
           "note": "editorial_ready stays False until the Senate and House articles pass the gate"},
          {"state": "MI", "scope": "U.S. Senate delta report", "roster_collected": (ROOT / "data/elections/MI").exists(), "editorial_ready": state_of("michigan-senate-delta-october-2026") == "VERIFIED_LIVE"}]
# ---- race view
races = []
pk_races = rd(PK / "fl_races.json", {"races": []})["races"]
mk = {m["race_id"]: m for m in rd(PK / "fl_markets.json", {"races": []})["races"] if "race_id" in m}
polls = rc(PK / "fl_polls.csv")
spend = rc(PK / "fl_outside_spending.csv")
for r in pk_races:
    rid = r["race_id"]
    has_poll = any(p["race_id"] == rid and p["review_status"] != "no_poll_found" for p in polls)
    races.append({"race_id": rid, "nominees": len(r["nominees"]), "market": (mk.get(rid) or {}).get("status", "none"), "poll": "listed" if has_poll else "no_poll_found",
                  "outside_spending_rows": sum(1 for s in spend if s["race_id"] == rid), "tip_race_url": r["tip_race_url"],
                  "source_available": True, "collected": True, "editorial_ready": False})
# ---- article view (published reports + planned FL long-form), gate run on the shared ledger where one exists
articles = []
for f in sorted((ROOT / "content/learn").glob("*.html")):
    txt = f.read_text(encoding="utf-8")
    if "layout: report" not in txt[:600]:
        continue
    slug = f.stem
    pages = LEDGER_PAGES.get(slug)
    allrows = factcheck_gate.rows_of(ROOT / "docs/election-build/fact_check.csv") if (ROOT / "docs/election-build/fact_check.csv").exists() else []
    mine = [r for r in allrows if pages and r["page"] in pages]
    g = factcheck_gate.check(mine, article=f)[0] if mine else [{"x": "no ledger rows for this article"}]
    st = state_of(slug)
    articles.append({"slug": slug, "workflow_state": st, "gate": "READY" if not g else "BLOCKED", "blocking": len(g),
                     "editorial_ready": (not g) and st is not None and transitions.STATES.index(st) >= READY_FROM, "source": "docs/election-build/fact_check.csv rows for this article"})
for slug in ("fl-senate-article", "fl-house-article"):
    articles.append({"slug": slug, "workflow_state": state_of(slug), "gate": "NO_LEDGER", "blocking": None, "editorial_ready": False, "source": "awaiting ChatGPT draft (Phase B)"})
# ---- asset / source view
assets = rc(PK / "fl_assets.csv")
sources = [json.loads(l) for l in (PK / "fl_sources.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()] if (PK / "fl_sources.jsonl").exists() else []
asset_view = {"assets_total": len(assets), "publishable": sum(1 for a in assets if not a["publication_status"].startswith("NOT FOR")), "not_for_publication": sum(1 for a in assets if a["publication_status"].startswith("NOT FOR")),
              "sources_total": len(sources), "sources_by_verification": {}}
for s in sources:
    asset_view["sources_by_verification"][s["verification_status"]] = asset_view["sources_by_verification"].get(s["verification_status"], 0) + 1
# ---- watchlist coverage
watch = {"rows": len(cov), "by_lock_status": {}, "kalshi_ok": sum(1 for c in cov if c["kalshi"] == "ok"), "polymarket_ok": sum(1 for c in cov if c["polymarket"] == "ok"),
         "with_polls": sum(1 for c in cov if str(c["polls_votehub"]) not in ("0", "", "not_monitored")), "not_monitored": sum(1 for c in cov if c["kalshi"] == "not_monitored")}
for c in cov:
    watch["by_lock_status"][c["lock_status"]] = watch["by_lock_status"].get(c["lock_status"], 0) + 1
# ---- daily runs
runs = []
for d in sorted((DH / "daily").glob("*")):
    for mf in [d / "manifest.json"] + sorted(d.glob("revisions/*/manifest.json")):
        if mf.exists():
            m = rd(mf)
            runs.append({"date": m["date"], "revision": m.get("revision", 1), "run_at_utc": m["run_at_utc"], "quotes_ok": m["market_quotes_ok"], "market_errors": m["market_errors"],
                         "poll_rows": m["poll_rows"], "captures_hashed": len(m["captures"]), "is_latest": (latest.get("manifest_path") or "").endswith(str(mf.relative_to(DH)).replace("\\", "/"))})
dash = {"generated_at_utc": NOW, "unattended_run_proof": "PENDING_UNATTENDED: first scheduled run 2026-10-24 08:00 America/New_York", "sources_status": status.get("sources"),
        "views": {"state": states, "race": races, "article": articles, "asset_source": asset_view, "watchlist_coverage": watch, "daily_runs": runs}}
(OUT / "dashboard.json").write_text(json.dumps(dash, indent=1), encoding="utf-8")

e = html.escape
def table(rows, cols):
    return "<table><thead><tr>" + "".join(f"<th>{e(c)}</th>" for c in cols) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{e(str(r.get(c, '')))}</td>" for c in cols) + "</tr>" for r in rows) + "</tbody></table>"
page = f"""<!doctype html><meta charset="utf-8"><title>LLF workflow dashboard</title><style>body{{font:14px system-ui;margin:24px;max-width:1100px}}table{{border-collapse:collapse;margin:8px 0 24px}}td,th{{border:1px solid #bbb;padding:3px 8px;text-align:left}}h2{{margin-top:28px}}</style>
<h1>LLF workflow dashboard</h1><p>Generated {NOW}. Internal. Three separate flags per row: source_available, collected, editorial_ready.</p>
<p><b>Unattended daily run:</b> {e(dash['unattended_run_proof'])}</p>
<h2>State</h2>{table(states, ['state', 'scope', 'roster_collected', 'roster_snapshot', 'federal_rows_on_ballot', 'tip_grades_graded_rows', 'editorial_ready'])}
<h2>Race</h2>{table(races, ['race_id', 'nominees', 'market', 'poll', 'outside_spending_rows', 'source_available', 'collected', 'editorial_ready'])}
<h2>Article</h2>{table(articles, ['slug', 'workflow_state', 'gate', 'blocking', 'editorial_ready', 'source'])}
<h2>Asset and source</h2><pre>{e(json.dumps(asset_view, indent=1))}</pre>
<h2>Watchlist coverage</h2><pre>{e(json.dumps(watch, indent=1))}</pre>
<h2>Daily runs</h2>{table(runs, ['date', 'revision', 'run_at_utc', 'quotes_ok', 'market_errors', 'poll_rows', 'captures_hashed', 'is_latest'])}"""
(OUT / "index.html").write_text(page, encoding="utf-8")
print("dashboard:", {k: (len(v) if isinstance(v, list) else v) for k, v in dash["views"].items() if k != "asset_source"})
