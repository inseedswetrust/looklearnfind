# Edition 001 source verification (2026-11-05)

Run by Claude as a reviewer who did not draft the text. Claim-level table: `CLAIMS.csv` (15 claims). The same table is on the local preview page under "Source review (draft)". **Result: flags remain. The edition is not approved and nothing was removed or changed.**

## What could and could not be read
| Source in the draft | Read? |
|---|---|
| Reuters (5 articles), AP Voter Poll | **No.** The fetch tool refuses reuters.com and apnews.com. Their claims are marked unverified, not wrong. |
| ABC News live blog, Nov. 4 (no. 3) | Yes |
| NCSL results overview (no. 7) | Yes |
| FEC and Brennan Center (nos. 9 and 10) | Not opened. Spending was checked through OpenSecrets and AdImpact projections reported by other outlets |
| Washington Examiner live blog, updated Nov. 5, 9:12 AM | Yes (not in the draft; used as a second source for results) |

## Result by claim
- **Supported (7):** Democrats projected to control the House and the Senate (ABC; Examiner: 240 House and 54 Senate seats, Alaska and Mississippi uncalled, 48 House races open); Trump remains in office; Jeffries announced a speaker bid by letter (ABC, Nov. 4); House Democratic leadership elections on Nov. 18 (ABC); spending estimates near $12 billion (OpenSecrets projected about $11.9 billion, AdImpact $11.6 billion for advertising only); NCSL's new Democratic trifectas in Michigan, Minnesota, Nevada, Pennsylvania and Wisconsin.
- **Partly supported (2):** the cost-of-living and presidency concerns (pre-election AP-NORC only); the five Senate victories (Kansas, Texas, Iowa and South Carolina are reported by one live blog; **Ohio is not supported for the Senate**).
- **Unverified (4):** Schumer expected as majority leader (Reuters); AP Voter Poll on corruption and checks on the president; Democratic leaders' stated priorities (Reuters, Nov. 5); "Democratic gains in Republican-held governorships, including Texas" (Reuters; no Texas governor result found).
- **Unsupported (2):** "larger than many election observers expected" (no comparison source); "areas that supported Trump by large margins two years earlier" (no margin data).

## Required corrections before approval
1. Ohio Senate: confirm the result or remove Ohio from the list (dek-level claim in teaser 02 and section 02).
2. Texas governorship: do not state a flip without a confirmed result.
3. "Secured" in the dek and the At a glance list: the sources say projected; seats are still being counted. The draft's own caution is right and should lead.
4. Name the spending source and its scope; the two $11.6 to $11.9 billion figures measure different things.
5. Open the Reuters and AP articles (or replace them) so claims 5, 8, 11, 12 and 14 can be checked.
6. Source or remove the two unsupported characterizations.
7. Assign an editor who is not the author; then set `fact_check.state` to `passed` with a reviewer name and `status` to `approved`.

## Resolution (2026-11-05): published with fixes on the owner's decision
The owner approved publishing with the flagged lines corrected. This is an **owner approval after a partial review, not an independent fact-check pass**: `fact_check.state` is `owner_approved`.
- Twelve corrections (K1 to K12, `CORRECTIONS.json`) removed or reworded the unsupported lines: Ohio dropped from the Senate list, the Texas governorship claim and the "governorships changed hands" wording removed, "secured" changed to "projected", the unsourced "larger than expected" and Trump-margin claims removed, and the spending estimate now names OpenSecrets and AdImpact as projections.
- The claims that rest on the unreadable Reuters and AP articles stay in the text and are disclosed in a published editor's note under the headline.
- The corrections are listed in the update log on the page. The source Markdown is kept unchanged; the completeness check applies the corrections before comparing (`CONTENT_COMPLETENESS_REPORT.md`).
- Still open: an independent check of the Reuters and AP claims (C08, C11, C12 and the Reuters state-race report).
