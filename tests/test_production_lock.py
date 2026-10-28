"""Acceptance tests for the LLF Production Lock v2.0 install (docs/production/04_CLAUDE_INSTALL_AND_TESTS.md tests a to i, plus install checks).
Run: python3 -m unittest tests/test_production_lock.py -v   (no network, no browser, no video is ever produced)."""
import copy, csv, json, re, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/video")); sys.path.insert(0, str(ROOT / "tools/workflow")); sys.path.insert(0, str(ROOT / "tools/qa"))
import scene_pack as sp
import transitions as tr
import skill_manifest
import factcheck_gate as gate

PY = sys.executable
FLORIDA_WORDS = ["Florida", "Moody", "Nixon", "Donalds", "Jolly", "Castor", "Moskowitz", "Wasserman", "FL-", "83¢", "Tallahassee"]
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}


def write_pack(d, **over):
    """A minimal valid, generic pack. Keyword overrides replace a whole file's text or row list."""
    d = Path(d); d.mkdir(parents=True, exist_ok=True)
    files = {
        "SCRIPT.md": "# Example 2026\n\nSTATUS: LOCKED (approved by Owner on 2026-10-28)\n\nScript text.\n",
        "STORYBOARD.md": "# Storyboard\nbeats\n", "CLIP_CAPTURE.md": "# Clips\n", "MIDJOURNEY_INSTRUCTIONS.md": "# MJ\nchecked 2026-10-28\n", "PREMIERE_ASSEMBLY.md": "# Premiere\nlayers\n",
        "DECISION_LOG.md": "# Decisions\n", "QA.md": "ARTICLE_AUTHOR: Drafter One\nFACTCHECK_REVIEWER: Reviewer Two\n",
    }
    facts = [
        ["F1", "Example poll: A 49, B 45 among 800 likely voters, fielded Oct 12 to 19", "49;45;800", "https://example.org/poll", "2026-10-21", "ATTRIBUTED", "poll", "", "true"],
        ["F2", "Contract X last traded 90 cents on 2026-10-23 (party contract)", "90", "https://example.org/market", "2026-10-23", "ATTRIBUTED", "market", "live odds", "true"],
        ["F3", "Candidate C has no graded issues (not graded)", "", "https://example.org/tip/C", "2026-10-28", "VERIFIED", "tip_grade", "failing grade", "false"],
    ]
    scenes = [
        ["S1", "0", "6", "A poll shows forty-nine to forty-five.", "poll", "49–45", "F1", "EXACT_DATA_GRAPHIC", "", "", "", "", "", "", "", "", "NOT_APPLICABLE", "", "DRAFT"],
        ["S2", "6", "4.5", "Candidate C has no graded issues.", "grades", "Not graded", "F3", "REAL_STILL", "", "https://example.org/photo", "", "", "", "", "", "", "NOT_APPLICABLE", "", "DRAFT"],
        ["S3", "10.5", "7", "An empty ballot box waits.", "mood", "", "", "AI_CONCEPT_STILL", "empty wooden ballot box, paper-cut collage, dawn", "", "A1", "A2", "slow push in", "", "", "", "NOT_APPLICABLE", "", "DRAFT"],
        ["S4", "17.5", "5", "The candidate speaks.", "clip", "", "", "REAL_CLIP", "", "", "", "", "", "https://example.org/clip", "", "", "NEEDS_LICENSE", "genuine still of the speaker", "DRAFT"],
    ]
    assets = [
        ["R1", "S2", "REAL_STILL", "owner", "https://example.org/photo", "", "", "", "1", "public domain (US government work)", "2026-10-28", "", "", "DRAFT", "9:16"],
        ["A1", "S3", "AI_CONCEPT_STILL", "ChatGPT", "", "", "empty wooden ballot box, paper-cut collage, dawn", "", "1", "generated", "2026-10-28", "", "", "DRAFT", "9:16"],
        ["A2", "S3", "AI_CONCEPT_STILL", "ChatGPT", "", "", "empty wooden ballot box, paper-cut collage, midday", "", "1", "generated", "2026-10-28", "", "", "DRAFT", "9:16"],
        ["C1", "S4", "REAL_CLIP", "owner", "https://example.org/clip", "", "", "", "1", "NEEDS_LICENSE: owner to request", "2026-10-28", "", "", "DRAFT", "16:9"],
    ]
    trans = [["T1", "A1", "A2", "slow push in", "light shifts from dawn to midday", "5", "gentle morph between two paper-cut ballot box scenes", "same composition", "2026-10-28", "READY", ""]]
    tables = {"FACTS.csv": (sp.FACTS, facts), "SCENES.csv": (sp.SCENES, scenes), "ASSETS.csv": (sp.ASSETS, assets), "TRANSITIONS.csv": (sp.TRANS, trans)}
    for k, v in over.items():
        if k in files:
            files[k] = v
        else:
            tables[k] = (tables[k][0], v)
    for fn, text in files.items():
        (d / fn).write_text(text, encoding="utf-8")
    for fn, (cols, rows) in tables.items():
        sp.write_csv(d / fn, cols, rows)
    return d


