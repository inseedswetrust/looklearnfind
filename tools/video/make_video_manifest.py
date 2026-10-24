#!/usr/bin/env python3
"""Write docs/video/florida-2026/VIDEO_ASSET_MANIFEST.csv: every file the Florida film's visuals depend on, with source, license and hash.

Same columns as docs/election-build/ASSET_MANIFEST.csv plus `role` (infographic_frame, infographic_master, capture, source_photo, data, select, source_video).
Run after build_florida_infographics.py and build_clip_manifest.py. Stdlib only.
"""
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "assets/video/florida-2026"
IG = BASE / "infographics"
OUT = ROOT / "docs/video/florida-2026/VIDEO_ASSET_MANIFEST.csv"
COLS = ["asset_id", "role", "type", "source", "license", "path", "usage", "credit", "sha256_16", "notes"]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def rel(p):
    return p.relative_to(ROOT).as_posix()


def main():
    rows = []
    for d in sorted(IG.glob("IG-*")):
        for f in sorted(d.iterdir()):
            role = "infographic_frame" if f.suffix == ".png" else "infographic_master"
            rows.append([f"VID-{f.stem}", role, f.suffix[1:], "built by tools/video/build_florida_infographics.py from the sources listed in INFOGRAPHIC_SOURCES.md",
                         "LLF original; embedded photos keep their own licenses (see source_photo rows)", rel(f), d.name, "LookLearnFind", sha(f),
                         "layered SVG, editable" if role == "infographic_master" else "1080 x 1920 start or end frame; B frames reuse the exact assets of A"])
    caps = json.loads((IG / "captures/capture_log.json").read_text(encoding="utf8"))
    for c in caps:
        f = IG / "captures" / c["file"]
        rows.append([f"VID-CAP-{f.stem}", "capture", "png", c["url"], "owner's own sites (LLF, TIP)", rel(f), "IG-11, IG-12-13", "LookLearnFind / The Issues Party", sha(f),
                     f"unedited screenshot, captured {c['captured_utc']}, clip {c['clip']}"])
    for f in sorted((IG / "data").glob("*")):
        src = json.loads((IG / "data/sources.json").read_text(encoding="utf8"))
        rows.append([f"VID-DATA-{f.stem}", "data", f.suffix[1:], "see sources.json in the same folder", "public record (Florida Division of Elections; U.S. Census Bureau)", rel(f), "IG-02, IG-04", "Florida Division of Elections; U.S. Census Bureau", sha(f), "retrieved by tools/video/fetch_florida_infographic_data.py"])
    rows.append(["VID-PHOTO-vindman_2019", "source_photo", "jpg", "https://commons.wikimedia.org/wiki/File:Alexander_Vindman_on_May_20,_2019.jpg", "CC BY 4.0",
                 rel(IG / "src/vindman_2019.jpg"), "IG-02 Vindman card", "Mykola Lazarenko / The Presidential Administration of Ukraine", sha(IG / "src/vindman_2019.jpg"),
                 "267 x 356 px, taken May 20, 2019 (Zelenskyy inauguration); upscaled 1.35x on the card; replace with a current licensed photo when one exists"])
    for sel in sorted((BASE / "selects").rglob("*.mp4")):
        rows.append([f"VID-SEL-{sel.stem}", "select", "mp4", "see CLIP_MANIFEST.csv", "see RIGHTS_REGISTER.csv (held, not cleared)", rel(sel), "review only", "see CLIP_MANIFEST.csv", sha(sel), "inside _review_hold: not for publication"])
    for src in sorted((BASE / "source").rglob("*.webm")) + sorted((BASE / "source").rglob("*.mp4")):
        rows.append([f"VID-SRC-{src.stem}", "source_video", src.suffix[1:], "see CLIP_MANIFEST.csv", "see RIGHTS_REGISTER.csv (held, not cleared)", rel(src), "review only", "see CLIP_MANIFEST.csv", sha(src), "git-ignored; local only"])
    with open(OUT, "w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(rows)
    print(len(rows), "rows ->", rel(OUT))


if __name__ == "__main__":
    main()
