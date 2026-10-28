#!/usr/bin/env python3
"""Asset-first video pack for any state (LLF Production Lock v2.0, docs/production/03_VIDEO_SKILL_AND_SHOT_CONTRACT.md). Assets only: this tool never writes a video.

    python3 tools/video/scene_pack.py init <ST> [--year 2026] [--root productions]     scaffold productions/<year>/<ST>/ and its video/ pack (generic: no other state's facts)
    python3 tools/video/scene_pack.py check <pack_dir>                                  validate a pack against the contract (exit 2 on any problem)
    python3 tools/video/scene_pack.py production <ST> [--year 2026] [--link a,b]        only the folder tree and logs (for a state already in progress)

A pack is: SCRIPT.md FACTS.csv STORYBOARD.md SCENES.csv ASSETS.csv TRANSITIONS.csv CLIP_CAPTURE.md MIDJOURNEY_INSTRUCTIONS.md PREMIERE_ASSEMBLY.md DECISION_LOG.md QA.md.
Order the contract enforces: fact-backed story -> full script LOCKED (SCRIPT.md contains `STATUS: LOCKED`) -> beat timings from the script -> scene assets -> start/end pairs ->
real clip capture guidance -> Premiere handoff. Timing is whatever the script needs (no fixed segment length). Rendering a video is a separate, explicitly authorized task
(`build_video_pack.py --render-video --authorization ...`); nothing here can do it.
"""
import csv, datetime, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_video_pack import spoken_numbers, screen_numbers, close, VIDEO_EXT          # one number parser for both video paths

FILES = ["SCRIPT.md", "FACTS.csv", "STORYBOARD.md", "SCENES.csv", "ASSETS.csv", "TRANSITIONS.csv", "CLIP_CAPTURE.md", "MIDJOURNEY_INSTRUCTIONS.md", "PREMIERE_ASSEMBLY.md", "DECISION_LOG.md", "QA.md"]
SCENES = "scene_id,start_sec,duration_sec,narration,purpose,on_screen_text,fact_ids,asset_type,still_prompt,real_still_url,frame_start_asset_id,frame_end_asset_id,transition_prompt,suggested_clip_url,in_timecode,out_timecode,rights_status,fallback,approval_status".split(",")
ASSETS = "asset_id,scene_id,type,created_by,source_url,local_path,prompt,reference_ids,version,license,capture_date,sha256,factual_overlay,approval_status,aspect_ratio".split(",")
TRANS = "transition_id,start_asset_id,end_asset_id,camera_action,subject_action,duration,mj_prompt,reference_frame_notes,setting_verified_date,status,qa_note".split(",")
FACTS = "fact_id,statement,numbers,source_url,source_date,status,type,never_say,refresh".split(",")
ASSET_TYPES = {"REAL_STILL", "AI_CONCEPT_STILL", "EXACT_DATA_GRAPHIC", "REAL_CLIP", "COMPOSITE"}
RIGHTS = {"CLEARED", "NEEDS_LICENSE", "EDITORIAL_REVIEW", "INTERNAL_REFERENCE_ONLY", "REJECTED", "NOT_APPLICABLE"}
FACT_STATUS = {"VERIFIED", "ATTRIBUTED"}
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d"
MJ_FORBIDDEN = r"\b(text|letters?|numbers?|digits?|logo|logos|poll|percent|map|district|contours?|face|faces|portrait|likeness|politician)\b"
GRADE_WORDS = r"(\bF[-+]?\b|\bfail|\bzero\b|\b0\b)"
WPS_MAX = 3.3
STATE_NAMES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
               "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
               "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
               "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
               "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"}
TREE = ["research", "articles", "graphics", "visuals", "clips", "transitions", "video", "qa", "release", "logs"]


