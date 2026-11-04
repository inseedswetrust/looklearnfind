# Post-election design follow-ups

Response to the eight follow-up requests in `LLF_POST_ELECTION_ARCHITECTURE_V1.md` (section 10). **Design and analysis only.** No application code, route, schema in any database, content file or live system was changed. Everything here is new files in this folder. Nothing was committed or deployed.

Evidence base: the discovery audit in `../post-election-discovery/` (LLF `159302a`, TIP `e6e6f4d`), plus new reads of `elections.py`, `build.py`, `data/threads.json` and the built site on 2026-11-04.

| Request | File |
|---|---|
| 1. Validate the sitemap, name the generator functions, flag Florida special cases | `01_SITEMAP_VALIDATION_AND_GENERATOR_PLAN.md` |
| 2. Current-to-proposed navigation map, the 21 political articles and 22 threads | `02_NAVIGATION_MAP.md` |
| 3. Content-mapping CSV | `CONTENT_MAPPING.csv` (31 rows: 21 political articles, 3 non-political samples, 7 state hubs) |
| 4. File-level JSON schemas, capture and validation jobs, source checklist | `03_RESULTS_SCHEMAS_JOBS_AND_SOURCE_CHECKLIST.md`, `schemas/*.schema.json` (5 files) |
| 5. Desktop and mobile mockups, no fabricated results | `mockups/site/` (open with the steps below) |
| 6. Staged deployment, regression testing and rollback preserving `robots.txt` | `04_STAGING_DEPLOYMENT_REGRESSION_AND_ROLLBACK.md` |
| 7. Safe staging preview given the manual zip deploy | `04_STAGING_DEPLOYMENT_REGRESSION_AND_ROLLBACK.md`, section 2 |
| 8. Contradictions with the Production Lock and authorization rules | `05_CONTRADICTIONS_AND_AUTHORIZATION_FLAGS.md` |

## Viewing the mockups
The pages use root-relative links like the real site, so they need a small web server rather than opening the files directly:
```
cd docs/post-election-design/mockups/site
python -m http.server 8092
```
Then open `http://localhost:8092/`. Pages: `national.html` (national election hub), `state-pa.html` (Pennsylvania living hub), `race.html` (district page showing six data states: unavailable, counting, called, certified, source stale, recount) and `article.html` (an existing article with the historical-context banner). A yellow ribbon on every page says the numbers are placeholders. Placeholder values appear as `0,000` and `00.0%` with a "SAMPLE" tag; the only real figures are contest counts, existing article titles and dates, and the Pennsylvania map and illustrations already on the site. Status chips use patterns and borders, not party colors.

**Mockup verification:** the four pages were loaded at 1280 and 390 pixels wide and checked for horizontal overflow (none). Screenshots were not saved, the desktop pages were viewed only in a small preview, and no accessibility or screen-reader review was done. They reuse the real site CSS plus one mockup-only file (`css/mock.css`).

## Limitations
- The JSON Schemas parse as JSON; they were not checked against the JSON Schema metaschema or exercised with sample data (no validator was installed).
- No results source was tested. Nothing assumes an official feed exists.
- Staging options (file 04) were not tested; whether the hosting plan permits another subdomain is Unknown.
- Content mapping (`CONTENT_MAPPING.csv`) is a proposed editorial grouping; banner types and review flags need an editor's confirmation.

## Correction to the earlier discovery files
While reading `elections.py` for this work I found that the discovery write-up was wrong on one point: **Florida does carry county data** (`counties=True`; each of its 28 districts lists its largest counties by area share, plus a population). The other six states do not, and no state has county vote totals. The statement was corrected in `../post-election-discovery/01_EXECUTIVE_READOUT.md`, `07_RESULTS_DATA_READINESS.md` and `09_ARCHITECTURE_RECOMMENDATIONS.md`, and `../LLF_POST_ELECTION_DISCOVERY.zip` was rebuilt. The copy ChatGPT holds is the older version.

## Update 2026-11-04: mockups on the new global shell
The mockups were regenerated on the shared shell and design tokens v1 (`docs/design/LLF_GLOBAL_SHELL.md`): the charcoal rail and mobile bar come from the built Pennsylvania hub, the palette uses the `--llf-*` tokens, the yellow ribbon is now a neutral hatched notice (yellow is reserved for mode and focus), the duplicate "Explore Pennsylvania" card became an in-page jump list and side cards stack under the content (no second permanent column). Screenshots: `docs/design/screenshots/mockups/`. Placeholder values only; no result is shown.
