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
MODULES = ("daily-signal", "follow-the-story", "explore-a-state", "the-record", "on-our-radar", "watch-read-verify")
RESULT_WORDS = re.compile(r"\b(won|wins|winner|winners|projected|elected|defeated|concede[sd]?|landslide|mandate|certified results?)\b", re.I)
REQUIRED_DAILY = ("story_id", "date", "title", "dek", "sources", "author", "editor", "update_log", "status")
MAX_DAILY_AGE_DAYS = 3


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def policy_files():
    return sorted(p for p in POLICY.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt")


def write_manifest():
    lines = [f"{sha(p)}  {p.relative_to(POLICY).as_posix()}" for p in policy_files()]
    (POLICY / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def check_manifest(policy=POLICY):
    probs = []
    m = policy / "SHA256SUMS.txt"
    if not m.exists():
        return ["policy: SHA256SUMS.txt missing"]
    want = dict(reversed(l.split("  ", 1)) for l in m.read_text(encoding="utf-8").splitlines() if l.strip())
    have = {p.relative_to(policy).as_posix(): sha(p) for p in policy.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"}
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
    if (policy / "STATUS").exists() and "STATUS=LOCKED" not in (policy / "STATUS").read_text(encoding="utf-8"):
        probs.append("policy: STATUS is not LOCKED")
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
    import datetime
    probs, ids = [], {}
    today = today or datetime.date.today()
    for f in sorted(pathlib.Path(directory).glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        miss = [k for k in REQUIRED_DAILY if not r.get(k)]
        if miss:
            probs.append(f"daily {f.name}: missing {', '.join(miss)}")
            continue
        if r["story_id"] in ids:
            probs.append(f"daily {f.name}: duplicate story ID {r['story_id']} (also {ids[r['story_id']]})")
        ids[r["story_id"]] = f.name
        for s in r["sources"]:
            if not (s.get("url") and s.get("date") and s.get("label")):
                probs.append(f"daily {f.name}: a source lacks url, label or date")
        if r["editor"] == r["author"]:
            probs.append(f"daily {f.name}: editor must differ from author")
        try:
            d = datetime.date.fromisoformat(r["date"])
            if d > today:
                probs.append(f"daily {f.name}: dated in the future")
            if r["status"] == "approved" and (today - d).days > MAX_DAILY_AGE_DAYS and r.get("pinned") != "yes":
                probs.append(f"daily {f.name}: approved item is {(today - d).days} days old and shown as current (stale)")
        except ValueError:
            probs.append(f"daily {f.name}: bad date")
        if r["status"] not in ("draft", "approved"):
            probs.append(f"daily {f.name}: status must be draft or approved")
    return probs


def check_pages(dist, baseline=None):
    probs = []
    land, idx = page(dist, "/politics/"), page(dist, "/politics/daily/")
    for name, h in (("/politics/", land), ("/politics/daily/", idx)):
        if h is None:
            probs.append(f"{name}: page not built")
            continue
        if h.count("data-llf-global-shell") != 1 or h.count('id="llf-rail"') != 1:
            probs.append(f"{name}: needs exactly one shared shell and rail")
        if re.search(r'<body[^>]*data-format="(look|learn|find)"', h):
            probs.append(f"{name}: Politics pages carry no lit mode word")
        main = re.search(r"<main.*?</main>", h, re.S)
        text = re.sub(r"<[^>]+>", " ", main.group(0) if main else "")
        for m in RESULT_WORDS.finditer(text):
            # allowed inside the explicit "states no result" status sentence and earlier-reporting titles
            probs.append(f"{name}: result language '{m.group(0)}' (no result may be stated without a validated source)")
            break
        if 'class="pol-phase"' not in h and name == "/politics/":
            probs.append(f"{name}: missing the status statement")
    if land:
        for mod in MODULES:
            m = re.search(rf'<section class="pol-mod {mod}" id="{mod}">(.*?)</section>', land, re.S)
            if not m:
                probs.append(f"/politics/: module {mod} missing")
            elif len(re.sub(r"<[^>]+>|\s", "", m.group(1))) < 40:
                probs.append(f"/politics/: module {mod} is blank (needs content or an intentional empty state)")
        for href in set(re.findall(r'href="(/[^"]*)"', re.search(r"<main.*?</main>", land, re.S).group(0))):
            if not exists(dist, href):
                probs.append(f"/politics/: link {href} does not resolve")
        if "theissuesparty.org" in land and "Not LookLearnFind reporting" not in land:
            probs.append("/politics/: TIP link must be labeled external advocacy")
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
    probs = check_manifest() + check_daily_records(ROOT / "data" / "politics_daily") + check_pages(dist, POLICY / "URL_BASELINE.txt")
    print(f"POLITICS CONTRACT: {len(probs)} problem(s)")
    for p in probs:
        print("  " + p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
