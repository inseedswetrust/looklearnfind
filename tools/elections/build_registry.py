#!/usr/bin/env python3
"""Build the candidate registry (the data behind /find/candidates/) from the per-state election files and the TIP export.

    python tools/elections/build_registry.py            # every state that has data/elections/<ST>/candidates.json
    python tools/elections/build_registry.py MI NY      # just these
    python tools/elections/build_registry.py --check    # build in memory, fail if data/candidates/ differs or validation fails

Writes data/candidates/<ST>.json, data/candidates/races.json and productions/2026/<ST>/gaps.csv. Pure function of repository files: no network, no wall clock,
so running it twice gives the same bytes. Spec: docs/election-build/CANDIDATE_DIRECTORY_SPEC.md.

TIP owns person-level facts (name, party, incumbency, photo, links, grades). This file keeps a few ballot facts and a link to the TIP profile; grades are not copied
(only how many of the six issues are graded). There are no per-candidate pages on LookLearnFind.
"""
import csv, io, json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import elections  # noqa: E402  (STATES and PLET live there)

D = ROOT / "data/elections"
OUT = ROOT / "data/candidates"
SUFFIX = {"jr", "sr", "ii", "iii", "iv"}
OFFICE_ORDER = {"governor": 0, "senate": 1, "house": 2}
SCHEMA = 1


def _j(p, default=None):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def ascii_slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def split_name(name):
    words = [w for w in re.sub(r'"[^"]*"', "", name).replace(",", " ").split() if w]
    surname_words = [w for w in words if w.lower().strip(".") not in SUFFIX]
    surname = surname_words[-1] if surname_words else name
    given = words[0] if words else ""
    return given, surname


def story_index():
    """slug -> body text for every published report, to find which stories mention a candidate's TIP profile."""
    out = {}
    for p in sorted((ROOT / "content/learn").glob("*.html")):
        out[p.stem] = p.read_text(encoding="utf-8")
    return out


def state_registry(code, stories):
    st = elections.STATES[code]
    cj = _j(D / code / "candidates.json")
    if not cj:
        return None
    roster = _j(D / code / "roster.json", {})
    tipc = {}
    for r in _j(D / code / "tip_export/candidates.json", []):
        tipc[r["fec_candidate_id"]] = r
    entries = {}
    for r in _j(D / code / "tip_export/race_entries.json", []):
        entries.setdefault(r.get("fec_candidate_id"), []).append(r)
    summ = _j(D / code / "tip_export/summary.json", {})
    official = bool(st.get("official", True))  # Florida predates the flag and is official
    limitations = ""
    if not official:
        limitations = "The state board's own candidate list could not be read, so this roster is transcribed from Green Papers and cross-checked against OpenFEC and TIP. It is not an official or certified list and may omit late changes."
    cands, seen = [], {}
    for c in cj["candidates"]:
        office = c["office"]
        dm = re.search(r"house-(\d+)", c["race"])
        district = int(dm.group(1)) if dm else None
        given, surname = split_name(c["name"])
        letter = {"governor": "G", "senate": "S", "house": "H"}[office]
        base = f"{code}-{letter}{district:02d}" if district is not None else f"{code}-{letter}"
        lid = f"{base}-{ascii_slug(surname)}-{ascii_slug(given)}"
        n = seen.get(lid, 0)
        seen[lid] = n + 1
        if n:
            lid += f"-{n + 1}"
        race_key = {"governor": f"2026-GOV-{code}", "senate": f"2026-S-{code}"}.get(office) or f"2026-H-{code}-{district:02d}"
        tip = c.get("tip") or {}
        grades = (tip.get("grades") or {})
        graded = sum(1 for g in grades.values() if g.get("state") != "not_graded") if tip.get("http_status") == 200 else None
        te = tipc.get(c.get("fec_candidate_id")) or tipc.get(c.get("tip_page_id")) or {}
        ents = entries.get(c.get("fec_candidate_id")) or entries.get(c.get("tip_page_id")) or []
        entry_status = sorted({x.get("status") for x in ents if x.get("race_key") == race_key}) or None
        site = te.get("official_website_url") or te.get("bp_official_website") or te.get("bp_campaign_website")
        gaps = []
        if tip.get("http_status") != 200:
            gaps.append("tip_profile_missing")
        elif entry_status and entry_status != ["active"]:
            gaps.append("tip_entry_review")
        elif not entry_status and tip.get("http_status") == 200:
            gaps.append("tip_entry_missing")
        if tip.get("http_status") == 200:
            if not te.get("photo_filename"):
                gaps.append("tip_photo_missing")
            if not te.get("ballotpedia_url") and not site:
                gaps.append("tip_links_missing")
            if te.get("verification_status") in (None, "needs_review"):
                gaps.append("profile_unverified")
        tid = c.get("tip_page_id") or c.get("fec_candidate_id")
        cover = [slug for slug, body in stories.items() if tid and f"theissuesparty.org/candidates/{tid}" in body]
        llf_path = {"governor": "governor/", "senate": "senate/"}.get(office) or f"house/{district}/"
        cands.append({
            "llf_id": lid,
            "name": c["name"],
            "sort_name": f"{surname}, {given}",
            "office": office,
            "district": district,
            "race_key": race_key,
            "party": {"code": c["party_code"], "letter": elections.PLET.get(c["party_code"], "?"), "label": c["party"]},
            "incumbent": bool(c.get("incumbent")),
            "running_mate": c.get("running_mate"),
            "ballot": {"status": (c.get("status") or "Qualified").lower(), "write_in": bool(c.get("write_in")), "note": c.get("note")},
            "ids": {"fec": c.get("fec_candidate_id"), "tip_slug": c.get("tip_page_id")},
            "tip": {"url": tip.get("url") if tip.get("http_status") == 200 else None, "http": tip.get("http_status"), "checked_at": tip.get("checked_at"),
                    "graded_count": graded, "profile_status": te.get("verification_status"), "entry_status": entry_status},
            "tip_photo": bool(te.get("photo_filename")) if te else False,
            "links": {"state_record": c.get("state_url"), "ballotpedia": te.get("ballotpedia_url"), "website": site},
            "llf_race_path": f"/elections/2026/{st['slug']}/{llf_path}",
            "gaps": gaps,
            "coverage": cover,
        })
    cands.sort(key=lambda r: (OFFICE_ORDER[r["office"]], r["district"] or 0, r["sort_name"].lower()))
    return {
        "schema": SCHEMA, "state": code, "state_name": st["name"], "state_slug": st["slug"], "cycle": 2026,
        "built_from": {"roster_captured_at": roster.get("captured_at_utc"), "candidates_as_of": cj.get("as_of_utc"), "tip_export_as_of": summ.get("as_of_utc")},
        "roster": {"basis": "official" if official else "secondary", "label": st["record_label"], "limitations": limitations},
        "candidates": cands,
    }


