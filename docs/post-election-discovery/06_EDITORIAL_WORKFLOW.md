# 06 Editorial workflow

Sources: `CLAUDE.md`, `docs/production/` (00 to 10, CHAT_REGISTRY, DATA_ACCESS_LIMITATIONS), `docs/election-build/PUBLISHING_RULES.md` and `AGENT_RUNBOOK.md`, `docs/schemas/`, `build.py`, `tools/workflow/`, `tools/qa/`, the Minnesota and Pennsylvania ledgers, and this session's own work shipping both states. The process below is what was actually run, not only what is documented.

## 1. The pipeline in practice
1. **Set up a state** (`handoff.py init <ST>`): roster, TIP export and join, TIP gap list shown to the owner, portraits, Kalshi markets, district geometry, registry, state pages, strict build and tests.
2. **Find the story** (skill `llf-story-scout`): search recent coverage, open the original, write a brief per angle with sources marked opened or discovered, TIP grades, unknowns and a `ready_to_write` flag; `tools/story/story_brief_check.py` marks each angle READY or NOT_READY.
3. **Brief and claims:** each READY angle gets `STORY_BRIEF.md` and `CLAIMS.csv` (claim, source URL and date, status VERIFIED, ATTRIBUTED or NEEDS_CONTEXT) in the state's ledger as an `articles` task.
4. **Package for the writer:** `handoff.py build <ST> --lane articles --mode fresh` generates a zip plus `PASTE_THIS_FIRST.txt` from the ledger. The writer (ChatGPT or Kimi) returns an HTML draft, a claims file and notes. Image requests go to ChatGPT as a short separate brief.
5. **Ingest and convert:** a Claude session installs the draft into `content/learn/`, removes drafting language, sets the hero and openfile, adds the `data/discovery.json` entry and any homepage tile, then runs `build.py --strict` and the tests.
6. **Independent fact-check:** a different reviewer (a separate subagent) opens the original sources, checks local data with separately written code and writes `productions/2026/<ST>/qa/FACTCHECK_REPORT.md` with a verdict per article. Fixes are applied and the resolution is appended.
7. **Owner sign-off, then deploy:** the owner signs off the fact-check and says "deploy". The build zip is uploaded to hosting.com after a server-side backup; URLs are checked with curl.
8. **Close out:** ledger stages and task statuses updated, decision log appended, `handoff.py stamp <ST>`, commit, push on the owner's word.

Stop points that need a person: TIP database writes, anything that publishes or deploys, fact-check sign-off, image generation, and any payment or key (`AGENT_RUNBOOK.md`).

## 2. Article format (Verified)
- **File:** `content/learn/{slug}.html`, front matter between `---` lines: `kind` (story), `layout` (report), `title` (never quoted), `dek`, `date`, `updated`, `author`, `category`, `format` (a public label), `topics`, `threads`, `hero` (an image key), `hero_alt`, `hero_title`, `hero_text`, optional `og`.
- **Body blocks** (HTML comments parsed by `take_block()` in `build.py`): `openfile` (question, checked, supported, other, open), `sources` (numbered rows: title, outlet, date, URL, note), `corrections` (dated lines). Inline `[[s:n]]` markers resolve to the source list.
- **Rendering:** a custom Python build, not Markdown or MDX. HTML is written by hand or by the drafting chat; `build.py` adds the shell, rail, footnotes, JSON-LD and canonical tags.
- **Schemas** (`docs/schemas/`): 1 State of the Race, 2 Delta Report, 3 Spending Report, 4 Dark Horse vs party establishment, 5 Dark Horse vs AIPAC-supported, 6 AIPAC-supported candidates still running, 7 State and race article requirements. Several were drafted by ChatGPT and adopted by Claude. Since the 2026-10-24 "lean reset" the working standard is a short sourced story over a complete dataset.
- **Rules enforced by the build:** R1 (first mention of a featured candidate links to TIP; a missing TIP profile is a violation) and R2 (race mentions link to the race), via `autolink()` and `RACE_PATTERNS`. `python build.py --strict` fails on any violation. A politics story without a `data/discovery.json` entry fails the build.
- **Rules enforced by convention and the QA gate:** R3 reported numbers attributed, R4 same-source comparisons only, R5 drafter never fact-checks, R6 alt text, R7 freshness check (`tools/qa/freshness_check.py`), R14 recorded authorization, R15 unreadable sources recorded.

