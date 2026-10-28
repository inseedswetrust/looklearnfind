#!/usr/bin/env python3
"""LLF handoff protocol: one ledger per state, generated kickoffs and packages, a readback check and an ingest check.

    handoff.py init <ST> [--name Michigan]          scaffold productions/<year>/<ST>/ with a ledger from the template
    handoff.py status <ST> [--strict]               check the ledger against the repository; say if it is stale
    handoff.py stamp <ST>                           record HEAD in the ledger (run at the end of every stage, then commit)
    handoff.py build <ST> --lane articles|images|all|claude [--mode existing|fresh]
    handoff.py verify-readback <ST> <package_id|latest> <file>
    handoff.py ingest <ST> <dir_or_zip> [--package-id ID]

Source of truth: productions/<year>/<ST>/STATE_LEDGER.json. Kickoff prompts and ChatGPT packages are generated from it, never hand-written, so they
cannot say something the ledger does not. Protocol: docs/production/08_HANDOFF_PROTOCOL.md.
"""
import argparse, csv, datetime, fnmatch, hashlib, io, json, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

R = Path(__file__).resolve().parents[2]
YEAR = 2026
TODAY = datetime.date.today().isoformat()

TASK_OPEN = {"ready"}
STAGE_STATUSES = {"done", "in_progress", "todo", "blocked", "waiting_owner"}
TASK_STATUSES = {"ready", "sent", "returned", "accepted", "withdrawn", "not_ready", "done", "todo", "blocked", "waiting_owner"}


# ---------------------------------------------------------------- helpers
def git(*a):
    return subprocess.run(["git", "-C", str(R), *a], capture_output=True, text=True, encoding="utf-8").stdout.strip()


def head():
    return git("rev-parse", "--short", "HEAD")


def pdir(st):
    return R / f"productions/{YEAR}/{st}"


def lpath(st):
    return pdir(st) / "STATE_LEDGER.json"


def load(st):
    p = lpath(st)
    if not p.exists():
        sys.exit(f"no ledger at {p}. Run: handoff.py init {st}")
    return json.loads(p.read_text(encoding="utf-8"))


def save(st, led):
    lpath(st).write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def put(root, rel, src):
    s = Path(src)
    if not s.is_absolute():
        s = R / s
    if not s.exists():
        sys.exit(f"missing source for package: {s}")
    d = root / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(s, d)


def text(root, rel, body):
    d = root / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(body, encoding="utf-8", newline="\n")


def lane_tasks(led, lane):
    return led["lanes"].get(lane, {}).get("tasks", [])


# ---------------------------------------------------------------- status
def changed_since(led):
    base = led.get("as_of_commit")
    if not base:
        return None
    out = git("log", f"{base}..HEAD", "--name-only", "--format=@@%h\t%s", "--", *led.get("paths", []))
    commits, cur = [], None
    for line in out.splitlines():
        if line.startswith("@@"):
            cur = [line[2:], []]
            commits.append(cur)
        elif line.strip() and cur is not None:
            cur[1].append(line.strip())
    keep = []
    for c, files in commits:
        if all(f.endswith("STATE_LEDGER.json") for f in files):
            continue
        keep.append(c)
    return keep