def templates(st, name, year):
    return {
     "SCRIPT.md": f"# {name} {year}: video script\n\nSTATUS: DRAFT\n<!-- Change to `STATUS: LOCKED (approved by <owner name> on <date>)` only after the owner approves every line. Scene art may not be made before that. -->\n\n## Story and hook\nMost compelling sourced story (from the checked articles' CLAIMS.csv): <fill>\nHook options (each a verified fact): <fill>\n\n## Script (one block per beat; duration follows the speech, not a template)\n<fill>\n",
     "STORYBOARD.md": f"# {name} {year}: storyboard\n\nBeats, durations from the locked script, and for each beat the visual choice (REAL_STILL, AI_CONCEPT_STILL, EXACT_DATA_GRAPHIC, REAL_CLIP, COMPOSITE). Real people appear as real licensed stills or real clips, never generated likenesses.\n\n<fill>\n",
     "CLIP_CAPTURE.md": f"# {name} {year}: real clip capture list\n\nA public URL is not permission. For each clip: scene, source URL, why it works, inspected in/out only if actually seen, rights status, fallback still. The owner chooses and captures.\n\n| scene | url | why | in | out | rights_status | fallback |\n|---|---|---|---|---|---|---|\n",
     "MIDJOURNEY_INSTRUCTIONS.md": f"# {name} {year}: Midjourney instructions\n\nPrimary use: animated transitions between two prepared images (start asset and end asset, same aspect ratio). Single-image animation is allowed where useful. Midjourney must not be asked for text, numbers, polls, maps, TIP grades, logos or politicians' faces; all of that is a deterministic overlay added afterward.\nConfirm the current start/end frame interface and settings against Midjourney's official documentation on production day and record the date in TRANSITIONS.csv `setting_verified_date`.\n\n<fill>\n",
     "PREMIERE_ASSEMBLY.md": f"# {name} {year}: Premiere Pro assembly notes\n\nLayer order, per scene: base clip or still, transition clip (paired Midjourney animation), deterministic overlays (names, numbers, maps, TIP grades, dates), captions, credits and disclosures, music, narration. No exported video is part of this pack.\n\n<fill>\n",
     "DECISION_LOG.md": f"# {name} {year}: video decision log (append-only)\n\n| date | decision | reason | by |\n|---|---|---|---|\n",
     "QA.md": f"# {name} {year}: video QA\n\nARTICLE_AUTHOR: <fill>\nFACTCHECK_REVIEWER: <fill>\n<!-- The reviewer must be a different person or agent than the author. -->\n\n- [ ] every fact has a source, date and status (VERIFIED or ATTRIBUTED)\n- [ ] market and poll facts carry dates\n- [ ] ungraded TIP records are shown as not graded, never as a poor grade\n- [ ] every clip has an explicit rights status; none is called cleared without a written basis\n- [ ] no generated candidate likeness; AI art and synthetic narration are disclosed\n- [ ] owner approved the locked script\n",
    }


def write_csv(path, cols, rows=()):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)


def production_tree(st, year, root, link=None):
    base = Path(root) / str(year) / st
    for d in TREE:
        (base / d).mkdir(parents=True, exist_ok=True)
        if not any((base / d).iterdir()):
            (base / d / ".gitkeep").write_text("", encoding="utf-8")        # keep the folder tree in git
    for n, title in (("WORKFLOW_LOG.md", "workflow log"), ("DECISIONS.md", "decisions")):
        f = base / "logs" / n
        if not f.exists():
            f.write_text(f"# {STATE_NAMES.get(st, st)} {year}: {title} (append-only)\n\n| date | stage | input | output | actor | skill versions | note |\n|---|---|---|---|---|---|---|\n" if n.startswith("WORK") else f"# {STATE_NAMES.get(st, st)} {year}: {title} (append-only)\n\n| date | decision | reason | by |\n|---|---|---|---|\n", encoding="utf-8")
    if link:
        (base / "README.md").write_text(f"# {STATE_NAMES.get(st, st)} {year}: production folder\n\nWork already done for this state is kept where it was produced and is NOT moved: " + ", ".join(f"`{x}`" for x in link) + ". New research, articles, visuals and video assets go in the folders here.\n", encoding="utf-8")
    return base


def init(st, year="2026", root="productions"):
    st = st.upper()
    if st not in STATE_NAMES:
        raise SystemExit(f"unknown state code {st}")
    name = STATE_NAMES[st]
    base = production_tree(st, year, ROOT / root if not Path(root).is_absolute() else root)
    vid = base / "video"
    for fn, text in templates(st, name, year).items():
        if not (vid / fn).exists():
            (vid / fn).write_text(text, encoding="utf-8")
    for fn, cols in (("SCENES.csv", SCENES), ("ASSETS.csv", ASSETS), ("TRANSITIONS.csv", TRANS), ("FACTS.csv", FACTS)):
        if not (vid / fn).exists():
            write_csv(vid / fn, cols)
    return vid


