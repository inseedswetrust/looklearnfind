"""Fixtures for tools/video (spec validator, number parsing, template, video lane). Run: python3 -m unittest tests/test_video_pack.py -v  (no network, no browser)."""
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/video"))
sys.path.insert(0, str(ROOT / "tools/workflow"))
import build_video_pack as v
import transitions as t

SPEC = json.loads((ROOT / "data/video/fl_2026_state_of_the_race.json").read_text(encoding="utf-8"))


def mut(fn):
    s = copy.deepcopy(SPEC)
    fn(s)
    return v.validate(s)


class TestNumbers(unittest.TestCase):
    def test_spoken_numbers(self):
        self.assertEqual(v.spoken_numbers("twenty-eight House members"), [28.0])
        self.assertEqual(v.spoken_numbers("one hundred seven million versus six point four"), [107.0, 6.4])
        self.assertEqual(v.spoken_numbers("fourteen and a half million"), [14.5])
        self.assertEqual(v.spoken_numbers("eighty-three cents"), [83.0])
        self.assertEqual(v.spoken_numbers("November third and thirty-first, September eleventh"), [])     # ordinals are not facts
    def test_screen_numbers_ignore_dates_districts_and_years(self):
        self.assertEqual(v.screen_numbers(["Oct 12–19 · FL-14 · 2024 vote · Nov 3", "1,471 likely voters · ±2.81", "$107.6M · 83¢"]), [1471.0, 2.81, 107.6, 83.0])


class TestSpec(unittest.TestCase):
    def test_the_florida_spec_is_valid(self):
        self.assertEqual(v.validate(SPEC), [])
    def test_shape(self):
        self.assertEqual((len(SPEC["segments"]), len(SPEC["transitions"]), SPEC["duration_seconds"]), (18, 17, 90))
    def test_narration_over_the_word_limit_fails(self):
        p = mut(lambda s: s["segments"][0].update(vo="word " * 20))
        self.assertTrue(any("words (max" in x for x in p))
    def test_an_invented_spoken_number_fails(self):
        p = mut(lambda s: s["segments"][7].update(vo="UNF's poll says sixty to forty. Close, not a lead."))
        self.assertTrue(any("narration says 60" in x for x in p))
    def test_an_invented_on_screen_number_fails(self):
        p = mut(lambda s: s["segments"][8]["on_screen"].append("91¢"))
        self.assertTrue(any("on-screen number 91" in x for x in p))
    def test_unknown_fact_id_fails(self):
        p = mut(lambda s: s["segments"][2]["facts"].append("F-99"))
        self.assertTrue(any("unknown fact F-99" in x for x in p))
    def test_a_segment_with_no_facts_fails(self):
        p = mut(lambda s: s["segments"][3].update(facts=[]))
        self.assertTrue(any("no fact IDs" in x for x in p))
    def test_plate_prompts_may_not_ask_for_people_text_numbers_or_party_colors(self):
        for bad in ("a crowd of people holding signs", "a banner with text", "a red wave", "page 3 of paper"):
            p = mut(lambda s, b=bad: s["segments"][1]["plate"].update(desc=b))
            self.assertTrue(any("plate P02" in x for x in p), bad)
    def test_transition_prompts_may_not_ask_for_faces_or_text(self):
        p = mut(lambda s: s["transitions"][0].update(motion="A face appears and text scrolls."))
        self.assertTrue(any("transition T01" in x for x in p))
    def test_animation_running_past_its_segment_fails(self):
        p = mut(lambda s: s["segments"][0]["animations"][0].update(duration=9.0))
        self.assertTrue(any("runs past" in x for x in p))
    def test_wrong_duration_or_broken_transition_chain_fails(self):
        self.assertTrue(any("segments add up" in x for x in mut(lambda s: s.update(duration_seconds=85))))
        self.assertTrue(any("transitions do not link" in x for x in mut(lambda s: s["transitions"].pop())))
    def test_attributed_facts_need_a_source_and_status_must_be_known(self):
        p = mut(lambda s: s["facts"][0].update(source="", status="MAYBE"))
        self.assertTrue(any("status must be" in x for x in p) and any("missing source" in x for x in p))
    def test_disclosures_and_credits_are_required(self):
        self.assertTrue(any("disclosures and credits" in x for x in mut(lambda s: s.update(disclosures=[]))))
    def test_senate_candidates_share_one_portrait_size(self):
        for n in (12, 14, 17):
            prm = SPEC["segments"][n - 1]["params"]
            self.assertIn("portrait_px", prm)                     # one value serves both candidates: equal size by construction


class TestTemplate(unittest.TestCase):
    def test_a_new_state_spec_is_refused_until_every_placeholder_is_filled(self):
        with tempfile.TemporaryDirectory() as d:
            out = ROOT / "data/video/zz_2026_state_of_the_race.json"
            try:
                subprocess.run([sys.executable, str(ROOT / "tools/video/init_state_spec.py"), "ZZ", "--legacy"], check=True, capture_output=True)
                r = subprocess.run([sys.executable, str(ROOT / "tools/video/build_video_pack.py"), str(out), "--check"], capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(r.returncode, 2)
                self.assertIn("placeholder", r.stdout)
                self.assertGreaterEqual(r.stdout.count("PROBLEM"), 18)
            finally:
                out.unlink(missing_ok=True)


class TestVideoLane(unittest.TestCase):
    def test_video_lane_states_and_gates(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "l.jsonl"
            t.record("video:fl-state", "BRIEFED", "claude", path=p)
            with self.assertRaises(ValueError):
                t.record("video:fl-state", "STORYBOARDED", "claude", path=p)       # no skipping SCRIPTED
            with self.assertRaises(ValueError):
                t.record("video:fl-state", "DISCOVERED", "claude", path=p)         # a story state is not a video state
            t.record("video:fl-state", "SCRIPTED", "claude", path=p)
            self.assertEqual(t.current("video:fl-state", p), "SCRIPTED")


if __name__ == "__main__":
    unittest.main()
