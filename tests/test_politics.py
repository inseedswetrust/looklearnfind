"""Politics 2.0 contract tests (docs/politics/INDEX.md). Uses the built dist/ when present."""
import datetime, json, pathlib, shutil, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools" / "qa"))
import politics
import politics_contract_check as pc

FIX = ROOT / "tests" / "fixtures" / "politics"
TODAY = datetime.date(2026, 11, 6)
DIST = ROOT / "dist"


def rec(**kw):
    r = json.loads((FIX / "good.json").read_text(encoding="utf-8")); r.update(kw); return r


class Daily(unittest.TestCase):
    def check(self, **kw):
        d = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        for i, r in enumerate(kw.pop("recs", [rec(**kw)])):
            (d / f"{i}.json").write_text(json.dumps(r), encoding="utf-8")
        return pc.check_daily_records(d, TODAY)

    def test_good_record_passes(self):
        self.assertEqual(self.check(), [])

    def test_missing_fields_fail(self):
        self.assertTrue(any("missing" in p for p in self.check(editor="")))
        self.assertTrue(any("missing" in p for p in self.check(sources=[])))
        self.assertTrue(any("missing" in p for p in self.check(update_log=[])))

    def test_source_needs_date(self):
        self.assertTrue(any("source" in p for p in self.check(sources=[{"url": "https://x.org", "label": "x"}])))

    def test_editor_differs_from_author(self):
        self.assertTrue(any("editor" in p for p in self.check(editor="Writer")))

    def test_duplicate_story_id(self):
        self.assertTrue(any("duplicate" in p for p in self.check(recs=[rec(), rec()])))

    def test_future_and_stale(self):
        self.assertTrue(any("future" in p for p in self.check(date="2026-11-09")))
        self.assertTrue(any("stale" in p for p in self.check(date="2026-10-20")))

    def test_loader_skips_drafts_and_reports_incomplete(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        (d / "a.json").write_text(json.dumps(rec(status="draft")), encoding="utf-8")
        (d / "b.json").write_text(json.dumps(rec(story_id="")), encoding="utf-8")
        out, bad = politics.load_daily(d)
        self.assertEqual(out, []); self.assertEqual(len(bad), 1)


class Policy(unittest.TestCase):
    def test_manifest_current(self):
        self.assertEqual(pc.check_manifest(), [])

    def test_changed_file_without_manifest_fails(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        shutil.copytree(pc.POLICY, d / "p")
        (d / "p" / "INDEX.md").write_text("tampered", encoding="utf-8")
        self.assertTrue(any("changed since the manifest" in p for p in pc.check_manifest(d / "p")))
        (d / "p" / "STATUS").write_text("STATUS=DRAFT\n", encoding="utf-8")
        self.assertTrue(any("not LOCKED" in p for p in pc.check_manifest(d / "p")))


@unittest.skipUnless((DIST / "politics" / "index.html").exists(), "run build.py first")
class Built(unittest.TestCase):
    def test_contract_clean(self):
        self.assertEqual(pc.check_pages(DIST, pc.POLICY / "URL_BASELINE.txt"), [])

    def test_landing_has_intentional_empty_states_not_cards(self):
        h = (DIST / "politics" / "index.html").read_text(encoding="utf-8")
        self.assertIn("No Daily Signal has been published yet", h)
        self.assertNotIn("pol-daily", h)

    def test_broken_dist_is_caught(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        shutil.copytree(DIST / "politics", d / "politics")
        p = d / "politics" / "index.html"
        p.write_text(p.read_text(encoding="utf-8").replace("data-llf-global-shell", "x-shell").replace('id="watch-read-verify"', 'id="gone"'), encoding="utf-8")
        probs = pc.check_pages(d)
        self.assertTrue(any("shared shell" in x for x in probs))
        self.assertTrue(any("watch-read-verify" in x for x in probs))

    def test_result_language_is_caught(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        shutil.copytree(DIST / "politics", d / "politics")
        p = d / "politics" / "index.html"
        p.write_text(p.read_text(encoding="utf-8").replace("<main", "<main data-x=1", 1).replace("</main>", "<p>The challenger won.</p></main>", 1), encoding="utf-8")
        self.assertTrue(any("result language" in x for x in pc.check_pages(d)))

    def test_search_includes_hubs(self):
        urls = {x["url"] for x in json.loads((DIST / "search-index.json").read_text(encoding="utf-8"))}
        for u in ("/politics/", "/politics/daily/", "/elections/2026/michigan/", "/elections/2026/pennsylvania/senate/" if False else "/elections/2026/minnesota/senate/"):
            self.assertIn(u, urls)

    def test_approved_record_renders_page(self):
        calls = {}
        def shell(title, desc, path, body, **k): calls[path] = body
        html = politics.render_daily_record(rec(), lambda s: s)
        self.assertIn("DS-2026-11-05-001", html); self.assertIn("Update log", html); self.assertIn("Edited by Editor", html)


if __name__ == "__main__":
    unittest.main()
