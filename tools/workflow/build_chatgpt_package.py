#!/usr/bin/env python3
"""Build the portable knowledge package that goes to a fresh ChatGPT session for one state.

    python tools/workflow/build_chatgpt_package.py MI

Authored text lives in productions/2026/<ST>/package_src/ (edit those files, not the zip). Everything else is copied from the repository so the
package cannot drift from it. Output: productions/2026/<ST>/chatgpt_package/LLF_<ST>_KNOWLEDGE_<date>.zip with manifest.json (sha256 per file and
the git commit). The build fails if a secret-looking string or the FEC key appears in any file.
"""
import hashlib, json, re, shutil, subprocess, sys, zipfile
from datetime import date
from pathlib import Path

R = Path(__file__).resolve().parents[2]
ST = (sys.argv[1] if len(sys.argv) > 1 else "MI").upper()
PROD = R / f"productions/2026/{ST}"
SRC = PROD / "package_src"
OUT = PROD / "chatgpt_package"
TODAY = date.today().isoformat()
NAME = f"LLF_{ST}_KNOWLEDGE_{TODAY}"
ROOT = OUT / NAME

if OUT.exists():
    shutil.rmtree(OUT)
ROOT.mkdir(parents=True)


def put(rel, src):
    s = Path(src)
    if not s.is_absolute():
        s = R / s
    if not s.exists():
        sys.exit(f"missing source: {s}")
    d = ROOT / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(s, d)


def text(rel, body):
    d = ROOT / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(body, encoding="utf-8", newline="\n")


# top level and authored files
put("00_START_HERE.md", SRC / "00_START_HERE.md")
put("CHATGPT_OPENING_PROMPT.md", SRC / "CHATGPT_OPENING_PROMPT.md")
put("06_OPEN_ITEMS.md", SRC / "OPEN_ITEMS.md")

# 01 workflow
for f in ("00_READ_FIRST", "01_END_TO_END_WORKFLOW", "02_AGENT_SKILL_MAP", "03_VIDEO_SKILL_AND_SHOT_CONTRACT", "06_DECISION_LOG"):
    put(f"01_WORKFLOW/{f}.md", f"docs/production/{f}.md")
put("01_WORKFLOW/DATA_ACCESS_LIMITATIONS.md", "docs/production/DATA_ACCESS_LIMITATIONS.md")
put("01_WORKFLOW/STATE_STATUS.md", SRC / "STATE_STATUS.md")

# 02 standards
put("02_STANDARDS/HOUSE_RULES_ONE_PAGE.md", SRC / "HOUSE_RULES_ONE_PAGE.md")
put("02_STANDARDS/PUBLISHING_RULES.md", "docs/election-build/PUBLISHING_RULES.md")
put("02_STANDARDS/BRAND.md", "docs/BRAND.md")
for p in sorted((R / "docs/schemas").glob("0*.md")):
    put(f"02_STANDARDS/schemas/{p.name}", p)
put("02_STANDARDS/tip_issue_definitions.json", f"data/elections/{ST}/tip_export/issue_definitions.json")
for sk in ("llf-article-format", "llf-delta-editorial", "llf-story-scout", "llf-factcheck-finalize", "llf-video-director"):
    put(f"02_STANDARDS/skills/{sk}.md", f".claude/skills/{sk}/SKILL.md")
text("02_STANDARDS/skills/README.md", "These are Claude Code's working skill files, copied as plain markdown so ChatGPT can follow the same procedures. They mention repository paths and scripts that only Claude Code can run; skip those parts. `llf-article-format` is the drafting checklist.\n")

# 03 examples
for n in ("01_senate_money", "02_il07_ford", "03_il04_handoff"):
    for f in ("STORY_BRIEF.md", "CLAIMS.csv"):
        put(f"03_EXAMPLES/illinois_briefs/{n}/{f}", f"docs/illinois/stories/{n}/{f}")
for slug in ("aipac-udp-money-delta-october-2026", "michigan-senate-delta-october-2026", "illinois-il07-ford-outside-money-october-2026",
             "illinois-senate-primary-money-october-2026", "illinois-il04-ballot-access-october-2026",
             "florida-house-independent-spending-october-2026", "florida-governor-fundraising-polling-2026"):
    put(f"03_EXAMPLES/published_pieces/{slug}.html", f"content/learn/{slug}.html")
text("03_EXAMPLES/README.md", "Illinois briefs show the brief and claims you receive. Published pieces show where a drafted article ends up (the front matter, the openfile, sources and corrections blocks, `[[s:n]]` markers). Match their tone: plain, specific, neutral, and explicit about what a figure does not show.\n")

