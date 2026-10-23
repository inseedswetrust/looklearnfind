"""Phase A acceptance fixtures (no network). Run: python3 -m unittest tests/test_phase_a.py -v

Covers: revision-safe latest pointer, idempotent rerun, stale quote, missing market, mistaken-person Polymarket match,
FEC Schedule E de-duplication (AIPAC/UDP rows), and TIP grade/profile correctness in the research packet.
"""
import csv, json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "dark_horse"))
sys.path.insert(0, str(ROOT / "tests"))
import daily, schedule_e, contracts
from test_dark_horse import HEAD, WATCH, CMAP, make_fetch, kmarket


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        with open(self.base / "watchlist.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(HEAD); w.writerows(WATCH)
        (self.base / "contract_map.json").write_text(json.dumps(CMAP))
    def tearDown(self): self.tmp.cleanup()
    def run_day(self, day, hour="12", **kw):
        return daily.run(day, base=self.base, now=f"{day}T{hour}:00:00Z", **kw)


class TestPointerAndRerun(Base):
    def test_rerun_same_day_is_a_new_revision_and_keeps_the_original(self):
        self.run_day("2026-10-23", fetch=make_fetch(kprice="0.60"))
        orig = (self.base / "daily/2026-10-23/markets.json").read_bytes()
        orig_manifest = (self.base / "daily/2026-10-23/manifest.json").read_bytes()
        self.run_day("2026-10-23", hour="15", fetch=make_fetch(kprice="0.64"))
        self.assertEqual((self.base / "daily/2026-10-23/markets.json").read_bytes(), orig)          # historical snapshot untouched
        self.assertEqual((self.base / "daily/2026-10-23/manifest.json").read_bytes(), orig_manifest)
        self.assertTrue((self.base / "daily/2026-10-23/revisions/r2/markets.json").exists())
        latest = json.loads((self.base / "latest.json").read_text())
        self.assertEqual((latest["date"], latest["revision"]), ("2026-10-23", 2))
        self.assertTrue((self.base / latest["markets_path"]).exists())

    def test_rerun_does_not_duplicate_alerts_in_the_original_day(self):
        self.run_day("2026-10-23", fetch=make_fetch(kprice="0.60"))
        self.run_day("2026-10-24", fetch=make_fetch(kprice="0.70"))
        a1 = (self.base / "daily/2026-10-24/alerts.json").read_bytes()
        self.run_day("2026-10-24", hour="15", fetch=make_fetch(kprice="0.70"))
        self.assertEqual((self.base / "daily/2026-10-24/alerts.json").read_bytes(), a1)

    def test_latest_pointer_never_moves_backward(self):
        self.run_day("2026-10-24", fetch=make_fetch())
        status, _ = self.run_day("2026-10-23", fetch=make_fetch())     # a late backfill of an older day
        self.assertEqual(json.loads((self.base / "latest.json").read_text())["date"], "2026-10-24")
        self.assertFalse(status["latest_pointer_updated"])
        self.assertTrue((self.base / "daily/2026-10-23/manifest.json").exists())    # the older day is still stored


class TestDryRun(Base):
    def test_dry_run_does_not_consume_the_real_day(self):
        def boom(url): raise AssertionError("network used in dry run")
        self.run_day("2026-10-23", dry=True, fetch=boom)
        self.assertFalse((self.base / "daily/2026-10-23").exists())
        self.run_day("2026-10-23", fetch=make_fetch())
        self.assertTrue((self.base / "daily/2026-10-23/manifest.json").exists())          # the real run is revision 1, not 2
        self.assertEqual(json.loads((self.base / "latest.json").read_text())["revision"], 1)


class TestQuoteQuality(Base):
    def test_old_quote_is_flagged_stale_and_missing_timestamp_is_unknown(self):
        _, _ = self.run_day("2026-10-27", fetch=make_fetch())         # venue timestamp 2026-10-23T12:00Z is 96 hours old
        rows = {(r["candidate_name"], r["provider"]): r for r in json.loads((self.base / "daily/2026-10-27/markets.json").read_text())["rows"]}
        k = rows[("Alice Example", "kalshi")]
        self.assertTrue(k["stale_quote"]); self.assertEqual(k["quote_age_hours"], 96.0)
        pm = rows[("Bob Seat", "polymarket")]
        self.assertFalse(pm["stale_quote"])                           # Polymarket row is stamped with our retrieval time
        self.assertIsNone(rows[("Cara Unmapped", "kalshi")]["stale_quote"])
        rows2 = [{"fetch_status": "ok", "observed_at_utc": None}]
        self.assertEqual(daily.flag_stale(rows2, "2026-10-27T12:00:00Z")[0]["stale_quote"], "unknown")

    def test_delisted_market_is_market_not_found_not_an_outage(self):
        def fetch(url):
            if "kalshi.com" in url and "SENATEMI" in url:
                raise daily.HttpError(404, "Not Found")
            return make_fetch()(url)
        status, m = self.run_day("2026-10-23", fetch=fetch)
        rows = {(r["candidate_name"], r["provider"]): r for r in json.loads((self.base / "daily/2026-10-23/markets.json").read_text())["rows"]}
        self.assertEqual(rows[("Alice Example", "kalshi")]["fetch_status"], "market_not_found")
        self.assertIsNone(rows[("Alice Example", "kalshi")]["quoted_price"])        # never a made-up price
        self.assertEqual(m["market_errors"], 0)
        self.assertIsNone(status["sources"]["kalshi"]["last_error"] if "kalshi" in status["sources"] else None)

    def test_race_without_any_contract_has_no_quote_row_value(self):
        self.run_day("2026-10-23", fetch=make_fetch())
        r = [x for x in json.loads((self.base / "daily/2026-10-23/markets.json").read_text())["rows"] if x["candidate_name"] == "Cara Unmapped"]
        self.assertTrue(all(x["fetch_status"] == "unavailable" and x["quoted_price"] is None and x["bid"] is None for x in r))


class TestPolymarketMatch(unittest.TestCase):
    def test_wrong_person_or_wrong_race_is_rejected(self):
        ok = contracts.polymarket_match_ok
        self.assertTrue(ok("Will Aisha Wahab win the CA-14 House race?", "Aisha Wahab", "CA", "HOUSE-14"))
        self.assertTrue(ok("Will Scott Wiener win California's 11th congressional district?", "Scott Wiener", "CA", "HOUSE-11"))
        self.assertFalse(ok("Will Wahab Mohammed score in the NHL game tonight?", "Aisha Wahab", "CA", "HOUSE-14"))      # same surname, no race
        self.assertFalse(ok("Will Aisha Wahab win the CA-11 House race?", "Aisha Wahab", "CA", "HOUSE-14"))              # right person, wrong district
        self.assertFalse(ok("Will the Democrats win the CA-14 House race?", "Aisha Wahab", "CA", "HOUSE-14"))            # race named, person not
        self.assertTrue(ok("Will Ashley Moody win the Florida Senate seat?", "Ashley Moody", "FL", "SEN"))
        self.assertFalse(ok("Will Ashley Moody win the Georgia Senate seat?", "Ashley Moody", "FL", "SEN"))


class TestScheduleE(unittest.TestCase):
    def row(self, **k):
        r = {"transaction_id": "T1", "expenditure_amount": 1000.0, "expenditure_date": "2026-10-01", "candidate_id": "H0FL01", "support_oppose_indicator": "O",
             "is_notice": False, "memo_code": None, "filing_form": "F3X"}
        r.update(k); return r
    def test_notice_and_periodic_collapse_to_one_and_notice_is_preferred(self):
        kept, memo = schedule_e.dedupe([self.row(), self.row(is_notice=True, filing_form="F24")])
        self.assertEqual(len(kept), 1); self.assertEqual(kept[0]["filing_form"], "F24"); self.assertEqual(kept[0]["duplicates_collapsed"], 1); self.assertEqual(memo, 0)
    def test_memo_rows_are_dropped_and_counted(self):
        kept, memo = schedule_e.dedupe([self.row(), self.row(memo_code="X", transaction_id="T2")])
        self.assertEqual(len(kept), 1); self.assertEqual(memo, 1)
    def test_a_different_amount_is_a_different_row(self):
        kept, _ = schedule_e.dedupe([self.row(), self.row(expenditure_amount=1200.0)])
        self.assertEqual(len(kept), 2)
    def test_support_and_oppose_are_never_merged(self):
        kept, _ = schedule_e.dedupe([self.row(), self.row(support_oppose_indicator="S")])
        self.assertEqual(len(kept), 2)
    @unittest.skipUnless((ROOT / "tools/elections/export_packet.py").exists(), "export script not deployed here")
    def test_udp_and_aipac_ids_flag_committee_identity_only(self):
        src = (ROOT / "tools/elections/export_packet.py").read_text(encoding="utf-8")
        self.assertIn('"C00799031": "United Democracy Project (UDP)"', src)
        self.assertIn("not established in FEC data and is not asserted here", src)


@unittest.skipUnless((ROOT / "release/research_packet/tip_grades.csv").exists(), "run tools/elections/export_packet.py first")
class TestTipGradeProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        P = ROOT / "release/research_packet"
        cls.g = list(csv.DictReader(open(P / "tip_grades.csv", encoding="utf-8")))
        cls.d = list(csv.DictReader(open(P / "tip_issue_definitions.csv", encoding="utf-8")))
        cls.cand = json.loads((ROOT / "data/elections/FL/candidates.json").read_text(encoding="utf-8"))["candidates"]
    def test_six_issues_and_every_federal_candidate_has_six_rows(self):
        self.assertEqual(len(self.d), 6)
        fed = [c for c in self.cand if c["office"] != "governor"]
        per = {}
        for r in self.g: per.setdefault(r["candidate_id"], []).append(r["issue_slug"])
        self.assertEqual(len(per), len(fed))
        self.assertTrue(all(sorted(v) == sorted(x["slug"] for x in json.loads((ROOT / "data/elections/FL/candidates.json").read_text(encoding="utf-8"))["issues"]) for v in per.values()))
    def test_grade_comes_from_the_congressional_profile_never_a_governor_id(self):
        for r in self.g:
            self.assertNotIn("/candidates/GOV-FL", r["profile_holding_grade"])
            self.assertTrue(r["profile_holding_grade"].endswith("/" + r["candidate_id"]) or r["profile_holding_grade"] == "")
    def test_not_graded_is_blank_never_zero(self):
        for r in self.g:
            if r["grade_state"] == "not_graded":
                self.assertEqual((r["grade_label"], r["grade_value"], r["supporting_source_links"]), ("", "", ""))
            else:
                self.assertTrue(r["grade_label"] and r["grade_timestamp"] and int(r["evidence_count_recorded"]) >= 1)


if __name__ == "__main__":
    unittest.main()
