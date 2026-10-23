"""Fixture tests for tools/dark_horse/daily.py. Run: python3 -m unittest tests/test_dark_horse.py -v  (no network)."""
import csv, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "dark_horse"))
import daily

HEAD = ["candidate_name", "state", "race", "race_key", "tip_candidate_id", "current_ballot_verified", "monitor"]
WATCH = [
    ["Alice Example", "MI", "SEN", "2026-S-MI", "S6MI00001", "yes", "yes"],
    ["Bob Seat", "NY", "HOUSE-10", "2026-H-NY-10", "H6NY10001", "yes", "yes"],
    ["Cara Unmapped", "TX", "HOUSE-30", "2026-H-TX-30", "H6TX30001", "yes", "yes"],
    ["Dan Unverified", "CA", "HOUSE-22", "2026-H-CA-22", "H6CA22001", "no", "yes"],
]
CMAP = {
    "S6MI00001": {"kalshi_ticker": "SENATEMI-26-D", "kalshi_contract_kind": "party_winner", "kalshi_outcome": "Alice Example", "checked_at": "2026-10-23"},
    "H6NY10001": {"kalshi_ticker": "KXHOUSERACE-NY10-26-D", "kalshi_contract_kind": "party_winner", "polymarket_token_id": "tok123", "polymarket_contract_kind": "candidate_individual", "checked_at": "2026-10-23"},
}

def kmarket(price, bid="0.60", ask="0.70"):
    return {"market": {"last_price_dollars": price, "yes_bid_dollars": bid, "yes_ask_dollars": ask, "volume_fp": "10", "status": "active", "rules_primary": "If a representative of the Democratic party is sworn in ...", "updated_time": "2026-10-23T12:00:00Z"}}

def make_fetch(kprice="0.65", fail=None, polls=None, empty_markets=False):
    def fetch(url):
        if fail and fail in url:
            raise daily.HttpError(429, "Too Many Requests")
        if "kalshi.com" in url:
            if empty_markets:
                return {"market": {}}, b"{}"
            body = kmarket(kprice)
        elif "gamma-api" in url:
            body = [{"volume": "100", "liquidity": "50", "closed": False}]
        elif "last-trade-price" in url:
            body = {} if empty_markets else {"price": "0.40"}
        elif "clob.polymarket.com/book" in url:
            body = {"bids": [{"price": "0.39"}], "asks": [{"price": "0.42"}]}
        elif "votehub" in url:
            body = polls if polls is not None else []
        else:
            raise AssertionError(url)
        return body, json.dumps(body).encode()
    return fetch

