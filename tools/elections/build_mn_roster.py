#!/usr/bin/env python3
"""Build data/elections/MN/roster.json for the Minnesota 2026 general election in the same shape as the New York and New Jersey rosters.

    python3 tools/elections/build_mn_roster.py

PROVENANCE: the Minnesota Secretary of State candidate finder (candidates.sos.mn.gov) is an interactive form, and its downloadable state media file is behind a Radware
captcha (a bot check), so it was NOT read (recorded in docs/production/DATA_ACCESS_LIMITATIONS.md). This roster is PARSED from The Green Papers' Minnesota 2026 page (a
secondary tracker of the official lists; capture in data/elections/MN/captures/), including the FEC IDs it prints. Verification against the Secretary of State's list is PENDING.
Minnesota elects a Governor (open: Tim Walz is not running), a U.S. Senator (Class 2, open: Tina Smith is retiring) and eight U.S. House members. Sen. Amy Klobuchar is running for
Governor; her Senate seat is not up until 2030. Green Papers lists the Senate write-in Kevin Dwire without an FEC ID. The party's ballot name is Democratic-Farmer-Labor (DFL).
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_ny_roster as ny

ROOT = Path(__file__).resolve().parents[2]
CAP = ROOT / "data/elections/MN/captures/greenpapers_MN_2026-10-31.html"
GP = "https://www.thegreenpapers.com/G26/MN"
BULLET = "•"
ny.CODES.update({"Democratic-Farmer Labor": "DEM", "Independent": "IND", "Forward Independence": "OTH"})


def tidy(p):
    p["name"] = p["name"].replace(", Jr.", " Jr.")
    p["state_account"] = re.sub(r"[^A-Za-z0-9._-]", "_", p["name"])
    if p["party"] == "Democratic-Farmer Labor":
        p["party"] = "Democratic-Farmer-Labor"
        p["ballot_lines"] = ["Democratic-Farmer-Labor"]
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
    roster = {"captured_at_utc": "2026-10-31T00:00:00Z",
              "sources": {"official_checked": None,
                          "official_blocked": "candidates.sos.mn.gov offers its filing data through a form and a media-file download behind a Radware captcha on 2026-10-31; the Secretary of State list was NOT read",
                          "transcribed_from": GP, "cross_checks": ["TIP export docs/state-packets/MN (race_entries)"]},
              "governor": [], "senate": [], "house": {}}
    # Governor: three tickets (Green Papers prints no FEC IDs for state office)
    g = t[t.find("Candidate list (3)"):t.find("Lieutenant Governor|4 year term")]
    for party, nm, rm, inc in [("Democratic-Farmer Labor", "Amy J. Klobuchar", "Ben Schierer", False), ("Republican", "Lisa Demuth", "Ryan Wilson", False),
                               ("Green", "Steven Young", "Jane Kirby", False)]:
        assert nm in g and rm in g, nm
        d = tidy(ny.person(f"{party}|{nm}", None, GP))
        d.update(running_mate=rm, incumbent=inc)
        d["name"] = d["name"].replace("Amy J. Klobuchar", "Amy Klobuchar")
        roster["governor"].append(d)
    # Senate: Class 2 open seat
    s = t.find("Class 2|Open|Democratic|Senator")
    j = t.find("Candidate list", s)
    body = t[t.find("|", j) + 1:t.find("|Governor", j)]
    sen = block_people(body.split("Write-in;")[0])
    assert len(sen) == 4, len(sen)
    roster["senate"] = sen
    d = tidy(ny.person("Write-in|Kevin Dwire", None, GP))
    d.update(party="Socialist Workers Party", party_code="WRI", write_in=True, ballot_lines=["Write-in"], note="Write-in; Green Papers lists no FEC ID")
    assert "Kevin Dwire" in body
    roster["senate"].append(d)
    for x in roster["senate"]:
        if x["name"] == "Margaret \"Peggy\" Flanagan":
            x["note"] = "Lieutenant Governor; won the August 11 DFL primary for the Senate nomination"
    # House
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
    assert len(roster["house"]) == 8 and sum(len(v) for v in roster["house"].values()) == 17
    tip = ROOT / "data/elections/MN/tip_export/race_entries.json"
    if tip.exists():
        rows = json.loads(tip.read_text(encoding="utf-8"))
        by = {x["fec_candidate_id"]: x["display_name"] for x in rows if x.get("fec_candidate_id")}
        for x in roster["senate"] + [y for v in roster["house"].values() for y in v]:
            n = by.get(x["fec_candidate_id"]) if x["fec_candidate_id"] else None
            if n:
                if re.search(r"\d|:|Slogan|FEC|Ran for|Resident of", x["name"]) or not ({w for w in re.findall(r"[a-z]{3,}", x["name"].lower())} & {w for w in re.findall(r"[a-z]{3,}", n.lower())}):
                    x["parsed_name_was"] = x["name"]
                    x["name"], x["state_account"] = n, re.sub(r"[^A-Za-z0-9._-]", "_", n)
                x["tip_name"] = n if n != x["name"] else None
    out = ROOT / "data/elections/MN/roster.json"
    out.write_text(json.dumps(roster, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", out, len(roster["governor"]), "gov;", len(roster["senate"]), "senate;", len(roster["house"]), "districts;", sum(len(v) for v in roster["house"].values()), "house rows")


if __name__ == "__main__":
    main()