def cmd_status(a):
    led = load(a.state)
    errs, warns = [], []
    for s in led["stages"]:
        if s["status"] not in STAGE_STATUSES:
            errs.append(f"stage {s['id']}: unknown status {s['status']}")
        if s["status"] == "done":
            for ev in s.get("evidence", []):
                if not (R / ev).exists():
                    errs.append(f"stage {s['id']} is done but evidence is missing: {ev}")
    for lane, body in led["lanes"].items():
        for t in body["tasks"]:
            if t["status"] not in TASK_STATUSES:
                errs.append(f"task {t['id']}: unknown status {t['status']}")
            if t["status"] in TASK_OPEN:
                for i in t.get("inputs", []):
                    if not (R / i).exists():
                        errs.append(f"task {t['id']} is ready but input is missing: {i}")
    for t in led.get("claude_tasks", []):
        if t["status"] not in TASK_STATUSES:
            errs.append(f"claude task {t['id']}: unknown status {t['status']}")
    stale = changed_since(led)
    if stale is None:
        warns.append("ledger has never been stamped: run handoff.py stamp, then commit")
    elif stale:
        warns.append(f"STALE: {len(stale)} commit(s) touched this state since the ledger was stamped; read them before trusting the ledger:")
        warns += ["    " + c for c in stale[:12]]
    dirty = git("status", "--short", "--", *led.get("paths", []))
    if dirty:
        warns.append("uncommitted changes under this state's paths:\n    " + dirty.replace("\n", "\n    "))
    print(f"{led['state_name']} {led['year']}  ledger updated {led['updated']}  HEAD {head()}  stamped at {led.get('as_of_commit') or 'never'}")
    print(led["headline"], "\n")
    for s in led["stages"]:
        print(f"  [{s['status']:<13}] {s['id']}: {s['title']}")
    for lane, body in led["lanes"].items():
        print(f"\n  lane {lane} (chat: {body.get('chat', 'unrecorded')})")
        for t in body["tasks"]:
            print(f"    [{t['status']:<10}] {t['id']}: {t['title']}")
    print("\n  claude tasks")
    for t in led.get("claude_tasks", []):
        print(f"    [{t['status']:<14}] {t['id']}: {t['title']}  (gate: {t.get('gate', 'none')})")
    if led.get("waiting_on_owner"):
        print("\n  waiting on the owner:\n    - " + "\n    - ".join(led["waiting_on_owner"]))
    for w in warns:
        print("WARN", w)
    for e in errs:
        print("ERROR", e)
    print("\nRESULT:", "FAIL" if errs else ("STALE" if stale else "OK"))
    sys.exit(1 if errs or (a.strict and (stale or stale is None)) else 0)


def cmd_stamp(a):
    led = load(a.state)
    led["as_of_commit"] = head()
    led["updated"] = TODAY
    save(a.state, led)
    print(f"stamped {a.state} at {led['as_of_commit']} on {TODAY}. Commit the ledger.")


# ---------------------------------------------------------------- init
def cmd_init(a):
    st = a.state.upper()
    p = lpath(st)
    if p.exists():
        sys.exit(f"{p} exists; not overwriting")
    tpl = json.loads((R / "docs/production/templates/state/STATE_LEDGER.template.json").read_text(encoding="utf-8"))
    name = a.name or st
    raw = json.dumps(tpl).replace("{{ST}}", st).replace("{{NAME}}", name).replace("{{YEAR}}", str(YEAR)).replace("{{TODAY}}", TODAY)
    led = json.loads(raw)
    for sub in ("research", "stories", "articles", "visuals", "inbox", "handoff", "package_src"):
        (pdir(st) / sub).mkdir(parents=True, exist_ok=True)
    save(st, led)
    (pdir(st) / "DECISIONS_AND_HISTORY.md").write_text(f"# {name} {YEAR}: decisions and history\n\nNewest last. One entry per stage: what was done, what was decided, what is open.\n", encoding="utf-8")
    print(f"created {p}\nNext: docs/production/08_HANDOFF_PROTOCOL.md section 'Starting a new state'.")


# ---------------------------------------------------------------- rendering
def status_md(led):
    L = [f"# {led['state_name']} {led['year']}: state of play ({led['updated']})", "", led["headline"], "", "| Stage | Status | Note |", "|---|---|---|"]
    for s in led["stages"]:
        L.append(f"| {s['title']} | {s['status']} | {s.get('note', '')} |")
    if led.get("blocked"):
        L += ["", "## Blocked"] + [f"- {b['what']}: {b['why']}. Rule: {b['rule']}." for b in led["blocked"]]
    if led.get("do_not_redo"):
        L += ["", "## Do not redo"] + [f"- {x}" for x in led["do_not_redo"]]
    if led.get("conflicts_to_watch"):
        L += ["", "## Watch for"] + [f"- {x}" for x in led["conflicts_to_watch"]]
    return "\n".join(L) + "\n"


