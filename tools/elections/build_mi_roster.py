#!/usr/bin/env python3
"""Build data/elections/MI/roster.json for the Michigan 2026 general election in the same shape as the Illinois roster.

    python3 tools/elections/build_mi_roster.py

PROVENANCE (read this before trusting the file): the Michigan Bureau of Elections site (mielections.us) did not answer automated requests on 2026-10-28 (connection failed)
and michigan.gov/sos returned HTTP 403, so the official certified list could NOT be read. This roster is transcribed from The Green Papers' Michigan 2026 page
(a secondary tracker of the official lists, read 2026-10-28; capture in data/elections/MI/captures/), including the FEC IDs it prints. Cross-checks with OpenFEC and
TIP follow in join_tip.py. Verification against the Bureau's November General Candidate Listing is PENDING.
`tip_name` is the name TIP stores for the same person where it differs from the ballot name; it is used only for matching.
Scope is Governor, U.S. Senate and U.S. House only.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GP = "https://www.thegreenpapers.com/G26/MI"
S = "Qualified"
P = {"DEM": "Democratic", "REP": "Republican", "GRN": "Green", "LIB": "Libertarian", "UST": "U.S. Taxpayers", "NLP": "Natural Law",
     "WCP": "Working Class", "NPA": "No Party Affiliation"}


def c(name, code, fec=None, inc=False, tip=None, rm=None, note=None, write_in=False, primary="", party=None):
    d = {"name": name, "party_code": code, "party": party or P[code], "incumbent": inc, "running_mate": rm, "status": S, "primary": primary,
         "state_account": re.sub(r"[^A-Za-z0-9._-]", "_", tip or name), "source_url": GP, "tip_name": tip, "fec_candidate_id": fec}
    if note: d["note"] = note
    if write_in: d["write_in"] = True
    return d


roster = {
    "captured_at_utc": "2026-10-28T00:00:00Z",
    "sources": {"official_checked": "Michigan Department of State Official Candidate Listing, General Election 2026-11-03 (read 2026-10-28; 4 DISQ entries excluded)",
                "transcribed_from": GP,
                "cross_checks": ["OpenFEC /candidates (state MI, election_year 2026)", "TIP export docs/state-packets/MI (race_entries)"]},
    "governor": [
        c("Jocelyn Benson", "DEM", rm="Winnie Brinks", note="Secretary of State"),
        c("John James", "REP", rm="Jay DeBoyer", note="Member of Congress, MI-10 (open seat); received his party's nomination 2026-08-04"),
        c("Doug Campbell", "GRN", tip='Douglas "Doug" Campbell', rm="Bobbie Clay"),
        c("Anthony Hudson", "LIB", rm="Beau Parmenter"),
        c("Donna Brandenburg", "UST", rm="Robert Donald Cowper, II"),
    ],
    "senate": [
        c("Abdul El-Sayed", "DEM", "S6MI00418", tip='Abdulrahman Mohamed El-Sayed', note="open seat (Gary Peters not seeking re-election)"),
        c("Mike Rogers", "REP", "S4MI00595", tip='Michael J. "Mike" Rogers', note="former Member of Congress"),
        c("Doug Marsh", "GRN", "S4MI00512", tip="Douglas Philip Marsh"),
        c("Lydia Christensen", "LIB", "S6MI00442", tip="Lydia Lynn Christensen"),
        c("Tim Long", "UST", "S6MI00566", tip='Timothy E. "Tim" Long'),
        c("Walter Kristy", "NLP", "S6MI00590", tip="Walter P. Kristy"),
    ],
    "house": {
        "1": [c("Callie Barr", "DEM", "H4MI01155"), c("Jack Bergman", "REP", "H6MI01226", inc=True, tip='John W. "Jack" Bergman', primary="Renominated"),
              c("LaVeta Davenport", "GRN", "H6MI01309"), c("Arnett Satterla", "LIB", "H6MI01283"), c("Robert Kovaly", "UST", "H6MI02257", tip='Robert "Doc" Kovaly'),
              c("Zebulon Featherly", "NPA", "H6MI01275", tip="Zebulon Hart Featherly"), c("Liz Hakola", "WCP", "H2MI01167")],
        "2": [c("Ben Ambrose", "DEM", "H6MI02216", tip='Benjamin "Ben" Ambrose'), c("John Moolenaar", "REP", "H4MI04126", inc=True, tip="John R. Moolenaar", primary="Renominated"),
              c("Charlotte Magoon", "GRN", "H6MI02265", tip="Charlotte Irene Magoon"), c("Richard Sills", "NLP", "H6MI02273")],
        "3": [c("Hillary Scholten", "DEM", "H0MI03316", inc=True, primary="Renominated"), c("Terri DeBoer", "REP", "H6MI03198"), c("Joe Jock", "GRN", "H6MI03214")],
        "4": [c("Sean McCann", "DEM", "H6MI04204", note="state Senator"), c("Bill Huizenga", "REP", "H0MI02094", inc=True, tip='William P. "Bill" Huizenga', primary="Renominated"),
              c("Che Barnett", "GRN", "H6MI04220", tip='Shafina "Che" Barnett')],
        "5": [c("Christian Vukasovich", "DEM", "H6MI05227", tip="Christian A. Vukasovich"), c("Tim Walberg", "REP", "H4MI07103", inc=True, tip='Timothy L. "Tim" Walberg', primary="Renominated"),
              c("Jim Bronke", "GRN", "H4MI05172", tip='James "Jim" Bronke'), c("Ronald Muszynski", "LIB", "H6MI05235", tip="Ronald A. Muszynski"),
              c("Sharon Renier", "UST", "H4MI07137", tip="Sharon Marie Renier")],
        "6": [c("Debbie Dingell", "DEM", "H4MI12079", inc=True, primary="Renominated"), c("Heather Smiley", "REP", "H4MI06154"), c("Clyde Shabazz", "GRN", "H8MI14084", tip="Clyde K. Shabazz"),
              c("Timothy Teagan", "LIB", "H6MI06258", tip="Timothy A. Teagan"), c("Mike Mickevicius", "UST", "H6MI06241", tip='Michael Raymond "Mike" Mickevicius'),
              c("Linda Rayburn", "WCP", "H6MI06266"), c("Bree Taylor", "NPA", party="Write-in", write_in=True)],
        "7": [c("William Lawrence", "DEM", "H6MI07298"), c("Tom Barrett", "REP", "H2MI07123", inc=True, tip='Thomas More "Tom" Barrett', primary="Renominated"), c("Shane Dedrick", "GRN", "H6MI07306")],
        "8": [c("Kristen McDonald Rivet", "DEM", "H4MI08218", inc=True, primary="Renominated"),
              c("Tom Smith", "REP", "H6MI08312", tip='Thomas James "Tom" Smith', primary="Won", note="suspended campaign 2026-07-16 per Green Papers; remains on the ballot"),
              c("Jim Casha", "GRN", "H4MI08176"), c("Mia Pettus", "LIB", "H6MI08320", tip="C. Mia Pettus"), c("Kathy Goodwin", "WCP", "H8MI05124")],
        "9": [c("Ray Pooley", "DEM", "H6MI09245", tip='Steven Raymond "Ray" Pooley'), c("Lisa McClain", "REP", "H0MI10287", inc=True, primary="Renominated"),
              c("Destiny Clayton", "GRN", "H6MI09260"), c("Kevin Vayko", "LIB", "H4MI09133"), c("John Vlahos", "UST", "H6MI09278"), c("Jim Walkowicz", "WCP", "H2MI09178"),
              c("Jasen Cartwright", "NPA", "H6MI09211", tip="Jasen D. Cartwright", party="Independent (write-in)", write_in=True)],
        "10": [c("Christina Hines", "DEM", "H6MI10276", tip="Christina Bertrand Hines", note="open seat (John James running for Governor)"),
               c("Mike Bouchard", "REP", "H6MI10359", tip='Michael "Mike" Bouchard'), c("Cubby Nkromo", "GRN", tip='Kwabena "Cubby" Nkromo'),
               c("Mike Saliba", "LIB", "H6MI10383", note="Green Papers lists two possible FEC IDs (H0MI09206 or H6MI10383)"), c("Andrea Kirby", "WCP", "H8MI09142", tip="Andrea L. Kirby")],
        "11": [c("Jeremy Moss", "DEM", "H6MI11191", note="state Senator; open seat (Haley Stevens ran for the Senate and did not win the nomination)"),
               c("Ethan Baker", "REP", "H6MI11290", tip="Ethan D. Baker", note="Troy Mayor"), c("Ryan Teasdale", "GRN", "H6MI11308"), c("Farid Ishac", "LIB", "H6MI11316"),
               c("Anil Kumar", "NPA", "H4MI10131", note="Wayne State University Board Member; filed with the FEC as unaffiliated 2026-03-18; Democratic affiliation per Green Papers")],
        "12": [c("Rashida Tlaib", "DEM", "H8MI13250", inc=True, primary="Renominated"), c("James Hooper", "REP", "H2MI12198", tip="James D. Hooper"),
               c("Brenda Sanders", "GRN", "H4MI12145", tip="Brenda K. Sanders", note="former District Judge"), c("Marc Sosnowski", "UST", "H0MI14214", tip="Marc Joseph Sosnowski"),
               c("Gary Walkowicz", "WCP", "H8MI07039")],
        "13": [c("Donavan McKinney", "DEM", "H6MI13254", note="state Representative; open seat (Shri Thanedar lost the primary)"),
               c("T.P. Nykoriak", "REP", "H6MI13312", tip='Taras "T.P." Nykoriak'), c("Raelyn Light", "GRN", "H6MI13320"),
               c("Chris Dardzinski", "UST", "H2MI13337", tip='Christopher "Chris" Dardzinski', note="former Lincoln Park City Council Member"), c("Simone Coleman", "WCP", tip="Simone R. Coleman")],
    },
}
# Where the TIP export is present, take the name TIP stores on the race entry for a person from the FEC ID (more reliable than hand-typed tip_name hints).
tipc = ROOT / "data/elections/MI/tip_export/race_entries.json"  # join_tip.py matches on the race-entry display_name
if tipc.exists():
    byfec = {x["fec_candidate_id"]: x["display_name"] for x in json.loads(tipc.read_text(encoding="utf-8")) if x.get("fec_candidate_id")}
    rows = roster["governor"] + roster["senate"] + [x for v in roster["house"].values() for x in v]
    for x in rows:
        if x.get("fec_candidate_id") in byfec:
            x["tip_name"] = byfec[x["fec_candidate_id"]] if byfec[x["fec_candidate_id"]] != x["name"] else None
            x["state_account"] = re.sub(r"[^A-Za-z0-9._-]", "_", x["tip_name"] or x["name"])

out = ROOT / "data/elections/MI/roster.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(roster, indent=1, ensure_ascii=False), encoding="utf-8")
n = len(roster["governor"]) + len(roster["senate"]) + sum(len(v) for v in roster["house"].values())
print("wrote", out, n, "rows;", sum(1 for k in ("governor", "senate") for x in roster[k] if x.get("write_in")) + sum(1 for v in roster["house"].values() for x in v if x.get("write_in")), "write-ins")
