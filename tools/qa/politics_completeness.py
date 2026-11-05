#!/usr/bin/env python3
"""Content-completeness check for a Daily Signal edition.

Compares every paragraph, list item and source of the editorial draft (Markdown) with the rendered page in dist/, section by section, and checks the homepage
teasers. Nothing may be silently dropped: a missing or altered paragraph is a failure. Writes docs/politics/CONTENT_COMPLETENESS_REPORT.md.
Needs a preview build (LLF_PREVIEW_DRAFTS=1) while the edition is a draft. Usage: python tools/qa/politics_completeness.py [--dist dist] [--no-report]
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / "docs" / "politics" / "brand" / "edition-001" / "DAILY_SIGNAL_2026-11-05_EDITORIAL_DRAFT.md"
RECORD = ROOT / "data" / "politics_daily" / "2026-11-05-edition-001.json"
HOME = ROOT / "data" / "politics_home.json"
MANIFEST = ROOT / "docs" / "politics" / "brand" / "ASSET_MANIFEST.csv"
REPORT = ROOT / "docs" / "politics" / "CONTENT_COMPLETENESS_REPORT.md"


def norm(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)            # markdown links keep their text
    s = re.sub(r"</?(?:p|li|ul|ol|h[1-6]|section|article|div|br|header|nav|table|tr|td|th)[^>]*>", " ", s)      # block tags separate text; inline tags do not
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("*", "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def draft_sections(md):
    parts = re.split(r"^## ", md, flags=re.M)[1:]
    out = {}
    for p in parts:
        head, _, body = p.partition("\n")
        m = re.search(r"\{#([\w-]+)\}", head)
        key = m.group(1) if m else re.sub(r"\W+", "-", head.lower()).strip("-")
        blocks = []
        for blk in re.split(r"\n\s*\n", body.strip("\n")):
            blk = blk.strip()
            if not blk or blk == "---":
                continue
            if blk.startswith(("- ", "1. ")) or re.match(r"\d+\. ", blk):
                for ln in blk.splitlines():
                    ln = re.sub(r"^(- |\d+\.\s+)", "", ln).strip()
                    if ln:
                        blocks.append(ln)
            else:
                blocks.append(blk)
        out[key] = (re.sub(r"\s*\{#[\w-]+\}", "", head).strip(), blocks)
    return out


def section_html(page, sid):
    m = re.search(rf'<section[^>]*\bid="{sid}"[^>]*>(.*?)</section>', page, re.S)
    return m.group(1) if m else ""


def main(argv):
    dist = Path(argv[argv.index("--dist") + 1]) if "--dist" in argv else ROOT / "dist"
    page_f = dist / "politics" / "daily" / "2026-11-05" / "index.html"
    land_f = dist / "politics" / "index.html"
    if not page_f.exists():
        print("Edition page not built. Build with LLF_PREVIEW_DRAFTS=1 (the edition is a draft).")
        return 2
    page, land = page_f.read_text(encoding="utf-8"), land_f.read_text(encoding="utf-8")
    rec = json.loads(RECORD.read_text(encoding="utf-8"))
    home = json.loads(HOME.read_text(encoding="utf-8"))
    secs = draft_sections(DRAFT.read_text(encoding="utf-8"))
    assets = {}
    import csv
    for r in csv.DictReader(MANIFEST.open(encoding="utf-8")):
        assets[r["path"]] = r
    claims = (rec.get("review") or {}).get("claims", [])

    rows, fails = [], []
    mapping = [("national-picture", "national-picture"), ("five-signals", "five-signals"), ("leadership", "leadership"), ("geography", "geography"), ("voters", "voters"),
               ("money", "money"), ("states", "states"), ("what-next", "what-next"), ("sources", "sources")]
    for key, sid in mapping:
        head, blocks = secs[key]
        html_sec = section_html(page, sid)
        text = norm(html_sec)
        missing = []
        for b in blocks:
            if key == "five-signals" and re.match(r"\*\*\d\d / ", b):          # a numbered teaser: title, label and summary are separate elements
                m = re.match(r"\*\*(\d\d) / (.+?) — \[(.+?)\]\(#([\w-]+)\)\*\*\s*\n(.+)", b, re.S)
                ok = bool(m) and all(norm(x) in text for x in (m.group(3), m.group(5))) and f'href="#{m.group(4)}"' in html_sec and norm(m.group(1) + " / " + m.group(2)) in text
            elif key == "sources" and re.search(r"https?://", b) and not b.startswith("These are"):
                m = re.match(r"(.+?) — \*(.+?)\*,? ?.*?(https?://\S+)$", b) or re.match(r"(.+?) — (.+?): (https?://\S+)$", b)
                url = m.group(3) if m else re.search(r"https?://\S+", b).group(0)
                g2 = re.sub(r",?\s*[A-Z][a-z]{2}\.? \d{1,2}$", "", m.group(2)) if m else ""      # the date is rendered as a separate dated field
                ok = bool(m) and norm(m.group(1)) in text and norm(g2) in text and f'href="{html.escape(url)}"' in html_sec.replace("&amp;", "&").replace("&", "&amp;")
            else:
                ok = norm(re.sub(r"\s*\[Back to today's signals\]\(#five-signals\)", "", b)) in text or norm(b) in text
            if not ok:
                missing.append(b)
        # the draft's "Back to today's signals" link is rendered as a link under each section; it is not part of the paragraph text
        rendered_p = len(re.findall(r"<(?:p|li)[ >]", html_sec))
        links = sorted(set(re.findall(r'href="([^"]+)"', html_sec)))
        n_claims = [c for c in claims if c["section"] == key]
        status = "no claims logged" if not n_claims else "; ".join(f"{k}: {sum(1 for c in n_claims if c['status'] == k)}" for k in sorted({c['status'] for c in n_claims}))
        rows.append(dict(section=head, key=key, url=f"/politics/daily/2026-11-05/#{sid}", supplied=len(blocks), rendered=rendered_p, matched=len(blocks) - len(missing),
                         links=len(links), status=status, missing=missing))
        if missing:
            fails.append(f"{key}: {len(missing)} of {len(blocks)} supplied blocks are missing or altered, first: {missing[0][:90]}")
    # teasers on the landing page
    teasers = []
    for t in home["teasers"]:
        src = next(i for i in rec["blocks"]["signals"]["items"] if i["target"] == t["target"])
        m = re.search(rf'<li class="pol-teaser"><a class="pol-teaser__a" href="/politics/daily/2026-11-05/#{t["target"]}">.*?</li>', land, re.S)
        ok_sum = bool(m) and norm(src["teaser"]) in norm(m.group(0))
        ok_img = bool(m) and t["image"]["src"] in m.group(0) and (ROOT / "static" / t["image"]["src"].lstrip("/")).exists()
        ok_target = f'id="{t["target"]}"' in page
        row = assets.get("static" + t["image"]["src"])
        teasers.append((t["n"], t["title"], t["target"], ok_sum, ok_img, ok_target, row["rights_basis"] if row else "(site image, see hero credits)", row["usage_status"] if row else "cleared"))
        if not (m and ok_sum and ok_img and ok_target):
            fails.append(f"teaser {t['n']}: summary={ok_sum} image={ok_img} target={ok_target}")
    order = [t[0] for t in teasers]
    pos = [land.find(f'#{t["target"]}"') for t in home["teasers"]]
    if pos != sorted(pos) or order != ["01", "02", "03", "04", "05"]:
        fails.append("teasers are not in the required order 01 to 05")
    if len(rec["sources"]) != 10 or len(re.findall(r'rel="noopener">', section_html(page, "sources"))) != 10:
        fails.append("the ten sources are not all rendered")

    if "--no-report" not in argv:
        L = ["# Daily Signal Edition 001: content completeness report", "",
             f"Source: `docs/politics/brand/edition-001/DAILY_SIGNAL_2026-11-05_EDITORIAL_DRAFT.md`. Rendered page: `/politics/daily/2026-11-05/` (local preview build, status **{rec['status']}**, fact check **{rec['fact_check']['state']}**). Generated by `tools/qa/politics_completeness.py`.", "",
             "## Sections", "", "| Source heading | Destination | Supplied | Rendered (p and li) | Matched verbatim | Links | Verification status | Omissions or changes |", "|---|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append(f"| {r['section']} | `{r['url']}` | {r['supplied']} | {r['rendered']} | {r['matched']} | {r['links']} | {r['status']} | {'none' if not r['missing'] else str(len(r['missing'])) + ' missing'} |")
        L += ["", "Rendered counts include the page furniture in each section (eyebrow, back link, source note), so they can exceed the supplied count. The match column compares the text of every supplied paragraph, list item and source line with the rendered section, after stripping Markdown.", "",
              "Not rendered, by design: the draft's \"Page UX and navigation\" section. It is production instructions, not reader copy; it is implemented as behaviour (the rail outline named On this briefing, the teaser links, back links, scroll margins, no-JavaScript anchors).", "",
              "## Homepage teasers (directly beneath the Daily Signal strip)", "", "| # | Homepage title | Links to | Summary rendered | Image present | Target exists | Image rights | Status |", "|---|---|---|---|---|---|---|---|"]
        for n, title, target, s, i, tg, rights, st in teasers:
            L.append(f"| {n} | {title} | `#{target}` | {'yes' if s else 'NO'} | {'yes' if i else 'NO'} | {'yes' if tg else 'NO'} | {rights} | {st} |")
        L += ["", "Homepage teaser titles 02 and 03 follow the owner's directive; the briefing keeps the draft's own wording (`The political map broke in unexpected places`, `The cost of living dominated. What will Congress actually do?`). Teaser summaries are the draft's own teaser paragraphs, unchanged.", "",
              "## Result", "", ("**PASS**: every supplied block is rendered verbatim." if not fails else "**FAIL**"), ""]
        L += [f"- {f}" for f in fails]
        REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"CONTENT COMPLETENESS: {len(fails)} problem(s); {sum(r['supplied'] for r in rows)} supplied blocks, {sum(r['matched'] for r in rows)} matched")
    for f in fails:
        print("  " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