def races_index(regs):
    races = {}
    for reg in regs:
        for c in reg["candidates"]:
            r = races.setdefault(c["race_key"], {"race_key": c["race_key"], "state": reg["state"], "office": c["office"], "district": c["district"],
                                                 "llf_url": c["llf_race_path"], "tip_url": f"https://theissuesparty.org/races/{c['race_key']}",
                                                 "roster_basis": reg["roster"]["basis"], "candidate_ids": []})
            r["candidate_ids"].append(c["llf_id"])
    return [races[k] for k in sorted(races)]


FORBIDDEN = re.compile(r"\$\s?\d|probab|poll|market price|odds", re.I)
REQ = ("llf_id", "name", "sort_name", "office", "district", "race_key", "party", "incumbent", "ballot", "ids", "tip", "links", "llf_race_path", "gaps", "coverage")


def validate(regs, races):
    errs = []
    all_ids, keys = set(), set()
    race_keys = {r["race_key"] for r in races}
    for reg in regs:
        if reg["roster"]["basis"] != "official" and not reg["roster"]["limitations"]:
            errs.append(f"{reg['state']}: unofficial roster without limitations text")
        for c in reg["candidates"]:
            for k in REQ:
                if k not in c:
                    errs.append(f"{c.get('llf_id')}: missing {k}")
            if c["llf_id"] in all_ids:
                errs.append(f"duplicate llf_id {c['llf_id']}")
            all_ids.add(c["llf_id"])
            k = (reg["state"], c["office"], c["district"], c["party"]["code"], c["name"])
            if k in keys:
                errs.append(f"duplicate person {k}")
            keys.add(k)
            if c["race_key"] not in race_keys:
                errs.append(f"{c['llf_id']}: race {c['race_key']} not in races")
            if c["tip"]["url"] and c["tip"]["http"] != 200:
                errs.append(f"{c['llf_id']}: TIP url without HTTP 200")
            if FORBIDDEN.search(json.dumps({"name": c["name"], "ballot": c["ballot"], "links": c["links"]}, ensure_ascii=False)):
                errs.append(f"{c['llf_id']}: a public field looks like a market, poll or money figure")
    return errs


def dump(o):
    return json.dumps(o, indent=1, ensure_ascii=False) + "\n"


def gaps_csv(reg):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["llf_id", "name", "office", "district", "party", "gap", "action"])
    act = {"tip_profile_missing": "Add to the TIP fix list (owner approves the write), then re-export",
           "tip_entry_missing": "Add a race entry on TIP (owner approves the write), then re-export",
           "tip_entry_review": "Owner promotes the entry from review to active, or re-export if already promoted",
           "tip_photo_missing": "Report only: TIP enrichment; LLF keeps no copy",
           "tip_links_missing": "Report only: TIP enrichment; LLF keeps no copy",
           "profile_unverified": "Editor information only"}
    for c in reg["candidates"]:
        for g in c["gaps"]:
            w.writerow([c["llf_id"], c["name"], c["office"], c["district"] or "", c["party"]["code"], g, act[g]])
    return buf.getvalue()


def build(codes):
    stories = story_index()
    regs = [r for r in (state_registry(c, stories) for c in codes) if r]
    races = races_index(regs)
    return regs, races


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    codes = [a.upper() for a in args] or [c for c in elections.STATES if (D / c / "candidates.json").exists()]
    regs, races = build(codes)
    errs = validate(regs, races)
    files = {OUT / f"{r['state']}.json": dump(r) for r in regs}
    if not args:
        files[OUT / "races.json"] = dump(races)
    gaps = {ROOT / f"productions/2026/{r['state']}/gaps.csv": gaps_csv(r) for r in regs}
    if "--check" in sys.argv:
        bad = [str(p.relative_to(ROOT)) for p, t in {**files, **gaps}.items() if not p.exists() or p.read_text(encoding="utf-8") != t]
        for e in errs:
            print("ERROR", e)
        for b in bad:
            print("STALE", b)
        print("registry check:", "FAIL" if errs or bad else "OK")
        sys.exit(1 if errs or bad else 0)
    if errs:
        for e in errs:
            print("ERROR", e)
        sys.exit(1)
    OUT.mkdir(parents=True, exist_ok=True)
    for p, t in {**files, **gaps}.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t, encoding="utf-8", newline="\n")
    for r in regs:
        gp = sum(len(c["gaps"]) for c in r["candidates"])
        print(f"{r['state']}: {len(r['candidates'])} candidates, roster {r['roster']['basis']}, {gp} gap flags, "
              f"{sum(1 for c in r['candidates'] if c['tip']['url'])} linked to TIP")


if __name__ == "__main__":
    main()
