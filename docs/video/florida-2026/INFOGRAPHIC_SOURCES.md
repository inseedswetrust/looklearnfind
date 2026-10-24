# Infographic evidence: every figure, name and image on the Florida frames

Checked 2026-10-24. Frames: `assets/video/florida-2026/infographics/IG-*/`. Status: VERIFIED (read in a primary source), ATTRIBUTED (said "according to"), GAP (not shown, or shown with a visible caveat). No figure was typed from memory or generated.

## IG-02 Primary result
| Element | Value | Source | Status |
|---|---|---|---|
| Nixon and Vindman votes | 705,835 (56.06%) and 553,138 (43.94%), total 1,258,973 | Florida Division of Elections, https://floridaelectionwatch.gov/FederalOffices/USSenator, read 2026-10-24, sha256 in `infographics/data/sources.json` | VERIFIED. Page is headed "Official Election Results"; certification not read |
| "~12-point margin" | 56.06 minus 43.94 = 12.1 points; 152,697 votes | computed from the row above | VERIFIED |
| Portraits | Nixon: Florida House official, public domain. Vindman: Alexander Vindman at the Zelenskyy inauguration, May 20 2019, Mykola Lazarenko / Presidential Administration of Ukraine, CC BY 4.0 | Wikimedia Commons | Genuine photos. Vindman's is 267 x 356 px and 5 years old; replace when a current licensed photo exists |
| "$16M vs under $1M" (packet hook) | NOT SHOWN | Washington Post analysis via DNYUZ repost (Aug 19): Nixon raised just under $1 million, Vindman $16 million. OpenFEC on Oct 24: Nixon $11.3M through Oct 14, Vindman $20.5M through Sep 30 | GAP by choice: true only as of the primary, stale now. If used, say "through the primary". Original Post URL not read |

## IG-04 County map
| Element | Value | Source | Status |
|---|---|---|---|
| County shares, 67 counties | Nixon votes ÷ (Nixon + Vindman) per county; rows sum to the statewide totals (tested) | https://floridaelectionwatch.gov/ContestResultsByCounty/120002 | VERIFIED |
| Boundaries | U.S. Census cb_2024_us_county_500k, projected to Florida Albers (EPSG:3086) | Census Bureau | VERIFIED geodata, generalized |
| Spotlights | Duval 80.2% (55,079 to 13,558); Gadsden 80.0% (5,475 to 1,367); Sumter 33.3% (3,252 to 6,527) | county file | VERIFIED. Chosen as the top and bottom of the county range plus Nixon's home county |
| Sidebar | "Strong support in lower-income, less-college-educated and heavily Black counties" | Washington Post analysis, read via DNYUZ repost | ATTRIBUTED; with the note that county totals do not show individual motives |

## IG-06 Poll and debate
| Element | Value | Source | Status |
|---|---|---|---|
| Moody 49, Nixon 45, 5 undecided, ±2.81, Oct 12–19 | UNF poll as reported | WLRN and Action News Jax, Oct 21 (fact F-13) | ATTRIBUTED through news reports; the UNF release itself was not opened. Sample size not shown (not in the fact sheet for this poll) |
| Earlier wider lead | "8 points, July" | WLRN only (F-13) | ATTRIBUTED, single report. Replaces the packet's "other polling has shown wider Moody leads", which has no second source |
| Debate card | Moody declined to debate Nixon; she told the News Service of Florida she will keep engaging with voters | WUSF / News Service of Florida, Oct 1 (F-14) | ATTRIBUTED. No "invitation document" is shown because none was obtained |

## IG-08 Governor contrast
| Element | Value | Source | Status |
|---|---|---|---|
| Donalds 49, Jolly 47, 4 undecided, 1,471 likely voters, ±2.81, Oct 12–19 | UNF poll | Action News Jax, Oct 21 (F-08) | ATTRIBUTED; marked REFRESH in the fact sheet |
| Summit | Sept 23, 2026, WLRN Sunshine Economy Summit, candidates in separate sessions | CBS Miami report transcript (captions) | ATTRIBUTED |
| Images | official portraits, not summit freeze frames | Commons / Congress | Freeze frames need the CBS or WLRN license |
| Topic chips | insurance, property taxes, affordability | CBS Miami and WLRN titles and captions | ATTRIBUTED |

## IG-09/10 House map to FL-14
| Element | Value | Source | Status |
|---|---|---|---|
| District outlines | plan EOGPCRP2026 (HB 1-D) | Florida Legislature EDR shapefile, sha256 253cfc70… (see `data/elections/FL/districts.json`) | VERIFIED |
| "21 of 28 districts reworked" | as reported | WLRN May 5, WUSF June 15 (F-18) | ATTRIBUTED |
| "District boundaries changed" and Castor running in the new FL-14 | as reported | WLRN May 5 (F-20, F-21) | ATTRIBUTED |
| Portraits | Castor: U.S. Government, public domain. Beltran: Florida House, public domain | Commons | Beltran's file is 150 x 200 px; shown at 200 x 267 |

## IG-11 Six issues
Names exactly as stored in `data/elections/FL/tip_export/issue_definitions.json` (display_name; sub-line is the stored short label for the sixth). Record panels: unedited screenshots of theissuesparty.org/candidates/S6FL00640 (Moody: War-Crime Accountability F-, Universal Healthcare F-, others not graded) and /S6FL00830 (Nixon: none graded), captured 2026-10-24. VERIFIED (live site). Both shown at equal size; the packet asked for one card.

## IG-12/13 Ecosystem and CTA
Screenshots of looklearnfind.com/elections/2026/florida/ (hero) and the TIP record panel, captured 2026-10-24. The LLF page is live (HTTP 200, title "Florida 2026: State of the Race"); publishing it was not done in this pass. LLF logo from `static/img/logo-ink.png`.

## Gaps
- Vote shares were not in the video spec (F-15 said "no vote share until the Division of Elections count is read"). The count is now read; the spec and fact sheet should gain a fact row before IG-02's numbers are narrated.
- UNF release not opened for either poll. Kalshi, money and committee figures are not used by these frames.
- Current licensed Vindman and Beltran photos.
