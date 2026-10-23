# Florida reporting digest (Senate and House)

Prepared 2026-10-23 for the ChatGPT writing phase. Every item has a source ID that resolves in `fl_sources.jsonl`. Items marked **opened** were read in full by Claude on 2026-10-23. Items marked **search summary only** were seen only as a search-result snippet and must be opened and verified before use. Nothing here is a prediction. Quotes are avoided; claims are paraphrased.

## Senate (target: at least two; delivered: four, one flagged unverified)

### S1. The newest independent poll shows a four-point Moody lead, narrower than July
- **Claim (paraphrase):** A University of North Florida Public Opinion Research Lab poll of 1,471 likely midterm voters, fielded Oct 12 to 19 by telephone with a ±2.81-point margin, had Ashley Moody at 49, Angie Nixon at 45 and 5 percent undecided. The July UNF poll had Moody ahead by 8.
- **Source:** SRC-NEWS-WLRN-UNF, published 2026-10-21 (**opened**). Original UNF release not yet opened: Phase C must pull it for sponsor and exact wording.
- **Dissent or response:** The report quotes UNF's faculty director attributing the tightening to the national environment and the president's approval. That is the pollster's reading, not a finding of the poll; do not adopt it as a cause.
- **Why it is worth reporting:** It is the most recent high-quality poll, shows direction over the same pollster's July survey, and contrasts with the earlier September polls (S3). Kalshi's party contract for the Senate seat was last captured at 0.904 on 2026-10-23 (`fl_markets.json`); the two are different instruments and the story must not say one moved the other.

### S2. Moody declined to debate; Democrats say she is avoiding reporters; Hope Florida background
- **Claim (paraphrase):** Earlier in September Moody declined to debate Nixon, telling a Jacksonville station she would focus on Nixon being a self-described socialist. On Oct 1 the state Democratic chair and a state representative said Moody was avoiding reporters and town halls. Moody told the News Service of Florida she keeps working for constituents in Washington, and attacked Nixon on social media.
- **Source:** SRC-NEWS-WUSF-MOODY (News Service of Florida), published 2026-10-01 (**opened**).
- **Dissent or response:** Moody's side is in the article. Nixon's relationship to the Democratic Socialists of America is characterized differently by the two campaigns; Search results say Nixon has said she does not fully align with the DSA platform (**search summary only**, verify).
- **Background in the same article:** Moody was attorney general when her office approved a Medicaid settlement that sent $10 million to the Hope Florida Foundation. The article says a grand jury found the administration misappropriated the funds and no charges were filed. It calls the grand jury "2024"; verify that date against the grand jury report before repeating it.
- **Why it is worth reporting:** The debate decision and the Hope Florida record are the campaign's two stated lines of attack and defense.

### S3. September polls disagreed because of pollster, sponsor and population
- **Claim (paraphrase):** Three September polls of likely voters: St. Pete Polls (Sep 15 to 17, n=913, ±3.2) had Moody 45.2, Nixon 44.8; Change Research for Freedom Project USA (Sep 7 to 9, n=1,107, ±2.8) had 47 to 47; Quantus Insights (Sep 8 to 10, n=733, ±4.1) had Moody 50, Nixon 43. Moody's campaign described the race as a dead heat in a supporter email.
- **Source:** SRC-NEWS-NEWSWEEK-POLLS (**opened**; the page is undated, linked source dated 2026-09-19).
- **Why it is worth reporting:** The spread is mostly sponsor and house-effect, which the VoteHub listing in `fl_polls.csv` also shows (28 Florida Senate rows). Report the range with sponsors; do not average.

### S4. Outside spending in the Senate race (FEC data, not a news claim)
- **Claim:** In de-duplicated FEC Schedule E data for the 2026 cycle, the committee STRONGER SAFER NATION shows about $9.32 million opposing Nixon and about $2.46 million supporting Moody; NEW DEAL FOR ALL, INC. shows about $3.10 million opposing Moody. Committee types are blank in the FEC payload we captured.
- **Source:** `fl_outside_spending.csv` (FEC Schedule E, captured 2026-10-23). No claim about who funds these committees is made here.
- **Why it is worth reporting:** The size is larger than the whole recorded Moody-supporting spending by any other committee. **Research to do:** identify each committee's registered purpose, top donors (FEC Form 3X) and any stated affiliation from the committee's own filings before the article characterizes it.

### Flagged, do not use until verified
- Nixon's Oct 14 remark in a CNN interview about Moody (SRC-NEWS-FOX-NIXON-JAIL, **search summary only**). Check the original interview and context. Not recommended as a lead.

