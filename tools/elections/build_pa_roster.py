#!/usr/bin/env python3
"""Build data/elections/PA/roster.json for the Pennsylvania 2026 general election in the same shape as the Minnesota and New York rosters.

    python3 tools/elections/build_pa_roster.py

PROVENANCE: PARSED from The Green Papers' Pennsylvania 2026 page (a secondary tracker of the official lists; capture in data/elections/PA/captures/), including the FEC IDs it
prints. The Department of State candidate list was not located by a plain request, so verification against it is PENDING and every page must say the list is not official.
Pennsylvania elects a Governor (Josh Shapiro, the incumbent, seeks a second term) and 17 U.S. House members. There is NO U.S. Senate race in 2026 (Class 1 was 2024, Class 3 is 2028).
Anthony Dastra (Green write-in) withdrew on 25 August 2026 per Green Papers and is not listed. Tony Lane and James Moore are write-ins with no ballot line and are not listed.
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_ny_roster as ny

ROOT = Path(__file__).resolve().parents[2]
CAP = ROOT / "data/elections/PA/captures/greenpapers_PA_2026-11-01.html"
GP = "https://www.thegreenpapers.com/G26/PA"
BULLET = "•"
ny.CODES.update({"Independent": "IND"})


def tidy(p):
    p["name"] = p["name"].replace(", Jr.", " Jr.").replace(", III", " III")
    p["state_account"] = re.sub(r"[^A-Za-z0-9._-]", "_", p["name"])
    return p


def block_people(body):
    rows, pos = [], 0
    for m in re.finditer(r"\|" + BULLET + r"\|FEC \|([HS]\w{8})[^|]*", body):
        rows.append(tidy(ny.person(body[pos:m.start()], m.group(1), GP)))
        pos = m.end()
    return rows


def main():
    ny.CAP = CAP
    t = ny.text()
    roster = {"captured_at_utc": "2026-11-01T00:00:00Z",
              "sources": {"official_checked": None,
                          "official_blocked": "The Pennsylvania Department of State candidate list was not found by a plain request on 2026-11-01; it was NOT read",
                          "transcribed_from": GP, "cross_checks": ["TIP export docs/state-packets/PA (race_entries)"]},
              "governor": [], "senate": [], "house": {}}
    g = t[t.find("Candidate list (3, 3 write-ins)"):t.find("Lieutenant Governor|4 year term")]
    for party, nm, rm, inc in [("Democratic", "Joshua D. \"Josh\" Shapiro", "Austin Davis", True), ("Republican", "Stacy Lorraine Garrity", "Jason L. Richey", False),
                               ("Libertarian", "Kenneth V. \"Ken\" Krawchuk", "John C. Thomas", False)]:
        assert nm in g and rm in g, nm
        d = tidy(ny.person(f"{party}|{nm}", None, GP))
        d.update(running_mate=rm, incumbent=inc)
        d["name"] = (d["name"].replace("Joshua D. \"Josh\" Shapiro", "Josh Shapiro").replace("Stacy Lorraine Garrity", "Stacy Garrity")
                     .replace("Kenneth V. \"Ken\" Krawchuk", "Ken Krawchuk"))
        d["state_account"] = re.sub(r"[^A-Za-z0-9._-]", "_", d["name"])
        roster["governor"].append(d)
    start = t.find("U.S. House of Representatives")
    blocks = re.split(r"\|CD (\d+)\|", t[start:])
    for i in range(1, len(blocks), 2):
        cd, body = blocks[i], blocks[i + 1]
        j = body.find("Candidate list")
        if j < 0:
            continue
        body = body[body.find("|", j) + 1:]
        body = re.split(r"Incumbent - 119th Congress|Secretary of State", body)[0]
        roster["house"][cd] = block_people(body)
    assert len(roster["house"]) == 17, len(roster["house"])
    tip = ROOT / "data/elections/PA/tip_export/race_entries.json"
    if tip.exists():
        rows = json.loads(tip.read_text(encoding="utf-8"))
        by = {x["fec_candidate_id"]: x["display_name"] for x in rows if x.get("fec_candidate_id")}
        for x in [y for v in roster["house"].values() for y in v]:
            n = by.get(x["fec_candidate_id"]) if x["fec_candidate_id"] else None
            if n:
                if re.search(r"\d|:|Slogan|FEC|Ran for|Resident of", x["name"]) or not ({w for w in re.findall(r"[a-z]{3,}", x["name"].lower())} & {w for w in re.findall(r"[a-z]{3,}", n.lower())}):
                    x["parsed_name_was"] = x["name"]
                    x["name"], x["state_account"] = n, re.sub(r"[^A-Za-z0-9._-]", "_", n)
                x["tip_name"] = n if n != x["name"] else None
    out = ROOT / "data/elections/PA/roster.json"
    out.write_text(json.dumps(roster, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", out, len(roster["governor"]), "gov;", len(roster["house"]), "districts;", sum(len(v) for v in roster["house"].values()), "house rows")
    for cd, v in roster["house"].items():
        print(cd, [(x["name"], x["party_code"], x["incumbent"], x["fec_candidate_id"]) for x in v])


if __name__ == "__main__":
    main()
