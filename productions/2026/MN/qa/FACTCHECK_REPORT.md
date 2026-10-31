# Fact-check report: Minnesota Senate and MN-01 articles

Reviewer: claude-factcheck-subagent-3. Date: 2026-10-31. No article was edited.

- Senate article (minnesota-senate-quiet-campaign-poll-october-2026.html): CLEARS_WITH_FIXES
- MN-01 article (minnesota-first-district-outside-spending-october-2026.html): BLOCKED (headline and lede overstate the MPR comparison; one unsupported claim about FOX 9)

Sources opened: MPR 10/12, KTTC 10/16, MPR 10/09, FOX 9 10/22 (all four fetched). Local: markets.json (capture 2026-10-31T19:51:49Z) and candidates.json. WebFetch returns summaries, so quotes below are as returned by the fetch tool.

## Required fixes (do these first)

### MN-01 article
1. WRONG / misleading (headline, section 1 heading, paras 1-2, openfile `supported:`): "outpaced the Senate race". MPR 10/09 says the spending "now outpaces the statewide U.S. Senate race as a draw for group money" after spending "ramped up in recent weeks". MPR 10/12 reports more than $20 million of outside spending in the Senate primary and about $2 million since. A reader takes the headline as a totals comparison, which MPR's own figures contradict. Fix: retitle "Outside spending in Minnesota's 1st District tops $2.5 million, MPR reported". Para 1: "MPR News reported October 9 that outside group money was flowing into the district at a pace that now outpaces the statewide Senate race, citing FEC data for a total above $2.5 million." Add: "MPR's October 12 report put Senate outside spending at more than $20 million in the primary and about $2 million since, so the comparisons cover different periods." Rename the heading "A House contest drawing outside money" (drop "statewide-scale attention"). Revise para 2 and openfile to match.
2. WRONG / unsupported (final spending paragraph): treats FOX 9's "Johnson is outspending Finstad by more than $500,000" as candidate campaign spending. FOX 9 gives no source or type. Fix: "FOX 9 did not say whether the more than $500,000 gap counts candidate spending, outside spending or both, so it cannot be compared with MPR's outside-spending total."
3. ATTRIBUTION_FIX / misleading (dek, openfile `other:`): "Two outlets give different Republican-side figures." The $600,000 (one group tied to House Majority Whip Tom Emmer, ads criticizing Johnson, week of Oct 9, MPR) and about $400,000 (GOP PACs "recently", FOX 9) are different items, not competing figures. Fix: "Two outlets report separate Republican-side figures."
4. Odd/misleading sentence (spending para 1): "The report supplies both directions of attack without making either candidate the sole target." Vague and editorial. MPR says most outside money opposes Finstad, $600,000 criticized Johnson and left-leaning groups boosted field organizing and canvassing. Fix: "MPR's account includes most of the more than $2.5 million opposing Finstad and a $600,000 ad buy criticizing Johnson in one week; it does not say whether the figures overlap." Also name Tom Emmer (MPR does; it does not name the group).
5. ATTRIBUTION_FIX (health care paragraph): MPR reports Finstad said the Trump administration "put $50 billion into rural health care funding" and Johnson said it "cut $137 billion from rural health care through Medicaid". Article says "cited $50 billion in funding" and "cut $137 billion through Medicaid". Fix: restore the fuller wording.
6. Reader-facing process language: "supplied material", "supplied account", "this draft", "this record". Replace with "the reporting" or "the published account". Same in the Senate article.

