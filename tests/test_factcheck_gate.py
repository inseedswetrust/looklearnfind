"""Fixtures for tools/qa/factcheck_gate.py. Run: python3 -m unittest tests/test_factcheck_gate.py -v  (no network)."""
import sys, tempfile, unittest, csv, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "qa"))
import factcheck_gate as g

PK = ROOT / "release/research_packet"
def row(**k):
    r = {"claim_id": "C1", "page": "p", "claim": "x", "value": "1", "source": "FEC", "as_of": "2026-10-23", "verdict": "VERIFIED", "notes": "", "type": "", "evidence_ref": "", "reviewer": "standards", "resolution": ""}
    r.update(k); return r
def why(rows, **kw): return [b["reason"] for b in g.check(rows, **kw)[0]]


class TestGate(unittest.TestCase):
    def test_clean_ledger_is_ready(self): self.assertEqual(g.check([row()], author="editorial")[0], [])
    def test_unresolved_unverified_blocks_but_removed_does_not(self):
        self.assertTrue(why([row(verdict="UNVERIFIED")]))
        self.assertEqual(why([row(verdict="UNVERIFIED", resolution="removed")]), [])
        self.assertEqual(why([row(claim_id="REMOVED-01", verdict="CONTRADICTED")]), [])
    def test_missing_source_or_timestamp_blocks(self):
        self.assertIn("no source", why([row(source="")])); self.assertIn("no as_of timestamp", why([row(as_of="")]))
    def test_invalid_verdict_blocks(self): self.assertTrue(why([row(verdict="")]))
    def test_reviewer_must_be_independent(self): self.assertTrue(any("independent" in w for w in why([row(reviewer="editorial")], author="editorial")))
    def test_duplicate_ids_block(self): self.assertIn("duplicate claim_id", why([row(), row()]))
    def test_grade_from_governor_profile_blocks(self):
        self.assertTrue(any("gubernatorial" in w for w in why([row(type="grade", evidence_ref="https://theissuesparty.org/candidates/GOV-FL-DONALDS")])))
    @unittest.skipUnless((PK / "tip_grades.csv").exists(), "packet not built")
    def test_grade_must_exist_as_graded_on_the_congressional_profile(self):
        graded = [x for x in csv.DictReader(open(PK / "tip_grades.csv", encoding="utf-8")) if x["grade_state"] == "graded"][0]
        ungraded = [x for x in csv.DictReader(open(PK / "tip_grades.csv", encoding="utf-8")) if x["grade_state"] == "not_graded"][0]
        ok = row(type="grade", evidence_ref=graded["profile_holding_grade"])
        self.assertEqual(why([ok], packet=PK), [])
        bad = row(type="grade", evidence_ref=ungraded["profile_holding_grade"])
        # a profile with SOME graded issues is acceptable as a profile reference; a profile with none is not
        by = {}
        for x in csv.DictReader(open(PK / "tip_grades.csv", encoding="utf-8")): by.setdefault(x["candidate_id"], []).append(x["grade_state"])
        none_graded = [c for c, s in by.items() if "graded" not in s][0]
        self.assertTrue(why([row(type="grade", evidence_ref=f"https://theissuesparty.org/candidates/{none_graded}")], packet=PK))
    @unittest.skipUnless((PK / "fl_polls.csv").exists(), "packet not built")
    def test_poll_from_aggregator_listing_blocks_until_original_reviewed(self):
        p = [x for x in csv.DictReader(open(PK / "fl_polls.csv", encoding="utf-8")) if x["original_poll_url"]][0]
        self.assertTrue(any("aggregator listing" in w for w in why([row(type="poll", evidence_ref=p["original_poll_url"])], packet=PK)))
        self.assertFalse(any("aggregator listing" in w for w in why([row(type="poll", evidence_ref=p["original_poll_url"], notes="original reviewed 2026-10-24")], packet=PK)))
    @unittest.skipUnless((PK / "fl_candidate_finance.csv").exists(), "packet not built")
    def test_finance_with_no_totals_cannot_be_reported(self):
        gap = [x for x in csv.DictReader(open(PK / "fl_candidate_finance.csv", encoding="utf-8")) if x["gaps"]][0]
        self.assertTrue(why([row(type="finance", evidence_ref=gap["candidate_id"])], packet=PK))
    def test_market_needs_quote_kind_and_contract_kind(self):
        self.assertTrue(why([row(type="market", evidence_ref="X", notes="")]))
        self.assertFalse([w for w in why([row(type="market", evidence_ref="X", notes="party contract, last trade 0.90")]) if "quote kind" in w or "party-winner" in w])
    @unittest.skipUnless((PK / "fl_assets.csv").exists(), "packet not built")
    def test_not_for_publication_image_blocks(self):
        a = [x for x in csv.DictReader(open(PK / "fl_assets.csv", encoding="utf-8")) if x["publication_status"].startswith("NOT FOR")][0]
        self.assertTrue(any("NOT FOR PUBLICATION" in w for w in why([row(type="image", evidence_ref=a["asset_id"])], packet=PK)))
    def test_data_macro_without_ledger_row_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "a.html"; f.write_text("<p>[[v:est14]] and [[v:other]]</p>", encoding="utf-8")
            self.assertEqual([w for w in why([row(value="est14")], article=f)], ["data macro [[v:other]] has no ledger row"])

if __name__ == "__main__":
    unittest.main()
