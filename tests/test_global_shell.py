"""Global shell: every generated page receives the one shared rail, mobile bar and Explore sheet from build.shell(); nothing is per template.

Run: python3 -m unittest tests/test_global_shell.py -v    (builds dist/ first if it is missing or was built without the shell)
Render-level checks (Playwright, six widths): python3 tools/qa/shell_check.py   or   LLF_RENDER_TESTS=1 python3 -m unittest tests/test_global_shell.py
Design rules: docs/design/LLF_GLOBAL_SHELL.md
"""
import os, re, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DIST = ROOT / "dist"
import shared_nav  # noqa: E402


def pages():
    return {str(p.relative_to(DIST)).replace("\\", "/"): p.read_text(encoding="utf-8") for p in DIST.rglob("*.html")}


class ShellInBuiltSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        idx = DIST / "index.html"
        if not idx.exists() or "data-llf-global-shell" not in idx.read_text(encoding="utf-8"):
            subprocess.run([sys.executable, "build.py", "--strict"], cwd=ROOT, check=True, capture_output=True, env={**os.environ, "PYTHONUTF8": "1"})
        cls.pages = pages()

    def test_there_are_pages(self):
        self.assertGreaterEqual(len(self.pages), 200)

    def test_every_page_has_exactly_one_shell(self):
        bad = []
        for rel, h in self.pages.items():
            if h.count("data-llf-global-shell") != 1 or h.count(f'data-llf-nav-version="{shared_nav.NAV_VERSION}"') != 1:
                bad.append(rel)
        self.assertEqual(bad, [], "pages without exactly one shared shell root")

    def test_one_rail_one_mobile_bar_one_sheet_everywhere(self):
        for rel, h in self.pages.items():
            with self.subTest(page=rel):
                self.assertEqual(h.count('id="llf-rail"'), 1)
                self.assertEqual(h.count('class="mobile-bar"'), 1)
                self.assertEqual(h.count('id="explore-sheet"'), 1)

    def test_global_search_everywhere(self):
        for rel, h in self.pages.items():
            with self.subTest(page=rel):
                self.assertIn('action="/search/"', h)
                self.assertGreaterEqual(h.count('type="search"'), 2)     # rail and Explore sheet (some pages carry a third page-level search)
                self.assertIn('id="llf-site-search"', h)
                self.assertIn('id="llf-mobile-search"', h)

    def test_browse_links_are_the_same_on_every_page(self):
        def browse(h):
            m = re.search(r'<nav class="rail-browse" aria-label="Browse">(.*?)</nav>', h, re.S)
            return re.findall(r'href="([^"]+)"', m.group(1)) if m else None
        ref = browse(self.pages["index.html"])
        self.assertEqual(ref, ["/politics/", "/economy/", "/society/", "/everyday-life/", "/topics/", "/latest/"])
        for rel, h in self.pages.items():
            with self.subTest(page=rel):
                self.assertEqual(browse(h), ref)

    def test_mode_comes_from_the_route_not_the_section(self):
        for rel, h in self.pages.items():
            path = "/" + rel[:-len("index.html")] if rel.endswith("index.html") else "/" + rel
            want = shared_nav.page_mode(path)
            with self.subTest(page=rel):
                self.assertIn(f'<body class="', h)
                self.assertRegex(h, rf'<body class="[^"]*" data-format="{want}">')
                lit = re.findall(r'<nav class="format-nav" aria-label="Formats">(.*?)</nav>', h, re.S)[0]
                lit_words = re.findall(r'aria-current="page">([A-Za-z]+)<', lit)
                self.assertEqual(lit_words, [want.capitalize()] if want else [])

    def test_route_matrix(self):
        m = shared_nav.page_mode
        self.assertEqual(m("/"), "")
        for p in ("/politics/", "/economy/", "/topics/", "/topics/politics/", "/threads/midterms-2026/", "/latest/", "/search/", "/about/", "/privacy/", "/404.html", "/account/", "/admin/"):
            self.assertEqual(m(p), "", p)
        for p in ("/look/", "/look/add/", "/u/"):
            self.assertEqual(m(p), "look", p)
        for p in ("/find/", "/find/candidates/", "/find/guides/"):
            self.assertEqual(m(p), "find", p)
        for p in ("/learn/", "/learn/pennsylvania-governor-poll-party-market-2026/", "/elections/2026/pennsylvania/", "/elections/2026/florida/house/1/"):
            self.assertEqual(m(p), "learn", p)
        self.assertEqual(m("/politics/", override="find"), "find")      # the page model can override; the section never decides

    def test_no_second_rail_and_legacy_sidebar_not_loaded(self):
        for rel, h in self.pages.items():
            with self.subTest(page=rel):
                self.assertEqual(len(re.findall(r'class="llf-rail"', h)), 1)
                self.assertNotIn("has-rail", h)
                self.assertNotIn("/css/sidebar.css", h)
                self.assertNotIn("/js/sidebar.js", h)
                self.assertIn("/css/shell.css", h)
                self.assertIn("/js/shell.js", h)

    def test_stories_carry_the_lens_and_recommendations_in_the_one_rail(self):
        h = self.pages["learn/pennsylvania-governor-poll-party-market-2026/index.html"]
        self.assertIn('data-context="pennsylvania-governor-poll-party-market-2026"', h)
        self.assertIn("data-state-select", h)
        self.assertIn("data-recs", h)
        # and a non-story page has the state picker (political pages) but no lens
        hub = self.pages["elections/2026/pennsylvania/index.html"]
        self.assertIn("data-state-nav-select", hub)
        self.assertNotIn("data-state-select", hub)
        self.assertNotIn("data-state-nav", self.pages["economy/index.html"])     # the state picker is contextual: political pages only

    def test_skip_link_and_landmarks(self):
        for rel, h in self.pages.items():
            with self.subTest(page=rel):
                self.assertIn('href="#main"', h)
                self.assertEqual(h.count('<main id="main"'), 1)
                self.assertIn('aria-label="LookLearnFind navigation"', h)

    def test_canonicals_and_noindex_are_unchanged_by_the_shell(self):
        h = self.pages["elections/2026/pennsylvania/index.html"]
        self.assertIn('<link rel="canonical" href="https://looklearnfind.com/elections/2026/pennsylvania/">', h)
        self.assertNotIn('name="robots"', h)
        self.assertIn('<meta name="robots" content="noindex">', self.pages["account/index.html"])


