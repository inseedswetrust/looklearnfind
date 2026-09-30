#!/usr/bin/env python3
"""Every internal link and asset reference in dist/ must resolve (dynamic shell routes are whitelisted)."""
import re, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "dist"
dyn = [r"^/look/L-\d+/$", r"^/u/[A-Za-z0-9_]+/$", r"^/api/", r"^/threads/[a-z0-9-]+/$"]
bad = set()
for f in D.rglob("*.html"):
    h = f.read_text()
    for m in re.finditer(r'(?:href|src)="(/[^"#?]*)', h):
        u = m.group(1)
        if any(re.match(p, u) for p in dyn) and not (D / u.lstrip("/")).exists():
            continue
        t = D / u.lstrip("/")
        if not (t.is_file() or (t / "index.html").is_file()):
            bad.add((str(f.relative_to(D)), u))
for b in sorted(bad):
    print("BROKEN", *b)
print("links ok" if not bad else f"{len(bad)} broken")
sys.exit(1 if bad else 0)
