# Operating procedures (durable, every state)

Moved here on 2026-10-28 from the Michigan handoff so no state's handoff has to repeat them. State-specific facts live in that state's `STATE_LEDGER.json`; how sessions and chats exchange work is in `08_HANDOFF_PROTOCOL.md`. When a rule here changes, change it here only.

## A. Standing rules (the owner's, in force for every state)
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

## B. Procedures
**FEC key.** The owner's OpenFEC key is `FEC_API_KEY` in `looklearnfind/.env.local` (git-ignored; `.env` and `.env.local` are in `.gitignore`). `tools/dark_horse/udp_delta.py` reads it from there; other FEC tools read the `FEC_API_KEY` environment variable. Use it without asking. Never print it, commit it, or put it in a document or chat. DEMO_KEY is rate-limited (429).

**FEC facts that matter.** `/committee/{id}/totals/` is report-based and cumulative; `/schedules/schedule_e/` has Form 24/48-hour notices with a date, not a time. Do not add independent expenditures, contributions to committees and total disbursements together.

**Windows and shell.** Use `PYTHONUTF8=1`. Write patch scripts with the Write tool rather than multiple heredocs in one Bash call. Run Python with `-I` only for scripts that do not import repo modules (`build.py` imports `elections`, so no `-I`). Stop any local `python -m http.server` on `dist` before `build.py` (it locks the folder). `scp` breaks on paths with spaces: copy the file to the scratchpad first and use `"$HOME/.ssh/hosting_com"` quoted. Console output mangles accents (the "Patty Garc?a" scare was a console artifact; the database was fine).

**Deploy LookLearnFind** (last used 2026-10-28; verify the steps still match `docs/DEPLOY.md` and the server before using):
1. `python build.py --strict --zip --keep-live-robots` writes `release/looklearnfind-elections-update.zip` (it skips `robots.txt`, `config.php` and the SQLite files).
2. Copy the zip to the scratchpad, then `scp -i "$HOME/.ssh/hosting_com" llf-update.zip ascendan@65.181.121.38:looklearnfind.com/looklearnfind-elections-update.zip`.
3. Back up first: on the server `cd ~ && tar czf backups/looklearnfind.com-pre-<date>.tgz --exclude=looklearnfind-elections-update.zip looklearnfind.com`.
4. `cd ~/looklearnfind.com && unzip -oq looklearnfind-elections-update.zip && rm looklearnfind-elections-update.zip`.
5. `curl` every new URL and the homepage; confirm 200.
Rollback tars on the server: `~/backups/looklearnfind.com-pre-20261028.tgz` (before the four articles) and `...-pre-20261028b.tgz` (before the homepage images). Bump `config.json` `updated` when CSS changes so browsers reload (it is the cache-busting `?v=`).

**TIP is separate.** TIP (theissuesparty.org, Next.js plus Supabase) is served from the same hosting.com account with its own runbook: `the-issues-party/docs/HOSTING-RUNBOOK-2026-10-20.md` and `docs/HANDOFF-2026-10-20-hosting-migration.md`. Another Claude session may deploy TIP; never touch `~/tip` from the LLF lane.

**TIP data model.** `candidates` (profile URL key is `fec_candidate_id`, for example `GOV-IL-PRITZKER`), `race_entries` (`race_key`, `source_key`, `ballot_type` printed or write_in, `status` active, review or withdrawn; public access shows only `active`), `candidate_issue_grades`. TIP SQL migrations are normally run by hand in the Supabase SQL editor.

