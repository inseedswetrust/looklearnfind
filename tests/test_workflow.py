"""Fixtures for tools/workflow/transitions.py. Run: python3 -m unittest tests/test_workflow.py"""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "workflow"))
import transitions as t

class T(unittest.TestCase):
    def setUp(self): self.d = tempfile.TemporaryDirectory(); self.p = Path(self.d.name) / "l.jsonl"
    def tearDown(self): self.d.cleanup()
    def rec(self, e, to, **k): return t.record(e, to, "claude", path=self.p, **k)
    def test_starts_at_discovered_and_cannot_skip_a_gate(self):
        with self.assertRaises(ValueError): self.rec("fl-senate", "DATA_CAPTURED")
        self.rec("fl-senate", "DISCOVERED"); self.rec("fl-senate", "ROSTER_VERIFIED")
        with self.assertRaises(ValueError): self.rec("fl-senate", "RESEARCH_COMMISSIONED")
        self.assertEqual(t.current("fl-senate", self.p), "ROSTER_VERIFIED")
    def test_failed_check_cannot_advance_and_rejection_needs_a_correction_id(self):
        for s in ("DISCOVERED", "ROSTER_VERIFIED", "DATA_CAPTURED"): self.rec("x", s)
        with self.assertRaises(ValueError): self.rec("x", "RESEARCH_COMMISSIONED", checks={"strict_build": "fail"})
        with self.assertRaises(ValueError): self.rec("x", "ROSTER_VERIFIED")
        e = self.rec("x", "ROSTER_VERIFIED", correction_id="CORR-1", blocked_reason="roster changed")
        self.assertEqual(e["from_state"], "DATA_CAPTURED")
    def test_ledger_is_append_only_and_records_hashes(self):
        self.rec("y", "DISCOVERED", outputs=["tools/workflow/transitions.py"])
        self.rec("y", "ROSTER_VERIFIED")
        rows = t.read(self.p)
        self.assertEqual(len(rows), 2); self.assertEqual(len(next(iter(rows[0]["outputs"].values()))), 64)
    def test_lean_lane_has_six_states_and_still_blocks_skipping(self):
        self.rec("story:fl-senate", "DISCOVERED"); self.rec("story:fl-senate", "SOURCE_CHECKED", links={"article": "https://example.org/a", "candidate": "https://theissuesparty.org/candidates/S6FL00640"})
        with self.assertRaises(ValueError): self.rec("story:fl-senate", "FACT_CHECKED")
        with self.assertRaises(ValueError): self.rec("story:fl-senate", "ARTICLE_DRAFTED")        # a 15-lane state is not valid in the lean lane
        self.assertEqual(t.read(self.p)[-1]["links"]["candidate"].split("/")[-1], "S6FL00640")
if __name__ == "__main__": unittest.main()