### Senate article
1. ATTRIBUTION_FIX (para 1): MPR says the race "has been seen just a trickle of outside attention" and the campaigns "have not held many news conferences or big rallies". "Outside attention" is ambiguous with outside spending. Fix: "MPR reported the race had received only 'a trickle of outside attention' and that the candidates had not held many news conferences or big rallies."
2. WRONG (Thune sentence): "did not commit Senate Leadership Fund money" is the article's characterization. MPR describes Thune as "not exactly enthusiastic" when asked about SLF spending and quotes him saying translating interest into "financial resources and support coming here is something we hope to see happen". Fix: "Senate Majority Leader John Thune, asked whether the Senate Leadership Fund would spend in the race, said there was 'more interest'; MPR described him as not exactly enthusiastic about spending."
3. Source title mismatch: sources line 1 and openfile cite "Peggy Flanagan and Michele Tafoya's Senate race stays quiet in Minnesota", but the page headline is "Minnesota U.S. Senate race simmers as first debate nears" (byline Peter Cox; the URL slug carries the older headline). Fix the source title.
4. Speculative sentence (money section): "That contrast helps explain what MPR meant by a quiet general-election contest." MPR attributes the lower post-primary spending partly to Republicans spending heavily in reliably red states. Fix: delete, or replace with that attribution.
5. Odd phrasing: "Yet the poll MPR described did not show a large separation" (editorial; "Yet" does not follow). Fix: "MPR described a Star Tribune/KARE 11 poll with Flanagan at 47 percent and Tafoya at 43 percent." Also "date this draft was prepared" and "supplied research" (see MN-01 fix 6).

## Article 1: Senate (S6MN00440 Flanagan, S6MN00556 Tafoya)

| Claim | Where | Source checked | Verdict | Exact fix |
|---|---|---|---|---|
| Front matter title has no quotation marks | title | style | VERIFIED | none |
| MPR reported Oct 12 | para 1, sources | MPR 10/12 | VERIFIED | none |
| Little outside attention, few news conferences or large rallies | para 1 | MPR | ATTRIBUTION_FIX | Senate fix 1 |
| Flanagan of DFL, Republican Tafoya | para 1 | MPR | VERIFIED | none |
| Poll 47% Flanagan, 43% Tafoya | para 2, openfile | MPR | VERIFIED | none |
| About 9% undecided | para 2 | MPR | VERIFIED | none |
| Margin of error 3.5 points | para 2 | MPR (plus or minus 3.5) | VERIFIED | none |
| Star Tribune/KARE 11 poll, published Oct 12, fielded previous week | poll section | MPR ("published Monday", "conducted last week"; Oct 12 2026 is a Monday) | VERIFIED | none |
| No field dates, sample or method available | poll section | MPR gives none | VERIFIED | none |
| Lead is four points; not called tied or within margin | poll section | arithmetic | VERIFIED | none |
| Outside groups spent more than $20 million in primary, mostly DFL side | money | MPR | VERIFIED | none |
| About $2 million since, about $1.3 million pro-Flanagan freeway billboards | money | MPR (per public records, as of Oct 9) | VERIFIED | add "as of October 9" |
| Contrast "helps explain what MPR meant by quiet" | money | MPR | UNVERIFIED | Senate fix 4 |
| Thune "more interest", did not commit SLF money | money | MPR | WRONG | Senate fix 2 |
| Flanagan tied Tafoya to Trump | debate | KTTC | VERIFIED | none |
| Tafoya tied Flanagan to Walz and fraud cases | debate | KTTC | VERIFIED | none |
| Oct 16, only scheduled debate | debate | KTTC | VERIFIED | none |
| Tafoya called herself a pro-choice Republican | debate | KTTC quote | VERIFIED | none |
| Kalshi capture 2026-10-31 19:51:49 UTC, event SENATEMN-26 | market | markets.json | VERIFIED | none |
| SENATEMN-26-D last 0.908, bid 0.907, ask 0.908 | market | markets.json | VERIFIED | none |
| SENATEMN-26-R last 0.096, bid 0.094, ask 0.096 | market | markets.json | VERIFIED | none |
| Rules wording; party contracts with candidate labels | market | markets.json rules and yes_label | VERIFIED | none |
| Price is not a forecast; no probability stated | market | interpretation | VERIFIED | none |
| Both candidates Not graded on six issues; no congressional record | record | candidates.json (all six not_graded, both) | VERIFIED | none |
| Source 1 title | sources | MPR page headline differs | ATTRIBUTION_FIX | Senate fix 3 |
| Oxford comma | whole file | scan | VERIFIED (none found) | none |

## Article 2: MN-01 (H2MN01223 Finstad, H6MN01190 Johnson)

