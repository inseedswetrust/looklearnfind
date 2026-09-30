#!/usr/bin/env python3
"""Lists pages that still contain [BRACKETED] placeholders, 'Placeholder' markers, or illustrative samples.
Exit 1 if any *indexable* page has bracketed fields (policy drafts are noindex until reviewed)."""
import re, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "dist"
bad, info = [], []
for f in sorted(D.rglob("index.html")):
    h = f.read_text()
    page = "/" + str(f.parent.relative_to(D)).replace("\\", "/") + "/"
    noindex = 'name="robots" content="noindex"' in h
    body = h.split('<main id="main">')[-1].split("</main>")[0]
    brackets = re.findall(r"\[[A-Z][A-Z0-9 /,\-'’]{4,}\]", body)
    if brackets and not noindex:
        bad.append((page, brackets[:3]))
    elif brackets:
        info.append((page, len(brackets), "noindex draft"))
    if "Illustrative sample" in body or "illustrative" in body.lower() and "placeholder" in body.lower():
        info.append((page, 0, "illustrative sample"))
for p, n, why in info:
    print(f"note  {p:45s} {why}" + (f" ({n} bracketed fields)" if n else ""))
for p, b in bad:
    print("FAIL ", p, b)
sys.exit(1 if bad else 0)
