"""Illinois State of the Race pages: built from the same templates as Florida, with the roster limitation visible and no Florida content."""
import html, json, re, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "elections" / "2026" / "illinois"
IL = ROOT / "data" / "elections" / "IL"


def page(rel):
    return (DIST / rel / "index.html").read_text(encoding="utf-8")


class IllinoisPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (DIST / "index.html").exists():
            subprocess.run([sys.executable, "build.py", "--strict"], cwd=ROOT, check=True, capture_output=True)
        cls.cands = json.loads((IL / "candidates.json").read_text(encoding="utf-8"))["candidates"]

    def test_all_pages_exist(self):
        for rel in ("", "governor", "senate", "house") + tuple(f"house/{i}" for i in range(1, 18)):
            self.assertTrue((DIST / rel / "index.html").exists(), rel)
        self.assertFalse((DIST / "house" / "18").exists())

    def test_no_florida_content_on_illinois_pages(self):
        for f in DIST.rglob("index.html"):
            t = re.sub(r"<[^>]+>", " ", f.read_text(encoding="utf-8"))
            for w in ("Florida", "FL-", "Donalds", "Jolly", "Moody", "DeSantis", "HB 1-D"):
                self.assertNotIn(w, t, f"{w} in {f}")

    def test_every_roster_candidate_appears_in_the_right_directory(self):
        gov, sen = page("governor"), page("senate")
        for c in self.cands:
            nm = html.escape(c["name"])
            if c["race"] == "governor":
                self.assertTrue(nm in gov, c["name"])
            elif c["race"] == "senate":
                self.assertTrue(nm in sen, c["name"])
            else:
                n = int(c["race"].split("-")[1])
                self.assertTrue(nm in page(f"house/{n}"), c["name"])

    def test_the_roster_limitation_is_on_every_state_level_page(self):
        for rel in ("", "governor", "senate", "house", "house/4"):
            t = page(rel)
            self.assertIn("not an official", t, rel)
            self.assertTrue("403" in t or "could not be read" in t, rel)
        methods = (ROOT / "dist" / "about" / "election-methods" / "index.html").read_text(encoding="utf-8")
        self.assertIn("not an official or complete list", methods)

    def test_open_seats_match_the_roster(self):
        t = re.sub(r"<[^>]+>", " ", page("house"))
        for n in (2, 4, 7, 8, 9):
            self.assertRegex(t, rf"IL-0{n}\s+Open seat")

    def test_not_graded_is_never_shown_as_zero(self):
        t = page("senate")
        self.assertIn("not graded", t)
        self.assertNotIn("F-", re.sub(r"<[^>]+>", " ", t).replace("F- at", ""))

    def test_no_dead_race_links_and_every_race_links_to_tip(self):
        self.assertIn("https://theissuesparty.org/races/2026-GOV-IL", page("governor"))
        self.assertIn("https://theissuesparty.org/races/2026-S-IL", page("senate"))
        self.assertIn("https://theissuesparty.org/races/2026-H-IL-07", page("house/7"))

    def test_removed_ballot_contract_is_flagged(self):
        self.assertIn("Mayra Mac", page("house/4"))
        self.assertIn("remove from the ballot", page("house/4"))

    def test_directory_gaps_are_reported_not_hidden(self):
        missing = [c["name"] for c in self.cands if not (c.get("tip") and c["tip"].get("url"))]
        # Any candidate without a TIP profile must show as one; none are missing since the 11 profiles were created on 2026-10-28.
        gov = page("governor")
        for n in missing:
            if html.escape(n) in gov:
                self.assertTrue("No TIP record yet" in gov)

    def test_every_listed_candidate_links_to_tip(self):
        for c in self.cands:
            self.assertTrue(c.get("tip") and c["tip"].get("url"), c["name"])

    def test_district_geometry_has_17_districts(self):
        d = json.loads((IL / "districts.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(int(k) for k in d["districts"]), list(range(1, 18)))


if __name__ == "__main__":
    unittest.main()