def tasks_md(led, lanes, pid):
    L = [f"# Tasks for this chat (lanes: {', '.join(lanes)}; package {pid})", ""]
    for lane in lanes:
        L += [f"## Lane: {lane}", led["lanes"][lane]["role"], "", "### Assigned to you now"]
        mine = [t for t in led["lanes"][lane]["tasks"] if t["status"] in TASK_OPEN]
        if not mine:
            L.append("- none")
        for t in mine:
            L += [f"#### {t['id']}: {t['title']}", "Inputs (in `inputs/`): " + ", ".join(f"`{Path(i).name}`" for i in t.get("inputs", [])),
                  "Return: " + ", ".join(f"`{r}`" for r in t.get("returns", [])), ""]
        L += ["### Not yours (do not draft, do not ask about)"]
        for t in led["lanes"][lane]["tasks"]:
            if t["status"] not in TASK_OPEN:
                L.append(f"- {t['id']} ({t['status']}): {t['title']}. {t.get('note', '')}")
        L.append("")
    if len(lanes) > 1:
        L += ["## Order of work", "Do the article first, then the images for it, unless the owner says otherwise.", ""]
    L += ["## Standing role for the rest of this chat",
          "The owner will bring more requests here: story-board or STORY_BRIEF files, claims files, new angles, image briefs and later video scripts. Treat each new file as a new task: read its brief, follow `RETURN_FORMAT.md` and keep the house rules. Claude Code writes every new brief, so you never need to ask where one goes. If something would be published or sent to anyone, stop: that is the owner's decision."]
    return "\n".join(L) + "\n"


def handshake_md(led, lanes, pid, mine):
    qs = [c["q"] for c in led["readback_checks"] if c["lane"] in lanes]
    ids = ", ".join(t["id"] for t in mine)
    L = ["# Handshake: your first reply", "",
         f"Package `{pid}`. Before any work, post exactly this block as your **first reply** (fill in the blanks). Then start the first assigned task right away; do not wait for an answer unless `blocking_questions` is not `none`. The owner passes the block to Claude Code, which checks it against the package.", "",
         "```", "READBACK", f"package_id: {pid}", "role: <one sentence: what you do and what you never do>", f"tasks: <the task ids you will do now; expected from TASKS.md: {ids or 'none'}>",
         "not_mine: <task ids listed as not yours>", "answers:"]
    L += [f"  {i}. <your answer to: {q}>" for i, q in enumerate(qs, 1)]
    L += ["missing: <inputs you expected but cannot find, or none>", "blocking_questions: <at most 3, or none>", "plan: <your order of work in 4 lines or fewer>", "```", "",
          "Why: Claude Code cannot see this chat. The readback is the only proof that what you understood matches what the ledger says. If it does not match, Claude will say what to correct before you spend effort on the wrong thing.", "",
          "When you finish, return files exactly as `RETURN_FORMAT.md` says, put the package id at the top of your notes file, and end with a one-line status per task: `complete`, `partial` (say what is missing) or `blocked` (say why)."]
    return "\n".join(L) + "\n"


IMAGES_RETURN = """# Returning images to Claude Code

One ZIP per brief, with: `masters/`, `web/`, `social/` (when the brief asks), `originals/` untouched, `prompts/` with the exact prompt, `manifest.json` (size, bytes, focal point as percentages, quiet-zone check) and `README.md`.

- The README starts with the package id and the task id, then one pass or fail line per hard rule, then anything you could not verify. Say plainly if a file was upscaled and from what native size.
- File names are the key in the brief (for example `mi-duggan.jpg`).
- Web exports are 350 KB or less unless the brief says otherwise.
- Do not paint any words into the art. The page adds all text.
- Alt text and caption lines go in the README, using the copy deck in the brief.
"""


def paste_prompt(led, lanes, mode, pid):
    n = led["state_name"]
    ids = ", ".join(t["id"] for ln in lanes for t in lane_tasks(led, ln) if t["status"] in TASK_OPEN)
    verbs = {"articles": "draft the assigned article(s)", "images": "make the assigned image(s)"}
    what = " and ".join(verbs[l] for l in lanes) + f" ({ids}) from Claude's briefs"
    have = ("You already know the LLF voice, formats and rules from this chat; this package adds the {n} state of play and your assigned tasks." if mode == "existing"
            else "You have not seen this project before: read `standards/00_READ_ORDER.md` first. This chat is also where I will bring later story briefs, claims and image or video requests, so keep what you read.").format(n=n)
    return (f"{n} {led['year']} update for LookLearnFind (package {pid}). Unzip the attached file and read `HANDSHAKE.md`, then `TASKS.md`. {have}\n\n"
            f"Your job: {what}. Post the READBACK block from `HANDSHAKE.md` as your first reply, then start without waiting. Use only the facts in the package; list anything else as a data request (format in `DATA_REQUEST.md`). "
            f"Return files as the `RETURN_FORMAT` file for each lane says. Never fact-check your own draft and never publish anything.\n")


