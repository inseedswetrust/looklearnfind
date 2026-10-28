# Handoff protocol (v1, 2026-10-28)

Added to the Production Lock after the Michigan start showed what was missing: three hand-written handoff documents that drifted from the work, no record of which ChatGPT chat held what, no proof a receiving chat understood its job, and no check on what came back. This protocol replaces hand-written kickoffs with **one ledger per state and generated, verified exchanges**. It adds to `00` to `03` and `06`; it does not change them.

## 1. The model
```
                 owner (approves, routes, runs Midjourney and Premiere)
                        │
   Claude Code ◄────────┼────────► ChatGPT chat(s)
   (repository,         │          (writes, directs images, scripts)
    research, build,    │
    fact-check, publish)│
        │
  STATE_LEDGER.json  (single source of truth, one per state)
        │ generates
  CLAUDE_KICKOFF.md   +   <package>.zip + PASTE_THIS_FIRST.txt
        ▲                         │
        │  READBACK (verified)    │
        └──── ingest ◄── returned files
```
- **The ledger** is `productions/2026/<ST>/STATE_LEDGER.json`: stages, tasks per lane with status, what is waiting on the owner, what is blocked, what not to redo, and the comprehension checks. Everything handed to anyone is generated from it. Nothing is hand-written twice.
- **Lanes.** `articles` (ChatGPT drafts), `images` (ChatGPT makes images), later `video` (ChatGPT script and storyboard). A lane can be one chat or all lanes can share one general chat; `CHAT_REGISTRY.md` records which.
- **One writer.** Only one Claude session writes to a state at a time. A second session reads, never writes, unless the first has stamped the ledger and said it is finished.

## 2. Commands (`tools/workflow/handoff.py`)
| Command | What it does |
|---|---|
| `init <ST> --name <Name>` | New state: scaffold the folder and a ledger from `templates/state/STATE_LEDGER.template.json` |
| `status <ST> [--strict]` | Compare the ledger with the repository: evidence files exist, ready tasks have their inputs, and whether commits touched the state since the ledger was last stamped (prints STALE and lists them) |
| `stamp <ST>` | Record HEAD and today in the ledger. Run at the end of every stage, then commit |
| `build <ST> --lane claude` | Write `CLAUDE_KICKOFF.md` for a new Claude session |
| `build <ST> --lane articles\|images\|all --mode existing\|fresh` | Write a ChatGPT package zip, `PASTE_THIS_FIRST.txt` and a private `ANSWER_KEY.json` under `productions/2026/<ST>/handoff/<package_id>/` |
| `verify-readback <ST> <package_id\|latest> <file>` | Check the READBACK a chat posted against the answer key |
| `ingest <ST> <dir\|zip>` | Check returned files against the package's task list, copy them to `inbox/<package_id>/`, write `INGEST_REPORT.md` and mark tasks `returned` |

`existing` packages assume the chat already holds the project (voice, formats, rules) and carry only the state's current tasks and inputs. `fresh` packages add the standards, schemas, skills, examples, reference images and state data, so a brand-new chat can work without anything else. Use `fresh` whenever you are not sure.

## 3. The exchange, step by step
1. **Claude** finishes a stage, updates the ledger (statuses, tasks, inputs), runs `stamp`, commits.
2. **Claude** runs `build` for the lane and tells the owner: the zip, the paste text, which chat (from the registry) and why.
3. **Owner** opens the chat named, attaches the zip and pastes `PASTE_THIS_FIRST.txt`. (Short on purpose: long rule-heavy prompts degrade ChatGPT's output; the rules are in the package.)
4. **ChatGPT** replies first with a **READBACK**: package id, its role, the tasks it will do and the ones it will not, answers to the comprehension questions, what it is missing, blocking questions. It then starts work without waiting, unless it has blocking questions.
5. **Owner** pastes the READBACK into the Claude session (or saves it as a file). **Claude** runs `verify-readback`. PASS: nothing to do. FAIL: Claude writes the correction in one short message for the owner to paste back.
6. **ChatGPT** returns files in the formats in `RETURN_FORMAT*.md`, with the package id at the top of its notes and a one-line status per task. Data it lacks goes in `DATA_REQUEST.md` format; it keeps going.
7. **Owner** saves the returned files to a folder or zip and tells Claude the path. **Claude** runs `ingest`, reads `INGEST_REPORT.md`, converts to site form, sends used claims to an independent fact-check, fixes or cuts, builds with `--strict`.
8. **Owner** approves publication. **Claude** deploys with the procedure in `09_OPERATING_PROCEDURES.md`. Approvals are per action.

## 4. What every package guarantees
`HANDSHAKE.md` (the READBACK format), `TASKS.md` (assigned now, and not yours), `STATE_STATUS.md` (generated from the ledger), `RETURN_FORMAT*.md`, `DATA_REQUEST.md`, the house rules, each task's inputs, a `manifest.json` with SHA-256 hashes and the commit it was built from, and no secrets (the build fails if the FEC key or a service key appears).

## 5. Session start and end (Claude)
**Start:** `python tools/workflow/handoff.py status <ST>`; if STALE or ERROR, read the commits it lists and repair the ledger before anything else. Read `CLAUDE.md`, this file, `09_OPERATING_PROCEDURES.md`, the ledger and the tail of the decisions log. Report in five lines.
**End of every stage:** update the ledger and the decisions log, `stamp`, commit, report with exact file paths. A session that ends with the ledger behind the code has broken the protocol.

## 6. Starting a new state (what to say and what happens)
1. Owner says: "Start <State> <year>."
2. Claude: `python tools/workflow/handoff.py init <ST> --name <State>`, then follows the five `claude_tasks` the template seeds (roster, TIP export and join with the gap list shown to the owner, portraits, markets and pages, Story Scout, image briefs). As each READY angle gets a `STORY_BRIEF.md` and `CLAIMS.csv` in `productions/2026/<ST>/stories/<ID>/`, Claude adds it to the articles lane as a task with its inputs and returns; as each image brief is written, it is added to the images lane.
3. Claude updates `CHAT_REGISTRY.md` suggestions, runs `build --lane all --mode fresh` (or `existing` per lane) and gives the owner the zip, the paste text and the chat to use.
4. Steps 3 to 8 of section 3 repeat for every batch. Video starts only after approved articles and a script direction, as a new lane in the ledger.

## 7. Conflict rules
- The ledger wins over any prompt, handoff document or chat message. If the ledger is wrong, fix the ledger.
- An angle belongs to exactly one lane and one chat. Withdrawn angles stay in the ledger with the reason so no one rewrites them.
- Files that belong to another workstream (for example the TIP video rounds R10 and R11) are never sent to an LLF lane, and LLF briefs never go to that workstream, unless the owner says so.
- Blocked sources (HTTP 403 and bot checks) are recorded in the ledger's `blocked` list and `DATA_ACCESS_LIMITATIONS.md`; the rule is never to work around them.
