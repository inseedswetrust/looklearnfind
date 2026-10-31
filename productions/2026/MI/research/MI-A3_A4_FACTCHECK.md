# Fact-check: MI-A3 and MI-A4 (2026-10-31)

Drafter: ChatGPT (package MI-articles-20261031-9410948, returned in `MI_ARTICLE_DRAFTS_RETURN_20261031.zip`). Checker: Claude Code, who built the briefs. That is not fully independent for the figures, so every number below was **recomputed from the raw FEC pull with separately written code** (not by reading the reconcile output) and the committee facts were re-queried from the FEC API on 2026-10-31. Owner sign-off is still required before publishing.

Published files: `content/learn/michigan-13-primary-outside-spending-2026.html` and `content/learn/michigan-10-outside-spending-reporting-calendar-2026.html`. The drafts are kept unchanged in `productions/2026/MI/inbox/MI-articles-20261031-9410948/`.

## What was wrong in the drafts and what I changed
Both drafts carried drafting-process language and unusable source lists:
- Body text said "the supplied FEC pull", "the brief identifies", "the supplied reconciliation", "Keep those categories visible" (an instruction to a writer) and "What this pull says about UDP". Rewritten as reporting.
- The `sources` blocks listed 27 and 35 claim rows ("Supplied story brief and reconciliation method") instead of sources. Replaced with seven real sources each.
- The openfile box said "The drafter did not independently fact-check" and named internal files. Rewritten.
- Hero keys were blank. MI-A3 uses `mi-capitol` (the licensed Lansing photo already on the governor page) and MI-A4 uses `mi-udp` (AI illustration, credited). Both are placeholders; new heroes are optional.

### MI-A3 specific
1. **Date window error (mine, in the brief; copied by the draft).** The brief and draft said the entries ran "January 8 through September 15". That mixed payment dates with dissemination dates. By dissemination date every entry is dated January 8 through August 4. Six small periodic-report entries for McKinney carry payment dates August 10 to September 15 ($60,363.01, all support) and were disseminated on or before August 4. The article now says so. The brief and claims generator (`research/build_mi13_brief.py`) now uses dissemination dates, and the brief and claims were regenerated.
2. "Primary spending" framing: 99.8 percent of the dollars were disseminated in June and July (recomputed). Stated.
3. "Protect Progress's support is 96 percent of the support reported for Thanedar": $1,774,655.00 / $1,848,181.00 = 96.0 percent. Added.
4. "The super PAC affiliated with AIPAC" (my own phrasing in an interim edit) removed: the FEC record carries a name and an ID only, so the article says "a super PAC" and links our existing report.
5. Working Families Party PAC: FEC roll-up $297,869.11 equals the sum of its periodic-report entries exactly; the reconciled $427,788.40 adds notices. Verified.

### MI-A4 specific
1. **Bouchard's "authorized committees" figures replaced.** The draft used $2,884,259.39 receipts and $1,310,789.75 disbursements from the FEC candidate summary. Bouchard has four authorized committees (a principal committee and three nominee funds), and the candidate summary includes $536,042.24 transferred between his own committees, so adding them can count the same dollars twice. The article now uses his principal committee only: receipts $2,672,721.59, disbursements $1,112,737.40, cash on hand $1,559,984.19 through October 14 (PRE-GENERAL, received October 22), re-queried 2026-10-31.
2. "A joint nominee fund filed a termination report on October 13": the FEC shows the EMB Nominee Fund (C00934745) filed a TERMINATION REPORT (coverage through September 30) received October 13 and later a PRE-GENERAL (coverage through October 14) received October 22. It is not called "joint" by the FEC; the article now names it and says it is a different committee from the principal committee.
3. "The roll-up matches periodic-report entries in all 13 committee-and-side lines": recomputed from the raw pull, 13 of 13 lines equal the sum of non-memo F3X entries to the cent. HMP against Bouchard: $175,718.76 is four F3X entries (three on September 15 totaling $109,102.76 and one on September 22 of $66,616.00).
4. "Without pairing the totals would have been about $2.8 million for Hines and $10.3 million against Bouchard": first-pass (`schedule_e.dedupe`) lines for the two largest movers, as recorded on October 28. Stated as "would have been about".
5. HMP: 23 entries, September 15 to October 24, $7,212,674.95; three television notices (October 6, 13, 20) labeled ESTIMATE, payee Waterfront Strategies Inc., $5,961,621.60, 82.65 percent ("about 83 percent"). Verified in the raw pull.
6. Committee types (hybrid PAC or Super PAC) verified against `fec_committees_MI10.json`: HMP, Giffords PAC, CLF, Ready for the Fight, Pro-Choice Majority Action, CFFE PAC are hybrid PACs; Restoration of America PAC, LCV Victory Fund, No Going Back PAC Inc. and Honor, Duty and Discipline PAC are Super PACs.

## Recomputed figures (all match the articles)
| Figure | Value |
|---|---|
| Supporting McKinney / opposing McKinney | $1,727,586.94 / $268,690.00 |
| Supporting Thanedar / opposing Thanedar | $1,848,181.00 / $463,165.48 |
| Protect Progress for Thanedar / against McKinney / together | $1,774,655.00 / $268,690.00 / $2,043,345.00 |
| Supporting Hines / opposing Hines | $2,537,611.79 / $4,164,104.66 |
| Supporting Bouchard / opposing Bouchard | $918,413.55 / $10,135,610.20 |
| HMP against Bouchard | $7,212,674.95 (23 entries) |
| McKinney committee through Oct 14 | receipts $1,876,779.88; disbursements $1,747,106.34; cash $129,673.54 |
| Thanedar committee through Sept 30 | receipts $3,194,222.05; disbursements $4,163,399.35; cash $5,935,390.40; candidate loans $2,970,000.00 |
| Hines committee through Oct 14 | receipts $4,159,692.85; disbursements $3,152,065.09; cash $1,007,627.76 |

## Still open (stated in the articles)
- The official August 4 canvass was not read; the result is attributed to WDIV and Bridge Michigan as unofficial.
- Notice amounts are the filers' own and labeled estimates for HMP; later reports can change them.
- Who funds each committee, alignment, whether ads ran, effect on votes: not established and not claimed.
- CLF has no entry after September 30 in the pull; its figure is described as not final.
- The Michigan Advance coverage of MI-13 returned 403 and was not circumvented. Nothing about T.P. Nykoriak's past is used.
- Two findings for the owner: (a) the MI-A3 brief I wrote had the date window error above; (b) the FEC candidate summary is unsafe to use for candidates with several authorized committees (the same caution applies to any future "authorized committees" figure).
