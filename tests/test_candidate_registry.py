"""Candidate registry and directory: the data behind /find/candidates/. No network."""
import json, subprocess, sys, unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "tools/elections"))
import build_registry as br  # noqa: E402


class RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codes = [c for c in br.elections.STATES if (br.D / c / "candidates.json").exists()]
        cls.regs, cls.races = br.build(cls.codes)

    def test_counts_match_the_state_files(self):
        for reg in self.regs:
            src = json.loads((br.D / reg["state"] / "candidates.json").read_text(encoding="utf-8"))["candidates"]
            self.assertEqual(len(reg["candidates"]), len(src), reg["state"])

    def test_validation_passes(self):
        self.assertEqual(br.validate(self.regs, self.races), [])

    def test_committed_files_are_current(self):
        r = subprocess.run([sys.executable, str(R / "tools/elections/build_registry.py"), "--check"], capture_output=True, text=True, encoding="utf-8", cwd=R)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_listed_person_links_to_tip_or_is_a_gap(self):
        for reg in self.regs:
            for c in reg["candidates"]:
                if c["tip"]["url"]:
                    self.assertTrue(c["tip"]["url"].startswith("https://theissuesparty.org/candidates/"))
                    self.assertEqual(c["tip"]["http"], 200)
                else:
                    self.assertIn("tip_profile_missing", c["gaps"])

    def test_unofficial_rosters_carry_limitations(self):
        for reg in self.regs:
            if reg["roster"]["basis"] != "official":
                self.assertTrue(reg["roster"]["limitations"])

    def test_order_is_by_race_then_surname_not_party_or_grade(self):
        for reg in self.regs:
            keys = [(br.OFFICE_ORDER[c["office"]], c["district"] or 0, c["sort_name"].lower()) for c in reg["candidates"]]
            self.assertEqual(keys, sorted(keys), reg["state"])

    def test_no_grades_copied(self):
        for reg in self.regs:
            for c in reg["candidates"]:
                self.assertNotIn("grades", c["tip"])

    def test_ids_are_unique_and_stable_format(self):
        ids = [c["llf_id"] for reg in self.regs for c in reg["candidates"]]
        self.assertEqual(len(ids), len(set(ids)))
        for i in ids:
            self.assertRegex(i, r"^[A-Z]{2}-[GSH]\d*-[a-z0-9-]+$")


class DirectoryPageTests(unittest.TestCase):
    def test_built_directory_has_no_per_person_pages(self):
        d = R / "dist/find/candidates"
        if not d.exists():
            self.skipTest("dist not built")
        pages = sorted(p.relative_to(d).as_posix() for p in d.rglob("index.html"))
        self.assertIn("index.html", pages)
        for p in pages:
            if p != "index.html":
                self.assertEqual(p.count("/"), 1, f"unexpected deep page {p}")  # state lists only

    def test_secondary_roster_lists_are_noindex(self):
        for slug, expect in (("illinois", True), ("new-york", True), ("michigan", False)):
            f = R / f"dist/find/candidates/{slug}/index.html"
            if not f.exists():
                self.skipTest("dist not built")
            self.assertEqual("noindex" in f.read_text(encoding="utf-8"), expect, slug)


if __name__ == "__main__":
    unittest.main()
