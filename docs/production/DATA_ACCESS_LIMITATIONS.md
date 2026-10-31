# Data access limitations (specific, dated, and what each one means)

A limitation is recorded here instead of being worked around or treated as a complete result. Add a row when a source cannot be read; remove it only when a person has read the source.

| Date | Source | What happened | What it means | What clears it |
|---|---|---|---|---|
| 2026-10-28 | **Illinois State Board of Elections** certified candidate list, `https://www.elections.il.gov/ElectionOperations/CandidateList.aspx` and the Board's other candidate pages found by search | HTTP 403 to automated requests during the Illinois discovery pass | The Illinois roster (54 rows) is **not** an official, complete list. It is transcribed from The Green Papers (secondary) and cross-checked against OpenFEC (federal IDs) and TIP race entries; every row's `isbe_verified` is `PENDING`. State-office and write-in rows rest on the secondary source alone. Primary results are unofficial. Nothing in the roster may be called "certified" or "complete" | a person opens the Board's list in a browser, ticks `isbe_verified` row by row in `data/elections/IL/il_candidate_tip_mapping.csv`, and confirms final results for the Senate, IL-2, IL-4, IL-7, IL-8 and IL-9 |
| 2026-10-28 | WTTW (`news.wttw.com`) | HTTP 403 to automated fetches | Facts from WTTW (Ford and Bean results, Davis endorsement) are used only through search summaries and are marked so in the briefs | a person opens the articles |
| 2026-10-28 | Wikimedia API | HTTP 503 under load | portrait fetch retries with backoff; rerun if any `error` remains in `portraits.json` | rerun `fetch_portraits.py` |
| 2026-10-23 | Florida campaign finance database (state office money) | blocked to automated access | governor money is quoted from press reports with dates | a person exports the data |
| 2026-10-23 | VoteHub terms page | HTTP 403 | licensing of VoteHub poll listings is unverified; originals must be opened before a poll figure is published | a person reads the terms |
| 2026-10-28 | Illinois: the Sigcho-Lopez lawsuit docket | not checked | lawsuit status is unknown in the IL-04 brief | a person checks the court docket |
| 2026-10-30 | New York State Board of Elections (`elections.ny.gov`) | HTTP 403 to automated fetches | NY roster is parsed from The Green Papers; certification not read | a person opens the State Board November certification |
