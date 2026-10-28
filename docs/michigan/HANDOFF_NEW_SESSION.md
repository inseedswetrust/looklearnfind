# Michigan 2026: handoff to a new session

Written 2026-10-28 at the end of the Illinois session. Branch `claude/funny-shannon-dg9qoe`, last commit when written: see `git log -1`. Read this file first, then follow the reading order in section 2.

## 1. Why a new session
The Illinois session ran across several context compactions. Michigan is a self-contained task (own roster, own TIP join, own stories), so a fresh session starts clean and reads the repository instead of a long summary. Nothing lives only in the old conversation: every decision, rule and procedure it used is written down below or in the files listed in section 9.

## 2. Open it in the right folder, read in this order
Open the session with the **LookLearnFind repo** as the working folder: `C:\Users\Red Right Hand\Desktop\Issues Party\looklearnfind`. Add the TIP repo (`...\the-issues-party`) as a second folder, because the TIP export script and TIP writes run there. The auto-memory of the old session is stored under the TIP project path and will not load in an LLF-folder session, so its contents are copied into section 5 and section 6.

Reading order:
1. `CLAUDE.md` (root) and `AGENTS.md` if present (no Oxford comma; mandatory pointers).
2. `docs/production/README.md`, `00_READ_FIRST.md`, `01_END_TO_END_WORKFLOW.md` (Production Lock v2.0: lean articles, video is an asset pack and never an MP4 unless explicitly requested, stage gates and lanes `production:<state>-<year>` and `render:<state>-<year>`).
3. `docs/production/05_MICHIGAN_KICKOFF.md` (the owner's own Michigan kickoff text).
4. `docs/election-build/INDEX.md` (the one index of schemas, skills, tools, data contracts), `PUBLISHING_RULES.md`, `AGENT_RUNBOOK.md`.
5. `docs/illinois/README.md`, `DECISIONS_AND_HISTORY.md`, `ILLINOIS_SKILLS_QA_AND_BLOCKERS.md` (the worked example of a fresh state, including what went wrong).
6. `docs/schemas/01_STATE_OF_THE_RACE.md` to `07_STATE_AND_RACE_ARTICLE_REQUIREMENTS.md` (the article formats).
7. `productions/2026/MI/README.md` and everything under `productions/2026/MI/research/` (the money delta work, already built).

## 3. What exists for Michigan today
| Item | Status | Where |
|---|---|---|
| AIPAC/UDP money delta report | **Live** since 2026-10-28 | `content/learn/aipac-udp-money-delta-october-2026.html`; research in `productions/2026/MI/research/` (`UDP_SPENDING_BRIEF.md`, `CLAIMS.csv`, `udp_schedule_e_raw.json`, `udp_delta_summary.json`, `udp_el_sayed_oct_2026.csv`); rebuild with `tools/dark_horse/udp_delta.py` |
| Kalshi market delta report (El-Sayed contract, October 8 debate) | Live since 2026-10-23 | `content/learn/michigan-senate-delta-october-2026.html` |
| Senate-only data from the Florida-era work | Exists, Senate only | `data/elections/MI/` (`candidates.json`, `finance_fec.json`, `kalshi_SENATEMI-26-D.json`, `kalshi_SENATEMI-26-R.json`, `portraits.json`, `captures/`) |
| Michigan State of the Race pages (hub, governor, Senate, House directory, 13 districts) | **Not built** | `elections.py` has `STATES` for FL and IL only |
| Michigan roster (all Governor, U.S. Senate and U.S. House candidates) | **Not built** | needs `data/elections/MI/roster.json` |
| TIP profiles and race entries for all Michigan candidates | **Unknown, must be checked** | TIP Supabase; see section 6 |
| Michigan hero images | Only `mi-udp` (the money delta hero) | `static/img/elections/mi-udp.jpg`; credits in `data/elections/hero_credits.json` |
| Michigan video asset pack | Not started | follow `llf-video-director`; script first |

Note: the Michigan hub does not exist, so the homepage does not link a Michigan state file yet. When it is built, add a third `state-tile` in `build.py` (search `state-tiles`) and a hero image for it.

## 4. The Michigan plan (suggested order; each step names its output)
1. **Roster.** Find the official Michigan Secretary of State or Bureau of Elections candidate list. If it blocks automation (Illinois did), do not work around the block (see the bot-check rule in section 5); use a published source such as the Green Papers, cross-check with OpenFEC and TIP, and label the list as not official on the page, as the Illinois pages do (`STATES["IL"]["source_note"]` in `elections.py`). Output: `data/elections/MI/roster.json` (copy the shape of `data/elections/IL/roster.json`; Illinois used `tools/elections/build_il_roster.py` and `build_il_mapping.py` as patterns).
2. **TIP export (read-only).** In the TIP repo: `node scripts/export/state-packet.mjs MI`, copy the output files to `data/elections/MI/tip_export/`. Then `LLF_STATE=MI python tools/elections/join_tip.py data/elections/MI/tip_export` (it links a profile only when a live GET returns 200).
3. **TIP gaps.** Produce a fix list of missing profiles and race entries and **show it to the owner before writing anything to TIP**. Illinois precedent: `docs/illinois/TIP_FIX_LIST_FOR_APPROVAL.md` and the applied SQL record `the-issues-party/docs/state-packets/IL/11_missing_profiles.sql` (applied through the PostgREST API with the service-role key from the TIP `.env.local`, never printed; new profiles use `verification_status = 'needs_review'`).
4. **Portraits.** `tools/elections/fetch_portraits.py` (public domain, CC0, CC BY and BY-SA only; credit recorded; no licensed image means a monogram marked not for publication).
5. **Markets.** `tools/elections/fetch_kalshi.py` for the state's contests.
6. **Build the pages.** Add an `"MI"` record to `STATES` in `elections.py` and to the list in `build()`, using the Illinois entry as the template (`finance=False` unless FEC data is wanted; `ndist=13`). Run `python build.py --strict` (no `-I`, it needs the repo on the path). Run the tests: `python -m unittest discover -s tests`. `tests/test_illinois_pages.py` is the model for a state test.
7. **Story Scout.** Use `llf-story-scout` to propose ranked stories; hand ChatGPT a short `STORY_BRIEF.md` and take back `CLAIMS.csv` (the lean lane). Candidates already researched: the money delta (done) and anything the owner brings.
8. **Heroes.** Copy the pattern of `productions/2026/visuals/HERO_IMAGE_BRIEF_FOR_CHATGPT.md` and `HOMEPAGE_IMAGES_BRIEF_FOR_CHATGPT.md`. Heroes are AI illustrations with the credit "AI illustration. Not a photograph of a real place or event." (entries in `hero_credits.json` use `"ai": true`; `_hero()` in `elections.py` prints that credit). No AI portraits of real candidates.
9. **Fact-check, then publish.** The drafter does not fact-check their own article; the owner (or a reviewer) does. Publishing means moving the article into `content/learn/` (remove any `status:` line; `format:` must be a public label such as "Spending Report", never a schema name), building with `--strict`, and deploying (section 6). Only with the owner's explicit approval.
10. **Video (only after the owner approves a script).** `llf-video-director` is the single entry point; asset pack only, no MP4.

## 5. Standing rules (the owner's, in force for every state)
- **Scope:** Governor, U.S. Senate and U.S. House only.
- **Links:** R1 the first mention of a featured candidate links to their TIP profile; R2 every mentioned race links to that race. Enforced by `build.py --strict` (0 violations required).
- **Grades:** cite a grade only from the profile that shows it. "Not graded" is never zero.
- **Neutral reporting:** no win probabilities, no causal claims about spending and results, no rankings or endorsements. Reported numbers are attributed and never called audited. Keep documented spending apart from described ties (AIPAC/UDP wording rule).
- **Copy:** no Oxford comma in any copy, UI text, scripts or docs.
- **Fact-check:** the drafter does not check their own article.
- **Approval:** nothing is published, uploaded, deployed, rendered or written to production (TIP database included) without the owner's explicit approval. Approval for one thing does not carry to the next.
- **FEC data** is optional and never a gate. **No synthetic footage** of real people or events. **AI visuals are disclosed.** **No AI portraits** of real candidates.
- **Video:** asset pack only, never an MP4 unless explicitly requested.
- **Fewer stops:** the owner is frustrated by repeated questions; decide sensible defaults, report them, and ask only when the decision is truly theirs.
- **Bot-check rule:** do not get past an HTTP 403 or bot check by spoofing a browser user agent (the auto-mode classifier blocks it). If a government site refuses automated access, say so, use a clearly labeled alternative source, and note it as a blocker.
- **Names:** the money delta piece is "the money delta piece" for the owner's concept; the folder `productions/2026/MI/` is only a state folder. Do not call a piece by the state name when the owner has a concept name for it.

## 6. Procedures the old session learned
**FEC key.** The owner's OpenFEC key is `FEC_API_KEY` in `looklearnfind/.env.local` (git-ignored; `.env` and `.env.local` are in `.gitignore`). `tools/dark_horse/udp_delta.py` reads it from there; other FEC tools read the `FEC_API_KEY` environment variable. Use it without asking. Never print it, commit it, or put it in a document or chat. DEMO_KEY is rate-limited (429).

**FEC facts that matter.** `/committee/{id}/totals/` is report-based and cumulative; `/schedules/schedule_e/` has Form 24/48-hour notices with a date, not a time. Do not add independent expenditures, contributions to committees and total disbursements together.

**Windows and shell.** Use `PYTHONUTF8=1`. Write patch scripts with the Write tool rather than multiple heredocs in one Bash call. Run Python with `-I` only for scripts that do not import repo modules (`build.py` imports `elections`, so no `-I`). Stop any local `python -m http.server` on `dist` before `build.py` (it locks the folder). `scp` breaks on paths with spaces: copy the file to the scratchpad first and use `"$HOME/.ssh/hosting_com"` quoted. Console output mangles accents (the "Patty Garc?a" scare was a console artifact; the database was fine).

**Deploy LookLearnFind** (done twice on 2026-10-28):
1. `python build.py --strict --zip --keep-live-robots` writes `release/looklearnfind-elections-update.zip` (it skips `robots.txt`, `config.php` and the SQLite files).
2. Copy the zip to the scratchpad, then `scp -i "$HOME/.ssh/hosting_com" llf-update.zip ascendan@65.181.121.38:looklearnfind.com/looklearnfind-elections-update.zip`.
3. Back up first: on the server `cd ~ && tar czf backups/looklearnfind.com-pre-<date>.tgz --exclude=looklearnfind-elections-update.zip looklearnfind.com`.
4. `cd ~/looklearnfind.com && unzip -oq looklearnfind-elections-update.zip && rm looklearnfind-elections-update.zip`.
5. `curl` every new URL and the homepage; confirm 200.
Rollback tars on the server: `~/backups/looklearnfind.com-pre-20261028.tgz` (before the four articles) and `...-pre-20261028b.tgz` (before the homepage images). Bump `config.json` `updated` when CSS changes so browsers reload (it is the cache-busting `?v=`).

**TIP is separate.** TIP (theissuesparty.org, Next.js plus Supabase) is served from the same hosting.com account with its own runbook: `the-issues-party/docs/HOSTING-RUNBOOK-2026-10-20.md` and `docs/HANDOFF-2026-10-20-hosting-migration.md`. Another Claude session may deploy TIP; never touch `~/tip` from the LLF lane.

**TIP data model.** `candidates` (profile URL key is `fec_candidate_id`, for example `GOV-IL-PRITZKER`), `race_entries` (`race_key`, `source_key`, `ballot_type` printed or write_in, `status` active, review or withdrawn; public access shows only `active`), `candidate_issue_grades`. TIP SQL migrations are normally run by hand in the Supabase SQL editor.

## 7. Carried-over open items (Illinois and site)
- The Illinois State Board of Elections list is unread (HTTP 403, and the bot-check rule applies). Until it is read: the Illinois roster is labeled not official, the Ford piece's "field of 13" is unconfirmed, and 9 governor entries plus the 11 added profiles sit at `review` on TIP. Promote them to `active` only after the Board list is read and only with the owner's approval.
- Licensed portraits are missing for some Illinois people (monograms marked not for publication).
- Five Illinois "National source only" entries.
- The AIPAC money delta still needs: the New York Times original for the $9 million (paywalled; the figure is described as reported and unconfirmed), any UDP notices dated after October 23 (none as of 2026-10-28; rerun `tools/dark_horse/udp_delta.py`), the Great Lakes Conservatives Fund filings when they appear, and a response from UDP or AIPAC.
- Illinois Senate piece cites shares at 82 percent of precincts; a certified statewide result was not read. The Sigcho-Lopez lawsuits (state suit Aug 4, federal suit Jul 31) have no ruling found.
- The Florida and Illinois state tiles on the homepage use `s1-florida.jpg` and `s2-illinois.jpg`; the homepage social card is `static/img/og-elections.jpg`.
- Patty García accent on TIP (`display_name`) is optional.
- `productions/2026/IL/articles/*` and `productions/2026/MI/articles/*` are the pre-publication drafts. The published, canonical copies are in `content/learn/`. Edit those, not the drafts.
- Nothing has been pushed to GitHub; all commits are local on the branch. The old public download link in `docs/DEPLOY.md` is stale for that reason.

## 8. What the live site shows (2026-10-28)
Homepage with the money delta lead, three Illinois reports and two state tiles; four new reports at `/learn/<slug>/` (`aipac-udp-money-delta-october-2026`, `illinois-il07-ford-outside-money-october-2026`, `illinois-senate-primary-money-october-2026`, `illinois-il04-ballot-access-october-2026`); Florida and Illinois state hubs under `/elections/2026/`; the Illinois pages are `noindex`. Listing pages no longer show raw `[[v:...]]` tokens.

## 9. Document and file reference
| Need | File |
|---|---|
| Workflow, gates, lanes | `docs/production/00_READ_FIRST.md`, `01_END_TO_END_WORKFLOW.md`, `02_AGENT_SKILL_MAP.md`, `06_DECISION_LOG.md` |
| Everything indexed | `docs/election-build/INDEX.md` |
| Publishing rules R1 R2 | `docs/election-build/PUBLISHING_RULES.md` |
| Illinois worked example | `docs/illinois/*` |
| Article formats | `docs/schemas/01` to `07` |
| Skills | `.claude/skills/*/SKILL.md` (election-state-packet 1.0.2, llf-story-scout, llf-article-format, llf-factcheck-finalize, llf-election-render, llf-publication-qa, llf-video-director 2.0.0, llf-footage-scout, llf-video-storyboard, llf-delta-editorial, darkhorse-source-monitor, workflow-retrospective) |
| Ledger of decisions | `docs/election-build/WORKFLOW_LOG.md`, `data/elections/workflow_ledger.jsonl` |
| Hero and homepage image briefs | `productions/2026/visuals/HERO_IMAGE_BRIEF_FOR_CHATGPT.md`, `HOMEPAGE_IMAGES_BRIEF_FOR_CHATGPT.md` |
| Money delta | `productions/2026/MI/` |
| Hero credits | `data/elections/hero_credits.json` |
| Tests | `python -m unittest discover -s tests` (124 passing on 2026-10-28) |
| TIP fix precedent | `docs/illinois/TIP_FIX_LIST_FOR_APPROVAL.md`, TIP repo `docs/state-packets/IL/11_missing_profiles.sql` |
| Opening prompt for the new session | `docs/michigan/OPENING_PROMPT.md` |

## 10. Definition of done for Michigan
Roster reconciled to TIP with every listed candidate linked; Michigan hub, governor, Senate, House directory and 13 district pages built and strict-clean; at least one reported piece fact-checked and approved by the owner; heroes in place with disclosed credits; deployed with the owner's approval and checked by `curl`; this folder updated with a decisions log (`docs/michigan/DECISIONS_AND_HISTORY.md`, same shape as Illinois).
