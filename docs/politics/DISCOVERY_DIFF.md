# Politics 2.0 discovery diff (the eight unknowns only)

Date 2026-11-05. Source package: `LLF_POLITICS_2_0_BLUEPRINT_V0_1`, docs/03. Local, read-only inventory. Nothing was changed, committed, pushed or deployed. "Unknown" means not verified here.

## 1. Skills (12) and distribution tools
Manifest: `docs/production/SKILL_MANIFEST.json`. Versions: darkhorse-source-monitor 1.1.1, election-state-packet 1.0.2, llf-article-format 1.3.1, llf-delta-editorial 1.0.0, llf-election-render 1.1.1, llf-factcheck-finalize 2.2.0, llf-footage-scout 1.1.0, llf-publication-qa 1.4.0, llf-story-scout 1.0.0, llf-video-director 2.0.0, llf-video-storyboard 2.0.0, workflow-retrospective 1.0.0.
Tools present: `tools/video/` (clip manifest, scene pack, video pack and Florida infographic builders), `tools/social/render_cards.py`. **No Remotion or ElevenLabs code was found in this repository** (video audio and rendering happened outside it); Unknown whether those tools exist elsewhere on the owner's machine. Per-skill inputs and outputs are in each SKILL.md.

## 2. Shared navigation after the local UX work
Entry point `shared_nav.render()` via `build.shell()`. Drawer: the one `#llf-rail` element, left slide-in under 901px. Tokens `--llf-*` in `static/css/site.css`. Snapshots at 320, 390, 1024 and 1440 exist in `docs/design/screenshots/`. Live since 2026-11-04 (commit `464de4e`, not yet on GitHub). Strict build asserts it.

## 3. Assets
`ASSET_REUSE.csv` in this folder: 31 rows (hero credits plus state illustrations), with path, dimensions, source, license, credit and shipped status. All are in `static/img/elections/`. The seven state illustrations (`s1` to `s8`) have rights recorded as "Unknown: confirm"; the owner commissioned them, and `docs/election-build/ASSET_MANIFEST.csv` holds the fuller record.

## 4. TIP Action Party, ping and social posting
TIP routes exist in the TIP repo: `app/(public)/parties/*` (create, host, committee, `let-the-people-know`), candidate `ping` pages and `app/api/social`. LLF has no write path to TIP and none is assumed. Whether a public, approved snapshot can be read without account data: Unknown; no such endpoint was inspected. LLF links to TIP by stable candidate URL only.

## 5. Results-source inventory
No official results feed has been opened or validated for any state. Recorded failures in `docs/production/DATA_ACCESS_LIMITATIONS.md`: Illinois and New York boards (403), Minnesota Secretary of State (bot check), Pennsylvania Department of State (candidate list not found), VoteHub terms (403, licensing unverified), Florida finance (blocked). Rosters come from The Green Papers (secondary, unofficial). **Result: nothing may be shown as a result, margin or certification.**

## 6. Articles, threads and the four clusters
21 political articles at their `/learn/` URLs (registry `data/discovery.json`): outside-money 10, polls-and-markets 9, districts-and-ballots 2. Politics threads (5): midterms-2026, candidate-forums, local-ballot, following-a-promise, public-money. Of 22 threads in total. Proposed mapping to the four landing clusters (no article renamed or altered): Record = state hubs plus district pages; Daily Signal = new items only (none exist); Accountability = none yet; Follow the Money = the 10 outside-money articles plus the public-money thread. The 9 polls-and-markets pieces and 2 district pieces go to an "Earlier election coverage" shelf with the historical-context label. Row-level mapping is in `docs/post-election-design/CONTENT_MAPPING.csv`.

## 7. Publish procedure and JSON-only updates
Manual: `python build.py --strict --zip --keep-live-robots`, tar backup of the docroot, scp, `unzip -oq`, curl checks, rollback by restoring the tar (see the deploy memory). `robots.txt` is excluded from the zip. A JSON-only upload is technically possible (`static/api` and `/data` files are plain files) but no daily-JSON path exists, caches are not configured by `.htaccess` for it (Unknown), and no tested procedure exists. Recommendation: do not ship a JSON-only path until a stale-data test exists.

## 8. Hubs locally and in search
National `/elections/2026/` does not exist (built nowhere; returns 403 live). All seven state hubs, six governor pages, five Senate pages, seven House indexes and 121 district pages exist. **`search-index.json` does not index them**: it holds 24 stories, 386 candidates, 22 threads, 12 topics, 4 pages and 3 finds, and no `/elections/` URL. Extending it is a small change in `write_search_index()` (needs approval because it changes a live file).

## Conflicts with existing rules
- The blueprint's `STATUS=LOCKED` policy needs the owner's approval date; staged files are marked DRAFT.
- The Production Lock bars results claims; the landing page may therefore carry only labeled empty states until a source is validated.
- Pointers in `CLAUDE.md` and `docs/election-build/INDEX.md` are not wired until the policy is approved.