## House (target: at least three beyond FL-14/FL-25 ad spend; delivered: three plus context)

### H1. The new congressional map reworked 21 of 28 districts
- **Claim (paraphrase):** According to the News Service of Florida as relayed by WUSF, 21 of the 28 districts were reworked, districts 1 to 7 were unchanged, and four more Republican-leaning seats were added. District 14 shifted south and east into rural Hillsborough County, with the reporters estimating Trump would have won it by about 10 points. District 20 is now plurality Black (about 48 percent). The Florida Supreme Court declined an emergency request to block the map, and the case was proceeding in a lower court.
- **Source:** SRC-NEWS-WUSF-MAP, published 2026-06-15 (**opened**). Official boundaries: plan EOGPCRP2026, SRC-MAP, used in `fl_races.json` with population and county shares.
- **Dissent or response:** A voting-rights group sued in Leon Circuit Court (**search summary only**, verify the plaintiff and case status).
- **Why it is worth reporting:** It determines every district comparison. The Trump-margin figures are reporters' estimates; do not present them as official.

### H2. FL-20: an open Democratic primary after the former member resigned
- **Claim (paraphrase):** Sheila Cherfilus-McCormick resigned in April 2026 and has been indicted on federal charges, which she denies; the trial was reported as scheduled for February 2027. Debbie Wasserman Schultz moved to the redrawn 20th after her old 25th shifted toward Republicans. The official roster records Wasserman Schultz as the Aug 18 winner, and Cherfilus-McCormick, Dale Holness, Luther Campbell and Elijah Manley as defeated.
- **Source:** SRC-NEWS-BALLOTPEDIA-FL20 (**opened**, published 2026-06-23, before the primary) for the background; SRC-DOS-FED (official roster) for the result.
- **Dissent or response:** Cherfilus-McCormick denies wrongdoing (stated in the Ballotpedia piece and by search summary; confirm with a court filing or a primary news report).
- **Why it is worth reporting:** It is the clearest example of the new map displacing an incumbent across districts, and the nominee has no TIP grade for several issues (see `tip_grades.csv`). A neutral account needs the indictment status verified against the docket.

### H3. FL-25: Moskowitz moved into the redrawn 25th and won a primary against a DSA-backed challenger
- **Claim (paraphrase):** Reuters reported on Aug 18 that Jared Moskowitz was projected to win the Democratic primary in the redrawn 25th over Oliver Larkin, who was backed by the Democratic Socialists of America. The wire copy gave no vote shares. The official roster confirms Moskowitz Won and Larkin Eliminated; Scott Singer is the Republican nominee.
- **Source:** SRC-NEWS-REUTERS-FL25 (**opened**); SRC-DOS-FED.
- **Dissent or response:** None in the wire copy. Phase C should pull vote counts from the Division of Elections.
- **Why it is worth reporting:** It pairs with the FEC record: about $7.73 million opposing Moskowitz and about $12.62 million opposing Singer in de-duplicated Schedule E data (`fl_outside_spending.csv`). That spending exceeds any other House race in the file. Only describe the dollars, not their effect.

### H4. FL-6 and FL-22: large single-committee outside spending (FEC data, not a news claim)
- **Claim:** CONSERVATIVE FIGHTER PAC (about $3.48 million) and DEFEND AMERICAN JOBS (about $3.35 million) show support for Randy Fine in FL-6; NO GOING BACK PAC INC. shows about $3.84 million opposing Pia Dandiya in FL-22. Both are in the FEC Schedule E data.
- **Source:** `fl_outside_spending.csv`.
- **Research to do:** identify the funders and stated purposes from the committees' own filings, and find independent local reporting on each race. None was found in this pass; this is a gap, not a finding.

### Supporting reference: FL-14 and FL-25 ad spending (already used on LLF)
- The published LLF report uses FEC independent expenditures only. The ad-tracker article it cites (Washington Post, Oct 7, with AdImpact data) **could not be retrieved**, so its figures were removed and the report says ad-tracking estimates and FEC independent expenditures measure different things. **Unconfirmed:** I could not verify the original ad-tracker category definitions. Phase C should obtain the article or AdImpact's own page before restating that difference as a fact with numbers.

## Gaps
- Only one independent local source per House story was found; the quota of "independently sourced" House items is met in count but not in depth. H2 and H3 rest on one article plus the official roster.
- No debate, poll or fundraising report was found for the Senate after Oct 21 beyond S1.
- No reporting was found on FL-14 candidate Mike Beltran or Kathy Castor beyond the map story and FEC data.