FRESH_STANDARDS = [
    ("standards/house/HOUSE_RULES_ONE_PAGE.md", None), ("standards/house/PUBLISHING_RULES.md", "docs/election-build/PUBLISHING_RULES.md"),
    ("standards/house/BRAND.md", "docs/BRAND.md"), ("standards/workflow/00_READ_FIRST.md", "docs/production/00_READ_FIRST.md"),
    ("standards/workflow/01_END_TO_END_WORKFLOW.md", "docs/production/01_END_TO_END_WORKFLOW.md"),
    ("standards/workflow/02_AGENT_SKILL_MAP.md", "docs/production/02_AGENT_SKILL_MAP.md"),
    ("standards/workflow/03_VIDEO_SKILL_AND_SHOT_CONTRACT.md", "docs/production/03_VIDEO_SKILL_AND_SHOT_CONTRACT.md"),
    ("standards/workflow/08_HANDOFF_PROTOCOL.md", "docs/production/08_HANDOFF_PROTOCOL.md"),
]
HOUSE_RULES = """# House rules (one page)

- Scope: Governor, U.S. Senate, U.S. House only. No ballot measures, legislature, judges or Cabinet offices.
- No Oxford comma anywhere ("first, second and third").
- Neutral: no win probabilities, no rankings, no endorsements, no causal claims linking spending, polls or markets to outcomes.
- Every number: source, date, unit, period. Never "audited" or "official" unless the source is the official record.
- Kalshi: exact contract, price side, UTC timestamp. A price is not a forecast. Most contracts resolve on party, not person: read the rules text.
- Polls: field dates, sponsor, sample, method, margin of error, question wording. Give no number the release does not give.
- TIP grades: cite a grade only if visible on the TIP profile you link. "Not graded" is never zero.
- Links: first mention of each named candidate to their TIP profile; first mention of each race to the race page.
- The drafter does not fact-check their own article. Nothing is published without the owner's approval; approval for one item does not cover another.
- Images: AI illustrations only, disclosed; no faces, hands or silhouettes; no readable text; no campaign branding; no AI portraits of real candidates; no synthetic footage of real people or events.
- Video: asset pack only; no MP4 unless the owner explicitly requests a render.
"""


def read_order(lane):
    return ("# Read order (fresh chat)\n\n1. `standards/house/HOUSE_RULES_ONE_PAGE.md`\n2. `standards/workflow/00_READ_FIRST.md` and `01_END_TO_END_WORKFLOW.md` (who does what; stage gates)\n"
            "3. `standards/workflow/08_HANDOFF_PROTOCOL.md` (how this exchange works)\n4. `standards/house/PUBLISHING_RULES.md` and `BRAND.md`\n"
            + ("5. `standards/schemas/` (the article formats) and `standards/skills/llf-article-format.md`\n6. `examples/` (briefs and the published pieces they became)\n" if lane == "articles"
               else "5. `examples/reference_images/` (match these) and `examples/earlier_briefs/`\n6. `examples/hero_credits.json`\n")
            + "7. then `TASKS.md`, and post the READBACK from `HANDSHAKE.md`\n")


