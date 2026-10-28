#!/usr/bin/env python3
"""Join the official Florida roster to TIP records. Writes data/elections/FL/candidates.json.

    python3 tools/elections/join_tip.py <path-to-TIP-repo>/docs/state-packets/FL

Inputs: data/elections/FL/roster.json (official), TIP exports (race_entries, candidates, issue_ratings, issue_definitions).
A TIP page is linked only if a live HEAD/GET to theissuesparty.org returns 200. Nothing is guessed:
  - names are matched on (race, first token, last token); governor candidates match a TIP governor row or any FL TIP row by name
  - a candidate with no TIP row has tip=null and is shown as "No TIP record yet"
"""
import json, re, sys, unicodedata, urllib.request, concurrent.futures as cf, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import os
ST = os.environ.get("LLF_STATE", "FL").upper()          # state code; default Florida keeps the old behavior
D = ROOT / "data/elections" / ST
TIP = Path(sys.argv[1])
rd = lambda p: json.loads(p.read_text(encoding="utf-8"))
roster = rd(D / "roster.json")
entries, cands = rd(TIP / "race_entries.json"), rd(TIP / "candidates.json")
ratings, defs = rd(TIP / "issue_ratings.json"), rd(TIP / "issue_definitions.json")

def norm(n):
    n = unicodedata.normalize("NFKD", n).lower()
    w = [x for x in re.sub(r"[^a-z ]", " ", n).split() if x not in ("jr", "sr", "ii", "iii", "iv")]
    return (w[0], w[-1]) if w else ("", "")

PARTY = {"DEM": "Democratic", "REP": "Republican", "NPA": "No Party Affiliation", "LPF": "Libertarian", "WRI": "Write-in",
         "IND": "Independent Party of Florida", "FFP": "Forward Party", "ASP": "American Solidarity"}
live = lambda c: c["status"] in ("Qualified", "Unopposed")

out = []
def add(office, race, c):
    out.append({"id": c["state_account"], "name": c["name"], "party_code": c["party_code"], "party": c.get("party") or PARTY.get(c["party_code"], c["party_code"]), "tip_name": c.get("tip_name"), "write_in": bool(c.get("write_in")), "note": c.get("note"),
                "office": office, "race": race, "incumbent": c["incumbent"], "running_mate": c.get("running_mate"),
                "status": c["status"], "primary": c["primary"], "state_url": c.get("source_url") or f"https://dos.elections.myflorida.com/candidates/CanDetail.asp?account={c['state_account']}"})

for c in roster["governor"]:
    if live(c): add("governor", "governor", c)
for c in roster["senate"]:
    if live(c): add("senate", "senate", c)
for d, lst in roster["house"].items():
    for c in lst:
        if live(c): add("house", f"house-{int(d):02d}", c)

ent_by = {}
for e in entries:
    ent_by[(e["race_key"], norm(e["display_name"]))] = e
cand_by_name = {}
for c in cands:
    cand_by_name.setdefault(norm(c["display_name"]), []).append(c)
grades = {}
for r in ratings:
    grades.setdefault(r["fec_candidate_id"], {})[r["commitment_slug"]] = r
issue_order = [d["slug"] for d in sorted(defs, key=lambda x: x["sort_order"])]

for c in out:
    key = {"governor": f"2026-GOV-{ST}", "senate": f"2026-S-{ST}"}.get(c["office"]) or f"2026-H-{ST}-{int(c['race'].split('-')[1]):02d}"
    e = ent_by.get((key, norm(c.get("tip_name") or c["name"])))
    tip_page_id = fec = None
    if e and e["fec_candidate_id"]:
        tip_page_id = fec = e["fec_candidate_id"]
    # A person can carry a newer FEC ID on the race entry than on their profile (new district, new committee). The profile is the
    # candidate row the entry points at, so link to that row's ID, not the entry's.
    if e and e.get("candidate_id") is not None:
        row = next((x for x in cands if x["candidate_id"] == e["candidate_id"]), None)
        if row:
            tip_page_id = row["fec_candidate_id"]
            fec = fec or tip_page_id
    if c["office"] == "governor":
        for tc in cand_by_name.get(norm(c.get("tip_name") or c["name"]), []):
            if tc["office_code"] == "GOV":
                tip_page_id = tc["fec_candidate_id"]
            elif tc["fec_candidate_id"] in grades or tc["office_code"] in ("H", "S"):
                fec = tc["fec_candidate_id"]
        if tip_page_id and not fec:
            fec = tip_page_id
    c["fec_candidate_id"] = fec
    c["tip_page_id"] = tip_page_id
    c["tip"] = None
    if tip_page_id:
        g = grades.get(fec or "", {})
        # Grades are keyed to the FEC id of the record they were computed from. For a governor who is also a member of Congress that is the
        # congressional profile, which can differ from the governor profile. Keep both URLs so the page links to where the grades are visible.
        c["tip"] = {"url": f"https://theissuesparty.org/candidates/{tip_page_id}", "grades_url": f"https://theissuesparty.org/candidates/{fec}" if fec and fec != tip_page_id else None, "grades": {
            s: ({"state": "graded", "grade": g[s]["grade"], "score": g[s]["rounded_score"], "aligned": g[s]["aligned"], "against": g[s]["against"],
                 "recorded": g[s]["recorded"], "computed_at": g[s]["computed_at"]} if s in g and g[s]["rating_state"] == "graded" else {"state": "not_graded"})
            for s in issue_order}}

def head(u):
    import time
    code = 0
    for attempt in range(4):                       # one failed request (timeout, 520, 429) is not a missing page: retry with backoff
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "LLF-election-desk"}, method="GET")
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status
        except Exception as ex:
            code = getattr(ex, "code", 0)
            if code == 404:
                return 404
            time.sleep(2 * (attempt + 1))
    return code

urls = {c["tip"]["url"] for c in out if c["tip"]} | {c["tip"]["grades_url"] for c in out if c["tip"] and c["tip"].get("grades_url")}
with cf.ThreadPoolExecutor(6) as ex:
    status = dict(zip(urls, ex.map(head, urls)))
for c in out:
    if c["tip"]:
        c["tip"]["http_status"] = status[c["tip"]["url"]]
        c["tip"]["checked_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        if status[c["tip"]["url"]] != 200:
            c["tip"]["url"] = None
        if c["tip"].get("grades_url") and status[c["tip"]["grades_url"]] != 200:
            c["tip"]["grades_url"] = None

issues = [{"slug": d["slug"], "name": d["display_name"], "short": d["short_label"], "question": d["candidate_question"]} for d in sorted(defs, key=lambda x: x["sort_order"])]
(D / "candidates.json").write_text(json.dumps({"as_of_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": issues, "candidates": out}, indent=1, ensure_ascii=False))
import collections
print(len(out), collections.Counter(c["office"] for c in out), "with TIP page", sum(1 for c in out if c["tip"] and c["tip"]["url"]),
      "with any grade", sum(1 for c in out if c["tip"] and any(v["state"] == "graded" for v in c["tip"]["grades"].values())),
      "non-200:", {u: s for u, s in status.items() if s != 200})
