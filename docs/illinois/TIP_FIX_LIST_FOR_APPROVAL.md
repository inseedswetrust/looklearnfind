# Illinois: TIP-side fixes, for owner approval

Prepared 2026-10-28. **Status 2026-10-28:** item A was approved ("Create all 11") and applied to production: 11 candidate rows, 9 governor race entries (status review) and 2 existing entries linked; SQL kept at the-issues-party/docs/state-packets/IL/11_missing_profiles.sql. Items B and C are not applied and still need approval. The rest of this file is the original proposal.

Sources: `data/elections/IL/il_candidate_tip_mapping.csv` (54 rows), `il_tip_mapping_summary.json`, `tip_export/` (captured with the discovery pass) and the live TIP profile and race URLs checked then (all returned 200).

## A. Eleven candidates with no TIP profile (decision, then data)

LLF currently shows "No TIP record yet" for each and lists them as non-blocking directory gaps in the build. For every one, the race page on TIP already exists (HTTP 200). None has an FEC ID in our data, except where noted; none is graded, and not graded is not zero.

| # | Name | Race | Ballot status per roster | Note |
|---|---|---|---|---|
| 1 | Collin Corbett | Governor | Independent, on the ballot | Roster notes a Republican affiliation per Green Papers. Polled at 6 percent in one disputed poll |
| 2 | Taegun Eimer | Governor | Libertarian, write-in | |
| 3 | Richard Mayers | Governor | Write-in | |
| 4 | Mistry Metroz | Governor | Write-in | |
| 5 | Griselda Romero | Governor | Green, write-in | Removed from the printed ballot July 14, 2026 |
| 6 | Elizabeth Sebesta | Governor | Write-in | |
| 7 | Patricia L. Tillman | Governor | Write-in | |
| 8 | Rafael Varela | Governor | Write-in | |
| 9 | Mike Vick | Governor | American Solidarity, write-in | |
| 10 | Naomi Craine | U.S. Senate | Socialist Workers Party, write-in | On TIP's reconciliation list as "entry without FEC ID, review" |
| 11 | Alexandria Keating-Sofiakis | IL-10 | Green, write-in | Same reconciliation entry |

**Decision for you (pick one for the set, or per candidate):**
1. **Create TIP profiles** for all 11 (profile plus race entry, status "review" until the State Board list is read).
2. **Create profiles only for the printed-ballot candidate** (Corbett) and leave write-ins as "No TIP record yet" on LLF.
3. **Create none.** LLF keeps the "No TIP record yet" label and the gap line. This is the cheapest option and is accurate, but it leaves rule R1 unmet for Illinois under the strict reading Florida uses.

Whichever you choose for the write-ins, the State Board list (HTTP 403) is still the right basis for confirming who is a certified write-in. Creating profiles from Green Papers alone repeats the same limitation.

## B. Governor race has no entries

TIP's `2026-GOV-IL` race page exists but lists nobody. Profiles exist for both major candidates, so the fix is race entries only:

| Candidate | TIP profile | Needed |
|---|---|---|
| JB Pritzker (D, incumbent) | `GOV-IL-PRITZKER` | Add race entry to `2026-GOV-IL` |
| Darren Bailey (R) | `GOV-IL-BAILEY` | Add race entry to `2026-GOV-IL` |

Plus entries for whichever of items 1 to 9 above you approve. Correction to how this was worded in the request: this is missing race entries, not a misspelled race name. The race title ("IL Governor") and key are correct.

LLF's governor page does not depend on this fix; it links to the TIP profiles directly. But the TIP race page that LLF links to will show an empty field until it is done.

## C. "Patty Garcia" name

- FEC ID `H6IL04153`, TIP profile `https://theissuesparty.org/candidates/H6IL04153`.
- The name in the live record has a corrupted character where the "í" belongs (the discovery capture read it as `Patty Garc?a`). The captured export spells it `Patty Garcia` with no accent, so the corruption may be in the display layer rather than the stored value. Needs a look at the live record before choosing the fix.
- **Proposed value:** `Patty García`, matching the usage in the news sources LLF cites. FEC spells it `GARCIA, PATTY`.
- The same fix probably applies to Rep. Jesús García (`H8IL04134`), whose profile is not in the LLF pages as a candidate but is the current member. Check the same field.
- LLF side: the roster already keeps `tip_name` separate from the display name, so nothing changes on LLF when TIP is fixed.

## D. Related items found while mapping (not in your request; listed so they are not lost)

1. **Five entries rest on "National source only"** (no state-level verification): Whitfield Harrington Jr. (Senate, American Center), Je'Rico J. Brown (IL-01 write-in, status review), Chris Getty and Ed Hershey (IL-04) and John Kitover (IL-16 write-in, status review). They are on the LLF pages. Getty and Hershey are named in the IL-04 draft, which says nothing beyond who is on the ballot. Re-verification waits on the State Board list.
2. **Portraits:** licensed images are missing for several candidates; the drafts use "licensed image pending" alt text. Not a TIP fix; tracked in `data/elections/IL/il_assets.csv`.

## What I need from you

- A yes or no on B (race entries for Pritzker and Bailey).
- A choice of 1, 2 or 3 on A.
- A yes on C, after I confirm the live value (read-only check of the profile page).

Until then nothing changes on TIP, and the Illinois pages stay unpublished.
