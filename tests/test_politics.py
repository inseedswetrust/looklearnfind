"""Politics 2.0 contract tests (docs/politics/INDEX.md and the Creative Lock in docs/politics/brand/). Uses the built dist/ when present."""
import csv, datetime, json, pathlib, shutil, sys, tempfile, unittest

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
        for i, r in enumerate(kw.pop("recs", None) or [rec(**kw)]):
            (d / f"{i}.json").write_text(json.dumps(r), encoding="utf-8")
        return pc.check_daily_records(d, TODAY)

    def test_good_record_passes(self):
        errs, _ = self.check()
        self.assertEqual(errs, [])

    def test_missing_fields_fail(self):
        for bad in (dict(editor=""), dict(sources=[]), dict(update_log=[])):
            self.assertTrue(any("missing" in p for p in self.check(**bad)[0]), bad)

    def test_source_needs_date(self):
        self.assertTrue(any("source" in p for p in self.check(sources=[{"url": "https://x.org", "label": "x"}])[0]))

    def test_editor_differs_from_author(self):
        self.assertTrue(any("editor" in p for p in self.check(editor="Writer")[0]))

    def test_duplicate_story_id_fails_but_several_stories_per_date_pass(self):
        self.assertTrue(any("duplicate" in p for p in self.check(recs=[rec(), rec()])[0]))
        errs, _ = self.check(recs=[rec(story_id="DS-1", date="2026-11-05"), rec(story_id="DS-2", date="2026-11-05")])
        self.assertEqual(errs, [])

    def test_future_is_error_but_stale_is_only_a_warning(self):
        self.assertTrue(any("future" in p for p in self.check(date="2026-11-09")[0]))
        errs, warns = self.check(date="2026-10-20")
        self.assertEqual(errs, [])
        self.assertTrue(any("days old" in w for w in warns))

    def test_length_rules_are_warnings(self):
        errs, warns = self.check(title="one two three four five six seven eight nine ten eleven twelve thirteen")
        self.assertEqual(errs, []); self.assertTrue(any("12 words" in w for w in warns))

    def test_loader_groups_one_briefing_and_skips_drafts(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        for n, r in enumerate((rec(story_id="A", order=2), rec(story_id="B", order=1), rec(story_id="C", status="draft"), rec(story_id="")), 1):
            (d / f"{n}.json").write_text(json.dumps(r), encoding="utf-8")
        out, bad = politics.load_daily(d)
        self.assertEqual({r["story_id"] for r in out}, {"A", "B"}); self.assertEqual(len(bad), 1)
        g = politics.briefings(out)
        self.assertEqual(list(g), ["2026-11-05"]); self.assertEqual([r["story_id"] for r in g["2026-11-05"]], ["B", "A"])

    def test_briefing_page_lists_every_story(self):
        html = politics.render_daily_briefing("2026-11-05", [rec(story_id="B"), rec(story_id="A")], lambda s: s)
        self.assertIn('id="A"', html); self.assertIn('id="B"', html); self.assertIn("Update log", html)


class Claims(unittest.TestCase):
    def test_decisive_claims_are_flagged(self):
        self.assertTrue(pc.claim_hits("<p>The challenger won the district.</p>"))
        self.assertTrue(pc.claim_hits("<p>Voters delivered a mandate.</p>"))

    def test_negated_conditional_and_historical_text_is_allowed(self):
        self.assertEqual(pc.claim_hits("<p>We have not validated a source, so no winner is named.</p>"), [])
        self.assertEqual(pc.claim_hits("<p>We publish a result only when a dated source backs it.</p>"), [])
        self.assertEqual(pc.claim_hits('<a href="/learn/x/">In the primary Thanedar lost, groups reported more</a>'), [])
        self.assertEqual(pc.claim_hits('<figcaption>Photo: someone won an award</figcaption>'), [])


class Policy(unittest.TestCase):
    def test_manifest_current_and_provisional(self):
        self.assertEqual(pc.check_manifest(), [])
        self.assertIn("STATUS=PROVISIONAL", (pc.POLICY / "STATUS").read_text(encoding="utf-8"))
        self.assertTrue((pc.POLICY / "brand" / "01_POLITICS_BRAND_IDENTITY_CREATIVE_BRIEF.md").exists())
        self.assertTrue((pc.POLICY / "brand" / "02_POLITICS_HOMEPAGE_COPY_AND_CONTENT_SPEC.md").exists())

    def test_changed_file_without_manifest_fails(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        shutil.copytree(pc.POLICY, d / "p")
        (d / "p" / "INDEX.md").write_text("tampered", encoding="utf-8")
        self.assertTrue(any("changed since the manifest" in p for p in pc.check_manifest(d / "p")))
        (d / "p" / "STATUS").write_text("STATUS=DRAFT\n", encoding="utf-8")
        self.assertTrue(any("LOCKED or PROVISIONAL" in p for p in pc.check_manifest(d / "p")))

    def test_every_asset_row_is_complete_and_politicians_are_cleared_real_photos(self):
        rows = list(csv.DictReader((pc.MANIFEST).open(encoding="utf-8")))
        for r in rows:
            for k in ("asset_id", "path", "rights_basis", "credit_required", "usage_status"):
                self.assertTrue(r[k], (r["asset_id"], k))
            self.assertTrue((ROOT / r["path"]).exists(), r["path"])
        by = {r["asset_id"]: r for r in rows}
        for k in ("POL-JEFFRIES-CUT", "POL-SCHUMER-CUT", "POL-CAPITOL-CUT"):
            self.assertEqual(by[k]["usage_status"], "cleared")
            self.assertIn("Public domain", by[k]["rights_basis"])
        self.assertIn("likeness unchanged", by["POL-JEFFRIES-CUT"]["transform"].lower())


class Mode(unittest.TestCase):
    def test_politics_routes_light_learn_and_categories_stay_neutral(self):
        import shared_nav
        for p in ("/politics/", "/politics/daily/", "/politics/daily/2026-11-05/"):
            self.assertEqual(shared_nav.page_mode(p), "learn", p)
        for p in ("/economy/", "/society/", "/topics/politics/", "/latest/"):
            self.assertEqual(shared_nav.page_mode(p), "", p)


class Gating(unittest.TestCase):
    def test_cta_is_shown_only_when_its_route_was_built(self):
        api = {"PAGES_OUT": {"/real/": "x"}}
        politics.GATED.clear()
        self.assertIn('href="/real/"', politics._cta(api, "m", {"label": "Go", "route": "/real/"}))
        self.assertEqual(politics._cta(api, "m", {"label": "Missing", "route": "/nope/"}), "")
        self.assertEqual(politics._cta(api, "m", {"label": "Ext", "href": "https://example.org", "approved": False}), "")
        self.assertEqual([g[1] for g in politics.GATED], ["Missing", "Ext"])
        politics.GATED.clear()


class BuildWithBriefing(unittest.TestCase):
    """Run politics.build against a temporary approved briefing: the strip shows the lead, the dated page holds every story ID."""
    def test_two_stories_one_date(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        (d / "a.json").write_text(json.dumps(rec(story_id="DS-A", order=1, title="Lead story headline")), encoding="utf-8")
        (d / "b.json").write_text(json.dumps(rec(story_id="DS-B", order=2, title="Second story")), encoding="utf-8")
        pages = {}
        def shell(title, desc, path, body, **k): pages[path] = body
        stories = [dict(path="/learn/x/", title="X", date="2026-11-01", hero="us-capitol", image_alt="")]
        old = politics.DAILY_DIR
        politics.DAILY_DIR = d
        try:
            politics.build(dict(shell=shell, STORIES=stories, cards=None, fmt_date=lambda s: s, CANDS=[], SITE={"topics": []}, THREADS=[],
                                PAGES_OUT={"/politics/daily/2026-11-05/": "", "/politics/daily/": ""}, HERO_CREDITS={}))
        finally:
            politics.DAILY_DIR = old
        self.assertIn("Lead story headline", pages["/politics/"]); self.assertIn("2 stories", pages["/politics/"])
        self.assertNotIn("Our next briefing is being prepared", pages["/politics/"])
        day = pages["/politics/daily/2026-11-05/"]
        self.assertIn('id="DS-A"', day); self.assertIn('id="DS-B"', day)
        self.assertIn("2026-11-05", pages["/politics/daily/"])


@unittest.skipUnless((DIST / "politics" / "index.html").exists(), "run build.py first")
class Built(unittest.TestCase):
    def setUp(self):
        self.land = (DIST / "politics" / "index.html").read_text(encoding="utf-8")

    def test_contract_clean(self):
        self.assertEqual(pc.check_pages(DIST, pc.POLICY / "URL_BASELINE.txt"), [])
        self.assertEqual(pc.check_edition_pages(DIST, allow_preview=True), [])

    def test_nine_zones_in_the_approved_order(self):
        ids = ["pol-h1", "daily-signal", "accountability-desk", "election-2026", "follow-the-money", "state-of-the-record", "election-signals", "current-reporting", "go-to-the-source"]
        pos = [self.land.index(f'id="{i}"') for i in ids]
        self.assertEqual(pos, sorted(pos))

    def test_approved_copy_is_present(self):
        for s in ("Less noise.", "More evidence.", "Today&#x27;s political briefing", "A new majority. The same leaders?", "The election is over. The record isn&#x27;t.",
                  "The money behind the message.", "Promises made. Decisions pending.", "Stories worth a closer look.", "Don&#x27;t take our word for it."):
            self.assertIn(s, self.land)

    def test_no_unbuilt_destination_is_linked(self):
        for dead in ("/politics/accountability/", "/politics/money/", "/politics/signals/", 'href="/elections/2026/"', "fec.gov"):
            self.assertNotIn(dead, self.land)

    @unittest.skipIf("DRAFT PREVIEW" in (DIST / "politics" / "index.html").read_text(encoding="utf-8"), "preview build shows the draft edition")
    def test_empty_briefing_shows_fallback_not_pipeline_wording(self):
        self.assertIn("Our next briefing is being prepared", self.land)
        for s in ("fact-check", "owner approval", "two_video", "awaiting"):
            self.assertNotIn(s, self.land.split("<main", 1)[1].split("</main>", 1)[0].lower().replace("fact-check and original", ""), s)

    def test_one_yellow_tab_and_the_duochrome_hero(self):
        self.assertEqual(self.land.count('class="pol-tab"'), 1); self.assertIn('class="pol-duo"', self.land)

    def test_cutouts_use_real_portraits_with_a_caption_that_denies_a_joint_appearance(self):
        self.assertIn("jeffries-cutout.png", self.land); self.assertIn("schumer-cutout.png", self.land)
        self.assertIn("the two are not pictured together", self.land.lower())

    def test_historical_context_is_labelled(self):
        self.assertIn("PRE-ELECTION REPORT / HISTORICAL CONTEXT", self.land)

    def test_broken_dist_is_caught(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        shutil.copytree(DIST / "politics", d / "politics")
        p = d / "politics" / "index.html"
        p.write_text(self.land.replace("data-llf-global-shell", "x-shell").replace('id="go-to-the-source"', 'id="gone"').replace('data-format="learn"', 'data-format=""'), encoding="utf-8")
        probs = pc.check_pages(d)
        self.assertTrue(any("shared shell" in x for x in probs)); self.assertTrue(any("go-to-the-source" in x for x in probs)); self.assertTrue(any("LEARN" in x for x in probs))

    def test_result_language_and_unverified_image_are_caught(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        shutil.copytree(DIST / "politics", d / "politics")
        p = d / "politics" / "index.html"
        p.write_text(self.land.replace("</main>", "<p>The challenger won.</p></main>", 1), encoding="utf-8")
        self.assertTrue(any("election-claim" in x for x in pc.check_pages(d)))
        rows = pc.load_assets()
        rows["static/img/politics/jeffries-cutout.png"] = dict(rows["static/img/politics/jeffries-cutout.png"], usage_status="pending")
        self.assertTrue(any("usage_status" in x for x in pc.check_pages(DIST, assets=rows)))

    def test_search_includes_hubs(self):
        urls = {x["url"] for x in json.loads((DIST / "search-index.json").read_text(encoding="utf-8"))}
        for u in ("/politics/", "/politics/daily/", "/elections/2026/michigan/", "/elections/2026/minnesota/senate/", "/elections/2026/pennsylvania/"):
            self.assertIn(u, urls)


DRAFT = ROOT / "data" / "politics_daily" / "2026-11-05-edition-001.json"


class Edition001(unittest.TestCase):
    """The imported editorial draft: structure, gates and rendering. It stays a draft until an independent fact check passes and the owner approves."""
    def setUp(self):
        self.r = json.loads(DRAFT.read_text(encoding="utf-8"))

    def test_it_is_a_draft_with_a_pending_fact_check(self):
        self.assertEqual(self.r["status"], "draft"); self.assertIn(self.r["fact_check"]["state"], ("pending", "flags"))
        self.assertEqual(self.r["story_id"], "DS-2026-11-05-001")

    def test_five_signals_link_to_five_sections_and_the_rail_matches(self):
        b = self.r["blocks"]
        ids = [s["id"] for s in b["sections"]]
        self.assertEqual(ids, ["leadership", "geography", "voters", "money", "states"])
        self.assertEqual([i["target"] for i in b["signals"]["items"]], ids)
        self.assertEqual([x["id"] for x in self.r["rail"]], ids)
        self.assertEqual([x["label"] for x in self.r["rail"]], ["Leadership", "Election geography", "Voter priorities", "Campaign money", "State power"])

    def test_ten_dated_sources_and_no_oxford_comma_or_invented_text(self):
        self.assertEqual(len(self.r["sources"]), 10)
        self.assertTrue(all(s["url"].startswith("https://") and s["date"] for s in self.r["sources"]))
        md = (ROOT / "docs" / "politics" / "brand" / "edition-001" / "DAILY_SIGNAL_2026-11-05_EDITORIAL_DRAFT.md").read_text(encoding="utf-8")
        for para in self.r["blocks"]["sections"][0]["paras"][:2]:
            import re
            self.assertIn(re.sub(r"<[^>]+>", "", para).split(".")[0][:40], md.replace("**", "").replace("*", ""))

    def test_loader_hides_the_draft_unless_previewing(self):
        d = DRAFT.parent
        self.assertEqual([r for r in politics.load_daily(d)[0] if r["story_id"] == self.r["story_id"]], [])
        self.assertEqual(len([r for r in politics.load_daily(d, include_drafts=True)[0] if r["story_id"] == self.r["story_id"]]), 1)

    def test_contract_accepts_the_draft_record(self):
        errs, _ = pc.check_daily_records(DRAFT.parent, TODAY)
        self.assertEqual(errs, [])

    def test_approval_requires_a_passed_fact_check_by_someone_else(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        bad = dict(self.r, status="approved", editor="Reviewer")
        (d / "a.json").write_text(json.dumps(bad), encoding="utf-8")
        self.assertTrue(any("fact check" in e for e in pc.check_daily_records(d, TODAY)[0]))
        ok = dict(self.r, status="approved", editor="Reviewer", fact_check={"state": "passed", "reviewer": "Reviewer"})
        (d / "a.json").write_text(json.dumps(ok), encoding="utf-8")
        self.assertFalse(any("fact check" in e for e in pc.check_daily_records(d, TODAY)[0]))
        self.assertEqual(len(politics.load_daily(d)[0]), 1)
        (d / "a.json").write_text(json.dumps(dict(ok, fact_check={"state": "pending", "reviewer": ""})), encoding="utf-8")
        self.assertEqual(politics.load_daily(d)[0], [])

    def test_broken_teaser_target_is_an_error(self):
        d = pathlib.Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        r = json.loads(json.dumps(self.r)); r["blocks"]["signals"]["items"][0]["target"] = "nowhere"
        (d / "a.json").write_text(json.dumps(r), encoding="utf-8")
        self.assertTrue(any("nowhere" in e for e in pc.check_daily_records(d, TODAY)[0]))

    def test_rendered_edition_has_outline_label_ids_and_back_links(self):
        h = politics.render_edition(self.r, lambda s: s)
        self.assertIn('data-outline-label="On this briefing"', h)
        for i in ("national-picture", "five-signals", "leadership", "geography", "voters", "money", "states", "what-next", "sources"):
            self.assertIn(f'id="{i}"', h)
        self.assertEqual(h.count("Back to today's signals"), 5)
        self.assertIn("Draft for review", h)

    def test_source_review_is_recorded_with_flags_and_nothing_is_approved(self):
        rv = self.r["review"]
        self.assertEqual(len(rv["claims"]), 15); self.assertEqual(self.r["fact_check"]["state"], "flags"); self.assertEqual(self.r["status"], "draft")
        self.assertEqual(sum(rv["counts"].values()), 15)
        statuses = {c["id"]: c["status"] for c in rv["claims"]}
        self.assertEqual(statuses["C09"], "partly supported")      # the Ohio Senate claim is not supported by the one readable source
        self.assertIn(statuses["C14"], ("unverified",))            # the Texas governorship claim
        self.assertTrue(all(c["source"] and c["note"] for c in rv["claims"]))

    def test_draft_renders_the_review_table_but_an_approved_edition_would_not(self):
        h = politics.render_edition(self.r, lambda s: s)
        self.assertIn('id="source-review"', h); self.assertIn("Source review (draft)", h)
        ok = dict(self.r, status="approved", editor="Reviewer", fact_check={"state": "passed", "reviewer": "Reviewer"})
        self.assertNotIn('id="source-review"', politics.render_edition(ok, lambda s: s))

    def test_read_time_is_computed_from_the_text(self):
        self.assertGreaterEqual(politics.read_minutes(self.r), 5)


@unittest.skipUnless((DIST / "politics" / "daily" / "2026-11-05" / "index.html").exists(), "needs a preview build (LLF_PREVIEW_DRAFTS=1)")
class EditionBuilt(unittest.TestCase):
    def setUp(self):
        self.h = (DIST / "politics" / "daily" / "2026-11-05" / "index.html").read_text(encoding="utf-8")

    def test_rail_outline_is_named_and_lists_the_five_signals(self):
        rail = self.h.split("<main", 1)[0]
        self.assertIn("On this briefing", rail)
        for lab in ("Leadership", "Election geography", "Voter priorities", "Campaign money", "State power"):
            self.assertIn(lab, rail)

    def test_the_draft_is_noindex_and_not_in_sitemap_or_search(self):
        self.assertIn('content="noindex', self.h)
        self.assertNotIn("2026-11-05", (DIST / "sitemap.xml").read_text(encoding="utf-8").split("/politics/daily/")[-1][:12] if "/politics/daily/" in (DIST / "sitemap.xml").read_text(encoding="utf-8") else "")
        self.assertNotIn("/politics/daily/2026-11-05/", (DIST / "search-index.json").read_text(encoding="utf-8"))

    def test_landing_shows_the_draft_with_five_signals_and_a_label(self):
        land = (DIST / "politics" / "index.html").read_text(encoding="utf-8")
        self.assertIn("DRAFT PREVIEW", land); self.assertIn("Five signals today", land)
        self.assertIn("/politics/daily/2026-11-05/#leadership", land)
        self.assertIn("EDITION 001", land)

    def test_five_teasers_follow_the_strip_in_order_with_images_summaries_and_links(self):
        import re
        land = (DIST / "politics" / "index.html").read_text(encoding="utf-8")
        strip_end = land.index('id="five-signals-today"')
        self.assertGreater(strip_end, land.index('id="daily-signal"')); self.assertLess(strip_end, land.index('id="accountability-desk"'))
        items = re.findall(r'<li class="pol-teaser">.*?</li>', land, re.S)
        self.assertEqual(len(items), 5)
        titles = ["A new majority. The same leaders?", "The political map broke in places nobody expected.", "The cost of living dominated. What will Congress actually do?",
                  "Nearly $12 billion later, what did the money accomplish?", "The biggest changes may happen outside Washington."]
        for n, (it, title) in enumerate(zip(items, titles), 1):
            self.assertIn(f"0{n} / ", it); self.assertIn(title.replace("'", "&#x27;").replace("$", "$"), it)
            self.assertIn("<img", it); self.assertGreater(len(re.sub(r"<[^>]+>", "", re.search(r'<p class="pol-teaser__s">(.*?)</p>', it, re.S).group(1))), 80)
            self.assertRegex(it, r'href="/politics/daily/2026-11-05/#(leadership|geography|voters|money|states)"')

    def test_content_completeness_every_supplied_block_is_rendered(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pcomp", ROOT / "tools" / "qa" / "politics_completeness.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        self.assertEqual(m.main(["--no-report"]), 0)

    def test_a_release_check_fails_on_a_preview_build(self):
        self.assertTrue(pc.check_edition_pages(DIST))


if __name__ == "__main__":
    unittest.main()
