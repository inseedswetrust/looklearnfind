#!/usr/bin/env python3
"""Build data/elections/IL/roster.json for the Illinois 2026 general election in the same shape as the Florida roster.

    python3 tools/elections/build_il_roster.py

PROVENANCE (read this before trusting the file): the Illinois State Board of Elections site (elections.il.gov) returns HTTP 403 to automated requests, so the official
certified list could NOT be fetched. This roster is transcribed from The Green Papers' Illinois 2026 general election page (a secondary tracker of the official lists, read
2026-10-28), then cross-checked against OpenFEC's candidate list (federal IDs) and TIP's race entries. Every row carries the sources that agree. Verification against the
Board's own list is PENDING: a person with browser access should open the Board's candidate list and tick the `isbe_verified` column in `il_candidate_tip_mapping.csv`.
`tip_name` is the name TIP stores for the same person where it differs from the ballot name; it is used only for matching.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GP = "https://www.thegreenpapers.com/G26/IL"
S = "Qualified"

def c(name, party, code, inc=False, tip=None, rm=None, note=None, write_in=False, primary="Won"):
    d = {"name": name, "party_code": code, "party": party, "incumbent": inc, "running_mate": rm, "status": S, "primary": "" if write_in else primary,
         "state_account": re.sub(r"[^A-Za-z0-9._-]", "_", tip or name), "source_url": GP, "tip_name": tip}
    if note: d["note"] = note
    if write_in: d["write_in"] = True
    return d

D, R = ("Democratic", "DEM"), ("Republican", "REP")
roster = {
 "captured_at_utc": "2026-10-28T00:00:00Z",
 "sources": {"primary_pending": "Illinois State Board of Elections (HTTP 403 to automated access; not read)", "transcribed_from": GP, "cross_checks": ["OpenFEC /candidates (state IL, election_year 2026)", "TIP export docs/state-packets/IL (race_entries)"]},
 "governor": [
  c("JB Pritzker", *D, inc=True, rm="Christian Mitchell", primary="Renominated (unopposed)"),
  c("Darren Bailey", *R, rm="Aaron B. Del Mar"),
  c("Collin Corbett", "Independent", "IND", rm="Carolyn Schofield", primary="", note="independent; Republican affiliation per Green Papers"),
  c("Taegun Eimer", "Libertarian (write-in)", "WRI", write_in=True), c("Richard Mayers", "Write-in", "WRI", write_in=True), c("Mistry Metroz", "Write-in", "WRI", write_in=True),
  c("Griselda Romero", "Green (write-in)", "WRI", rm="Eyde Arndell", write_in=True, note="removed from the ballot July 14, 2026; now a write-in"),
  c("Elizabeth Sebesta", "Write-in", "WRI", write_in=True), c("Patricia L. Tillman", "Write-in", "WRI", write_in=True), c("Rafael Varela", "Write-in", "WRI", write_in=True),
  c("Mike Vick", "American Solidarity (write-in)", "WRI", write_in=True),
 ],
 "senate": [
  c("Juliana Stratton", *D), c("Don Tracy", *R, tip='Donald R. "Don" Tracy'),
  c("Whitfield Harrington Jr.", "American Center (IL)", "AMC", primary="", note="intends to form the American Center Party (Green Papers)"),
  c("Naomi Craine", "Socialist Workers Party (write-in)", "WRI", write_in=True),
 ],
 "house": {
  "1": [c("Jonathan L. Jackson", *D, inc=True, primary="Renominated"), c("Christian Maxwell", *R), c("Je'Rico J. Brown", "Democratic (write-in)", "WRI", write_in=True)],
  "2": [c("Donna Miller", *D, note="open seat (Robin Kelly ran for the Senate)"), c("Mike Noack", *R, tip='Michael Scott "Mike" Noack')],
  "3": [c("Delia C. Ramirez", *D, inc=True, primary="Renominated"), c("Angel Oakley", *R)],
  "4": [c("Patty García", *D, tip="Patty Garc�a", note="open seat (Jesús 'Chuy' García withdrew his petitions); TIP stores her name with a corrupted character"),
        c("Lupe Castillo", *R), c("Chris Getty", "Independent", "IND", tip='Christopher Roman "Chris" Getty', primary="", note="independent; Democratic affiliation per Green Papers; mayor of Lyons per WBEZ"),
        c("Ed Hershey", "Working Class Party", "WCP", tip='Edward "Ed" Hershey', primary="")],
  "5": [c("Mike Quigley", *D, inc=True, primary="Renominated"), c("Tom Hanson", *R, tip='Tom "Tommy" Hanson', note="Green Papers lists two FEC IDs for Hanson")],
  "6": [c("Sean Casten", *D, inc=True, primary="Renominated"), c("Niki Conforti", *R)],
  "7": [c("La Shawn K. Ford", *D, note="open seat (Danny Davis retiring)"), c("Chad Koppie Sr.", *R)],
  "8": [c("Melissa Bean", *D, tip="Melissa Luburich Bean", note="open seat (Raja Krishnamoorthi ran for the Senate)"), c("Jennifer Davis", *R)],
  "9": [c("Daniel Biss", *D, note="open seat (Jan Schakowsky retiring)"), c("John Elleson", *R)],
  "10": [c("Brad Schneider", *D, inc=True, tip='Bradley Scott "Brad" Schneider', primary="Renominated"), c("Carl Lambrecht", *R), c("Alexandria Keating-Sofiakis", "Green (write-in)", "WRI", write_in=True)],
  "11": [c("Bill Foster", *D, inc=True, tip='G. William "Bill" Foster', primary="Renominated"), c("Jeff Walter", *R, tip='Jeffrey D. "Jeff" Walter')],
  "12": [c("Mike Bost", *R, inc=True, tip='Michael J. "Mike" Bost', primary="Renominated"), c("Julie Fortier", *D)],
  "13": [c("Nikki Budzinski", *D, inc=True, primary="Renominated"), c("Jeff Wilson", *R)],
  "14": [c("Lauren Underwood", *D, inc=True, primary="Renominated"), c("Jim Marter", *R, tip='James Thomas "Jim" Marter')],
  "15": [c("Mary E. Miller", *R, inc=True, primary="Renominated"), c("Jennifer Ann Todd", *D)],
  "16": [c("Darin LaHood", *R, inc=True, tip="Darin McKay LaHood", primary="Renominated"), c("Paul Nolley", *D), c("John Kitover", "Republican (write-in)", "WRI", write_in=True)],
  "17": [c("Eric Sorensen", *D, inc=True, primary="Renominated"), c("Dillan Vancil", *R, tip="Dillan S. Vancil")],
 },
}
out = ROOT / "data/elections/IL/roster.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(roster, indent=1, ensure_ascii=False), encoding="utf-8")
n = len(roster["governor"]) + len(roster["senate"]) + sum(len(v) for v in roster["house"].values())
print("wrote", out, n, "rows;", sum(1 for k in ("governor", "senate") for x in roster[k] if x.get("write_in")) + sum(1 for v in roster["house"].values() for x in v if x.get("write_in")), "write-ins")