def add_fresh(root, led, lanes):
    lane = "all" if len(lanes) > 1 else lanes[0]
    for rel, src in FRESH_STANDARDS:
        if src is None:
            text(root, rel, HOUSE_RULES)
        else:
            put(root, rel, src)
    text(root, "standards/00_READ_ORDER.md", read_order(lane))
    if lane in ("articles", "all"):
        for p in sorted((R / "docs/schemas").glob("0*.md")):
            put(root, f"standards/schemas/{p.name}", p)
        for sk in ("llf-article-format", "llf-delta-editorial", "llf-story-scout", "llf-factcheck-finalize"):
            put(root, f"standards/skills/{sk}.md", f".claude/skills/{sk}/SKILL.md")
        put(root, "standards/tip_issue_definitions.json", f"data/elections/{led['state']}/tip_export/issue_definitions.json")
        for n in ("01_senate_money", "02_il07_ford", "03_il04_handoff"):
            for f in ("STORY_BRIEF.md", "CLAIMS.csv"):
                put(root, f"examples/illinois_briefs/{n}/{f}", f"docs/illinois/stories/{n}/{f}")
        for slug in ("aipac-udp-money-delta-october-2026", "michigan-senate-delta-october-2026", "illinois-il07-ford-outside-money-october-2026",
                     "illinois-senate-primary-money-october-2026", "illinois-il04-ballot-access-october-2026",
                     "florida-house-independent-spending-october-2026", "florida-governor-fundraising-polling-2026"):
            put(root, f"examples/published_pieces/{slug}.html", f"content/learn/{slug}.html")
        st = led["state"]
        put(root, "state_data/roster.json", f"data/elections/{st}/roster.json")
        put(root, "state_data/kalshi_capture.json", f"data/elections/{st}/markets.json")
        put(root, "state_data/official_listing_text.txt", f"data/elections/{st}/captures/boe_text.txt")
    if lane in ("images", "all"):
        for im in ("il-ford", "il-garcia", "il-stratton", "mi-udp", "s1-florida", "s2-illinois"):
            put(root, f"examples/reference_images/{im}.jpg", f"static/img/elections/{im}.jpg")
        put(root, "examples/reference_images/og-elections.jpg", "static/img/og-elections.jpg")
        put(root, "examples/hero_credits.json", "data/elections/hero_credits.json")
        put(root, "examples/earlier_briefs/HERO_IMAGE_BRIEF_ILLINOIS_MICHIGAN.md", "productions/2026/IL/visuals/HERO_IMAGE_BRIEF_FOR_CHATGPT.md")
        put(root, "examples/earlier_briefs/HOMEPAGE_IMAGES_BRIEF_FOR_CHATGPT.md", "productions/2026/visuals/HOMEPAGE_IMAGES_BRIEF_FOR_CHATGPT.md")


