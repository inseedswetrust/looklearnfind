#!/usr/bin/env python3
"""Export the machine-readable Florida Senate + House research packet from the data already captured in this repo.

    python3 tools/elections/export_packet.py [outdir]        (default: release/research_packet)

Reads data/elections/FL/* (official roster, TIP join, FEC totals and independent expenditures, Kalshi capture, portraits, district geometry),
data/elections/FL/tip_export/* (TIP database export), data/elections/dark_horse/* (VoteHub captures, AIPAC/UDP records) and
docs/election-build/ASSET_MANIFEST.csv. Writes the 14 packet files that are generated from data, plus manifest.json. The three
hand-written files (fl_reporting_digest.md, fl_conflicts_and_unknowns.md, fl_story_assignments.md) are read from docs/research-packet/
and copied in; the manifest hashes every file. Nothing is filled in: a missing value is null and is listed in `missing_coverage`.
"""
import csv, json, sys, hashlib, datetime, shutil, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dark_horse"))
from schedule_e import dedupe

ROOT = Path(__file__).resolve().parents[2]
FL = ROOT / "data/elections/FL"
DH = ROOT / "data/elections/dark_horse"
TIPX = FL / "tip_export"
SRC_DOCS = ROOT / "docs/research-packet"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "release/research_packet"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
rd = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))

roster, cand, dist = rd(FL / "roster.json"), rd(FL / "candidates.json"), rd(FL / "districts.json")
fin, ieall, mk, port = rd(FL / "finance_fec.json"), rd(FL / "ie_all.json"), rd(FL / "markets.json"), rd(FL / "portraits.json")
idefs, iratings, tracks = rd(TIPX / "issue_definitions.json"), rd(TIPX / "issue_ratings.json"), rd(TIPX / "races.json")
OUT.mkdir(parents=True, exist_ok=True)
missing = []


