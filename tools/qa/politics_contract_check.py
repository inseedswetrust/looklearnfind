#!/usr/bin/env python3
"""Politics 2.0 contract check (docs/politics/INDEX.md).

Verifies: policy hash manifest, shell and mode on Politics pages, required modules (or intentional empty states),
card and state links that resolve, daily record completeness, story ID uniqueness, source dates, stale-data guard,
search inclusion, URL preservation and the absence of result language.
Usage: python tools/qa/politics_contract_check.py [--dist dist] [--write-manifest]
Exit 1 on any problem.
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
POLICY = ROOT / "docs" / "politics"
MODULES = ("daily-signal", "accountability-desk", "election-2026", "follow-the-money", "state-of-the-record", "election-signals", "current-reporting", "go-to-the-source")
H1_TEXT = "Less noise. More evidence."
# Election-claim language. Applied only to copy written for the Politics pages: text inside links to dated /learn/ reports, credits and
# captions is historical reporting or provenance and is not scanned. A hit needs a decisive term; a negated or conditional sentence
# ("has not validated", "until a dated official source", "no result") is allowed.
RESULT_TERMS = re.compile(r"\b(won|wins|winning|winner|winners|projected to win|elected|defeated|conced(?:e|es|ed)|landslide|mandate|certified (?:results?|winner)|declared (?:the )?winner|called (?:the )?race)\b", re.I)
SAFE_CONTEXT = re.compile(r"\b(not|no|never|until|unless|without|only when|if|before|cannot|isn't|is not|has not|have not)\b", re.I)
DAILY_FILE = ROOT / "data" / "politics_daily" / "2026-11-05-edition-001.json"
MANIFEST = ROOT / "docs" / "politics" / "brand" / "ASSET_MANIFEST.csv"
OK_ASSET_STATUS = ("cleared", "labelled_ai", "owner_supplied")
REQUIRED_DAILY = ("story_id", "date", "title", "dek", "sources", "author", "editor", "update_log", "status")
MAX_DAILY_AGE_DAYS = 3        # an approved briefing older than this is a WARNING (historical records stay), never a build failure


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hashed(p, base=POLICY):
    """Policy text is hashed; regenerated screenshots are evidence, not policy, and are not."""
    return p.is_file() and p.name != "SHA256SUMS.txt" and "screenshots" not in p.relative_to(base).parts


def policy_files():
    return sorted(p for p in POLICY.rglob("*") if hashed(p))


def write_manifest():
    lines = [f"{sha(p)}  {p.relative_to(POLICY).as_posix()}" for p in policy_files()]
    (POLICY / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def check_manifest(policy=POLICY):
    probs = []
    m = policy / "SHA256SUMS.txt"
    if not m.exists():
        return ["policy: SHA256SUMS.txt missing"]
    want = dict(reversed(l.split("  ", 1)) for l in m.read_text(encoding="utf-8").splitlines() if l.strip())
    have = {p.relative_to(policy).as_posix(): sha(p) for p in policy.rglob("*") if hashed(p, policy)}
    for name, h in have.items():
        if name not in want:
            probs.append(f"policy: {name} is not in the manifest (add a changelog entry, then regenerate)")
        elif want[name] != h:
            probs.append(f"policy: {name} changed since the manifest (record a numbered revision in CHANGELOG.md, then regenerate)")
    for name in want:
        if name not in have:
            probs.append(f"policy: {name} listed in the manifest but missing")
    for f in ("VERSION", "STATUS", "CHANGELOG.md"):
        if not (policy / f).exists():
            probs.append(f"policy: {f} missing")
    if (policy / "STATUS").exists() and not re.search(r"STATUS=(LOCKED|PROVISIONAL)\b", (policy / "STATUS").read_text(encoding="utf-8")):
        probs.append("policy: STATUS must be LOCKED or PROVISIONAL")
    if (policy / "STATUS").exists() and "APPROVED_ON=" not in (policy / "STATUS").read_text(encoding="utf-8"):
        probs.append("policy: STATUS has no approval date")
    ver = (policy / "VERSION").read_text(encoding="utf-8").strip() if (policy / "VERSION").exists() else ""
    if ver and (policy / "CHANGELOG.md").exists() and f"## {ver} " not in (policy / "CHANGELOG.md").read_text(encoding="utf-8"):
        probs.append(f"policy: CHANGELOG.md has no entry for version {ver}")
    return probs


def page(dist, path):
    f = dist / path.strip("/") / "index.html"
    return f.read_text(encoding="utf-8") if f.exists() else None


def exists(dist, href):
    h = href.split("#")[0].split("?")[0]
    if h.startswith("http") or not h.startswith("/"):
        return True
    return (dist / h.strip("/") / "index.html").exists() or (dist / h.lstrip("/")).is_file()


def check_daily_records(directory, today=None):
    """Returns (errors, warnings). Several records may share one briefing date (distinct story IDs). Freshness is a warning only."""
    import datetime
    errs, warns, ids = [], [], {}
    today = today or datetime.date.today()
    for f in sorted(pathlib.Path(directory).glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        miss = [k for k in REQUIRED_DAILY if not r.get(k)]
        if miss:
            errs.append(f"daily {f.name}: missing {', '.join(miss)}")
            continue
        if r["story_id"] in ids:
            errs.append(f"daily {f.name}: duplicate story ID {r['story_id']} (also {ids[r['story_id']]})")
        ids[r["story_id"]] = f.name
        for s in r["sources"]:
            if not (s.get("url") and s.get("date") and s.get("label")):
                errs.append(f"daily {f.name}: a source lacks url, label or date")
        if r["editor"] == r["author"]:
            errs.append(f"daily {f.name}: editor must differ from author")
        try:
            d = datetime.date.fromisoformat(r["date"])
            if d > today:
                errs.append(f"daily {f.name}: dated in the future")
            if r["status"] == "approved" and (today - d).days > MAX_DAILY_AGE_DAYS and r.get("pinned") != "yes":
                warns.append(f"daily {f.name}: approved briefing is {(today - d).days} days old (historical record stays public; refresh the landing)")
        except ValueError:
            errs.append(f"daily {f.name}: bad date")
        if r["status"] not in ("draft", "approved"):
            errs.append(f"daily {f.name}: status must be draft or approved")
        fc = r.get("fact_check") or {}
        if r["status"] == "approved":
            if fc.get("state") == "passed":
                if not fc.get("reviewer") or fc.get("reviewer") == r["author"]:
                    errs.append(f"daily {f.name}: approved needs a passed fact check by a reviewer other than the author")
            elif fc.get("state") == "owner_approved":
                if not (fc.get("approved_by") and fc.get("approved_on") and r.get("editors_note")):
                    errs.append(f"daily {f.name}: an owner approval needs approved_by, approved_on and a published editor's note")
            else:
                errs.append(f"daily {f.name}: approved needs a passed fact check or a recorded owner approval")
        b = r.get("blocks")
        if b:
            sec_ids = {s["id"] for s in b.get("sections", [])}
            rail_ids = {x["id"] for x in r.get("rail", [])}
            for i in b["signals"]["items"]:
                if i["target"] not in sec_ids:
                    errs.append(f"daily {f.name}: teaser {i['n']} points to #{i['target']}, which is not a section")
            if rail_ids != sec_ids:
                errs.append(f"daily {f.name}: rail outline ids {sorted(rail_ids)} differ from section ids {sorted(sec_ids)}")
            if len(sec_ids) != len(b.get("sections", [])):
                errs.append(f"daily {f.name}: duplicate section id")
        if len(r["title"].split()) > 12:
            warns.append(f"daily {f.name}: headline is over 12 words")
        if not 25 <= len(r["dek"].split()) <= 45:
            warns.append(f"daily {f.name}: summary should be 25 to 45 words (is {len(r['dek'].split())})")
    return errs, warns


def claim_hits(html_text):
    """Election-claim language in copy written for the page. Historical report links, credits and captions are excluded; negated or conditional
    sentences are allowed. Returns [(term, sentence)]."""
    body = re.sub(r'<a [^>]*href="/learn/[^"]*"[^>]*>.*?</a>', " ", html_text, flags=re.S)
    body = re.sub(r'<figcaption[^>]*>.*?</figcaption>', " ", body, flags=re.S)
    body = re.sub(r'<p class="pol-teaser__s">.*?</p>', " ", body, flags=re.S)         # edition teaser summaries are the briefing's own text, held to the fact-check gate
    body = re.sub(r'<p class="pol-daily__lead">.*?</p>', " ", body, flags=re.S)
    body = re.sub(r'<span class="pol-(?:credit|badge)">.*?</span>', " ", body, flags=re.S)
    body = re.sub(r'<p class="pol-badge[^"]*">.*?</p>', " ", body, flags=re.S)
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.S)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
    hits = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        m = RESULT_TERMS.search(sent)
        if m and not SAFE_CONTEXT.search(sent):
            hits.append((m.group(0), sent.strip()[:140]))
    return hits


def load_assets():
    import csv
    if not MANIFEST.exists():
        return {}
    with MANIFEST.open(encoding="utf-8") as fh:
        return {r["path"]: r for r in csv.DictReader(fh)}


def check_edition_pages(dist, allow_preview=False):
    """Dated Daily Signal pages: one shell, a named rail outline whose anchors exist, every in-page link resolves, drafts never public."""
    probs = []
    base = dist / "politics" / "daily"
    sm = (dist / "sitemap.xml").read_text(encoding="utf-8") if (dist / "sitemap.xml").exists() else ""
    si = (dist / "search-index.json").read_text(encoding="utf-8") if (dist / "search-index.json").exists() else ""
    for f in sorted(base.glob("*/index.html")) if base.exists() else []:
        date = f.parent.name
        h = f.read_text(encoding="utf-8")
        name = f"/politics/daily/{date}/"
        draft = 'class="pol-draftbar"' in h
        if h.count("data-llf-global-shell") != 1 or h.count('id="llf-rail"') != 1:
            probs.append(f"{name}: needs exactly one shared shell and rail")
        if not re.search(r'<body[^>]*data-format="learn"', h):
            probs.append(f"{name}: must light LEARN")
        ids = set(re.findall(r'\sid="([^"]+)"', h))
        for a in set(re.findall(r'href="#([^"]+)"', h)):
            if a not in ids and a != "main":
                probs.append(f"{name}: in-page link #{a} has no target")
        if "pol-ed" in h:
            if "In this edition" not in h.split('<main', 1)[0]:
                probs.append(f"{name}: the rail outline must read 'In this edition'")
            for need in ("leadership", "geography", "voters", "money", "states", "sources", "five-signals"):
                if need not in ids:
                    probs.append(f"{name}: missing section id {need}")
        if not draft:
            if 'name="robots" content="noindex' in h:
                probs.append(f"{name}: an approved edition must be indexable")
            if name not in sm:
                probs.append(f"{name}: an approved edition must be in the sitemap")
            if "pol-ed" in h and 'class="pol-note"' not in h and "owner_approved" in (DAILY_FILE.read_text(encoding="utf-8") if DAILY_FILE.exists() else ""):
                probs.append(f"{name}: an owner-approved edition must show its editor's note")
        if draft:
            if not allow_preview:
                probs.append(f"{name}: a draft edition is built (preview build). Rebuild without LLF_PREVIEW_DRAFTS before any release")
            if 'name="robots" content="noindex' not in h:
                probs.append(f"{name}: a draft edition must be noindex")
            if name in sm or name in si:
                probs.append(f"{name}: a draft edition must not be in the sitemap or the search index")
    land = (dist / "politics" / "index.html")
    if land.exists() and "DRAFT PREVIEW" in land.read_text(encoding="utf-8") and not allow_preview:
        probs.append("/politics/: shows a draft preview (build without LLF_PREVIEW_DRAFTS before any release)")
    return probs


def check_pages(dist, baseline=None, assets=None):
    probs = []
    land, idx = page(dist, "/politics/"), page(dist, "/politics/daily/")
    assets = load_assets() if assets is None else assets
    for name, h in (("/politics/", land), ("/politics/daily/", idx)):
        if h is None:
            probs.append(f"{name}: page not built")
            continue
        if h.count("data-llf-global-shell") != 1 or h.count('id="llf-rail"') != 1:
            probs.append(f"{name}: needs exactly one shared shell and rail")
        if not re.search(r'<body[^>]*data-format="learn"', h):
            probs.append(f"{name}: Politics pages light the LEARN word (owner decision 2026-11-05)")
        main = re.search(r"<main.*?</main>", h, re.S)
        for term, sent in claim_hits(main.group(0) if main else ""):
            probs.append(f"{name}: election-claim language '{term}' in: {sent}")
    if land:
        main = re.search(r"<main.*?</main>", land, re.S).group(0)
        h1 = re.search(r"<h1.*?</h1>", main, re.S)
        h1_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h1.group(0))).replace(" .", ".").strip() if h1 else ""
        if len(re.findall(r"<h1[ >]", main)) != 1 or h1_text != H1_TEXT:
            probs.append(f"/politics/: needs exactly one H1 reading '{H1_TEXT}' (found '{h1_text}')")
        for mod in MODULES:
            m = re.search(rf'id="{mod}"(.*?)(?=<section|\Z)', land, re.S)
            if not m:
                probs.append(f"/politics/: module {mod} missing")
            elif len(re.sub(r"<[^>]+>|\s", "", m.group(1))) < 60:
                probs.append(f"/politics/: module {mod} is blank")
        for href in set(re.findall(r'href="(/[^"]*)"', main)):
            if not exists(dist, href):
                probs.append(f"/politics/: link {href} does not resolve")
        if "theissuesparty.org" in land and "not lookLearnfind reporting".lower() not in land.lower():
            probs.append("/politics/: TIP link must be labeled external advocacy")
        order = ["pol-h1", "daily-signal", "accountability-desk", "five-signals-today", "election-2026", "follow-the-money", "state-of-the-record", "election-signals", "current-reporting", "go-to-the-source"]
        pos = [(land.find(f'id="{i}"'), i) for i in order if f'id="{i}"' in land]
        if [p for p, _ in pos] != sorted(p for p, _ in pos):
            probs.append("/politics/: the modules are out of the approved order (hero, Daily Signal, Accountability, Five Signals, tiles, signals and reporting, source)")
        if len(re.findall(r'class="pol-tab"', land)) > 1:
            probs.append("/politics/: more than one yellow tab (one attention marker per viewport)")
        if 'class="pol-duo"' not in land:
            probs.append("/politics/: the directional duochrome hero is missing")
        for src in sorted(set(re.findall(r'<img[^>]+src="(/img/(?:politics|elections)/[^"]+)"', land))):
            row = assets.get("static" + src.split("?")[0])
            if row is None:
                probs.append(f"/politics/: image {src} has no row in docs/politics/brand/ASSET_MANIFEST.csv")
            elif row["usage_status"] not in OK_ASSET_STATUS:
                probs.append(f"/politics/: image {src} usage_status is '{row['usage_status']}' (rights or identity not verified)")
        for tag in re.findall(r"<img[^>]*>", land):
            if "alt=" not in tag:
                probs.append("/politics/: an image has no alt attribute")
    si = dist / "search-index.json"
    if si.exists():
        urls = {x["url"] for x in json.loads(si.read_text(encoding="utf-8"))}
        for need in ("/politics/", "/politics/daily/", "/elections/2026/pennsylvania/", "/elections/2026/florida/governor/"):
            if need not in urls:
                probs.append(f"search: {need} not indexed")
    else:
        probs.append("search-index.json missing")
    if baseline and baseline.exists():
        for u in baseline.read_text(encoding="utf-8").split():
            if not exists(dist, u):
                probs.append(f"URL preservation: {u} no longer built")
    return probs


def main(argv):
    if "--write-manifest" in argv:
        write_manifest()
        print("manifest written")
        return 0
    dist = pathlib.Path(argv[argv.index("--dist") + 1]) if "--dist" in argv else ROOT / "dist"
    derr, dwarn = check_daily_records(ROOT / "data" / "politics_daily")
    probs = check_manifest() + derr + check_pages(dist, POLICY / "URL_BASELINE.txt") + check_edition_pages(dist, allow_preview="--allow-preview" in argv)
    print(f"POLITICS CONTRACT: {len(probs)} problem(s), {len(dwarn)} warning(s)")
    for p in probs:
        print("  " + p)
    for w in dwarn:
        print("  warning: " + w)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