def rows(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def check(d):
    d = Path(d)
    P = []
    for fn in FILES:
        if not (d / fn).exists():
            P.append(f"missing file {fn}")
    if P:
        return P
    vids = [x for x in d.rglob("*") if x.suffix.lower() in VIDEO_EXT]
    if vids:
        P.append("video file in the pack (assets only; an MP4 needs an explicit render request): " + ", ".join(x.name for x in vids))
    for fn in FILES:
        if "<fill>" in (d / fn).read_text(encoding="utf-8"):
            P.append(f"unfilled placeholder in {fn}")
    script = (d / "SCRIPT.md").read_text(encoding="utf-8")
    locked = re.search(r"^STATUS:\s*LOCKED\b", script, flags=re.M) is not None
    facts = {f["fact_id"]: f for f in rows(d / "FACTS.csv")}
    scenes, assets, trans = rows(d / "SCENES.csv"), rows(d / "ASSETS.csv"), rows(d / "TRANSITIONS.csv")
    aid = {a["asset_id"]: a for a in assets}
    for fid, f in facts.items():
        if f["status"] not in FACT_STATUS:
            P.append(f"fact {fid}: status must be VERIFIED or ATTRIBUTED")
        if not f["source_url"].startswith("http") or not f["source_date"]:
            P.append(f"fact {fid}: needs a real source URL and a source date")
        if f["type"] == "market" and (not f["source_date"] or f["refresh"].lower() != "true"):
            P.append(f"fact {fid}: a market observation needs its date and refresh=true (a quote is never presented as live)")
        if f["type"] == "poll" and not re.search(MONTH, f["statement"]):
            P.append(f"fact {fid}: a poll fact needs its field dates in the statement")
    if (scenes or assets) and not locked:
        P.append("scene or asset rows exist but SCRIPT.md is not `STATUS: LOCKED`: the script is approved before scene art")
    if locked:
        qa = (d / "QA.md").read_text(encoding="utf-8")
        au, rv = re.search(r"^ARTICLE_AUTHOR:\s*(.+)$", qa, flags=re.M), re.search(r"^FACTCHECK_REVIEWER:\s*(.+)$", qa, flags=re.M)
        if not au or not rv or not au.group(1).strip() or not rv.group(1).strip():
            P.append("locked script: QA.md must record ARTICLE_AUTHOR and FACTCHECK_REVIEWER")
        elif au.group(1).strip().lower() == rv.group(1).strip().lower():
            P.append("locked script: the fact-check reviewer must differ from the article author")
    names = set()
    for f in facts.values():
        names |= set(re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", f["statement"]))
    t = 0.0
    for s in scenes:
        sid = s["scene_id"]
        try:
            st_, du = float(s["start_sec"]), float(s["duration_sec"])
        except ValueError:
            P.append(f"scene {sid}: start_sec and duration_sec must be numbers")
            continue
        if du <= 0:
            P.append(f"scene {sid}: duration must be positive")
        if abs(st_ - t) > 0.05:
            P.append(f"scene {sid}: starts at {st_:g}s but the previous scene ends at {t:g}s")
        t = st_ + du
        words = len(s["narration"].split())
        if words > du * WPS_MAX + 1:
            P.append(f"scene {sid}: {words} words do not fit {du:g}s of speech")
        at = s["asset_type"]
        if at not in ASSET_TYPES:
            P.append(f"scene {sid}: asset_type must be one of {sorted(ASSET_TYPES)}")
        if at == "AI_CONCEPT_STILL" and not s["still_prompt"].strip():
            P.append(f"scene {sid}: an AI concept still needs a still_prompt")
        if at == "REAL_STILL" and not s["real_still_url"].startswith("http"):
            P.append(f"scene {sid}: a real still needs its source URL")
        if at == "REAL_CLIP":
            if not s["suggested_clip_url"].startswith("http"):
                P.append(f"scene {sid}: a real clip needs a source URL")
            if not s["fallback"].strip():
                P.append(f"scene {sid}: a real clip needs a fallback still")
        if at == "EXACT_DATA_GRAPHIC" and not s["fact_ids"].strip():
            P.append(f"scene {sid}: an exact data graphic needs fact IDs")
        if at == "COMPOSITE" and not (s["still_prompt"].strip() or s["real_still_url"].strip()):
            P.append(f"scene {sid}: a composite needs a still prompt or a real still")
        if at == "REAL_CLIP" and s["rights_status"] not in RIGHTS - {"NOT_APPLICABLE"}:
            P.append(f"scene {sid}: a real clip needs an explicit rights status")
        if s["rights_status"] and s["rights_status"] not in RIGHTS:
            P.append(f"scene {sid}: unknown rights status {s['rights_status']}")
        if s["rights_status"] == "CLEARED":
            if not any(a["scene_id"] == sid and a["license"].strip() for a in assets):
                P.append(f"scene {sid}: CLEARED needs the written license basis in ASSETS.csv (a public clip is not a permitted clip)")
        ids = [x.strip() for x in s["fact_ids"].replace(";", ",").split(",") if x.strip()]
        for fid in ids:
            if fid not in facts:
                P.append(f"scene {sid}: unknown fact {fid}")
        allowed = [float(x.replace(",", "")) for fid in ids if fid in facts for x in re.findall(r"\d[\d,]*\.?\d*", facts[fid]["numbers"])]
        for v in spoken_numbers(s["narration"]):
            if not any(close(v, a) for a in allowed):
                P.append(f"scene {sid}: narration says {v:g}, not in its facts")
        for v in screen_numbers([s["on_screen_text"]]):
            if not any(close(v, a) for a in allowed):
                P.append(f"scene {sid}: on-screen number {v:g} is not in its facts")
        if any(facts[fid]["type"] == "tip_grade" and "not graded" in facts[fid]["statement"].lower() for fid in ids if fid in facts) and re.search(GRADE_WORDS, s["on_screen_text"] + " " + s["narration"], flags=re.I):
            P.append(f"scene {sid}: a not-graded TIP record must not be shown as a failing grade or a zero")
        if at == "AI_CONCEPT_STILL":
            for n in names:
                if n in s["still_prompt"]:
                    P.append(f"scene {sid}: the AI still prompt names a real person ({n}); real people appear as real stills or clips")
            if re.search(r"\b(portrait of|photo of|face of|likeness)\b", s["still_prompt"], flags=re.I):
                P.append(f"scene {sid}: the AI still prompt asks for a person's likeness")
        a, b = s["frame_start_asset_id"].strip(), s["frame_end_asset_id"].strip()
        if a or b:
            if not (a in aid and b in aid):
                P.append(f"scene {sid}: start/end frame IDs must both exist in ASSETS.csv")
            elif not any(x["start_asset_id"] == a and x["end_asset_id"] == b for x in trans):
                P.append(f"scene {sid}: the start/end pair has no row in TRANSITIONS.csv")
    for a in assets:
        if a["type"] not in ASSET_TYPES:
            P.append(f"asset {a['asset_id']}: type must be one of {sorted(ASSET_TYPES)}")
        if a["type"] in ("REAL_STILL", "REAL_CLIP") and not (a["source_url"].startswith("http") and a["license"].strip()):
            P.append(f"asset {a['asset_id']}: a real asset needs a source URL and a license or rights note")
        if a["type"] == "AI_CONCEPT_STILL" and not a["prompt"].strip():
            P.append(f"asset {a['asset_id']}: an AI still needs its prompt")
        lp = a["local_path"].strip()
        if lp:                                                  # versioned assets: a listed file must exist and carry a matching sha256
            f = (d / lp) if not Path(lp).is_absolute() else Path(lp)
            if not f.exists():
                P.append(f"asset {a['asset_id']}: local_path {lp} does not exist")
            elif not a["sha256"].strip():
                P.append(f"asset {a['asset_id']}: a local file needs its sha256 (versioned assets)")
            elif hashlib.sha256(f.read_bytes()).hexdigest() != a["sha256"].strip().lower() and not hashlib.sha256(f.read_bytes()).hexdigest().startswith(a["sha256"].strip().lower()):
                P.append(f"asset {a['asset_id']}: sha256 does not match the file (the asset changed; bump the version)")
    for x in trans:
        tid = x["transition_id"]
        for k in ("start_asset_id", "end_asset_id"):
            if x[k] not in aid:
                P.append(f"transition {tid}: {k} {x[k]!r} is not in ASSETS.csv")
        if x["start_asset_id"] == x["end_asset_id"]:
            P.append(f"transition {tid}: start and end must be different assets")
        if x["start_asset_id"] in aid and x["end_asset_id"] in aid:
            ra, rb = aid[x["start_asset_id"]]["aspect_ratio"].strip(), aid[x["end_asset_id"]]["aspect_ratio"].strip()
            if not ra or ra != rb:
                P.append(f"transition {tid}: start and end assets need the same aspect ratio (got {ra or 'none'} and {rb or 'none'})")
        if not x["mj_prompt"].strip():
            P.append(f"transition {tid}: needs a Midjourney prompt")
        if re.search(MJ_FORBIDDEN, x["mj_prompt"] + " " + x["camera_action"] + " " + x["subject_action"], flags=re.I):
            P.append(f"transition {tid}: the prompt asks Midjourney for text, numbers, maps, logos or a person; those are deterministic overlays")
        if x["status"].upper() in ("READY", "APPROVED") and not re.match(r"\d{4}-\d{2}-\d{2}$", x["setting_verified_date"].strip()):
            P.append(f"transition {tid}: a ready transition needs setting_verified_date (settings checked against Midjourney's current documentation)")
    return P


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 1
    cmd = a[0]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    if cmd == "init":
        vid = init(a[1], opt("--year", "2026"), opt("--root", "productions"))
        print("scaffolded", vid)
        return 0
    if cmd == "production":
        base = production_tree(a[1].upper(), opt("--year", "2026"), ROOT / opt("--root", "productions"), [x for x in opt("--link", "").split(",") if x] or None)
        print("folder tree", base)
        return 0
    if cmd == "check":
        probs = check(a[1])
        for p in probs:
            print("PROBLEM:", p)
        print("pack valid" if not probs else f"{len(probs)} problem(s)")
        return 2 if probs else 0
    print("unknown command", cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
