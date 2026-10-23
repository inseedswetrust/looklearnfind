# Publishing rules for LLF election content

Owner rules, 2026-10-23. They are enforced by the build (`elections.py`, run by `build.py`), not left to memory.

## R1. Every featured candidate links to their TIP profile
- A candidate is *featured* when they appear on a candidate card, in a race directory or in the prose of a story.
- On a page, the first mention of each candidate in story prose is linked to their TIP profile. Cards carry a "View on TIP" button.
- If a candidate has no TIP profile (or the TIP URL does not return 200), the page shows "No TIP record yet", links to the LLF race page instead, and the build reports an **R1 violation**.
- **The grades you show must be visible on the TIP page you link.** TIP stores grades against a specific profile. Byron Donalds has two TIP profiles: a governor profile (all six issues "Not graded") and a congressional profile (his House record, with grades). LLF now links his grades to the congressional profile and also links the governor profile, and says so on the card.

## R2. Every mentioned race links to that race
- The first mention of a race in story prose links to the race: Florida races to the LLF race page (`/elections/2026/florida/...`), other states' races to the TIP race page (`https://theissuesparty.org/races/<race_key>`).
- Every LLF race page also carries a "Follow this race on TIP" link.
- Phrases the build recognizes today: `FL-nn`, "Florida's governor race", "governor race", "Florida's Senate race", "Michigan's Senate race". Add new phrases in `RACE_PATTERNS` in `elections.py`.

## How the build enforces them
- `python build.py` prints `PUBLISHING RULES: n violation(s)` with each candidate and page.
- `python build.py --strict` exits with an error when any violation remains. **Build release zips with `--strict` once the list below is cleared.**
- Existing exceptions require a written owner waiver; there are none today.

## Current violations (R1): 17 candidates have no working TIP profile
| Race | Candidates |
|---|---|
| Governor | David Jolly (Democratic nominee), Dean Ocean Abrams, Kathy Anderson, Charles Burkett, Jeffrey Peter "Dr. Jeff" Datto, Moliere "Moe" Dimanche, Scott Eckhard Jewett, Erik Morris, Frank J. Russo |
| U.S. Senate | Neil J. Gillespie |
| FL-06 | Alec Pavlik |
| FL-14 | Salomon Hernandez Sr. (TIP URL returns 404), Keith Varian |
| FL-15 | Angie Boone |
| FL-19 | Alexandra Zakhvatayev |
| FL-21 | David Fabrikant |
| FL-22 | Casey Askar (TIP URL returns 404) |

Cause: TIP's database has no candidate rows for these people (the governor roster is missing entirely, write-in candidates have no FEC IDs) or has rows whose pages return 404. The fix is on the TIP side: add or repair profiles for the full qualified roster. That is a production database write and needs your approval; the reviewable SQL for it is the item you approved earlier and is still to come.

Until then the pages are live with "No TIP record yet" on those cards, which is the honest state but does not meet R1. If you want R1 to block publication starting now, the Jolly and governor pages should come down until TIP has profiles. Say so and I will.

## Checks that run today
| Check | Where |
|---|---|
| Candidate TIP URL returns 200 | `tools/elections/join_tip.py` (at data time) |
| First mention linked, no profile reported | `autolink()` in `elections.py` (build time) |
| Race mention linked | `autolink()` and `RACE_PATTERNS` |
| Race page links to TIP race page | `race_link_span()` |
| All links resolve | `tools/qa/smoke.py` |