| Claim | Where | Source checked | Verdict | Exact fix |
|---|---|---|---|---|
| Spending "outpaced the Senate race" | title, h2, paras 1-2, openfile | MPR 10/09 and 10/12 | WRONG (misleading) | MN-01 fix 1 |
| Front matter title has no quotation marks | title | style | VERIFIED | none |
| FEC data: more than $2.5 million outside spending, most opposing Finstad | para 1 | MPR | VERIFIED | none |
| Finstad Republican incumbent; Johnson DFL Rochester math teacher | para 1 | MPR ("Rochester high school math teacher") | VERIFIED | optionally add "high school" |
| Oct 8 debate on two southern Minnesota TV stations | debate | MPR | VERIFIED | none |
| Finstad defended tariffs; Johnson: tariffs are a tax, would vote to end | debate | MPR | VERIFIED | none |
| $50 billion and $137 billion are candidate claims | debate | MPR | ATTRIBUTION_FIX | MN-01 fix 5 |
| Group tied to House majority whip, $600,000 against Johnson that week | spending | MPR (Tom Emmer; group not named) | VERIFIED | name Emmer |
| "supplies both directions of attack" | spending | MPR | WRONG (vague) | MN-01 fix 4 |
| About $400,000 added by GOP PACs (FOX 9, Oct 22) | spending | FOX 9 | VERIFIED | none |
| Johnson, first-time candidate, outspent Finstad by more than $500,000 | spending | FOX 9 | VERIFIED | none |
| That gap is candidate campaign spending | final spending para | FOX 9 does not say | WRONG | MN-01 fix 2 |
| "Two outlets give different Republican-side figures" | dek, openfile | MPR vs FOX 9 | ATTRIBUTION_FIX | MN-01 fix 3 |
| Finstad won by 17 points in 2024 | context | FOX 9 | VERIFIED | none |
| One of the closest among eight House races | context | FOX 9 | VERIFIED | none |
| Jacobs (U of M) pointed to farm affordability pressure, framed as interpretation | context | FOX 9 (also tied it to tariffs and the war in Iran; said the district is "the most competitive") | VERIFIED | optional: mention tariffs and Iran war |
| FOX 9 referred to polling without naming a poll | context | FOX 9 | VERIFIED | none |
| Kalshi KXHOUSERACE-MN01-26, capture 19:51:49 UTC | market | markets.json | VERIFIED | none |
| -D last 0.40, bid 0.40, ask 0.41 | market | markets.json | VERIFIED | none |
| -R last 0.61, bid 0.61, ask 0.62 | market | markets.json | VERIFIED | none |
| Rules wording; party contracts | market | markets.json | VERIFIED | none |
| Finstad A+ Data Bill of Rights; F- War-Crime Accountability, Universal Healthcare, US-Israel Military Merger | record | candidates.json (stock ban and Citizens United not_graded) | VERIFIED | none |
| Johnson not served in Congress, no graded issue | record | candidates.json (all six not_graded) | VERIFIED | none |
| Oxford comma | whole file | scan | VERIFIED (none found) | none |

## Other notes
- Neither article states win probabilities, rankings or endorsements; both decline causal claims. Keep that.
- Hero alt text is not checkable against the sources; not reviewed.

## Resolution (Claude Code, 2026-10-31)
All required fixes were applied to both articles: MN-01 retitled "Outside spending in Minnesota's 1st District tops $2.5 million, MPR reported" with MPR's comparison attributed and the different periods stated (MPR's October 12 Senate report added as source 6); FOX 9's $500,000 gap no longer called candidate spending; the two Republican-side figures called separate; Tom Emmer named; the candidates' health care claims restored in fuller wording (as paraphrase, not quotation, because the fetch tool returns summaries); process wording removed. Senate: Thune sentence attributed to MPR, source 1 title corrected, speculative sentence replaced with MPR's red-state suggestion, "a trickle of outside attention" wording, poll sentence and process wording fixed, "as of October 9" added. Revised wording was not re-run through the gate; the owner signs off the fact-check. Refresh the Kalshi quotes before any republish.