def cmd_build(a):
    st = a.state.upper()
    led = load(st)
    pid = f"{st}-{a.lane}-{TODAY.replace('-', '')}-{head()}"
    H = pdir(st) / "handoff" / pid
    if H.exists():
        shutil.rmtree(H)
    H.mkdir(parents=True)
    if a.lane == "claude":
        return build_claude(led, st, pid, H)
    lanes = list(led["lanes"]) if a.lane == "all" else [a.lane]
    for ln in lanes:
        if ln not in led["lanes"]:
            sys.exit(f"no lane {ln} in ledger")
    root = H / "pkg" / pid
    mine = [t for ln in lanes for t in lane_tasks(led, ln) if t["status"] in TASK_OPEN]
    if not mine:
        sys.exit(f"no ready tasks in lane {a.lane}; nothing to hand off")
    text(root, "HANDSHAKE.md", handshake_md(led, lanes, pid, mine))
    text(root, "TASKS.md", tasks_md(led, lanes, pid))
    text(root, "STATE_STATUS.md", status_md(led))
    for t in mine:
        for i in t.get("inputs", []):
            put(root, f"inputs/{t['id']}/{Path(i).name}", i)
    text(root, "HOUSE_RULES_ONE_PAGE.md", HOUSE_RULES)
    put(root, "DATA_REQUEST.md", f"productions/2026/{st}/package_src/return_templates/DATA_REQUEST.md")
    if "articles" in lanes:
        put(root, "RETURN_FORMAT_ARTICLES.md" if len(lanes) > 1 else "RETURN_FORMAT.md", f"productions/2026/{st}/package_src/return_templates/ARTICLE_RETURN.md")
    if "images" in lanes:
        text(root, "RETURN_FORMAT_IMAGES.md" if len(lanes) > 1 else "RETURN_FORMAT.md", IMAGES_RETURN)
    if a.mode == "fresh":
        add_fresh(root, led, lanes)
    scan_secrets(root)
    files = sorted(p for p in root.rglob("*") if p.is_file())
    man = {"package_id": pid, "state": st, "lane": a.lane, "mode": a.mode, "built": TODAY, "repo_commit": head(), "ledger_updated": led["updated"],
           "files": [{"path": str(p.relative_to(root)).replace("\\", "/"), "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    (root / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    z = H / f"{pid}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(root.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(root.parent))
    (H / "PASTE_THIS_FIRST.txt").write_text(paste_prompt(led, lanes, a.mode, pid), encoding="utf-8", newline="\n")
    key = {"package_id": pid, "lane": a.lane, "state": st, "tasks_assigned": [t["id"] for t in mine],
           "tasks_excluded": [t["id"] for ln in lanes for t in lane_tasks(led, ln) if t["status"] not in TASK_OPEN],
           "returns": {t["id"]: t.get("returns", []) for t in mine},
           "checks": [c for c in led["readback_checks"] if c["lane"] in lanes]}
    (H / "ANSWER_KEY.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    print(f"package {pid}\n  zip:    {z}\n  paste:  {H / 'PASTE_THIS_FIRST.txt'}\n  key:    {H / 'ANSWER_KEY.json'} (stays with Claude)\n  files:  {len(files) + 1}, {z.stat().st_size:,} bytes")
    if led.get("as_of_commit") and changed_since(led):
        print("WARN ledger is stale relative to the repository; run `handoff.py status` and re-stamp before sending.")


def build_claude(led, st, pid, H):
    c = [x for x in led.get("claude_tasks", [])]
    openc = [x for x in c if x["status"] in ("todo", "in_progress")]
    wait = [x for x in c if x["status"] == "waiting_owner"]
    blk = [x for x in c if x["status"] == "blocked"]
    n = led["state_name"]
    L = [f"# Claude Code kickoff: {n} {led['year']} (handoff {pid})", "",
         "Generated from the state ledger. Open a Claude Code session with working folder `C:\\Users\\Red Right Hand\\Desktop\\Issues Party\\looklearnfind` and add `...\\the-issues-party` as a second folder, then paste everything below the line.", "", "---", "",
         f"We are continuing **{n} {led['year']}** for LookLearnFind ({led['scope']} only). Same branch, local commits only. Handoff id `{pid}`. **Only one Claude session writes to this state at a time**; if another session is working on it, stop and tell me.", "",
         f"**Step 0.** Run `python tools/workflow/handoff.py status {st}`. If it prints STALE or ERROR, read the listed commits and fix the ledger before anything else; the ledger is the source of truth, this prompt is a copy of it.", "",
         f"**Step 1.** Read, in order: `CLAUDE.md`, `docs/production/08_HANDOFF_PROTOCOL.md`, `docs/production/09_OPERATING_PROCEDURES.md`, `productions/{YEAR}/{st}/STATE_LEDGER.json`, the last 40 lines of `{led['decisions_log']}`, `docs/production/CHAT_REGISTRY.md`. Then tell me in five lines what is done, who is waiting on whom, and what you will do first.", "",
         f"**Where things stand.** {led['headline']}", ""]
    L.append("**Your tasks, in this order** (decide, do and report; the gate column says when to stop):")
    for t in openc:
        L.append(f"- `{t['id']}` {t['title']} (gate: {t.get('gate', 'none')})")
    if wait:
        L += ["", "**Waiting on my approval (do not start; ask once, in one message, with the exact list you would apply):**"] + [f"- `{t['id']}` {t['title']}" for t in wait]
    if blk:
        L += ["", "**Blocked (do not start):**"] + [f"- `{t['id']}` {t['title']} ({t.get('gate', '')})" for t in blk]
    if led.get("blocked"):
        L += ["", "**Data you cannot reach (never work around a bot check):**"] + [f"- {b['what']}: {b['why']}" for b in led["blocked"]]
    L += ["", "**ChatGPT lanes.** When a task needs ChatGPT, generate its package instead of writing a prompt by hand: "
          f"`python tools/workflow/handoff.py build {st} --lane articles|images --mode existing|fresh` (use `existing` when I have a chat that already holds the project, `fresh` otherwise; ask me only if the registry does not say). "
          f"When I paste back a READBACK run `verify-readback`; when files come back run `ingest`. Both are in `docs/production/08_HANDOFF_PROTOCOL.md`.", "",
          "**Stop and ask me only for:** (1) any write to the TIP database, (2) anything that publishes, uploads or deploys, (3) fact-check sign-off before publishing. Everything else, decide, do and report.", "",
          f"**At the end of every stage:** update `{led['decisions_log']}` and the ledger (stage and task statuses), run `python tools/workflow/handoff.py stamp {st}`, commit locally and give me a short report with exact file paths. Do not leave the ledger behind the code.", "",
          "Standing rules are in `CLAUDE.md` and `docs/production/09_OPERATING_PROCEDURES.md`. No Oxford commas anywhere. The FEC key is in `.env.local`; never print it. Keep prompts to ChatGPT short (6 to 10 lines) except for animation."]
    out = H / "CLAUDE_KICKOFF.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(f"claude kickoff: {out}")


SECRET = [re.compile(r"eyJ[A-Za-z0-9_-]{20,}"), re.compile(r"service_role", re.I), re.compile(r"api_key=[A-Za-z0-9]{20,}")]


def scan_secrets(root):
    key = ""
    envf = R / ".env.local"
    if envf.exists():
        m = re.search(r"FEC_API_KEY\s*=\s*(\S+)", envf.read_text(encoding="utf-8"))
        key = m.group(1).strip("'\"") if m else ""
    for f in root.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".json", ".csv", ".html", ".txt"}:
            t = f.read_text(encoding="utf-8", errors="ignore")
            if key and key in t:
                sys.exit(f"FEC key found in {f}")
            for b in SECRET:
                if b.search(t):
                    sys.exit(f"secret-looking string in {f}: {b.pattern}")


# ---------------------------------------------------------------- readback
def find_pkg(st, pid):
    base = pdir(st) / "handoff"
    if pid == "latest":
        c = sorted((p for p in base.glob("*") if (p / "ANSWER_KEY.json").exists()), key=lambda p: p.stat().st_mtime)
        if not c:
            sys.exit("no packages built yet")
        return c[-1]
    p = base / pid
    if not p.exists():
        sys.exit(f"no package {pid}")
    return p


def cmd_verify(a):
    H = find_pkg(a.state.upper(), a.package)
    key = json.loads((H / "ANSWER_KEY.json").read_text(encoding="utf-8"))
    t = Path(a.file).read_text(encoding="utf-8", errors="ignore")
    fails, notes = [], []
    m = re.search(r"package_id:\s*(\S+)", t)
    if not m:
        fails.append("no package_id line")
    elif m.group(1).strip("`") != key["package_id"]:
        fails.append(f"package_id is {m.group(1)}, expected {key['package_id']} (an older or different package)")
    tm = re.search(r"^\s*tasks:\s*(.+)$", t, re.M)
    tl = tm.group(1) if tm else ""
    for tid in key["tasks_assigned"]:
        if tid not in tl:
            fails.append(f"assigned task {tid} not in `tasks:`")
    for tid in key["tasks_excluded"]:
        if re.search(rf"\b{re.escape(tid)}\b", tl):
            fails.append(f"excluded task {tid} appears in `tasks:` (it is not theirs)")
    ans = re.findall(r"^\s*(\d+)\.\s*(.+)$", t, re.M)
    amap = {int(n): s for n, s in ans}
    for i, c in enumerate(key["checks"], 1):
        s = amap.get(i, "").lower()
        if not s:
            fails.append(f"answer {i} missing: {c['q']}")
        elif not any(e.lower() in s for e in c["expect_any"]):
            fails.append(f"answer {i} does not mention any of {c['expect_any']}: {c['q']}")
    bq = re.search(r"blocking_questions:\s*(.+)", t)
    if bq and bq.group(1).strip().lower().strip("`.") not in ("none", ""):
        notes.append("they have blocking questions; answer them: " + bq.group(1).strip())
    ms = re.search(r"missing:\s*(.+)", t)
    if ms and ms.group(1).strip().lower().strip("`.") not in ("none", ""):
        notes.append("they report missing inputs: " + ms.group(1).strip())
    for n in notes:
        print("NOTE", n)
    for f in fails:
        print("FAIL", f)
    print("READBACK:", "PASS" if not fails else "FAIL")
    sys.exit(1 if fails else 0)


# ---------------------------------------------------------------- ingest
CLAIM_HDR = ["claim", "text_location", "source_url", "source_date", "checked_date", "status", "type", "evidence_ref"]


def cmd_ingest(a):
    st = a.state.upper()
    led = load(st)
    src = Path(a.path)
    tmp = Path(tempfile.mkdtemp())
    if src.is_file() and src.suffix == ".zip":
        zipfile.ZipFile(src).extractall(tmp)
        base = tmp
    else:
        base = src
    files = [p for p in base.rglob("*") if p.is_file()]
    names = [str(p.relative_to(base)).replace("\\", "/") for p in files]
    H = find_pkg(st, a.package_id or "latest")
    key = json.loads((H / "ANSWER_KEY.json").read_text(encoding="utf-8"))
    pid = key["package_id"]
    rep, fatal = [f"# Ingest report for {pid}", ""], False
    for tid in key["tasks_assigned"]:
        rep.append(f"## {tid}")
        for pat in key["returns"].get(tid, []):
            hits = [n for n in names if fnmatch.fnmatch(Path(n).name, pat) or fnmatch.fnmatch(n, pat)]
            rep.append(f"- {'OK  ' if hits else 'MISSING'} `{pat}`" + (f" -> {', '.join(hits)}" if hits else ""))
            fatal |= not hits
            for h in hits:
                p = base / h
                body = p.read_text(encoding="utf-8", errors="ignore") if p.suffix in {".html", ".md", ".csv", ".txt"} else ""
                if p.suffix == ".csv" and "CLAIMS" in p.name.upper():
                    rows = list(csv.reader(io.StringIO(body)))
                    if not rows or [x.strip() for x in rows[0]] != CLAIM_HDR:
                        rep.append(f"  - FAIL claims header is not {','.join(CLAIM_HDR)}")
                        fatal = True
                    else:
                        rep.append(f"  - claims rows: {len(rows) - 1}; NEW rows: {sum(1 for r in rows[1:] if len(r) > 5 and r[5].strip() == 'NEW')}")
                if p.suffix == ".html":
                    fm = re.match(r"---\n(.*?)\n---", body, re.S)
                    req = ["title", "dek", "format", "hero", "hero_alt", "hero_title", "hero_text"]
                    miss = [k for k in req if not fm or not re.search(rf"^{k}:", fm.group(1), re.M)]
                    rep.append(f"  - front matter missing: {miss}" if miss else "  - front matter keys present")
                    for blk in ("<!--openfile", "<!--sources", "<!--corrections"):
                        if blk not in body:
                            rep.append(f"  - FAIL block {blk} missing")
                            fatal = True
                    plain = re.sub(r"<[^>]+>", " ", body)
                    ox = re.findall(r"\b[\w'-]+, [\w' -]+, (?:and|or) \w+", plain)
                    rep.append(f"  - possible Oxford commas to check by eye: {len(ox)}" + ("".join(f"\n      - {x}" for x in ox[:6])))
                    rep.append(f"  - TIP candidate links: {len(re.findall('theissuesparty.org/candidates/', body))}; race links: {len(re.findall('theissuesparty.org/races/', body))}")
                    rep.append(f"  - [[s:n]] markers: {len(re.findall(r'\[\[s:\d+\]\]', body))}")
                if p.name.upper().endswith("NOTES.MD") and pid not in body:
                    rep.append("  - WARN notes do not carry the package id")
                if p.suffix in {".jpg", ".jpeg"} and "web" in h.split("/") and p.stat().st_size > 350_000:
                    rep.append(f"  - WARN web image is {p.stat().st_size:,} bytes (limit 350,000)")
    inbox = pdir(st) / "inbox" / pid
    inbox.mkdir(parents=True, exist_ok=True)
    for p in files:
        d = inbox / p.relative_to(base)
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(p, d)
    rep += ["", "Ingest copies files only. Nothing is converted, checked for truth or published. Next: convert, then independent fact-check."]
    (inbox / "INGEST_REPORT.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
    if not fatal:
        for lane in led["lanes"].values():
            for t in lane["tasks"]:
                if t["id"] in key["tasks_assigned"] and t["status"] in ("ready", "sent"):
                    t["status"] = "returned"
        save(st, led)
    print("\n".join(rep))
    print(f"\ninbox: {inbox}\nINGEST:", "INCOMPLETE" if fatal else "COMPLETE (ledger updated; commit it)")
    sys.exit(1 if fatal else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for n in ("status", "stamp", "init", "build", "verify-readback", "ingest"):
        s = sp.add_parser(n)
        s.add_argument("state")
        if n == "status":
            s.add_argument("--strict", action="store_true")
        if n == "init":
            s.add_argument("--name")
        if n == "build":
            s.add_argument("--lane", required=True)
            s.add_argument("--mode", choices=["existing", "fresh"], default="existing")
        if n == "verify-readback":
            s.add_argument("package")
            s.add_argument("file")
        if n == "ingest":
            s.add_argument("path")
            s.add_argument("--package-id")
    a = ap.parse_args()
    a.state = a.state.upper()
    {"status": cmd_status, "stamp": cmd_stamp, "init": cmd_init, "build": cmd_build, "verify-readback": cmd_verify, "ingest": cmd_ingest}[a.cmd](a)


if __name__ == "__main__":
    main()
