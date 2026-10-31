# New state quickstart (2026-10-31)

For the owner and for a Claude Code session starting a new state. Written after Florida, Illinois, Michigan, New York and New Jersey. The protocol is `08_HANDOFF_PROTOCOL.md`; durable rules and procedures are `09_OPERATING_PROCEDURES.md`. This file is the short path through them.

## What the owner says to start
Open a Claude Code session in the `looklearnfind` folder with the `the-issues-party` folder added, and paste:

> Start **<State> 2026** for LookLearnFind. First read `CLAUDE.md`, `docs/production/08_HANDOFF_PROTOCOL.md`, `09_OPERATING_PROCEDURES.md`, `10_NEW_STATE_QUICKSTART.md` and `docs/production/CHAT_REGISTRY.md`. Then run `python tools/workflow/handoff.py init <ST> --name "<State>"` and work the ledger. Decide and report; stop only for TIP database writes, anything that publishes or deploys, and fact-check sign-off.

A state that already has a ledger (Michigan) is continued with `python tools/workflow/handoff.py build <ST> --lane claude`, which writes the kickoff from the ledger.

## What the session does, in order
1. `handoff.py init <ST>`: creates `productions/2026/<ST>/STATE_LEDGER.json` and folders.
2. **Roster.** Official state list if the site answers a plain request; otherwise Green Papers, labeled "not an official list" on every page, and a line in `DATA_ACCESS_LIMITATIONS.md`. Never spoof a browser to get past a 403. Use `tools/elections/build_<st>_roster.py` from the nearest state as the pattern (`build_mi_roster.py`, `build_nj_roster.py`, `build_ny_roster.py`, `build_il_roster.py`).
3. **TIP export and join** (`node scripts/export/state-packet.mjs <ST>` in the TIP repo, then `LLF_STATE=<ST> python tools/elections/join_tip.py ...`). **Show the owner the TIP gap list before any TIP write.** Precedents: `docs/michigan/TIP_FIX_LIST_FOR_APPROVAL.md` and `apply-*-gap-*.mjs` in the TIP repo. New profiles go in as `needs_review`; new race entries as `review`. Promoting entries to `active` is a separate owner approval (`promote-mi-governor-entries.mjs` is the pattern: backs up the rows first).
4. **Portraits** (`fetch_portraits.py`; licensed only, monograms otherwise), **markets** (`fetch_kalshi.py`), district geometry.
5a. **Candidate registry:** `python tools/elections/build_registry.py <ST>` writes `data/candidates/<ST>.json` and `productions/2026/<ST>/gaps.csv`; the gaps become the TIP fix list (owner approves any TIP write). `build.py` puts every state in the registry on `/find/candidates/` automatically.
5. **State pages:** add the state to `STATES` in `elections.py` (copy a neighbor; set `official`, `governor` and `senate` flags honestly) and to the `build()` list. `python build.py --strict` must report 0 violations; run the full test suite.
6. **Story Scout** (`llf-story-scout`), then for each READY angle a brief and claims under `productions/2026/<ST>/package_src/stories/<ID>/`, added to the ledger's `articles` lane as a task. FEC-based stories: use `tools/elections/reconcile_ie.py` (pairs 24/48-hour notices with periodic-report rows) and never the FEC candidate summary for a candidate with more than one authorized committee.
7. **Image briefs** (short; 6 to 10 lines; match the existing set) added to the `images` lane.
8. `handoff.py build <ST> --lane all --mode fresh` (new ChatGPT chat) or `--lane articles|images --mode existing` (a chat that already holds the project). Give the owner the zip and `PASTE_THIS_FIRST.txt`; the owner records chat titles in `CHAT_REGISTRY.md`.
9. When files come back: `handoff.py ingest`, convert, **fact-check against the raw data with separately written code**, fix or cut, add the `data/discovery.json` story entry, strict build, tests. Owner signs off the fact-check.
10. Deploy only with the owner's yes (procedure in `09`). End every stage with the ledger update, decision log, `handoff.py stamp`, commit.

## Gotchas learned (each one cost time)
- Run `build.py` from the repository root. If the shell's working directory is `dist/`, the build dies with a PermissionError. Stop any `python -m http.server` first.
- Every new politics story needs an entry in `data/discovery.json` or the build fails with a KeyError. Insert it as a one-line entry; do not reformat the file.
- Never quote the `title:` in front matter. `format:` is a public label ("Spending Report", "Reported Feature", "Delta Report"), never a schema name.
- A story's dates: use the dissemination date for FEC independent expenditures, and say which. Payment dates and dissemination dates differ.
- Changing a shared counting rule (for example the independent-expenditure dedupe) changes live numbers on pages already published. Add a dated entry to each affected story's `<!--corrections-->` block in the same change.
- Kalshi contracts for the nominees usually resolve on party, not person. Read the rules text.
- A deploy that includes everything built locally will publish unapproved pages. Check what the zip contains, or upload only the files approved (the New York hub went up first by hand-built zip).
- `scp` breaks on paths with spaces: copy the zip to `$TEMP` first; quote the key path.
- Two Claude sessions must not write to the same state. The ledger names the owner of each task.

## Assets to point a new session at
| Need | Path |
|---|---|
| Session protocol and rules that never change | `CLAUDE.md` |
| How sessions and chats exchange work | `docs/production/08_HANDOFF_PROTOCOL.md`, `tools/workflow/handoff.py` |
| Durable rules, FEC key, deploy, TIP data model | `docs/production/09_OPERATING_PROCEDURES.md` |
| Which chat holds what | `docs/production/CHAT_REGISTRY.md` |
| Ledger template | `docs/production/templates/state/STATE_LEDGER.template.json` |
| Worked examples (full ledger, briefs, claims, fact-checks, decision logs) | `productions/2026/MI/` and `docs/michigan/DECISIONS_AND_HISTORY.md` |
| Candidate directory plan and status | `docs/election-build/CANDIDATE_DIRECTORY_SPEC.md` |
| Article formats and publishing rules | `docs/schemas/`, `docs/election-build/PUBLISHING_RULES.md`, `.claude/skills/` |
| Video (asset pack only; no MP4 unless asked) | `docs/production/03_VIDEO_SKILL_AND_SHOT_CONTRACT.md`, `llf-video-director`; the owner's Remotion workflow for rendering |
| Known unreadable sources | `docs/production/DATA_ACCESS_LIMITATIONS.md` |

## Open items that carry into new states
- The candidate directory (`/find/candidates/`) phase 1 is built; phases 2 and 3 are in `CANDIDATE_DIRECTORY_SPEC.md`.
- Illinois and New York rosters are unofficial until their state board lists can be read.
- Michigan, MI-A3 and MI-A4 use placeholder heroes.