class ShellForNewPages(unittest.TestCase):
    """A page authored tomorrow gets the shell with zero navigation markup of its own (build.shell is the only writer)."""

    @classmethod
    def setUpClass(cls):
        import build
        cls.build = build

    def render(self, path="/zz-new-page/", **kw):
        b = self.build
        before = len(b.SITEMAP)
        try:
            b.shell("A brand new page", "Description.", path, "<h1>New</h1><p>No navigation markup here.</p>", **kw)
            return b.PAGES_OUT[path]
        finally:
            b.PAGES_OUT.pop(path, None)
            del b.SITEMAP[before:]

    def test_plain_page(self):
        h = self.render()
        self.assertEqual(shared_nav.check_pages({"/zz-new-page/": h}), [])
        self.assertNotIn("llf-rail", "<h1>New</h1><p>No navigation markup here.</p>")

    def test_every_option_combination_still_gets_one_shell(self):
        for kw in (dict(nav="politics"), dict(nav="find", mode="find"), dict(noindex=True, sitemap=False), dict(illustrative=True), dict(bodyclass="home"), dict(nav="topics", css=("ledger",), js=("common",))):
            with self.subTest(**{k: str(v) for k, v in kw.items()}):
                self.assertEqual(shared_nav.check_pages({"/p/": self.render(**kw)}), [])

    def test_political_pages_get_the_state_picker(self):
        self.assertIn("data-state-nav-select", self.render("/elections/2026/zz/", nav="politics"))
        self.assertNotIn("data-state-nav", self.render("/zz-new-page/", nav="economy"))

    def test_outline_only_from_real_headings(self):
        b = self.build
        try:
            b.shell("x", "x", "/zz-outline/", '<h2 id="a">One</h2><h2 id="b">Two</h2>')
            self.assertIn('data-outline', b.PAGES_OUT["/zz-outline/"])
            self.assertIn('href="#b"', b.PAGES_OUT["/zz-outline/"])
            b.shell("x", "x", "/zz-outline2/", "<h2>No ids</h2><p>text</p>")
            self.assertNotIn("data-outline", b.PAGES_OUT["/zz-outline2/"])
        finally:
            for k in ("/zz-outline/", "/zz-outline2/"):
                b.PAGES_OUT.pop(k, None)
                if k in b.SITEMAP:
                    b.SITEMAP.remove(k)


class ShellAssertion(unittest.TestCase):
    def test_missing_shell_is_reported(self):
        self.assertTrue(shared_nav.check_pages({"/x/": "<html><body><main id='main'></main></body></html>"}))

    def test_duplicate_shell_is_reported(self):
        shell, _ = shared_nav.render(path="/x/", site_nav=[{"key": "politics", "label": "Politics", "href": "/politics/"}], active="", mode="", hubs={}, states={})
        self.assertEqual(shared_nav.check_pages({"/ok/": shell}), [])
        self.assertTrue(shared_nav.check_pages({"/dup/": shell + shell}))

    def test_strict_build_runs_the_assertion(self):
        src = (ROOT / "build.py").read_text(encoding="utf-8")
        self.assertIn("shared_nav.check_pages(PAGES_OUT)", src)
        self.assertRegex(src, r'--strict.*shell_bad|shell_bad.*--strict')


class NoHandCopiedNavigation(unittest.TestCase):
    """Page templates and content must never carry shell markup. Only shared_nav.py (and the legacy sidebar.py behind the rollback flag) may."""
    MARKERS = ('data-llf-global-shell', 'id="llf-rail"', 'class="llf-rail"', 'id="explore-sheet"', 'class="mobile-bar"', 'class="rail-browse"')
    ALLOWED = {"shared_nav.py", "sidebar.py"}

    def test_no_template_copies_the_shell(self):
        offenders = []
        files = [p for p in ROOT.glob("*.py")] + list((ROOT / "content").rglob("*.html")) + list((ROOT / "tools").rglob("*.py"))
        for p in files:
            if p.name in self.ALLOWED or p.parts[-2:] == ("qa", "shell_check.py") or p.name == "test_global_shell.py":
                continue
            t = p.read_text(encoding="utf-8", errors="ignore")
            for m in self.MARKERS:
                if m in t:
                    offenders.append(f"{p.relative_to(ROOT)}: {m}")
        self.assertEqual(offenders, [])


@unittest.skipUnless(os.environ.get("LLF_RENDER_TESTS") == "1", "set LLF_RENDER_TESTS=1 to run the Playwright render checks (about a minute)")
class RenderRegression(unittest.TestCase):
    def test_render_matrix(self):
        r = subprocess.run([sys.executable, "tools/qa/shell_check.py", "--quick"], cwd=ROOT, capture_output=True, text=True, env={**os.environ, "PYTHONUTF8": "1"})
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])


if __name__ == "__main__":
    unittest.main()
