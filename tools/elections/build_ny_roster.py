#!/usr/bin/env python3
"""Build data/elections/NY/roster.json for the New York 2026 general election in the same shape as the Michigan roster.

    python3 tools/elections/build_ny_roster.py

PROVENANCE: elections.ny.gov returned HTTP 403 to automated requests on 2026-10-30, so the State Board of Elections certification could NOT be read. This roster is
PARSED from The Green Papers' New York 2026 page (a secondary tracker of the official lists; capture in data/elections/NY/captures/), including the FEC IDs it prints.
Verification against the State Board's Nov 3 General Election certification is PENDING. New York has NO U.S. Senate race in 2026 (Gillibrand 2030, Schumer 2028); the five
Senate names on the Green Papers page are early filers for later cycles and are excluded. Write-in governor names are kept and flagged. Scope: Governor and U.S. House.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAP = ROOT / "data/elections/NY/captures/greenpapers_NY_2026-10-30.html"
GP = "https://www.thegreenpapers.com/G26/NY"
CODES = {"Democratic": "DEM", "Republican": "REP", "Conservative": "CON", "Working Families": "WFP", "Libertarian": "LIB", "Green": "GRN"}


def text():
    t = CAP.read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "|", t))
    return re.sub(r"\s*\n\s*", "\n", re.sub(r"\|(\s*\|)+", "|", t))


def person(chunk, fec, source_url=GP):
    parts = [p.strip() for p in chunk.split("|") if p.strip() and p.strip() != "•"]
    name = parts[-1]
    first = parts[0]
    lines = [x.strip() for x in first.split(";") if x.strip()]
    ballot = [x.strip("() ") for x in lines] if lines else []
    pc = ballot[0] if ballot else None
    return {"name": name, "party_code": CODES.get(pc, "OTH"), "party": pc, "ballot_lines": ballot, "incumbent": "Member of Congress" in parts[1:-1],
            "running_mate": None, "status": "Qualified", "primary": "", "state_account": re.sub(r"[^A-Za-z0-9._-]", "_", name), "source_url": source_url,
            "tip_name": None, "fec_candidate_id": fec}


def main():
    t = text()
    roster = {"captured_at_utc": "2026-10-30T00:00:00Z",
              "sources": {"official_checked": None, "official_blocked": "elections.ny.gov returned HTTP 403 on 2026-10-30; certification NOT read", "transcribed_from": GP,
                          "cross_checks": ["TIP export docs/state-packets/NY (race_entries)"]},
              "governor": [], "senate": [], "house": {}}
    # Governor
    g = t[t.find("Candidate list (2, 2 write-ins)"):t.find("4 year term, Election Cycle: 2022, 2026. Elected on a ticket")]
    for ln, nm, rm in [("Democratic; Working Families", "Kathleen Courtney \"Kathy\" Hochul", "Adrienne Adams"),
                       ("Republican; Conservative; Vote Affordable", "Bruce A. Blakeman", "Todd M. Hood")]:
        assert nm in g, nm
        d = person(f"{ln}|{nm}", None); d["running_mate"] = rm; d["name"] = nm.replace('Kathleen Courtney "Kathy" Hochul', "Kathy Hochul")
        d["incumbent"] = "Hochul" in nm
        roster["governor"].append(d)
    for nm, rm, party in [("Paul Mailhot", "Willie Cotton", "Socialist Workers Party"), ("Jonathan Makeley", None, "Prohibition Party")]:
        d = person(f"Write-in|{nm}", None); d.update(party=party, party_code="WRI", write_in=True, running_mate=rm); roster["governor"].append(d)
    # House: split on "|CD n|"
    start = t.find("U.S. House of Representatives")
    blocks = re.split(r"\|CD (\d+)\|", t[start:])
    for i in range(1, len(blocks), 2):
        cd, body = blocks[i], blocks[i + 1]
        j = body.find("Candidate list")
        if j < 0:
            continue
        body = body[body.find("|", j) + 1:]
        body = body.split("Incumbent - 119th Congress")[0]
        rows, pos = [], 0
        for m in re.finditer(r"\|•\|FEC \|(H\w{8})[^|]*", body):
            rows.append(person(body[pos:m.start()], m.group(1)))
            pos = m.end()
        roster["house"][cd] = rows
    tip = ROOT / "data/elections/NY/tip_export/race_entries.json"
    if tip.exists():
        by = {x["fec_candidate_id"]: x["display_name"] for x in json.loads(tip.read_text(encoding="utf-8")) if x.get("fec_candidate_id")}
        for v in roster["house"].values():
            for x in v:
                n = by.get(x["fec_candidate_id"])
                if n:
                    if re.search(r"\d|:|Slogan|FEC|Ran for|Resident of", x["name"]) or not ({w for w in re.findall(r"[a-z]{3,}", x["name"].lower())} & {w for w in re.findall(r"[a-z]{3,}", n.lower())}):          # a note line was read as the name: take TIP's spelling
                        x["parsed_name_was"] = x["name"]
                        x["name"], x["state_account"] = n, re.sub(r"[^A-Za-z0-9._-]", "_", n)
                    x["tip_name"] = n if n != x["name"] else None
    out = ROOT / "data/elections/NY/roster.json"
    out.write_text(json.dumps(roster, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", out, len(roster["governor"]), "gov;", len(roster["house"]), "districts;", sum(len(v) for v in roster["house"].values()), "house rows")


if __name__ == "__main__":
    main()