# 04 visuals
put("04_VISUALS/HERO_IMAGE_BRIEF_ILLINOIS_MICHIGAN.md", "productions/2026/IL/visuals/HERO_IMAGE_BRIEF_FOR_CHATGPT.md")
put("04_VISUALS/HOMEPAGE_IMAGES_BRIEF_FOR_CHATGPT.md", "productions/2026/visuals/HOMEPAGE_IMAGES_BRIEF_FOR_CHATGPT.md")
put("04_VISUALS/MICHIGAN_HERO_BRIEF_FOR_CHATGPT.md", "productions/2026/visuals/MICHIGAN_HERO_BRIEF_FOR_CHATGPT.md")
put("04_VISUALS/MI_A1_HERO_BRIEF.md", SRC / "MI_A1_HERO_BRIEF.md")
put("04_VISUALS/hero_credits.json", "data/elections/hero_credits.json")
for im in ("il-ford", "il-garcia", "il-stratton", "mi-udp", "s1-florida", "s2-illinois"):
    put(f"04_VISUALS/reference_images/{im}.jpg", f"static/img/elections/{im}.jpg")
put("04_VISUALS/reference_images/og-elections.jpg", "static/img/og-elections.jpg")

# 05 state data and stories
put("05_MICHIGAN/stories/MI-A1/STORY_BRIEF.md", SRC / "stories/MI-A1/STORY_BRIEF.md")
put("05_MICHIGAN/stories/MI-A1/CLAIMS.csv", SRC / "stories/MI-A1/CLAIMS.csv")
put("05_MICHIGAN/stories/MI-A3_A4_RESEARCH_NOTES.md", SRC / "stories/MI-A3_A4_RESEARCH_NOTES.md")
put("05_MICHIGAN/stories/scout_all_angles.md", f"productions/2026/{ST}/research/STORY_BRIEF.md")
put("05_MICHIGAN/LINK_MAP.md", SRC / "LINK_MAP.md")
put("05_MICHIGAN/data/roster.json", f"data/elections/{ST}/roster.json")
put("05_MICHIGAN/data/kalshi_capture.json", f"data/elections/{ST}/markets.json")
put("05_MICHIGAN/data/dept_of_state_listing_text.txt", f"data/elections/{ST}/captures/boe_text.txt")
tip = json.loads((R / f"data/elections/{ST}/tip_export/candidates.json").read_text(encoding="utf-8"))
fields = ["fec_candidate_id", "display_name", "office_full", "party_label", "incumbent", "race_key", "verification_status"]
text("05_MICHIGAN/data/tip_profiles.json", json.dumps([{k: c.get(k) for k in fields} for c in tip], indent=1))
races = json.loads((R / f"data/elections/{ST}/tip_export/races.json").read_text(encoding="utf-8"))
text("05_MICHIGAN/data/tip_races.json", json.dumps(races, indent=1))

# 07 templates
for f in ("ARTICLE_RETURN.md", "DATA_REQUEST.md"):
    put(f"07_RETURN_TEMPLATES/{f}", SRC / "return_templates" / f)

# safety scan
key = ""
envf = R / ".env.local"
if envf.exists():
    m = re.search(r"FEC_API_KEY\s*=\s*(\S+)", envf.read_text(encoding="utf-8"))
    key = m.group(1).strip("'\"") if m else ""
bad = [re.compile(r"eyJ[A-Za-z0-9_-]{20,}"), re.compile(r"service_role", re.I), re.compile(r"api_key=[A-Za-z0-9]{20,}")]
for f in ROOT.rglob("*"):
    if f.is_file() and f.suffix in {".md", ".json", ".csv", ".html", ".txt"}:
        t = f.read_text(encoding="utf-8", errors="ignore")
        if key and key in t:
            sys.exit(f"FEC key found in {f}")
        for b in bad:
            if b.search(t):
                sys.exit(f"secret-looking string in {f}: {b.pattern}")

# manifest and zip
commit = subprocess.run(["git", "-C", str(R), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
files = sorted(p for p in ROOT.rglob("*") if p.is_file())
man = {"package": NAME, "state": ST, "built": TODAY, "repo_commit": commit,
       "files": [{"path": str(p.relative_to(ROOT)).replace("\\", "/"), "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(ROOT / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
z = OUT / f"{NAME}.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():
            zf.write(p, p.relative_to(OUT))
print(z, z.stat().st_size, "bytes,", len(files) + 1, "files, commit", commit)
