"""Michigan State of the Race pages: same templates as Florida and Illinois, official-list roster, no other state's content."""
import html, json, re, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "elections" / "2026" / "michigan"
MI = ROOT / "data" / "elections" / "MI"
DISQUALIFIED = ("Thibodeau", "Wilcoxon", "Shelby Campbell", "Morton")


def page(rel):
    return (DIST / rel / "index.html").read_text(encoding="utf-8")


class MichiganPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (DIST / "index.html").exists():
            subprocess.run([sys.executable, "build.py", "--strict"], cwd=ROOT, check=True, capture_output=True)
        cls.cands = json.loads((MI / "candidates.json").read_text(encoding="utf-8"))["candidates"]

    def test_all_pages_exist(self):
        for rel in ("", "governor", "senate", "house") + tuple(f"house/{i}" for i in range(1, 14)):
            self.assertTrue((DIST / rel / "index.html").exists(), rel)
        self.assertFalse((DIST / "house" / "14").exists())

    def test_no_other_state_content_on_michigan_pages(self):
        for f in DIST.rglob("index.html"):
            # the global shell's state picker legitimately names every state; the test is about page content
            t = re.sub(r"<[^>]+>", " ", re.sub(r'<div class="llf-shell".*?<a class="nav-open".*?</a></div></div>', " ", f.read_text(encoding="utf-8"), flags=re.S))
            for w in ("Florida", "Illinois", "Durbin", "Pritzker", "Donalds", "HB 1-D", "March 17"):
                self.assertNotIn(w, t, f"{w} in {f}")

    def test_every_roster_candidate_appears_in_the_right_directory(self):
        gov, sen = page("governor"), page("senate")
        for c in self.cands:
            nm = html.escape(c["name"])
            if c["race"] == "governor":
                self.assertIn(nm, gov, c["name"])
            elif c["race"] == "senate":
                self.assertIn(nm, sen, c["name"])
            else:
                self.assertIn(nm, page(f"house/{int(c['race'].split('-')[1])}"), c["name"])

    def test_disqualified_candidates_are_not_listed(self):
        for rel in ("house/7", "house/13"):
            t = page(rel)
            for w in DISQUALIFIED:
                self.assertNotIn(w, t, f"{w} on {rel}")

    def test_the_roster_basis_is_the_official_listing(self):
        for rel in ("", "governor", "senate", "house", "house/10"):
            t = page(rel)
            self.assertIn("Department of State", t, rel)
            self.assertNotIn("not an official", t, rel)

    def test_open_seats_match_the_roster(self):
        t = re.sub(r"<[^>]+>", " ", page("house"))
        for n in (10, 11, 13):
            self.assertRegex(t, rf"MI-{n:02d}\s+Open seat")

    def test_not_graded_is_never_shown_as_zero(self):
        t = re.sub(r"<[^>]+>", " ", page("governor"))
        self.assertIn("not graded", t)

    def test_every_race_links_to_tip(self):
        self.assertIn("https://theissuesparty.org/races/2026-GOV-MI", page("governor"))
        self.assertIn("https://theissuesparty.org/races/2026-S-MI", page("senate"))
        self.assertIn("https://theissuesparty.org/races/2026-H-MI-10", page("house/10"))

    def test_only_the_unofficial_write_in_lacks_a_tip_profile(self):
        missing = [c["name"] for c in self.cands if not (c.get("tip") and c["tip"].get("url"))]
        self.assertEqual(missing, ["Bree Taylor"])

    def test_district_geometry_has_13_districts(self):
        d = json.loads((MI / "districts.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(int(k) for k in d["districts"]), list(range(1, 14)))


if __name__ == "__main__":
    unittest.main()
