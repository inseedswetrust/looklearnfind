# Illinois: State of the Race page structure and the Florida template adaptations

2026-10-28 · design and plan only: nothing is built or published in this pass, and no infrastructure is redesigned. The structure below reuses the approved Florida State of the Race pages (hub, governor, Senate, House directory, district pages, methods) and the article schema family (schema 07: A state guide, B race detail, C reported feature).

## Routes (same pattern as Florida)
| Route | Page | Florida equivalent | Notes for Illinois |
|---|---|---|---|
| `/elections/2026/illinois/` | State of the Race landing (the State Board) | `/elections/2026/florida/` | 1 governor, 1 Senate, 17 House districts = 19 contests; board of 19 tiles |
| `/elections/2026/illinois/governor/` | Governor guide | `.../florida/governor/` | Pritzker (D, incumbent), Bailey (R), Corbett (I); 8 write-ins; TIP has no governor race entries (gap) |
| `/elections/2026/illinois/senate/` | Senate guide | `.../florida/senate/` | open seat (Durbin retiring); Stratton, Tracy, Harrington (American Center), write-in Craine; a regular Class 2 election, not a special |
| `/elections/2026/illinois/house/` | House directory with district atlas | `.../florida/house/` | 17 districts; 5 open seats (IL-2, 4, 7, 8, 9); one map vintage (the 2021 plan in use since 2022) |
| `/elections/2026/illinois/house/<n>/` | One page per district (17) | `.../florida/house/<n>/` | every candidate appears here, including independents, minor parties and write-ins |
| `/about/election-methods/` | Methods (shared) | same | no change |
| `/learn/<slug>/` | Reported features (stories 1 to 3 once written) | Florida reports | linked from the guide pages by the "Latest reporting" band |

## Modules per page (reuse as is)
**Landing:** hero (Illinois State Capitol photo, licensed credit), as-of stamp, board of 19 tiles with names and party letters, highlights band naming the reported features, the Governor, Senate and House sections, TIP explore cards, sources and corrections. **Governor guide:** candidate cards (TIP profile where one exists), Kalshi governor card (party contract wording), the poll card only if an original release is opened (the two polls found have unstated or disputed sponsorship), campaign-issue summaries only from campaign pages. **Senate guide:** candidate cards with TIP grades or "not graded", Kalshi card, no poll card until a general-election poll is found. **House directory:** atlas with 17 districts, table of all 39 November candidates, open-seat tags. **District page:** all candidates, TIP grades, Kalshi card where a contract exists (IL-17 has none), link to any reported feature. **All pages:** R1 TIP links, R2 race links, "not graded is not zero", every number dated.

## Directory rule
Every November candidate appears in the right race directory (54 roster rows: 11 governor incl. 8 write-ins, 4 Senate incl. 1 write-in, 39 House incl. 3 write-ins). Features cover only the stories that meet the news standard; most candidates get a card and a TIP link, nothing more.

## Florida adaptations needed (nothing built yet)
`elections.py` has about 86 Florida-specific references. The adaptation is configuration, not redesign:
1. **State config:** one record per state (code `IL`, name, slug, contest counts, district count 17, data directory, race-key patterns `2026-H-IL-NN`, Kalshi event tickers `GOVPARTYIL-26`, `SENATEIL-26`, `KXHOUSERACE-ILNN-26`) replacing the constants `ST_URL = "/elections/2026/florida/"`, the `D / "FL/..."` loads and the `FL` dictionary name.
2. **Copy that is hard-coded for Florida** (governor page text, Senate page poll block, hub counts "30 contests", `gov_aside`, `stats_gov`, the alias table and `RACE_PATTERNS`) moves to `data/elections/IL/story_data.json` and templates with state variables; values keep their source and date as in Florida.
3. **Data files to create** (formats exist): `roster.json` (done, provenance pending the State Board), `candidates.json` (done by `join_tip.py` with `LLF_STATE=IL`), `districts.json` (needs geometry: use the Census cartographic boundary file `cb_2024_us_cd119_500k.zip`, public domain, HEAD check 200, filtered to Illinois; the Florida builder `build_fl_geometry.py` is the pattern), `markets.json` (Kalshi has a governor contract, a Senate contract and House contracts for IL-1 to IL-16; IL-17 returned 404 in the 2026-10-28 check; the Florida fetcher needs the state parameterized), `portraits.json` (running), `finance_fec.json` (optional, lean standard).
4. **`join_tip.py`** now takes `LLF_STATE` and optional roster fields (`tip_name`, `source_url`, `party`, `write_in`, `note`); the Florida result is unchanged (checked).
5. **TIP side fixes needed before publishing** (listed in the readiness report): add the governor race entries, fix the corrupted "Patty Garc?a" name, decide the 7 "National source only" entries, and update the stale race phases.
6. **Tests:** add a fixture that every Illinois candidate in `roster.json` has a TIP URL or a stated gap, and a build check that no Florida string appears on an Illinois page.
Order of work after approval: configuration and data loading, then geometry and markets, then the three features; each step ends with `build.py --strict` at 0 violations.
