# 03 Results schemas, capture jobs and source validation (follow-up 4)

Responds to architecture v1 section 10 item 4. **Nothing here is implemented, and no official results feed is assumed to exist.** No results source was tested for this document. The JSON Schema files in `schemas/` are proposals (draft 2020-12) for review; they contain no data.

## 1. Principles carried over from the plan and from LLF rules
- LLF-owned, versioned, normalized JSON is the display source; raw captures are kept and hashed (the existing pattern in `data/elections/<ST>/captures/`).
- TIP owns race and candidate identity; results link to TIP by `race_key` and FEC candidate ID where one exists. The TIP `races.result_status` values (`none`, `pending`, `reported`, `projected`, `certified`) are a single race-level field and do not describe per-candidate tallies, calls, recounts or contests. They are not reused as the model.
- **Leader, call and certification are three separate things.** A candidate can lead a count, be called by a named organization at a named time, and later be certified, each with its own source and timestamp.
- **Vote share and reporting completeness are different.** Percent of votes is computed only from a validated race total. A "percent reporting" is stored only if the authority publishes it, with the authority's own definition (precincts, ballots, counties or estimated votes). It is never derived.
- Nothing fetched is published until a reviewer approves it; an update to numbers does not rewrite human-authored text.
- A source that cannot be read is recorded in `docs/production/DATA_ACCESS_LIMITATIONS.md` (R15); bot checks and captchas are never circumvented.

## 2. Proposed file layout
```
data/elections/<ST>/results/
  sources.json                     # approved sources for this state (id, authority, URL, access method, owner_approved, notes)
  captures/<YYYYMMDDTHHMMSSZ>_<source_id>.<ext>   # raw bytes as fetched
  captures/<...>.meta.json         # provenance record (sha256, status, headers kept, retrieved_at)
  normalized/<capture-id>.json     # one normalized snapshot per capture (schema: contest_result, candidate_result)
  approved.json                    # pointer to the snapshot currently approved for display, with reviewer and time
  signals/<signal-id>.json         # Election Signals (schema: signal)
build output:
  /data/results/<ST>.json          # public, versioned payload (copy of approved snapshot; no raw captures)
  /data/results/<ST>.<version>.json  # immutable previous versions, for the update log
```
Page generators read `approved.json`. Missing or stale data renders the "data unavailable" or "source stale" state, never a number from an older snapshot presented as current.

## 3. Schemas (see `schemas/`)
| File | Purpose | Key rules |
|---|---|---|
| `race.schema.json` | Identity of a contest | `race_key` (TIP key such as `2026-GOV-PA`) or an explicit `local_key` with a mapping note; cycle, office, jurisdiction, election date, ballot type |
| `contest_result.schema.json` | A race's results at one capture | `result_stage` enum `not_available`, `counting`, `called`, `certified`, `recount`, `contested` (UI-neutral); optional `reporting` object with `basis` and `definition`; no required `percent_reporting`; `total_votes` optional; `capture_version`, `provider_observed_at`, `retrieved_at` |
| `candidate_result.schema.json` | One candidate's counted votes within a contest | `votes` integer; `vote_percent` allowed only with `percent_method` of `source` or `computed_from_total`; `is_leader` separate from `call`; ballot category `printed` or `write_in` |
| `provenance.schema.json` | Where a number came from | `sha256`, `raw_path`, `source_id`, `source_url`, `source_agency`, `retrieved_at`, `qa_state` (`captured`, `normalized`, `validated`, `approved`, `rejected`), `reviewer`, `editor_note` |
| `signal.schema.json` | An Election Signal | `statement`, `geography`, `comparison_period`, `evidence` (list of source and file references), `as_of`, `caveats`, `author`, `reviewer`, `approval_status`; a signal with no evidence list is invalid |

**Mapping caution:** TIP `result_status` to `result_stage` is many-to-one and lossy (`pending` and `reported` are both `counting` or `not_available` depending on the source; `projected` is a call by an organization and needs the call object; `certified` maps directly). Do not write results back to TIP until the owner decides whether TIP's enum is extended, replaced or left as a coarse summary.

## 4. Proposed capture and validation jobs (not built)
Patterned on `tools/dark_horse/daily.py` (dated output, last good data kept, staleness marked), `tools/elections/fetch_*.py` (hashed captures) and `tools/qa/smoke.py`.

| Job | Proposed path | What it does |
|---|---|---|
| `capture` | `tools/results/capture.py <ST> <source_id>` | One request per run to an approved source with a plain client identifier; stores raw bytes and `.meta.json`; on 403, 429, captcha or a changed format it stops, records the failure and never retries by other means |
| `normalize` | `tools/results/normalize_<source_id>.py` | Raw to `normalized/` JSON; one parser per source format; unknown fields kept in a `raw_extra` area, not dropped |
| `validate` | `tools/results/validate.py` | Schema check; candidate keys map to `data/elections/<ST>/candidates.json` or are flagged; vote sums equal the stated total where a total exists; computed percentages recomputed and compared; timestamps do not go backward; counts do not decrease without a flagged correction; write-ins handled per the source; race count equals the roster's contests |
| `diff` | `tools/results/diff.py` | Human-readable difference between the approved snapshot and a new one for the reviewer |
| `approve` | `tools/results/approve.py` | Writes `approved.json` only with a reviewer who is not the person who ran capture (R5 pattern) and an authorization note (R14) |
| `render` | existing generators | Read `approved.json`; show status, source, retrieved time and "as of" on every number |
| `status` | `tools/results/status.py` | Reports per state: last capture, last approval, staleness against a stated limit, blocked sources |

Cadence, polling interval and whether jobs run on the hosting account, on a developer machine or in a scheduler are open questions (hosting has process limits; the monitor's cron status on the server is unconfirmed).

## 5. Source validation checklist
Complete one per source and per state before a source is used. All answers are recorded in `sources.json` and the source registry; `owner_approved` stays false until the owner approves.

1. **Authority.** Who publishes it (state, county, commercial), and is it the official election authority?
2. **Official status labeling.** Does the source say unofficial, official or certified, and where?
3. **Access.** Is automated access permitted (terms, robots, rate limits)? Did a plain request succeed? Any 403, captcha or login? If blocked, record in `DATA_ACCESS_LIMITATIONS.md` and stop.
4. **Format.** File type, structure, stability of URLs and field names; whether a change in format would be detected.
5. **Coverage.** Which of this state's contests (governor, Senate, each House district) are present; write-ins; special elections.
6. **Field definitions.** What "votes", "percent", "reporting" and "counted" mean in the source's own words; whether precinct counts, ballots or estimates are used.
7. **Timestamps.** Whether the source states when data was last updated and whether that time is available per contest.
8. **Candidate identity.** Names and ballot order mapped to the TIP candidate and FEC ID; handling of withdrawn and write-in candidates.
9. **Calls and certification.** Does the source call races? Does it state certification date and body? Are recount and contest statuses shown?
10. **Revisions.** How corrections and late-arriving ballots appear; whether prior versions are retrievable.
11. **Sample review.** Two captures compared by hand to the source page; arithmetic checks pass.
12. **Fallback.** What the page shows if the source stops updating; who is told.
13. **Second-person check** of the mapping and of the first approved snapshot (R5), and the owner's approval of the source.
14. **Licence and attribution** for any commercial or third-party feed, including whether redistribution as static JSON is allowed.

## 6. What remains unknown
Which official sources exist in each of the seven states and what they provide; whether any is machine-readable; whether the hosting account permits scheduled capture jobs; whether a commercial feed is wanted; where `percent reporting` is published at all. These are answered only by testing each source against the checklist above, which has not been done.