## 3. Status, approval, revision
- **Status:** an article is published if its file is in `content/learn/`. The site has no draft or scheduled state.
- **Where draft state is tracked:** `productions/2026/<ST>/STATE_LEDGER.json` (tasks move ready, drafted, fact_checked, published or not_ready) and the append-only `data/elections/workflow_ledger.jsonl` (57 lines; lean lane DISCOVERED to PUBLISHED, production lane INTAKE to USER_MJ_PREMIERE_HANDOFF; `transitions.py` refuses skipped steps).
- **Approval:** recorded by hand in the ledger and decision log. The workflow ledger takes `--authorization "<owner's words>"` for publish, deploy and render stages and `--reviewer` for fact-check stages.
- **Revision history:** git (93 commits in the LLF repository), the dated `corrections` block shown on the page, the `updated` field (displayed as "Updated" and emitted as `dateModified`), and per-state fact-check reports. There is no per-article revision table and no diff viewer.
- **Corrections:** appended to the article's corrections block with a date and described in the decision log; 14 of 21 political articles have at least one dated entry.

## 4. Source attribution and metadata
Sources are text rows inside each article, not records. Provenance for data (rosters, markets, TIP exports) is kept as dated raw captures in `data/elections/<ST>/captures/` with hashes, a per-state `DECISIONS_AND_HISTORY.md`, and `docs/production/DATA_ACCESS_LIMITATIONS.md` for blocked sources (Illinois and New York boards returned 403 and the Minnesota Secretary of State sits behind a captcha; all three are recorded there). The Pennsylvania Department of State list was not found by a plain request and is noted only in the Pennsylvania decision log, not in that file. Editorial metadata for discovery lives in `data/discovery.json`.

## 5. Image asset management
Images are produced outside the repository (ChatGPT, Midjourney), delivered as zips with a 3600 x 2400 master and an 1800 x 1200 web JPEG per key, installed by script into `static/img/elections/` (web) and `productions/2026/<ST>/visuals/masters/` (masters), and credited as AI illustrations in `data/elections/hero_credits.json`. Keys follow a pattern (`s7-minnesota` state tile, `mn-capitol` governor hero, `mn-01` district hero). The repository records no image licensing database beyond that JSON and `docs/election-build/ASSET_MANIFEST.csv`. Hero image keys for an article are set in front matter.

## 6. Admin and CMS
**None for articles.** `/admin/` is the Look Ledger review desk (queue, reports, threads, entries, audit, people, desk) behind PHP role checks for `editor` and `admin`. TIP has a separate admin for applications, grants, parties, social and match tools; none edits articles or race content.

## 7. Automated workflows (Verified)
- `tools/dark_horse/daily.py` via `cron_run.sh`: market quotes (Kalshi, Polymarket) and polls (VoteHub) for a 28-row watchlist (24 monitored); writes dated JSON; copies `status.json` to the server. Last run 2026-11-03T15:26Z, no source errors. **Unknown:** whether the cron entry on the server is still active after Election Day.
- `tools/qa/`: `factcheck_gate.py`, `freshness_check.py`, `smoke.py` (link check), `skill_manifest.py`.
- Tests: 17 files, 149 tests, all passing at `159302a`.
- Twelve agent skills in `.claude/skills/` and `docs/production/skills/`.
- Social posting (TIP): `app/api/social/jobs/*` and `app/admin/social/*` handle outbound posts and responses; not part of LLF publishing.

## 8. Existing mechanisms relevant to a continuously updated page (facts, not recommendations)
- **`updated` and `dateModified`** are per-article fields already shown on the page and in JSON-LD, so an edited story can already declare itself updated. The sitemap `lastmod`, however, is a single site-wide value (`config.json` `updated`).
- **Corrections block** is a dated, human-readable change log per article.
- **Build-time JSON for client use:** `/data/discovery/{id}.json` (sidebar), `/search-index.json`, `/data/candidates.json` and `/elections/2026/dark-horse/status.json` are examples of data the browser reads after page load.
- **PHP API** can serve dynamic JSON (threads, ledger lists) from SQLite, with rate limiting and role checks.
- **Ledger tasks and `STATE_LEDGER.json`** already model a per-state task list with owners, blockers and `do_not_redo` notes, which is the closest existing thing to an editorial ledger.
- **Deployment is manual:** a local build, a zip, a server backup, `scp`, `unzip`. No continuous deployment exists for LLF (a GitHub push does not publish).
