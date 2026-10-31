# NY fact-check report, 2026-10-30

Reviewer: claude-factcheck-subagent (independent of drafter Kimi). Ledgers: CLAIMS_NY-GOV-A.csv (27 rows), CLAIMS_NY-17-A.csv (28 rows). Neither article was edited. READY is not publication approval.

Sources actually opened: Siena original release (sri.siena.edu/2026/10/28/...), City & State Siena story (Oct 28) and NY-17 profile (Oct 5), Marist release page, Emerson/PIX11 page, four TIP candidate pages and both TIP race pages, Kalshi public API (GOVPARTYNY-26, HOUSENY17-26, fetched 2026-10-30 13:54 ET), Spectrum News (Blakeman as Nassau County Executive).

## 1. Governor article: BLOCKED

Problems
1. Kalshi ask is not reproducible. Text: "with a Hochul bid of 0.956 and an ask of 0.959". Live API: yes_ask 0.957 (previous_yes_ask 0.958). 0.959 appears nowhere. Correction: refresh all quotes and state a clock time, or drop the ask.
2. Hochul last trade is stale. Text: "the last trade was 0.957 for Hochul and 0.044 for Blakeman". Live: Hochul last 0.955 (previous_price 0.957), Blakeman last 0.044 (matches, previous 0.047). Bid 0.956 matches. "Captured October 30" is honest for the date only if refreshed; add a time (for example "as of 1:54 p.m. ET").
3. Contract is a party contract. Text: "Kalshi's market last traded near 96 cents for her" and "0.957 for Hochul". Rules text: "If a representative of the Democratic party is inaugurated as the governor of New York pursuant to the 2026 election, then the market resolves to Yes." Hochul is only the label. Correction: "the Democratic-party contract". The article's "resolves on the party of the person sworn in" is consistent with the rules (inaugurated vs sworn in is a near match).
4. NEEDS_CONTEXT, not blocking: "TIP's six-issue grades come only from recorded congressional acts" is supported by no page I opened (race page says "No reviewed evidence"). Cite TIP methodology or soften. "Nassau County Executive", "Democratic incumbent" and the "November 3" date are not in the article's sources block (I confirmed them elsewhere); add sources.

Verified or attributed (headline test): "grew to double digits" is supported by the same pollster: Siena 9 points (Hochul 50, Blakeman 41) in September to 14 (54-40) in October, from Siena's own release. "Independents flipped": Siena's release confirms Hochul +11 among independents in October (51-40 split is from City & State); the September figure (Blakeman 44, Hochul 39) is ATTRIBUTED to City & State only, because the Siena summary I could open did not show it. Same pollster, so the word "flipped" is acceptable if that figure holds; consider adding the Siena release URL to the sources block (the openfile says it was not opened). Siena 6% undecided is ATTRIBUTED (C&S; Siena does not report it). Marist (Oct 22 to 25, 1,448 RV, LV 53-42, 4% undecided, LV MOE ±3.9, RV 14-point lead, no sponsor named) VERIFIED on Marist's page. "Two polls ahead by double digits" holds (Marist LV gap is 11). TIP: Hochul and Blakeman profiles show all six issues Not graded; article does not present that as zero. R1 and R2 links present and resolve. No Oxford commas, forecasts, causal claims or rankings found.

Not verified: Siena September independents at the original; Siena undecided; Marist likely-voter sample size (page does not state it, article does not claim one).

## 2. NY-17 article: BLOCKED

Problems
1. Headline and heading. Text: "NY-17: a tied poll and a market that leans Democratic" and "A tied poll in late September". Source: Emerson has Conley 48, Lawler 46, credibility interval ±4.9. That is inside the margin, not tied. Correction: "a poll inside the margin of error".
2. Unsupported fact. Text: "Cait Conley, a first-time candidate". City & State says only that she "has never been a legislator herself" (Army veteran, West Point, former NSC counterterrorism director, three Bronze Stars). Correction: "who has never been a legislator", or remove.
3. Contracts are party contracts. Text: "Kalshi lists a NY-17 House winner contract for each candidate." Rules: "If the House member sworn in for NY-17 for the term beginning in 2027 is a member of the Democratic Party, then the market resolves to Yes" (and Republican). Correction: say party-winner contracts labeled with each candidate's name.
4. NEEDS_CONTEXT: dek "a market that leans Democratic" reads as a probability judgment; state the prices instead. "and it can move on information a poll has not yet captured" is an unsourced explanation of price movement; delete. "in the Hudson Valley" is not in the cited text. "We found no public poll newer than September 29" is an absence claim I cannot prove.

Verified: Emerson/PIX11 dates, n=400, ±4.9, 48/46/7, favorability (Lawler 45/46; Conley 44/35/22), sponsor PIX11. Kalshi matched live exactly: Conley last 0.62 bid 0.61 ask 0.62; Lawler last 0.39 bid 0.38 ask 0.39 (the "captured October 30" wording is currently honest). All six Lawler grades match H2NY17162 (F- Data Bill of Rights, War-Crime Accountability, US-Israel Military Merger; A+ Stock Trading Ban, Universal Healthcare; Citizens United Reform not graded); Conley all six Not graded (H6NY17171). C&S geography, 2022 flip VERIFIED. ATTRIBUTED (not checked against official returns): about 78,000 more registered Democrats, Harris 49.9 to 49.3. R1, R2 links fine; no Oxford commas found.

Not verified: voter-registration and 2024 returns at official sources; absence of newer polls.

## 3. Notes on the gate
- Governor grade rows use type fact because the gate rejects GOV- IDs for type grade; they were still checked on the cited TIP pages.
- Market rows carry "party-winner contract" and quote kind in the claim text because the gate reads those from claim/notes, not evidence_ref.
- Unknown-type warnings for "fact" rows are non-blocking and omitted below. The gate was run without --build.

## 4. Gate output (PYTHONUTF8=1, --author Kimi, no --build)

Governor: result BLOCKED, rows 27, blocking: L17 "UNVERIFIED and not resolved (removed, replaced or relabeled)" (the 0.959 ask). Warnings: 7 "unknown type 'fact'" notices (L21 to L27), no other.

NY-17: result BLOCKED, rows 28, blocking: L06 (tied headline) and L13 (first-time candidate), both "UNVERIFIED and not resolved". Warnings: 9 "unknown type 'fact'" notices, no other.

Both end with: "READY means the ledger is complete and consistent. It does not approve publication: a person does that."
