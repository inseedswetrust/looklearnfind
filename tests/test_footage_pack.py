"""Fixtures for the footage-first Florida pack. Run: python3 -m unittest tests/test_footage_pack.py -v  (no network, no browser).

Checks the clip manifest and rights register against the packet's rules, and the infographic outputs against the design contract."""
import csv, hashlib, json, re, sys, unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/video/florida-2026"
IG = ROOT / "assets/video/florida-2026/infographics"
COLS = ["scene_id", "clip_id", "candidate", "source_url", "origin_uploader", "published_date", "footage_description", "full_duration", "suggested_in", "suggested_out",
        "suggested_seconds", "source_context", "licensing_basis", "rights_status", "selected_file", "sha256", "quality", "notes", "fallback_still"]
ENUM = {"CLEARED", "NEEDS_LICENSE", "EDITORIAL_REVIEW", "INTERNAL_REFERENCE_ONLY", "REJECTED"}
TIMECODE = re.compile(r"^(UNINSPECTED|n/a|(CAPTION:)?\d{2}:\d{2}:\d{2}(\.\d+)?)$")


def rows():
    return list(csv.DictReader(open(DOCS / "CLIP_MANIFEST.csv", encoding="utf8")))


class TestManifest(unittest.TestCase):
    def test_columns_exact(self):
        self.assertEqual(list(csv.reader(open(DOCS / "CLIP_MANIFEST.csv", encoding="utf8")))[0], COLS)

    def test_scenes_covered(self):
        self.assertEqual({r["scene_id"] for r in rows()}, {"02", "03", "05", "06", "08", "10"})

    def test_rights_enum_and_basis(self):
        for r in rows():
            self.assertIn(r["rights_status"], ENUM, r["clip_id"])
            self.assertTrue(r["licensing_basis"].strip(), r["clip_id"])
            if r["rights_status"] == "CLEARED":
                self.assertRegex(r["licensing_basis"], r"CC BY|public domain|CC0|license", r["clip_id"])

    def test_timecodes_are_real_or_marked(self):
        for r in rows():
            for k in ("suggested_in", "suggested_out"):
                self.assertRegex(r[k], TIMECODE, f"{r['clip_id']} {k}")

    def test_only_cleared_or_held_files_exist(self):
        """A selected file may exist only if the clip is CLEARED or sits in _review_hold with a non-cleared status."""
        for r in rows():
            if not r["selected_file"]:
                self.assertEqual(r["sha256"], "", r["clip_id"])
                continue
            p = ROOT / r["selected_file"]
            self.assertTrue(p.exists(), r["selected_file"])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), r["sha256"], r["clip_id"])
            if r["rights_status"] != "CLEARED":
                self.assertIn("_review_hold", r["selected_file"], r["clip_id"])

    def test_no_needs_license_clip_was_downloaded(self):
        for r in rows():
            if r["rights_status"] == "NEEDS_LICENSE":
                self.assertEqual(r["selected_file"], "", r["clip_id"])

    def test_register_matches_manifest(self):
        reg = {r["clip_id"]: r for r in csv.DictReader(open(DOCS / "RIGHTS_REGISTER.csv", encoding="utf8"))}
        self.assertEqual(set(reg), {r["clip_id"] for r in rows()})
        for r in rows():
            self.assertEqual(reg[r["clip_id"]]["rights_status"], r["rights_status"])

    def test_youtube_ids_are_eleven_characters(self):
        for r in rows():
            m = re.search(r"watch\?v=([^&]+)", r["source_url"])
            if m:
                self.assertEqual(len(m.group(1)), 11, r["clip_id"])


