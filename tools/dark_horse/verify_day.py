#!/usr/bin/env python3
"""Verify a daily folder: capture hashes match the manifest, no leftover .tmp files (atomic writes completed), no secrets in stored data.

    python3 tools/dark_horse/verify_day.py [path-to-day-or-revision-folder ...]     (default: the folder latest.json points to)
Exit 0 = all checks pass, 1 = a check failed (details printed).
"""
import hashlib, json, re, sys
from pathlib import Path
B = Path(__file__).resolve().parents[2] / "data/elections/dark_horse"
SECRET = re.compile(r"(api[_-]?key|apikey|authorization|bearer|secret|token=)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{12,}", re.I)
def check(folder):
    folder, bad, n = Path(folder).resolve(), [], 0
    man = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    for name, h in man["captures"].items():
        n += 1
        p = folder / "captures" / name
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != h:
            bad.append(f"hash mismatch or missing capture: {name}")
    bad += [f"leftover temp file: {p.name}" for p in folder.rglob("*.tmp")]
    for p in list(folder.glob("*.json")) + list(folder.glob("*.csv")) + list(folder.rglob("captures/*")):
        if p.is_file() and SECRET.search(p.read_text(encoding="utf-8", errors="ignore")):
            bad.append(f"possible secret in {p.name}")
    return {"folder": str(folder.relative_to(B)), "captures_checked": n, "problems": bad}
if __name__ == "__main__":
    targets = sys.argv[1:] or [str((B / json.loads((B / "latest.json").read_text())["manifest_path"]).parent)]
    rep = [check(t) for t in targets]
    print(json.dumps(rep, indent=1))
    sys.exit(1 if any(r["problems"] for r in rep) else 0)
