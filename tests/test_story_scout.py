"""Fixtures for tools/story/story_brief_check.py (the llf-story-scout tests). Run: python3 -m unittest tests/test_story_scout.py"""
import copy, datetime, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/story"))
import story_brief_check as sb

AS_OF = datetime.date(2026, 10, 24)
GOOD = {"id": "a1", "event_date": "2026-10-21", "labelled_new": True, "synopsis": "short", "ready_to_write": True,
        "sources": [{"role": "lead", "url": "https://example.org/a", "date": "2026-10-21", "opened": True}],
        "tip_grades": [{"candidate": "X", "issue": "universal_healthcare", "grade": "B-", "source_profile": "https://theissuesparty.org/candidates/H2FL10259"}]}


def angle(**k):
    a = copy.deepcopy(GOOD)
    a.update(k)
    return a


def res(a):
    return sb.check_angle(a, AS_OF)


class T(unittest.TestCase):
    def test_good_angle_is_ready(self):
        self.assertEqual(res(GOOD)["status"], "READY")

    def test_missing_url_or_date_is_not_ready(self):
        self.assertEqual(res(angle(sources=[{"role": "lead", "url": "", "date": "2026-10-21", "opened": True}]))["status"], "NOT_READY")
        self.assertEqual(res(angle(sources=[{"role": "lead", "url": "https://e.org", "date": "", "opened": True}]))["status"], "NOT_READY")

    def test_snippet_only_lead_is_not_ready(self):
        r = res(angle(sources=[{"role": "lead", "url": "https://e.org", "date": "2026-10-21", "opened": False}]))
        self.assertEqual(r["status"], "NOT_READY")
        self.assertIn("snippet-only", r["reasons"][0])

    def test_damaging_allegation_needs_original_and_response(self):
        self.assertEqual(res(angle(damaging_allegation={"present": True, "original_evidence_url": "", "response_sought": False}))["status"], "NOT_READY")
        self.assertEqual(res(angle(damaging_allegation={"present": True, "original_evidence_url": "https://court.example/doc", "response_sought": True}))["status"], "READY")

    def test_recycled_coverage_labeled_new_is_not_ready(self):
        self.assertEqual(res(angle(event_date="2026-08-01"))["status"], "NOT_READY")
        self.assertEqual(res(angle(event_date="2026-08-01", labelled_new=False))["status"], "READY")      # old context is fine when not sold as new

    def test_unverifiable_grade_is_hidden_as_not_graded(self):
        r = res(angle(tip_grades=[{"candidate": "Donalds", "issue": "x", "grade": "A", "source_profile": "https://theissuesparty.org/candidates/GOV-FL-DONALDS"}]))
        self.assertEqual(r["status"], "READY")
        self.assertEqual(r["tip_grades_shown"][0]["display"], "NOT_GRADED")
        self.assertIsNone(r["tip_grades_shown"][0]["grade"])

    def test_financial_claim_needs_attributed_source_and_period(self):
        self.assertEqual(res(angle(financial_claims=[{"claim": "group spent $5M", "source_url": "https://e.org"}]))["status"], "NOT_READY")
        ok = {"claim": "group spent $5M", "source_url": "https://e.org", "period": "through Sept 30", "attributed_to": "AdImpact, as reported by X"}
        self.assertEqual(res(angle(financial_claims=[ok]))["status"], "READY")

    def test_no_finance_data_is_never_a_blocker(self):
        self.assertEqual(res(angle(financial_claims=[]))["status"], "READY")

    def test_registry_growth_preserves_and_never_approves(self):
        reg = json.loads((ROOT / "data/elections/news_source_registry.json").read_text(encoding="utf-8"))
        before = copy.deepcopy(reg)
        new = sb.registry_add(reg, {"publication": "New Outlet", "domain": "new.example"})
        self.assertEqual(reg, before)                                       # original untouched
        self.assertEqual(new["sources"][:len(before["sources"])], before["sources"])
        self.assertFalse(new["sources"][-1]["owner_approved"])
        self.assertEqual(new["sources"][-1]["status"], "proposed")
        self.assertTrue(all(not s["owner_approved"] for s in reg["sources"]))


if __name__ == "__main__":
    unittest.main()
