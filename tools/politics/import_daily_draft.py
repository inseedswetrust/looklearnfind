#!/usr/bin/env python3
"""Convert an editorial Daily Signal draft (Markdown, docs/politics/brand/edition-001/DAILY_SIGNAL_*.md) into a data/politics_daily/*.json record.

The text is copied, never rewritten. Inline Markdown (bold, italic, links) becomes escaped HTML. The record is written with status "draft" and a pending
fact-check: it can be previewed locally (LLF_PREVIEW_DRAFTS=1) but is never built into a public page until an independent reviewer passes it and the owner approves.
Usage: python tools/politics/import_daily_draft.py <draft.md> <out.json> [--edition 001]
"""
import json
import re
import sys
from html import escape
from pathlib import Path

MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def inline(s):
    s = escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    return s


def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", inline(s))).strip()


def parse(md, edition):
    lines = md.splitlines()
    meta = {}
    for ln in lines[:14]:
        m = re.match(r"\*\*(.+?):\*\*\s*(.*)", ln)
        if m:
            meta[m.group(1).strip()] = m.group(2).strip().rstrip("  ")
    h1 = re.search(r"^# (.+)$", md, re.M).group(1)
    date_m = re.search(r"NOVEMBER (\d+), (\d{4})", h1.upper())
    date = f"{date_m.group(2)}-11-{int(date_m.group(1)):02d}" if date_m else "2026-11-05"

    # split into ## sections
    parts = re.split(r"^## ", md, flags=re.M)[1:]
    secs = {}
    for p in parts:
        head, _, body = p.partition("\n")
        sid = re.search(r"\{#([\w-]+)\}", head)
        key = sid.group(1) if sid else re.sub(r"\W+", "-", head.lower()).strip("-")
        secs[key] = (re.sub(r"\s*\{#[\w-]+\}", "", head).strip(), body.strip("\n"))

    def paras(body):
        out = []
        for blk in re.split(r"\n\s*\n", body):
            blk = blk.strip()
            if not blk or blk == "---":
                continue
            out.append(blk)
        return out

    # rail labels from the navigation table
    rail = []
    ux = secs["page-ux-and-navigation"][1]
    for row in ux.splitlines():
        m = re.match(r"\|\s*(\d\d)\s*\|\s*(.+?)\s*\|\s*`#([\w-]+)`\s*\|\s*(.+?)\s*\|", row)
        if m:
            rail.append({"n": m.group(1), "teaser": m.group(2), "id": m.group(3), "label": m.group(4)})

    # opening
    head, body = secs["national-picture"]
    op_paras, glance, src_note = [], [], ""
    for blk in paras(body):
        if blk.startswith("**At a glance**"):
            continue
        if blk.startswith("- "):
            glance = [inline(x[2:].strip()) for x in blk.splitlines() if x.startswith("- ")]
        elif blk.startswith("*Sources for verification:*"):
            src_note = inline(blk)
        else:
            op_paras.append(inline(blk))
    opening = {"id": "national-picture", "h2": head.replace("Opening: ", ""), "paras": op_paras, "glance": glance, "source_note": src_note}

    # five signals
    head, body = secs["five-signals"]
    ps = paras(body)
    intro = inline(ps[0])
    items = []
    for blk in ps[1:]:
        m = re.match(r"\*\*(\d\d) / (.+?) — \[(.+?)\]\(#([\w-]+)\)\*\*\s*\n(.+)", blk, re.S)
        if m:
            items.append({"n": m.group(1), "label": m.group(2), "title": plain(m.group(3)), "target": m.group(4), "teaser": inline(m.group(5).strip())})
    signals = {"id": "five-signals", "h2": head, "intro": intro, "items": items}

    # five deep sections, in teaser order
    sections = []
    for it in items:
        tid = it["target"]
        head, body = secs[next(k for k in secs if k == tid)]
        n = re.match(r"(\d\d) / (.+)", head)
        s = {"id": tid, "n": n.group(1), "h2": n.group(2), "paras": [], "source_review": ""}
        for blk in paras(body):
            if blk.startswith("*Source review:*"):
                s["source_review"] = inline(re.sub(r"\s*\[Back to today's signals\]\(#five-signals\)", "", blk))
            else:
                s["paras"].append(inline(blk))
        sections.append(s)

    # watching next
    head, body = secs["what-next"]
    ps = paras(body)
    watch = {"id": "what-next", "h2": head, "items": [inline(x[2:].strip()) for x in ps[0].splitlines() if x.startswith("- ")], "closing": inline(ps[-1])}

    # sources
    head, body = secs["sources"]
    sources, intro_src = [], ""
    for blk in paras(body):
        if blk.startswith("These are sources"):
            intro_src = inline(blk)
            continue
        for ln in blk.splitlines():
            m = re.match(r"\d+\.\s+(.+?)\s+(https?://\S+)\s*$", ln)
            if not m:
                continue
            label, url = plain(m.group(1)).rstrip(":").strip(), m.group(2)
            d = re.search(r"(\w{3})\.? (\d{1,2})\s*$", label)
            date = f"2026-{MONTHS[d.group(1)]:02d}-{int(d.group(2)):02d}" if d and d.group(1) in MONTHS else date_iso(meta)
            if d and d.group(1) in MONTHS:
                label = label[: d.start()].rstrip(", ").strip()
            sources.append({"label": label, "url": url, "date": date})

    cutoff = date_iso(meta)
    return {
        "story_id": f"DS-{date}-{edition}",
        "edition": edition,
        "date": date,
        "title": h1_title(md),
        "dek": plain(meta.get("Dek", "")),
        "status": "draft",
        "fact_check": {"state": "pending", "reviewer": "", "note": "Independent source review required before approval. Every figure, call and control claim must pass the fact-check gate."},
        "author": "LookLearnFind",
        "editor": "Not yet assigned",
        "source_cutoff": cutoff,
        "update_log": [{"date": cutoff, "note": "Imported the editorial draft (Edition 001) without changes. Not reviewed or approved."}],
        "sources": sources,
        "rail": rail,
        "blocks": {"opening": opening, "signals": signals, "sections": sections, "watching": watch, "sources_intro": intro_src},
    }


def date_iso(meta):
    m = re.search(r"November (\d+), (\d{4})", meta.get("Source cutoff", ""))
    return f"{m.group(2)}-11-{int(m.group(1)):02d}" if m else "2026-11-05"


def h1_title(md):
    m = re.search(r"\*\*H1:\*\*\s*(.+?)\s*$", md, re.M)
    return plain(m.group(1)) if m else ""


def main(argv):
    src, out = Path(argv[0]), Path(argv[1])
    edition = argv[argv.index("--edition") + 1] if "--edition" in argv else "001"
    rec = parse(src.read_text(encoding="utf-8"), edition)
    out.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    b = rec["blocks"]
    print(f"{out.name}: {len(b['sections'])} sections, {len(b['signals']['items'])} signals, {len(rec['sources'])} sources, rail {len(rec['rail'])}")


if __name__ == "__main__":
    main(sys.argv[1:])