class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        with open(self.base / "watchlist.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(HEAD); w.writerows(WATCH)
        (self.base / "contract_map.json").write_text(json.dumps(CMAP))
    def tearDown(self): self.tmp.cleanup()
    def run_day(self, day, **kw):
        return daily.run(day, base=self.base, now=f"{day}T12:00:00Z", **kw)
    def rows(self, day): return json.loads((self.base / "daily" / day / "markets.json").read_text())["rows"]

    def test_party_contract_is_labeled_and_unmapped_is_unavailable(self):
        self.run_day("2026-10-23", fetch=make_fetch())
        r = {(x["candidate_name"], x["provider"]): x for x in self.rows("2026-10-23")}
        self.assertEqual(r[("Alice Example", "kalshi")]["contract_kind"], "party_winner")
        self.assertEqual(r[("Alice Example", "kalshi")]["fetch_status"], "ok")
        self.assertEqual(r[("Cara Unmapped", "kalshi")]["fetch_status"], "unavailable")
        self.assertIsNone(r[("Cara Unmapped", "kalshi")]["quoted_price"])        # unavailable is never 0
        self.assertNotIn(("Dan Unverified", "kalshi"), r)                        # unverified ballot is not monitored
        self.assertEqual(r[("Bob Seat", "polymarket")]["contract_kind"], "candidate_individual")

    def test_missing_poll_is_no_poll_found_not_zero(self):
        self.run_day("2026-10-23", fetch=make_fetch())
        cov = json.loads((self.base / "daily" / "2026-10-23" / "polls.json").read_text())["coverage"]
        self.assertEqual(cov["S6MI00001"]["status"], "no_poll_found")
        self.assertEqual(cov["S6MI00001"]["polls"], 0)

    def test_partisan_sponsor_stays_visible(self):
        polls = [{"id": "p1", "subject": "2026 Michigan", "seat_name": None, "pollster": "X", "sponsors": ["Some PAC"], "partisan": "REP", "internal": False, "sample_size": 600,
                  "population": "lv", "start_date": "2026-10-01", "end_date": "2026-10-03", "url": "https://example.org/poll.pdf", "created_at": "2026-10-04",
                  "answers": [{"choice": "Alice Example", "pct": 44.0}, {"choice": "Other", "pct": 46.0}]}]
        self.run_day("2026-10-23", fetch=make_fetch(polls=polls))
        p = json.loads((self.base / "daily" / "2026-10-23" / "polls.json").read_text())["polls"]
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0]["sponsor"], ["Some PAC"]); self.assertEqual(p[0]["partisan_sponsor"], "REP")
        self.assertEqual(p[0]["original_poll_url"], "https://example.org/poll.pdf")

    def test_house_polls_match_on_district_seat(self):
        polls = [{"id": "h1", "subject": "2026 NY-10", "seat_name": "NY-10", "pollster": "Y", "sponsors": [], "partisan": None, "internal": False, "sample_size": 500, "population": "lv",
                  "start_date": "2026-10-01", "end_date": "2026-10-02", "url": "https://example.org/h.pdf", "created_at": "2026-10-03",
                  "answers": [{"choice": "Bob Seat", "pct": 60.0}, {"choice": "Rival", "pct": 30.0}]},
                 {"id": "h2", "subject": "2026 NY-11", "seat_name": "NY-11", "pollster": "Z", "sponsors": [], "partisan": None, "internal": False, "sample_size": 500, "population": "lv",
                  "start_date": "2026-10-01", "end_date": "2026-10-02", "url": "https://example.org/other.pdf", "created_at": "2026-10-03", "answers": [{"choice": "Bob Seat", "pct": 1.0}]}]
        self.run_day("2026-10-23", fetch=make_fetch(polls=polls))
        p = json.loads((self.base / "daily" / "2026-10-23" / "polls.json").read_text())["polls"]
        self.assertEqual([x["aggregator_poll_id"] for x in p], ["h1"])

    def test_empty_data_does_not_overwrite_latest(self):
        self.run_day("2026-10-23", fetch=make_fetch())
        before = (self.base / "latest.json").read_text()
        status, _ = self.run_day("2026-10-24", fetch=make_fetch(empty_markets=True))
        self.assertEqual((self.base / "latest.json").read_text(), before)
        self.assertFalse(status["latest_pointer_updated"])

    def test_rate_limit_keeps_previous_data_and_records_error(self):
        self.run_day("2026-10-23", fetch=make_fetch())
        status, m = self.run_day("2026-10-24", fetch=make_fetch(fail="kalshi.com"))
        self.assertTrue((self.base / "daily" / "2026-10-23" / "markets.json").exists())
        self.assertGreater(m["market_errors"], 0)
        self.assertIn("429", status["sources"]["kalshi"]["last_error"])
        self.assertIsNotNone(status["sources"]["kalshi"]["last_success_at"])     # previous success preserved
        self.assertEqual(json.loads((self.base / "latest.json").read_text())["date"], "2026-10-23")  # a provider failed: prior complete day stays latest
        self.assertFalse(status["latest_pointer_updated"])

    def test_two_runs_make_two_folders_and_same_contract_deltas(self):
        self.run_day("2026-10-23", fetch=make_fetch(kprice="0.60"))
        self.run_day("2026-10-24", fetch=make_fetch(kprice="0.70"))
        self.assertTrue((self.base / "daily" / "2026-10-23").is_dir() and (self.base / "daily" / "2026-10-24").is_dir())
        a = json.loads((self.base / "daily" / "2026-10-24" / "alerts.json").read_text())["alerts"]
        k = [x for x in a if x["provider"] == "kalshi" and x["candidate_id"] == "S6MI00001"]
        self.assertEqual(len(k), 1); self.assertAlmostEqual(k[0]["change"], 0.10, places=3)
        self.assertEqual(k[0]["possible_events"], [])                            # no causes asserted

    def test_no_tip_id_is_guessed_from_name(self):
        self.assertEqual(daily.key_of({"state": "TX", "race": "HOUSE-30", "candidate_name": "Cara Unmapped"}), "no_tip:TX:HOUSE-30:Cara Unmapped")

    def test_dry_run_calls_no_api(self):
        def boom(url): raise AssertionError("network used in dry run")
        self.run_day("2026-10-23", dry=True, fetch=boom)
        self.assertFalse((self.base / "latest.json").exists())

if __name__ == "__main__":
    unittest.main()