def write_csv(name, header, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="raise")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def write_json(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")


DOS_FED = roster["sources"]["fed"]["url"]
VERIFIED = roster["captured_at_utc"]
PARTY = {"DEM": "Democratic", "REP": "Republican", "NPA": "No Party Affiliation", "LPF": "Libertarian", "WRI": "Write-in", "IND": "Independent Party of Florida",
         "FFP": "Forward Party", "ASP": "American Solidarity"}
by_acct = {c["id"]: c for c in cand["candidates"]}          # Florida DOS account number -> joined row (live candidates only)

# ---------- 1. roster (every status the Division of Elections lists, Senate + all 28 districts, governor for link context)
rows = []
def add(office, race, district, x):
    c = by_acct.get(x["state_account"])
    tip = (c or {}).get("tip") or {}
    rows.append({
        "candidate_id": (c or {}).get("tip_page_id") or "", "race_id": race, "district": district, "office": office, "candidate_name": x["name"],
        "party": PARTY.get(x["party_code"], x["party_code"]), "incumbent": "yes" if x["incumbent"] else "no", "ballot_status": x["status"],
        "primary_result": x["primary"] or "", "ballot_source_url": (c or {}).get("state_url") or f"https://dos.elections.myflorida.com/candidates/CanDetail.asp?account={x['state_account']}",
        "roster_list_url": DOS_FED, "verified_as_of_utc": VERIFIED, "tip_candidate_url": tip.get("url") or "", "tip_http_status": tip.get("http_status") or "",
        "tip_grades_url": tip.get("grades_url") or "", "fec_candidate_id": (c or {}).get("fec_candidate_id") or "", "dos_account": x["state_account"],
        "identity_confidence": ("high: matched on race, first and last name; TIP page returned 200" if c and tip.get("http_status") == 200 else
                                ("none: not on the November ballot, no TIP profile joined" if not c else "low: no live TIP page")),
        "write_in_or_unopposed": "write-in" if x["party_code"] == "WRI" else ("unopposed" if x["status"] == "Unopposed" else "no"),
        "writing_target": "yes" if office in ("U.S. Senate", "U.S. House") else "no (link context only)"})
for x in roster["senate"]:
    add("U.S. Senate", "senate", "", x)
for d in sorted(roster["house"], key=int):
    for x in roster["house"][d]:
        add("U.S. House", f"house-{int(d):02d}", d, x)
for c in cand["candidates"]:
    if c["office"] == "governor":
        rows.append({"candidate_id": c["tip_page_id"], "race_id": "governor", "district": "", "office": "Governor", "candidate_name": c["name"], "party": c["party"],
                     "incumbent": "yes" if c["incumbent"] else "no", "ballot_status": c["status"], "primary_result": c["primary"], "ballot_source_url": c["state_url"],
                     "roster_list_url": roster["sources"]["gov"]["url"], "verified_as_of_utc": VERIFIED, "tip_candidate_url": (c.get("tip") or {}).get("url") or "",
                     "tip_http_status": (c.get("tip") or {}).get("http_status") or "", "tip_grades_url": (c.get("tip") or {}).get("grades_url") or "",
                     "fec_candidate_id": "" if c["fec_candidate_id"].startswith("GOV-") else c["fec_candidate_id"], "dos_account": c["id"],
                     "identity_confidence": "high: governor roster; TIP IDs beginning GOV-FL are state-level profile IDs, not FEC IDs",
                     "write_in_or_unopposed": "no", "writing_target": "no (link context only)"})
HDR = list(rows[0])
n_roster = write_csv("fl_candidate_roster.csv", HDR, rows)
fed_live = [r for r in rows if r["office"] != "Governor" and r["ballot_status"] in ("Qualified", "Unopposed")]
recon = {"senate_rows": sum(1 for r in rows if r["office"] == "U.S. Senate"), "house_rows": sum(1 for r in rows if r["office"] == "U.S. House"),
         "house_districts": len({r["district"] for r in rows if r["office"] == "U.S. House"}), "on_november_ballot_fed": len(fed_live),
         "by_status": dict(collections.Counter(r["ballot_status"] for r in rows if r["office"] != "Governor"))}
assert recon["house_districts"] == 28, recon

# ---------- 2. races
tr = {t["race_key"]: t for t in tracks}
races = []
for rid in ["senate"] + [f"house-{i:02d}" for i in range(1, 29)]:
    rr = [r for r in rows if r["race_id"] == rid]
    d = None if rid == "senate" else dist["districts"][str(int(rid[-2:]))]
    rk = "2026-S-FL" if rid == "senate" else f"2026-H-FL-{int(rid[-2:]):02d}"
    t = tr.get(rk) or {}
    races.append({
        "race_id": rid, "office": "U.S. Senate (Class III special election for the remainder of the term)" if rid == "senate" else "U.S. House",
        "district": None if rid == "senate" else int(rid[-2:]), "tip_race_key": rk, "tip_race_url": f"https://theissuesparty.org/races/{rk}",
        "district_vintage": None if rid == "senate" else {"plan": dist["source"]["plan"], "bill": dist["source"]["bill"], "publisher": dist["source"]["publisher"],
                                                          "source_url": dist["source"]["url"], "zip_sha256": dist["source"]["zip_sha256"], "population": d["population"],
                                                          "counties_by_share": d["counties"]},
        "general_election_date": "2026-11-03", "primary_date": "2026-08-18", "nominees": [r["candidate_name"] for r in rr if r["ballot_status"] in ("Qualified", "Unopposed")],
        "candidates": [{k: r[k] for k in ("candidate_name", "party", "incumbent", "ballot_status", "primary_result", "candidate_id", "tip_candidate_url", "dos_account")} for r in rr],
        "official_source": DOS_FED, "verified_at_utc": VERIFIED,
        "existing_llf_pages": ["/elections/2026/florida/senate/" if rid == "senate" else f"/elections/2026/florida/house/{int(rid[-2:])}/"],
        "tip_race_record_note": {"display_phase_in_tip_db": t.get("display_phase"), "primary_status_in_tip_db": t.get("primary_status"),
                                 "warning": "TIP races.display_phase is not read by any page (phases come from lib/elections/calendar.ts); treat as stale"} if t else None})
write_json("fl_races.json", {"state": "FL", "generated_at_utc": NOW, "map": {"plan": dist["source"]["plan"], "bill": dist["source"]["bill"], "note": "enacted May 2026, in force for the 2026 election"},
                             "races": races})

# ---------- 3. issue definitions
dh = ["issue_id", "slug", "display_name", "short_label", "candidate_question", "grade_scale", "evidence_rules", "rubric_url", "updated_at", "slot_for_llf_order"]
order = [i["slug"] for i in cand["issues"]]
rowsd = []
for d in idefs:
    rowsd.append({"issue_id": d["id"], "slug": d["slug"], "display_name": d["display_name"], "short_label": d["short_label"], "candidate_question": d["candidate_question"],
                  "grade_scale": "letters A+ to F- from score 0-100; formula = aligned / recorded actions, minimum 1 recorded action, +/-0.5 ping adjustment (lib/grading.ts in the TIP repo)",
                  "evidence_rules": "a candidate is graded only when at least one recorded action exists; otherwise state is not_graded, which is NOT a zero",
                  "rubric_url": "https://theissuesparty.org/methodology", "updated_at": d.get("updated_at") or "", "slot_for_llf_order": order.index(d["slug"]) + 1 if d["slug"] in order else ""})
assert len(rowsd) == 6
write_csv("tip_issue_definitions.csv", dh, rowsd)

# ---------- 4. grades: every Senate/House candidate x six issues
gh = ["candidate_id", "candidate_name", "race_id", "issue_id", "issue_slug", "grade_label", "grade_value", "grade_state", "missing_status", "confidence", "evidence_count_recorded",
      "aligned", "against", "grade_timestamp", "profile_holding_grade", "profile_class", "supporting_source_links"]
idmap = {d["slug"]: d["id"] for d in idefs}
rowsg = []
for c in cand["candidates"]:
    if c["office"] == "governor":
        continue
    tip = c.get("tip") or {}
    url = tip.get("url") or ""
    for slug in order:
        g = (tip.get("grades") or {}).get(slug) or {}
        graded = g.get("state") == "graded"
        recorded = g.get("recorded")
        rowsg.append({"candidate_id": c["tip_page_id"], "candidate_name": c["name"], "race_id": c["race"], "issue_id": idmap.get(slug, ""), "issue_slug": slug,
                      "grade_label": g.get("grade") if graded else "", "grade_value": g.get("score") if graded else "",
                      "grade_state": "graded" if graded else "not_graded", "missing_status": "" if graded else (g.get("state") or "no_data_returned"),
                      "confidence": ("recorded actions: %s" % recorded) if graded else "", "evidence_count_recorded": recorded if graded else "",
                      "aligned": g.get("aligned") if graded else "", "against": g.get("against") if graded else "", "grade_timestamp": g.get("computed_at") if graded else "",
                      "profile_holding_grade": url, "profile_class": "congressional (federal FEC ID; this is the profile that shows the grade)" if url else "none",
                      "supporting_source_links": (url + "#" + slug.replace("_", "-")) if graded else ""})
n_graded = sum(1 for r in rowsg if r["grade_state"] == "graded")
write_csv("tip_grades.csv", gh, rowsg)

# ---------- 5. finance (FEC federal only; Florida state governor finance is deliberately excluded and noted)
fh = ["candidate_id", "candidate_name", "race_id", "office", "committee_id", "receipts", "individual_itemized_contributions", "individual_unitemized_contributions",
      "other_political_committee_contributions", "party_committee_contributions", "candidate_contribution", "disbursements", "cash_on_hand_end_period", "debts_owed",
      "coverage_start", "coverage_end", "report_type", "as_of_utc", "currency", "provenance", "gaps"]
rowsf = []
for c in cand["candidates"]:
    if c["office"] == "governor":
        continue
    t = fin["totals"].get(c["fec_candidate_id"])
    rowsf.append({"candidate_id": c["fec_candidate_id"], "candidate_name": c["name"], "race_id": c["race"], "office": c["office"], "committee_id": "",
                  "receipts": (t or {}).get("receipts"), "individual_itemized_contributions": (t or {}).get("individual_itemized_contributions"),
                  "individual_unitemized_contributions": (t or {}).get("individual_unitemized_contributions"),
                  "other_political_committee_contributions": (t or {}).get("other_political_committee_contributions"),
                  "party_committee_contributions": (t or {}).get("political_party_committee_contributions"), "candidate_contribution": (t or {}).get("candidate_contribution"),
                  "disbursements": (t or {}).get("disbursements"), "cash_on_hand_end_period": (t or {}).get("cash_on_hand_end_period"),
                  "debts_owed": (t or {}).get("debts_owed_by_committee"), "coverage_start": (t or {}).get("coverage_start_date"), "coverage_end": (t or {}).get("coverage_end_date"),
                  "report_type": (t or {}).get("last_report_type_full"), "as_of_utc": fin["as_of_utc"], "currency": "USD",
                  "provenance": "OpenFEC /candidates/totals cycle 2026 (federal committees only)",
                  "gaps": "" if t else "no FEC totals row returned for this candidate ID (no federal committee found or no filing in the 2026 cycle)"})
n_fin_missing = sum(1 for r in rowsf if r["gaps"])
write_csv("fl_candidate_finance.csv", fh, rowsf)

# ---------- 6. outside spending (Schedule E): de-duplicated transactions; support/oppose kept; AIPAC/UDP flagged by committee ID only
AIPAC_IDS = {"C00797670": "AIPAC PAC", "C00799031": "United Democracy Project (UDP)"}
oh = ["fec_transaction_id", "fec_sub_id", "committee_id", "committee_name", "committee_type", "beneficiary_candidate_id", "beneficiary_candidate", "race_id", "support_oppose",
      "amount", "filing_form", "is_24_48_hour_notice", "disbursement_date", "dissemination_date", "report_year", "payee", "description", "amendment_indicator",
      "duplicates_collapsed", "memo_rows_dropped", "aipac_or_udp_committee", "organization_connection_evidence"]
ctype = {}
for cid_, lst in fin["independent_expenditures"].items():
    for e in lst:
        ctype[e["committee_id"]] = (e["committee"].get("type"), e["committee"].get("name"))
rowso, dropped_memo = [], 0
for cid_, v in ieall["candidates"].items():
    kept, memo = dedupe([dict(t, candidate_id=cid_) for t in v["transactions"]])
    dropped_memo += memo
    for t in kept:
        ct = ctype.get(t["committee_id"], (None, None))
        rowso.append({"fec_transaction_id": t["transaction_id"], "fec_sub_id": t["sub_id"], "committee_id": t["committee_id"], "committee_name": t["committee_name"],
                      "committee_type": ct[0] or "", "beneficiary_candidate_id": cid_, "beneficiary_candidate": v["name"], "race_id": v["race"],
                      "support_oppose": {"S": "support", "O": "oppose"}.get(t["support_oppose_indicator"], t["support_oppose_indicator"]), "amount": t["expenditure_amount"],
                      "filing_form": t["filing_form"], "is_24_48_hour_notice": t["is_notice"], "disbursement_date": t["expenditure_date"], "dissemination_date": t["dissemination_date"],
                      "report_year": t["report_year"], "payee": t["payee_name"], "description": t["expenditure_description"], "amendment_indicator": t["amendment_indicator"],
                      "duplicates_collapsed": t["duplicates_collapsed"], "memo_rows_dropped": "", "aipac_or_udp_committee": AIPAC_IDS.get(t["committee_id"], ""),
                      "organization_connection_evidence": ("committee identity only (FEC committee ID); any link to AIPAC beyond the committee name is not established in FEC data and is not asserted here"
                                                          if t["committee_id"] in AIPAC_IDS else "")})
rowso.sort(key=lambda r: (r["race_id"], r["beneficiary_candidate"], r["disbursement_date"] or ""))
write_csv("fl_outside_spending.csv", oh, rowso)
aip = [r for r in rowso if r["aipac_or_udp_committee"]]

# ---------- 7. markets (Kalshi captured; Polymarket explicit absence; every contract typed party-vs-candidate)
mrows = []
for rid in ["senate"] + [f"house-{i:02d}" for i in range(1, 29)]:
    ev = mk["races"].get(rid)
    if not ev or not ev.get("contracts"):
        mrows.append({"race_id": rid, "venue": "kalshi", "status": "no_contract_found", "contracts": [], "note": "no Kalshi event returned for this race; no odds are shown"})
        missing.append(f"market:{rid}")
        continue
    cs = []
    for c in ev["contracts"]:
        cs.append({"ticker": c["ticker"], "contract_kind": "party_winner", "plain_reading": "Resolves Yes if the member sworn in is of the named PARTY; the label shows a candidate name but it is not a named-candidate contract",
                   "yes_label": c.get("yes_label"), "settlement_rule": c["rules"], "status": c["status"], "bid": c.get("yes_bid"), "ask": c.get("yes_ask"), "last": c.get("last"),
                   "previous": c.get("previous"), "mid": (round((float(c["yes_bid"]) + float(c["yes_ask"])) / 2, 4) if c.get("yes_bid") and c.get("yes_ask") else None),
                   "volume_contracts": c.get("volume"), "volume_24h": c.get("volume_24h"), "open_interest": c.get("open_interest"), "close_time": c.get("close_time"),
                   "last_trade_time": None, "stale_status": "unknown: the Kalshi event payload carries no last-trade timestamp; snapshot_time is the capture time"})
    mrows.append({"race_id": rid, "venue": "kalshi", "status": "ok", "event_ticker": ev["event_ticker"], "title": ev["title"], "market_url": ev["url"],
                  "history_link": "https://kalshi.com/markets/" + ev["event_ticker"].split("-")[0].lower(), "contracts": cs})
mrows.append({"race_id": "all FL federal races", "venue": "polymarket", "status": "no_verified_instrument",
              "note": "Polymarket individual-winner markets matched in the dark-horse work were CA-14 and CA-11 only; none for Florida Senate or House was verified. No Polymarket odds are shown for Florida."})
write_json("fl_markets.json", {"snapshot_time_utc": mk["captured_at_utc"], "source": mk["source"], "quote_semantics": "bid, ask, last as returned (dollars per $1 contract); mid computed as (bid+ask)/2 and labeled; never substitute one for another; deltas only same contract and same quote kind",
                               "disclaimer": "market prices are not forecasts or probabilities", "races": mrows})

# ---------- 8. polls (VoteHub captures of 2026-10-23; originals not yet reviewed)
latest = rd(DH / "latest.json")["date"]
cap = DH / "daily" / latest / "captures"
ph = ["race_id", "pollster", "sponsor", "partisan_sponsor", "internal", "population", "sample_size", "field_start", "field_end", "release_date", "margin_of_error", "undecided",
      "estimates", "original_poll_url", "aggregator", "aggregator_poll_id", "aggregator_import_date", "mode", "review_status", "rights_note"]
rowsp = []
for t, fn in (("us-senator", "votehub_us-senator.json"), ("us-representative", "votehub_us-representative.json")):
    for p in rd(cap / fn):
        if t == "us-senator" and p.get("subject") != "2026 Florida":
            continue
        if t == "us-representative" and not str(p.get("seat_name") or "").startswith("FL-"):
            continue
        rid = "senate" if t == "us-senator" else "house-" + p["seat_name"].split("-")[1]
        rowsp.append({"race_id": rid, "pollster": p.get("pollster"), "sponsor": "; ".join(p.get("sponsors") or []), "partisan_sponsor": p.get("partisan") or "", "internal": p.get("internal"),
                      "population": p.get("population"), "sample_size": p.get("sample_size"), "field_start": p.get("start_date"), "field_end": p.get("end_date"), "release_date": "",
                      "margin_of_error": "", "undecided": "", "estimates": "; ".join(f"{a['choice']} {a['pct']}" for a in p.get("answers", [])), "original_poll_url": p.get("url"),
                      "aggregator": "VoteHub API (beta)", "aggregator_poll_id": p.get("id"), "aggregator_import_date": p.get("created_at"), "mode": "",
                      "review_status": "aggregator_listing; original release not reviewed here (MOE, mode, release date and undecided are blank until it is)",
                      "rights_note": "VoteHub terms unverified (page returned 403); facts stored with attribution; republish only after the original release is checked"})
rowsp.sort(key=lambda r: (r["race_id"], r["field_end"] or ""), reverse=False)
have = {r["race_id"] for r in rowsp}
for rid in ["senate"] + [f"house-{i:02d}" for i in range(1, 29)]:
    if rid not in have:
        rowsp.append({k: "" for k in ph} | {"race_id": rid, "review_status": "no_poll_found", "rights_note": "source checked: VoteHub us-%s on %s; absence is not evidence of a tie" % ("senator" if rid == "senate" else "representative", latest)})
write_csv("fl_polls.csv", ph, rowsp)

# ---------- 11. assets
ah = ["asset_id", "kind", "subject", "path", "license", "attribution", "original_url", "aspect_ratio", "publication_status", "layout_reference"]
rowsa = []
for rr in csv.DictReader(open(ROOT / "docs/election-build/ASSET_MANIFEST.csv", encoding="utf-8")):
    if "fl" in rr["asset_id"].lower() and "HERO" in rr["asset_id"]:
        rowsa.append({"asset_id": rr["asset_id"], "kind": "hero_photo", "subject": "Florida Old Capitol", "path": rr["path"], "license": rr["license"], "attribution": rr["credit"],
                      "original_url": rr["source"], "aspect_ratio": "16:9 crop", "publication_status": "publishable with attribution (CC BY-SA 4.0 requires share-alike credit)", "layout_reference": rr["reference_design"]})
for cid_, v in port.items():
    c = by_acct.get(cid_)
    if v.get("result") == "ok":
        rowsa.append({"asset_id": f"PORTRAIT-{(c or {}).get('tip_page_id') or cid_}", "kind": "portrait", "subject": v["name"], "path": f"static/img/elections/portraits/{cid_}.jpg",
                      "license": v["license"], "attribution": v["credit"], "original_url": v["source_page"], "aspect_ratio": "4:5", "publication_status": "publishable with attribution",
                      "layout_reference": "candidate card"})
    else:
        rowsa.append({"asset_id": f"PORTRAIT-{(c or {}).get('tip_page_id') or cid_}", "kind": "portrait", "subject": v["name"], "path": "", "license": "", "attribution": "",
                      "original_url": "", "aspect_ratio": "4:5", "publication_status": "NOT FOR PUBLICATION: no licensed image found; use monogram", "layout_reference": "candidate card"})
rowsa.append({"asset_id": "MAP-fl-districts-EOGPCRP2026", "kind": "district_map", "subject": "Florida congressional districts, plan EOGPCRP2026", "path": "generated by tools/elections/build_fl_geometry.py from data/elections/FL/districts.json",
              "license": "public record (Florida Legislature EDR shapefile; Census county boundaries)", "attribution": "Florida Legislature EDR", "original_url": dist["source"]["url"], "aspect_ratio": "per viewbox " + str(dist["viewbox"]),
              "publication_status": "publishable", "layout_reference": "house atlas"})
write_csv("fl_assets.csv", ah, rowsa)
n_port_missing = sum(1 for r in rowsa if r["kind"] == "portrait" and r["publication_status"].startswith("NOT FOR"))

# ---------- 12. existing pages
def live(route):
    """HTTP status of the live page, or null if the check could not run. The packet never depends on the answer."""
    import urllib.request, urllib.error
    try:
        with urllib.request.urlopen(urllib.request.Request("https://looklearnfind.com" + route, method="HEAD", headers={"User-Agent": "LLF-packet-check"}), timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as ex:
        return ex.code
    except Exception:
        return None
DIST = ROOT / "dist"
routes = [("/elections/2026/florida/", "state landing (the State Board)"), ("/elections/2026/florida/governor/", "governor guide"), ("/elections/2026/florida/senate/", "Senate guide (state guide module, NOT the long-form article)"),
          ("/elections/2026/florida/house/", "House atlas and directory (28 districts)"), ("/about/election-methods/", "methods, definitions, TIP grade formula"),
          ("/learn/florida-house-independent-spending-october-2026/", "report: Florida House independent spending"), ("/learn/florida-governor-fundraising-polling-2026/", "report: Florida governor fundraising and polling"),
          ("/learn/michigan-senate-delta-october-2026/", "report: Michigan Senate delta (reference article)"), ("/elections/2026/dark-horse/status/", "dark-horse status page"),
          ("/elections/2026/dark-horse/status.json", "public status feed")] + [(f"/elections/2026/florida/house/{i}/", f"district {i} page") for i in range(1, 29)]
pages = {"generated_at_utc": NOW, "base": "https://looklearnfind.com",
    "routes": [{"route": r, "kind": k, "built_in_repo": (DIST / r.strip("/") / "index.html").exists() or (DIST / r.strip("/")).is_file(), "live_http_status": live(r), "checked_at_utc": NOW} for r, k in routes],
    "note": "built_in_repo true with live_http_status 404 means the page is built but not yet uploaded (the dark-horse status page ships in release/looklearnfind-elections-update.zip)",
    "components_in_elections_py": ["candidate_card", "tip_button", "delta_chart", "spend_chart", "dedupe_ie", "render_report", "autolink (R1 and R2)", "expand_values ([[v:name]])", "expand_macros ([[s:n]], [[el:name]])"],
    "final_article_paths": {"florida_senate_long_form": "content/learn/florida-senate-<slug>.html with `layout: report` (elections.render_report); not yet created",
                            "florida_house_long_form": "content/learn/florida-house-<slug>.html with `layout: report`; not yet created",
                            "state_pages_to_link": ["/elections/2026/florida/senate/", "/elections/2026/florida/house/", "/elections/2026/florida/house/<n>/"]},
    "tip_deep_links": {"senate_race": "https://theissuesparty.org/races/2026-S-FL", "house_race_pattern": "https://theissuesparty.org/races/2026-H-FL-<dd>",
                       "candidate_pattern": "https://theissuesparty.org/candidates/<FEC id>"},
    "screenshots": "tools/qa/shots.py regenerates desktop and mobile screenshots on demand; none are committed", "last_qa": "docs/election-build/IMPLEMENTATION_REPORT.md; strict build 0 violations on 2026-10-23",
    "scope": {"senate_candidates_on_ballot": 3, "house_districts": 28, "house_candidates_on_ballot": 83}}
write_json("fl_existing_pages.json", pages)

# ---------- 10. sources registry (claim-level sources generated from captures; news sources are appended from the digest source list)
S = []
def src(i, url, typ, captured, date, locator, lic, lim, status):
    S.append({"source_id": i, "url": url, "type": typ, "captured_at": captured, "date": date, "excerpt_locator": locator, "license": lic, "limitations": lim, "verification_status": status})
src("SRC-DOS-FED", DOS_FED, "official_state_roster", roster["captured_at_utc"], roster["captured_at_utc"][:10], "table rows per office; sha256 " + roster["sources"]["fed"]["sha256"][:16], "public record", "state 'Qualified' filter omits Unopposed; statuses change on withdrawals", "primary: Florida Division of Elections")
src("SRC-DOS-GOV", roster["sources"]["gov"]["url"], "official_state_roster", roster["captured_at_utc"], roster["captured_at_utc"][:10], "governor table", "public record", "link context only", "primary")
src("SRC-MAP", dist["source"]["url"], "official_district_boundaries", "2026-10-23", "2026-05", "plan EOGPCRP2026 shapefile, sha256 " + dist["source"]["zip_sha256"][:16], "public record", "county shares computed from Census cb_2024 county boundaries", "primary")
src("SRC-FEC-TOTALS", "https://api.open.fec.gov/v1/candidates/totals/", "federal_campaign_finance", fin["as_of_utc"], fin["as_of_utc"][:10], "results[] per candidate_id", "public record (FEC)", "coverage_end_date varies by candidate; principal committee ID not in this payload", "primary: FEC")
src("SRC-FEC-SCHEDE", "https://api.open.fec.gov/v1/schedules/schedule_e/", "independent_expenditures", ieall["captured_at_utc"], ieall["captured_at_utc"][:10], "transaction_id", "public record (FEC)", "24/48-hour notices and periodic filings repeat the same spending; de-duplicated here; by_candidate aggregates cover periodic filings only", "primary: FEC")
src("SRC-KALSHI", "https://api.elections.kalshi.com/trade-api/v2/events", "prediction_market_quotes", mk["captured_at_utc"], mk["captured_at_utc"][:10], "event_ticker / ticker", "public API; terms not reviewed for republication of raw quotes", "party-winner contracts; no last-trade timestamp in payload", "primary: venue")
src("SRC-VOTEHUB", "https://api.votehub.com/polls", "poll_aggregator", latest, latest, "poll id", "UNVERIFIED (terms page returned 403)", "originals not reviewed; MOE and release date absent", "secondary")
src("SRC-TIP-DB", "https://theissuesparty.org/", "tip_database_export", NOW, NOW[:10], "docs/state-packets/FL export (candidate_issue_grades, race_entries)", "owner's own data", "grades appear on the profile named in tip_grades.csv only", "primary: owner")
for r in aip[:0]:
    pass
for ref in sorted(SRC_DOCS.glob("sources_news.jsonl")):
    for line in ref.read_text(encoding="utf-8").splitlines():
        if line.strip():
            S.append(json.loads(line))
(OUT / "fl_sources.jsonl").write_text("\n".join(json.dumps(s, ensure_ascii=False) for s in S) + "\n", encoding="utf-8")

# ---------- hand-written files
for fn in ("fl_reporting_digest.md", "fl_conflicts_and_unknowns.md", "fl_story_assignments.md"):
    p = SRC_DOCS / fn
    if p.exists():
        shutil.copy(p, OUT / fn)
    else:
        (OUT / fn).write_text(f"# {fn}\n\nBLOCKED: source file docs/research-packet/{fn} was not found when the packet was built.\n", encoding="utf-8")
        missing.append(fn)

# ---------- manifest
missing += [f"finance:{r['candidate_name']}" for r in rowsf if r["gaps"]]
missing += [f"portrait:{r['subject']}" for r in rowsa if r["kind"] == "portrait" and r["publication_status"].startswith("NOT FOR")]
missing += [f"poll:{r['race_id']}" for r in rowsp if r["review_status"] == "no_poll_found"]
missing.append("aipac_direct_pac_contributions (Schedule B): not pulled; fetch_aipac_direct.py is ready but needs an OpenFEC key (DEMO_KEY was rate limited)")
files = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "manifest.json")
man = {"packet": "florida-senate-house-research-packet", "version": "1.0.0", "generated_at_utc": NOW, "generator": "tools/elections/export_packet.py", "scope": "Florida U.S. Senate and U.S. House (28 districts); governor rows are link context only",
       "counts": {"roster_rows": n_roster, "federal_rows_on_november_ballot": recon["on_november_ballot_fed"], "races": len(races), "grade_rows": len(rowsg), "grade_rows_graded": n_graded,
                  "finance_rows": len(rowsf), "finance_rows_without_fec_totals": n_fin_missing, "outside_spending_rows": len(rowso), "outside_spending_aipac_udp_rows": len(aip),
                  "memo_x_rows_dropped": dropped_memo, "poll_rows": sum(1 for r in rowsp if r["review_status"] != "no_poll_found"), "races_without_poll": sum(1 for r in rowsp if r["review_status"] == "no_poll_found"),
                  "market_races_with_contract": sum(1 for r in mrows if r.get("status") == "ok"), "sources": len(S), "asset_rows": len(rowsa), "portraits_not_for_publication": n_port_missing},
       "roster_reconciliation": recon,
       "files": [{"name": p.name, "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
       "source_snapshots_utc": {"dos_roster": roster["captured_at_utc"], "fec_totals": fin["as_of_utc"], "fec_ie": ieall["captured_at_utc"], "kalshi": mk["captured_at_utc"], "votehub_day": latest,
                                "tip_candidates_join": cand["as_of_utc"]},
       "missing_coverage": missing}
write_json("manifest.json", man)
print(json.dumps(man["counts"], indent=1))
print("missing_coverage items:", len(missing))