def mutate(table, fn):
    d = tempfile.mkdtemp()
    base = write_pack(Path(d) / "base")
    rows = sp.rows(base / table)
    out = [[r[c] for c in {"FACTS.csv": sp.FACTS, "SCENES.csv": sp.SCENES, "ASSETS.csv": sp.ASSETS, "TRANSITIONS.csv": sp.TRANS}[table]] for r in rows]
    cols = {"FACTS.csv": sp.FACTS, "SCENES.csv": sp.SCENES, "ASSETS.csv": sp.ASSETS, "TRANSITIONS.csv": sp.TRANS}[table]
    fn(out, cols)
    return sp.check(write_pack(Path(d) / "m", **{table: out}))


def has(probs, text):
    return any(text in p for p in probs)


class TestInstall(unittest.TestCase):
    def test_package_files_are_installed_verbatim(self):
        for f in ["00_READ_FIRST.md", "01_END_TO_END_WORKFLOW.md", "02_AGENT_SKILL_MAP.md", "03_VIDEO_SKILL_AND_SHOT_CONTRACT.md", "04_CLAUDE_INSTALL_AND_TESTS.md", "05_MICHIGAN_KICKOFF.md",
                  "06_DECISION_LOG.md", "07_STARTER_PROMPT_FOR_CLAUDE.md", "ROOT_CLAUDE_POINTER.txt", "README.md", "INSTALL_REPORT.md", "DATA_ACCESS_LIMITATIONS.md", "SKILL_MANIFEST.json",
                  "templates/SCENES.csv", "templates/ASSETS.csv", "templates/TRANSITIONS.csv", "skills/llf-video-director.PACKAGE_ORIGINAL.md"]:
            self.assertTrue((ROOT / "docs/production" / f).exists(), f)
        self.assertIn("NEVER create/render a preview or final video/MP4", (ROOT / "docs/production/00_READ_FIRST.md").read_text(encoding="utf-8"))

    def test_session_startup_pointers(self):
        c = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("docs/production/00_READ_FIRST.md", c)
        self.assertIn("MANDATORY WORKFLOW", c)
        self.assertLess(c.index("MANDATORY WORKFLOW"), c.index("Static site built by"))                    # first thing a session reads
        idx = (ROOT / "docs/election-build/INDEX.md").read_text(encoding="utf-8")
        self.assertIn("docs/production/README.md", idx)
        self.assertIn("docs/production/", (ROOT / "docs/election-build/AGENT_RUNBOOK.md").read_text(encoding="utf-8"))

    def test_one_video_entry_point(self):
        d = {}
        for f in (ROOT / ".claude/skills").glob("*/SKILL.md"):
            t = f.read_text(encoding="utf-8")
            d[f.parent.name] = re.search(r"^description:\s*(.+)$", t, flags=re.M).group(1)
        self.assertIn("llf-video-director", d)
        self.assertTrue(d["llf-video-storyboard"].startswith("LEGACY ALIAS"))
        self.assertIn("sub-procedure", d["llf-footage-scout"])
        video = [n for n, x in d.items() if re.search(r"video", x, flags=re.I) and not x.startswith("LEGACY") and "sub-procedure" not in x and n not in ("llf-publication-qa", "llf-article-format", "workflow-retrospective", "llf-story-scout")]
        self.assertEqual(video, ["llf-video-director"])

    def test_skill_manifest_is_current_and_every_skill_has_a_version(self):
        rows = skill_manifest.scan()
        self.assertEqual([r["name"] for r in rows if not r["version"]], [])
        r = subprocess.run([PY, str(ROOT / "tools/qa/skill_manifest.py"), "--check"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(len(rows), 12)

    def test_the_illinois_discovery_material_is_untouched_and_the_limitation_is_recorded(self):
        self.assertIn("HTTP 403", (ROOT / "docs/production/DATA_ACCESS_LIMITATIONS.md").read_text(encoding="utf-8"))
        self.assertIn("not** an official or complete list", (ROOT / "docs/illinois/DATA_ACCESS_LIMITATIONS.md").read_text(encoding="utf-8"))
        roster = json.loads((ROOT / "data/elections/IL/roster.json").read_text(encoding="utf-8"))
        self.assertIn("403", roster["sources"]["primary_pending"])
        n = len(roster["governor"]) + len(roster["senate"]) + sum(len(v) for v in roster["house"].values())
        self.assertEqual(n, 54)


class TestAcceptance(unittest.TestCase):
    def test_a_michigan_intake_contains_no_florida_entities(self):
        with tempfile.TemporaryDirectory() as d:
            sp.init("MI", "2026", d)
            text = ""
            for f in Path(d).rglob("*"):
                if f.is_file():
                    text += f.read_text(encoding="utf-8")
            self.assertIn("Michigan", text)
            for w in FLORIDA_WORDS:
                self.assertNotIn(w, text, w)
            self.assertTrue({"research", "articles", "graphics", "visuals", "clips", "transitions", "video", "qa", "release", "logs"} <= {p.name for p in (Path(d) / "2026" / "MI").iterdir()})

    def test_b_default_builders_produce_no_video(self):
        with tempfile.TemporaryDirectory() as d:
            sp.init("MI", "2026", d)
            write_pack(Path(d) / "pack")
            self.assertEqual(sp.check(Path(d) / "pack"), [])
            self.assertEqual([p for p in Path(d).rglob("*") if p.suffix.lower() in VIDEO_EXT], [])
            out = Path(d) / "legacy"
            r = subprocess.run([PY, str(ROOT / "tools/video/build_video_pack.py"), str(ROOT / "data/video/fl_2026_state_of_the_race.json"), "--no-render", "--out", str(out)], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual([p for p in out.rglob("*") if p.suffix.lower() in VIDEO_EXT], [])

    def test_b_a_render_needs_the_owners_explicit_words(self):
        spec = str(ROOT / "data/video/fl_2026_state_of_the_race.json")
        log = ROOT / "docs/production/RENDER_REQUESTS.log"
        existed = log.exists()
        try:
            for extra in ([], ["--authorization", "ok"]):
                r = subprocess.run([PY, str(ROOT / "tools/video/build_video_pack.py"), spec, "--render-video"] + extra, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(r.returncode, 2)
                self.assertIn("REFUSED", r.stdout)
            self.assertFalse(log.exists() and not existed)
            r = subprocess.run([PY, str(ROOT / "tools/video/build_video_pack.py"), spec, "--render-video", "--authorization", "Owner: please render the Florida video now"], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 3)
            self.assertIn("nothing was rendered", r.stdout)
        finally:
            if not existed and log.exists():
                log.unlink()

    def test_b_the_legacy_builder_and_spec_template_are_fenced(self):
        spec = json.loads((ROOT / "data/video/fl_2026_state_of_the_race.json").read_text(encoding="utf-8"))
        spec["state"] = "MI"
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "mi.json"
            f.write_text(json.dumps(spec), encoding="utf-8")
            r = subprocess.run([PY, str(ROOT / "tools/video/build_video_pack.py"), str(f), "--no-render", "--out", str(Path(d) / "o")], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 2)
            self.assertIn("Florida example", r.stdout)
        r = subprocess.run([PY, str(ROOT / "tools/video/init_state_spec.py"), "MI"], capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("scene_pack.py init", r.stdout + r.stderr)
        self.assertFalse((ROOT / "data/video/mi_2026_state_of_the_race.json").exists())

    def test_script_led_timing_has_no_fixed_segment_length(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_pack(d)
            self.assertEqual([x["duration_sec"] for x in sp.rows(p / "SCENES.csv")], ["6", "4.5", "7", "5"])
            self.assertEqual(sp.check(p), [])

    def test_c_every_scene_has_a_prompt_or_a_real_source(self):
        def no_prompt(rows, cols): rows[2][cols.index("still_prompt")] = ""
        self.assertTrue(has(mutate("SCENES.csv", no_prompt), "needs a still_prompt"))
        def no_still(rows, cols): rows[1][cols.index("real_still_url")] = ""
        self.assertTrue(has(mutate("SCENES.csv", no_still), "real still needs its source URL"))
        def no_clip(rows, cols): rows[3][cols.index("suggested_clip_url")] = ""
        self.assertTrue(has(mutate("SCENES.csv", no_clip), "real clip needs a source URL"))
        def no_fallback(rows, cols): rows[3][cols.index("fallback")] = ""
        self.assertTrue(has(mutate("SCENES.csv", no_fallback), "needs a fallback still"))
        def no_facts(rows, cols): rows[0][cols.index("fact_ids")] = ""
        self.assertTrue(has(mutate("SCENES.csv", no_facts), "exact data graphic needs fact IDs"))

    def test_d_paired_transitions_use_both_ids_and_a_matching_aspect_ratio(self):
        def bad_id(rows, cols): rows[0][cols.index("end_asset_id")] = "NOPE"
        self.assertTrue(has(mutate("TRANSITIONS.csv", bad_id), "not in ASSETS.csv"))
        def same(rows, cols): rows[0][cols.index("end_asset_id")] = "A1"
        self.assertTrue(has(mutate("TRANSITIONS.csv", same), "must be different"))
        def ratio(rows, cols): rows[2][cols.index("aspect_ratio")] = "1:1"
        self.assertTrue(has(mutate("ASSETS.csv", ratio), "same aspect ratio"))
        def no_pair(rows, cols): rows[2][cols.index("frame_end_asset_id")] = "R1"
        self.assertTrue(has(mutate("SCENES.csv", no_pair), "no row in TRANSITIONS.csv"))
        def mj_text(rows, cols): rows[0][cols.index("mj_prompt")] = "morph and write the poll numbers on a map"
        self.assertTrue(has(mutate("TRANSITIONS.csv", mj_text), "deterministic overlays"))
        def unverified(rows, cols): rows[0][cols.index("setting_verified_date")] = ""
        self.assertTrue(has(mutate("TRANSITIONS.csv", unverified), "setting_verified_date"))

    def test_e_ungraded_tip_records_are_never_shown_as_failing(self):
        def f_grade(rows, cols): rows[1][cols.index("on_screen_text")] = "Grade: F-"
        self.assertTrue(has(mutate("SCENES.csv", f_grade), "not-graded TIP record"))
        def zero(rows, cols): rows[1][cols.index("narration")] = "Candidate C scored zero on every issue."
        self.assertTrue(has(mutate("SCENES.csv", zero), "not-graded TIP record"))

    def test_f_rights_statuses_are_explicit(self):
        def blank(rows, cols): rows[3][cols.index("rights_status")] = ""
        self.assertTrue(has(mutate("SCENES.csv", blank), "explicit rights status"))
        def unknown(rows, cols): rows[3][cols.index("rights_status")] = "PROBABLY_FINE"
        self.assertTrue(has(mutate("SCENES.csv", unknown), "unknown rights status"))
        def cleared(rows, cols):
            rows[3][cols.index("rights_status")] = "CLEARED"
        def nolicense(rows, cols): rows[3][cols.index("license")] = ""
        probs = mutate("SCENES.csv", cleared)
        self.assertEqual([p for p in probs if "CLEARED" in p], [])                         # a written license basis is on file in the sample
        d = tempfile.mkdtemp()
        base = write_pack(Path(d) / "b")
        rows = [[r[c] for c in sp.ASSETS] for r in sp.rows(base / "ASSETS.csv")]
        rows[3][sp.ASSETS.index("license")] = ""
        sc = [[r[c] for c in sp.SCENES] for r in sp.rows(base / "SCENES.csv")]
        sc[3][sp.SCENES.index("rights_status")] = "CLEARED"
        probs = sp.check(write_pack(Path(d) / "m", **{"ASSETS.csv": rows, "SCENES.csv": sc}))
        self.assertTrue(has(probs, "real asset needs a source URL and a license") and has(probs, "CLEARED needs the written license basis"))

    def test_market_and_poll_observations_are_dated(self):
        def undated(rows, cols): rows[1][cols.index("refresh")] = "false"
        self.assertTrue(has(mutate("FACTS.csv", undated), "never presented as live"))
        def nodate(rows, cols): rows[0][cols.index("statement")] = "Example poll: A 49, B 45 among 800 likely voters"
        self.assertTrue(has(mutate("FACTS.csv", nodate), "field dates"))
        def badstatus(rows, cols): rows[0][cols.index("status")] = "UNVERIFIED"
        self.assertTrue(has(mutate("FACTS.csv", badstatus), "VERIFIED or ATTRIBUTED"))

    def test_numbers_and_people_follow_the_facts(self):
        def spoken(rows, cols): rows[0][cols.index("narration")] = "A poll shows sixty to forty."
        self.assertTrue(has(mutate("SCENES.csv", spoken), "narration says 60"))
        def shown(rows, cols): rows[0][cols.index("on_screen_text")] = "49–45 and 91"
        self.assertTrue(has(mutate("SCENES.csv", shown), "on-screen number 91"))
        def person(rows, cols): rows[2][cols.index("still_prompt")] = "Example Person at a podium, photo of the candidate"
        probs = mutate("SCENES.csv", person)
        self.assertTrue(has(probs, "likeness"))
        def timing(rows, cols): rows[1][cols.index("start_sec")] = "9"
        self.assertTrue(has(mutate("SCENES.csv", timing), "previous scene ends"))
        def long_vo(rows, cols): rows[0][cols.index("narration")] = "word " * 40
        self.assertTrue(has(mutate("SCENES.csv", long_vo), "do not fit"))

    def test_script_is_locked_before_scene_art_and_review_is_independent(self):
        d = tempfile.mkdtemp()
        p = write_pack(d, **{"SCRIPT.md": "# x\n\nSTATUS: DRAFT\n"})
        self.assertTrue(has(sp.check(p), "not `STATUS: LOCKED`"))
        d = tempfile.mkdtemp()
        p = write_pack(d, **{"QA.md": "ARTICLE_AUTHOR: Same Person\nFACTCHECK_REVIEWER: same person\n"})
        self.assertTrue(has(sp.check(p), "reviewer must differ"))
        d = tempfile.mkdtemp()
        p = write_pack(d, **{"QA.md": "nothing recorded\n"})
        self.assertTrue(has(sp.check(p), "must record ARTICLE_AUTHOR"))

    def test_assets_are_versioned_by_hash(self):
        import hashlib
        d = tempfile.mkdtemp()
        base = write_pack(Path(d) / "b")
        (base / "img.png").write_bytes(b"png-bytes")
        good = hashlib.sha256(b"png-bytes").hexdigest()
        def with_hash(h):
            rows = [[r[c] for c in sp.ASSETS] for r in sp.rows(base / "ASSETS.csv")]
            rows[0][sp.ASSETS.index("local_path")] = "img.png"
            rows[0][sp.ASSETS.index("sha256")] = h
            return sp.check(write_pack(Path(d) / ("m" + h[:3]), **{"ASSETS.csv": rows}) if False else _rewrite(base, rows))
        def _rewrite(b, rows):
            sp.write_csv(b / "ASSETS.csv", sp.ASSETS, rows)
            return b
        self.assertEqual(with_hash(good), [])
        self.assertTrue(has(with_hash("0" * 64), "sha256 does not match"))
        self.assertTrue(has(with_hash(""), "needs its sha256"))

    def test_a_video_file_in_a_pack_fails(self):
        d = tempfile.mkdtemp()
        p = write_pack(d)
        (p / "preview.mp4").write_bytes(b"\x00")
        self.assertTrue(has(sp.check(p), "video file in the pack"))

    def test_g_the_story_gate_does_not_require_irrelevant_finance(self):
        rows = gate.rows_of(ROOT / "tests/fixtures/claims_lean_ok.csv")
        self.assertEqual(gate.check(rows)[0], [])
        self.assertFalse([r for r in rows if r.get("type")])

    def test_h_nothing_is_published_deployed_or_rendered_without_recorded_authorization(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "l.jsonl"
            tr.record("production:zz-2026", "INTAKE", "claude", path=p)
            for s in ["SOURCE_CHECKED", "ARTICLE_DRAFTED"]:
                tr.record("production:zz-2026", s, "claude", path=p)
            tr.record("production:zz-2026", "ARTICLE_FACTCHECKED", "claude", reviewer="Independent Reader", path=p)
            tr.record("production:zz-2026", "ARTICLE_APPROVED", "claude", path=p)
            with self.assertRaises(ValueError):
                tr.record("production:zz-2026", "ARTICLE_PUBLISHED", "claude", path=p)
            tr.record("production:zz-2026", "ARTICLE_PUBLISHED", "claude", authorization="Owner: publish the article now", path=p)
            self.assertEqual(tr.current("production:zz-2026", p), "ARTICLE_PUBLISHED")
            with self.assertRaises(ValueError):                                    # the render lane cannot even begin without the owner's words
                tr.record("render:zz-2026", "VIDEO_RENDER_REQUESTED", "claude", path=p)
            tr.record("render:zz-2026", "VIDEO_RENDER_REQUESTED", "claude", authorization="Owner: render the video", path=p)
            self.assertEqual(tr.lane_of("production:x")[-1], "USER_MJ_PREMIERE_HANDOFF")           # the production lane ends at the handoff, not a render
            self.assertNotIn("VIDEO_RENDER_REQUESTED", tr.PRODUCTION_STATES)

    def test_i_independent_factcheck_status_is_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "l.jsonl"
            for s in ["INTAKE", "SOURCE_CHECKED", "ARTICLE_DRAFTED"]:
                tr.record("production:zz-2026", s, "claude", path=p)
            for bad in ({}, {"reviewer": "claude"}, {"reviewer": "  "}):
                with self.assertRaises(ValueError):
                    tr.record("production:zz-2026", "ARTICLE_FACTCHECKED", "claude", path=p, **bad)
            e = tr.record("production:zz-2026", "ARTICLE_FACTCHECKED", "claude", reviewer="Independent Reader", path=p)
            self.assertEqual(e["reviewer"], "Independent Reader")
            e2 = tr.read(p)[-1]
            self.assertEqual(e2["reviewer"], "Independent Reader")

    def test_stage_gates_cannot_be_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "l.jsonl"
            tr.record("production:zz-2026", "INTAKE", "claude", path=p)
            with self.assertRaises(ValueError):
                tr.record("production:zz-2026", "VIDEO_SCRIPT_LOCKED", "claude", path=p)


if __name__ == "__main__":
    unittest.main()
