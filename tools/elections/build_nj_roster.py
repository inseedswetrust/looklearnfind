#!/usr/bin/env python3
"""Build data/elections/NJ/roster.json for the New Jersey 2026 general election in the same shape as the New York and Michigan rosters.

    python3 tools/elections/build_nj_roster.py

PROVENANCE: parsed from The Green Papers' New Jersey 2026 page (a secondary tracker of the
official lists; capture in data/elections/NJ/captures/), including the FEC IDs it prints. Verified 2026-10-31 against the Division's official lists (Senate 07/27/2026, House 09/04/2026): same 35 House and 4 Senate candidates; the Green Papers write-in Castillo Nicasio is not on the official list.
New Jersey has no governor election in 2026 (the 2025 election chose Mikie Sherrill). Scope: U.S. Senate (Class 2) and U.S. House. A write-in listed by Green Papers is kept and flagged.
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_ny_roster as ny

ROOT = Path(__file__).resolve().parents[2]
CAP = ROOT / "data/elections/NJ/captures/greenpapers_NJ_2026-10-31.html"
GP = "https://www.thegreenpapers.com/G26/NJ"
BULLET = "•"


def block_people(body):
    rows, pos = [], 0
    for m in re.finditer(r"\|" + BULLET + r"\|FEC \|([HS]\w{8})[^|]*", body):
        rows.append(ny.person(body[pos:m.start()], m.group(1), GP))
        pos = m.end()
    return rows


# Candidates Green Papers lists with no FEC ID (no federal filing): (district, ballot line, name). Read from the capture, 2026-10-31.
NO_FEC = [("7", "STOP ISRAEL'S GENOCIDE", "Seamus Patrick O'Toole"), ("8", "Socialist Workers Party", "Craig Honts"),
          ("8", "Independent", 'Aristotle "Ari" Eliopoulos'), ("12", "GET MONEY OUT", "Winston Jordan")]


def main():
    ny.CAP = CAP
    t = ny.text()
    roster = {"captured_at_utc": "2026-10-31T00:00:00Z",
              "sources": {"official_checked": "New Jersey Division of Elections Official Lists, General Election 11/03/2026: U.S. Senate dated 07/27/2026, U.S. House dated 09/04/2026 (PDFs in data/elections/NJ/captures; read 2026-10-31; 35 House names and 4 Senate names match)", "transcribed_from": GP,
                          "cross_checks": ["TIP export docs/state-packets/NJ (race_entries)"]},
              "governor": [], "senate": [], "house": {}}
    # Senate: the Class 2 candidate list, up to the Governor heading
    s = t.find("Class 2|Democratic|Senator")
    j = t.find("Candidate list", s)
    body = t[t.find("|", j) + 1:t.find("|Governor", j)]
    for p in block_people(body):
        if p["party"] == "Write-in":
            p.update(write_in=True, party_code="WRI")
        roster["senate"].append(p)
    start = t.find("U.S. House of Representatives")
    blocks = re.split(r"\|CD (\d+)\|", t[start:])
    for i in range(1, len(blocks), 2):
        cd, body = blocks[i], blocks[i + 1]
        j = body.find("Candidate list")
        if j < 0:
            continue
        body = body[body.find("|", j) + 1:].split("Incumbent - 119th Congress")[0]
        rows = block_people(body)
        for p in rows:
            if p["party"] == "Write-in":
                p.update(write_in=True, party_code="WRI")
        roster["house"][cd] = rows
    for cd, line, nm in NO_FEC:
        d = ny.person(f"{line}|{nm}", None, GP)
        d["note"] = "Green Papers lists no FEC ID (no federal filing found)"
        roster["house"][cd].append(d)
    tip = ROOT / "data/elections/NJ/tip_export/race_entries.json"
    if tip.exists():
        by = {x["fec_candidate_id"]: x["display_name"] for x in json.loads(tip.read_text(encoding="utf-8")) if x.get("fec_candidate_id")}
        byname = {x["display_name"]: x["display_name"] for x in json.loads(tip.read_text(encoding="utf-8")) if not x.get("fec_candidate_id")}
        for x in roster["senate"] + [y for v in roster["house"].values() for y in v]:
            n = by.get(x["fec_candidate_id"]) if x["fec_candidate_id"] else byname.get(x["name"])
            if n:
                bad = bool(re.search(r"\d|:|Slogan|FEC|Resident of", x["name"])) or not ({w for w in re.findall(r"[a-z]{3,}", x["name"].lower())} & {w for w in re.findall(r"[a-z]{3,}", n.lower())})          # a note line was read as the name: take TIP's spelling
                if bad:
                    x["parsed_name_was"] = x["name"]
                    n = n.title() if n.isupper() else n                           # TIP stores some names in capitals
                    x["name"], x["state_account"] = n, re.sub(r"[^A-Za-z0-9._-]", "_", n)
                x["tip_name"] = n if n != x["name"] else None
    # Incumbency: the Green Papers title line is not always parsed (a dated note can sit in front of the name), so also match the TIP race's incumbent by surname.
    races = ROOT / "data/elections/NJ/tip_export/races.json"
    if races.exists():
        inc = {r["race_key"]: (r.get("incumbent_name") or "") for r in json.loads(races.read_text(encoding="utf-8"))}
        def mark(rk, rows):
            last = inc.get(rk, "").replace(",", "").split()[-1].lower() if inc.get(rk) else None
            for x in rows:
                if last and x["name"].replace(",", "").split()[-1].lower().rstrip(".") in (last, last + " jr") or (last and last in x["name"].lower().replace(",", "").split()):
                    x["incumbent"] = True
        mark("2026-S-NJ", roster["senate"])
        for cd, rows in roster["house"].items():
            mark(f"2026-H-NJ-{int(cd):02d}", rows)
    out = ROOT / "data/elections/NJ/roster.json"
    out.write_text(json.dumps(roster, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", out, len(roster["senate"]), "senate;", len(roster["house"]), "districts;", sum(len(v) for v in roster["house"].values()), "house rows")


if __name__ == "__main__":
    main()