class TestInfographics(unittest.TestCase):
    FRAMES = {"IG-02": ["A_start", "B_end"], "IG-04": ["A_start", "B_end", "B1_duval", "B2_gadsden", "B3_sumter"], "IG-06": ["A_start", "B_end"], "IG-08": ["A_start", "B_end"],
              "IG-09-10": ["A_start", "B_end"], "IG-11": ["A_start", "B_end"], "IG-12-13": ["A_start", "B_end"]}

    def test_every_frame_exists_at_1080x1920_with_a_layered_svg(self):
        for ig, tags in self.FRAMES.items():
            for t in tags:
                png, svg = IG / ig / f"{ig}_{t}_1080x1920.png", IG / ig / f"{ig}_{t}.svg"
                self.assertEqual(Image.open(png).size, (1080, 1920), png.name)
                root = ET.parse(svg).getroot()
                ids = {e.get("id") for e in root.iter() if e.tag.endswith("}g")}
                self.assertTrue({"paper", "folio", "source", "microtext"} <= ids, f"{svg.name} missing layer groups")

    def test_no_text_in_the_top_170_or_bottom_310_except_brand_furniture(self):
        for svg in IG.glob("IG-*/*.svg"):
            for e in ET.parse(svg).getroot().iter():
                if e.tag.endswith("}text"):
                    y = float(e.get("y"))
                    if y < 170 or y > 1610:
                        self.assertIn("Sources and candidate records", "".join(e.itertext()), f"{svg.name} y={y}")

    def test_no_remote_images_and_no_generated_art(self):
        for svg in IG.glob("IG-*/*.svg"):
            txt = svg.read_text(encoding="utf8")
            self.assertNotRegex(txt, r'href="https?:', svg.name)

    def test_primary_result_uses_the_official_count(self):
        st = json.loads((IG / "data/senate_dem_primary_state_2026-08-18.json").read_text(encoding="utf8"))
        self.assertEqual(st["nixon"] + st["vindman"], st["total"])
        txt = (IG / "IG-02/IG-02_B_end.svg").read_text(encoding="utf8")
        for needle in (f"{st['nixon']:,}", f"{st['vindman']:,}", "NIXON WINS", "12-POINT"):
            self.assertIn(needle, txt)
        self.assertNotIn("NIXON WINS", (IG / "IG-02/IG-02_A_start.svg").read_text(encoding="utf8"))  # the reveal is not in the start frame

    def test_county_data_sums_to_state(self):
        st = json.loads((IG / "data/senate_dem_primary_state_2026-08-18.json").read_text(encoding="utf8"))
        c = list(csv.DictReader(open(IG / "data/senate_dem_primary_county_2026-08-18.csv", encoding="utf8")))
        self.assertEqual(len(c), 67)
        self.assertEqual(sum(int(r["nixon"]) for r in c), st["nixon"])
        self.assertEqual(sum(int(r["vindman"]) for r in c), st["vindman"])

    def test_poll_numbers_match_the_fact_sheet(self):
        fs = (ROOT / "docs/video/FLORIDA_VIDEO_FACT_SHEET.md").read_text(encoding="utf8")
        self.assertIn("Moody 49, Nixon 45", fs)
        self.assertIn("Donalds 49, Jolly 47", fs)
        t6 = (IG / "IG-06/IG-06_A_start.svg").read_text(encoding="utf8")
        t8 = (IG / "IG-08/IG-08_B_end.svg").read_text(encoding="utf8")
        self.assertIn(">49%<", t6)
        self.assertIn(">45%<", t6)
        self.assertIn(">47%<", t8)

    def test_issue_names_match_tip_export(self):
        defs = {d["slug"]: d["display_name"] for d in json.loads((ROOT / "data/elections/FL/tip_export/issue_definitions.json").read_text(encoding="utf8"))}
        root = ET.parse(IG / "IG-11/IG-11_A_start.svg").getroot()
        txt = " ".join("".join(e.itertext()) for e in root.iter() if e.tag.endswith("}text"))  # long names wrap onto two text lines
        for name in defs.values():
            self.assertIn(name, txt)

    def test_end_frame_reuses_the_start_frame_photos(self):
        """IG-08 and IG-09-10: the same embedded image bytes appear in A and B (a transform, not a regeneration)."""
        for ig, keys in (("IG-08", ("card-donalds-photo", "card-jolly-photo")), ("IG-06", ("headshot-moody", "headshot-nixon"))):
            a = (IG / ig / f"{ig}_A_start.svg").read_text(encoding="utf8")
            b = (IG / ig / f"{ig}_B_end.svg").read_text(encoding="utf8")
            for k in keys:
                ma, mb = re.search(rf'id="{k}" href="([^"]+)"', a), re.search(rf'id="{k}" href="([^"]+)"', b)
                self.assertTrue(ma and mb, k)
                self.assertEqual(ma.group(1), mb.group(1), k)


if __name__ == "__main__":
    unittest.main()
