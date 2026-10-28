# Illinois 2026 State of the Race: readiness report and site inventory

2026-10-28 · discovery pass only (nothing built or published). Machine-readable companions: `data/elections/IL/il_candidate_tip_mapping.csv` (54 rows), `il_tip_mapping_summary.json`, `il_assets.csv`, `roster.json`, `candidates.json`.

## Verdict
**Ready to write the three recommended features; not ready to build the State of the Race pages.** Content and TIP mapping are in place; four things block a build: (1) the Illinois State Board of Elections list could not be read (HTTP 403), so ballot status is transcribed from a secondary tracker and cross-checked, with the official check PENDING; (2) district geometry is not built; (3) TIP has no governor race entries and a few record problems; (4) the Florida templates are hard-wired to Florida and need the configuration step in `ILLINOIS_PAGE_STRUCTURE.md`.

## Contests and candidates (what is on the November 3 ballot)
| Office | Contests | Candidates | Notes |
|---|---|---|---|
| Governor | 1 | Pritzker (D, incumbent), Bailey (R), Corbett (independent) + 8 write-ins | Griselda Romero (Green) was removed from the ballot on Jul 14 and is a write-in |
| U.S. Senate | 1 | Stratton (D), Tracy (R), Harrington (American Center) + write-in Craine | open seat (Durbin retiring); a regular election |
| U.S. House | 17 | 39 incl. 3 write-ins | 12 incumbents renominated; 5 open seats: IL-2 Miller (D) v. Noack (R); IL-4 García (D) v. Castillo (R), Getty (I), Hershey (Working Class); IL-7 Ford (D) v. Koppie (R); IL-8 Bean (D) v. Davis (R); IL-9 Biss (D) v. Elleson (R) |
Total 54 roster rows (`roster.json`). Sources agreeing per row are in the mapping CSV: The Green Papers (transcribed 2026-10-28), OpenFEC candidate list (federal IDs; `fec_cross_check`), TIP race entries. Official ISBE verification: **PENDING** (column `isbe_verified`).

## TIP reconciliation (verified live 2026-10-28)
- **43 of 54 candidates have a live TIP profile** (HTTP 200); **all 19 TIP race pages return 200** (`2026-GOV-IL`, `2026-S-IL`, `2026-H-IL-01` to `17`).
- **11 candidates have no TIP profile:** Corbett, the 8 governor write-ins, Craine (Senate write-in) and Keating-Sofiakis (IL-10 Green write-in). LLF shows "No TIP record yet" for them.
- **Governor race on TIP has no race entries** although TIP holds profiles for Pritzker (GOV-IL-PRITZKER) and Bailey (GOV-IL-BAILEY): the TIP governor page lists nobody. Needs a TIP data fix.
- **5 entries rest on "National source only":** Harrington (Senate), Brown (IL-1 write-in), Getty and Hershey (IL-4), Kitover (IL-16 write-in).
- **Data bug:** the IL-04 race entry stores "Patty García" with a corrupted character (`Patty Garc?a`). Matching worked through a `tip_name` override; the name must be fixed in TIP before display.
- **Grades (TIP issue grades):** 12 candidates have at least one graded issue, all House incumbents (Jackson 5, Ramirez 6, Quigley 6, Casten 4, Schneider 4, Foster 5, Bost 4, Budzinski 6, Underwood 5, Miller (IL-15) 4, LaHood 4, Sorensen 5). The governor candidates, the Senate nominees and every open-seat nominee are **not graded**, which is not a zero. R1 and R2 can be met for all 43 profiles; 11 need a "No TIP record yet" state.

## Existing Illinois content on LLF and TIP (duplication check)
See `ILLINOIS_COVERAGE_AND_DUPLICATION_CHECK.md`. Short version: nothing published on LLF (the Illinois landing returns 404; the live sitemap has Florida pages only); no Illinois content in the repository apart from four watchlist rows; TIP has race and profile pages but no articles. No duplication risk.

## Site and data inventory
| Item | Status |
|---|---|
| LLF Illinois pages (landing, governor, Senate, House, 17 districts) | none exist; structure planned in `ILLINOIS_PAGE_STRUCTURE.md` |
| Roster, TIP join, mapping | built (`data/elections/IL/`) |
| TIP export (races, entries, candidates, ratings, definitions) | copied to `data/elections/IL/tip_export/` (exported 2026-10-28; 20 races, 43 entries, 238 candidate rows, 104 graded cells) |
| District geometry | not built; source verified: Census `cb_2024_us_cd119_500k.zip` (public domain, HTTP 200) |
| Markets (Kalshi) | governor, Senate and IL-1 to IL-16 contracts exist (captured in `data/elections/IL/captures/kalshi_il_2026-10-28.json`); IL-17 returned 404; all lopsided and not part of any recommended story |
| Polls | no Senate general-election poll found; governor: Victory Research (Nov 20 to 24, 2025, Pritzker 54.3, Bailey 34, sponsor not stated) and a PPP poll for Chicago News Weekly (Sept 30 to Oct 1, 54 to 34 with Corbett at 6, sponsorship questioned), neither opened in an original release |
| FEC data | not pulled (lean standard); UDP's cached 2026 FEC figures used for one claim |
| Portraits | 27 licensed images found (`il_assets.csv`), including Stratton, Ford, Bean, Biss, Pritzker, Bailey, Krishnamoorthi, Kelly, Conyears-Ervin, Fine, Abughazaleh, Chuy García, Davis; 17 of the people searched have none (Patty García, Tracy, Koppie, Sigcho-Lopez and other major-party nominees); minor-party and write-in candidates were not searched. All of these use a monogram and are marked NOT FOR PUBLICATION |
| Hero image | `static/img/elections/il-capitol.jpg`, Illinois State Capitol, public domain |
| Workflow | `story:il-senate-money`, `story:il-07-ford`, `story:il-04-handoff` at SOURCE_CHECKED in `data/elections/workflow_ledger.jsonl` |

## Blockers and open items
1. Illinois State Board of Elections list (403): a person opens it and confirms the 54 rows; also confirm final primary results for the Senate, IL-2, IL-4, IL-7, IL-8 and IL-9.
2. TIP fixes: governor race entries, "Patty García" name, 5 "National source only" entries, 11 missing profiles (decision for the owner: create profiles for write-ins or show "No TIP record yet").
3. Geometry and Illinois configuration (see the structure doc) before any page is built.
4. WTTW and several other outlets return 403 to automated fetches; their content was used only through search summaries and is marked so.
5. The governing specification "LLF Canonical Local Workflow & Skills Lock v2.0" and the directory `docs/production/` named in the request are **not in the repository or the Downloads folder**; see the skills report.
