# Florida State of the Race: video concept (foundation for the storyboard and script)

Prepared 2026-10-24. Scope: Governor, U.S. Senate, U.S. House (30 contests). Instagram only. 90 seconds, 9:16 (1080 x 1920, 30 fps). Synthetic narrator, no host. Music: the Artlist brass-techno bed already chosen (Meute-style, Meute itself not used). Real, public-domain portraits and deterministic graphics only; no synthetic footage of real people or events. This document is a concept, not a script: every spoken or on-screen number below is tagged to a fact ID in the callout sheet (section 5) with its source and its wording limit.

Run order: publish the Florida Senate and House articles first (they are built and linked), refresh the numbers (section 7), then storyboard from this file.

## 1. The idea in one sentence
**Three numbers disagree about Florida's governor, one poll tightened in the Senate race, and a new map changed the House: here is every contest, what each measurement shows and what it does not.**

Tone: premium editorial, calm, precise. No outrage, no endorsement, no prediction. The tension is real: the numbers do not agree, and the video says why.

## 2. Hooks (cut three versions, test them)
First 2.5 seconds carry the whole video. Each hook is one on-screen line plus one spoken line, and each is a verified fact.

| Hook | On screen (line 1) | Narrator | Facts | Why it should hold |
|---|---|---|---|---|
| **A (lead)** | "Florida's governor race: a 2-point poll, an 83¢ market, a 17-to-1 money gap." | "Three ways to measure Florida's governor race. They do not agree." | F-08, F-09, F-10 | an open loop with a promise to resolve it; the three numbers appear as three stamped chips |
| **B** | "Florida redrew 21 of 28 House districts." | "Florida redrew 21 of its 28 congressional districts. Then the primaries happened." | F-18, F-19 | one concrete, surprising number plus a "then what" |
| **C** | "The incumbent won't debate. The newest poll is 49 to 45." | "Florida's Senate seat is on the ballot. The incumbent will not debate. The latest poll has her up four." | F-12, F-13, F-14 | conflict plus a number; narrower audience |

Recommendation: ship A, hold B and C as the next two uploads in the same visual system (a series, section 8).

## 3. Beat sheet (90 seconds)
Safe zones: keep text out of the top 250 px and bottom 340 px. Burned-in captions on every spoken line. All graphics come from the existing renderers: `tools/social/render_cards.py` (data-driven HTML cards) and the components on the article pages.

| Time | Beat | On screen | Narrator (synthetic) | Facts | Asset |
|---|---|---|---|---|---|
| 0:00 to 0:03 | Hook A | three chips slam in: "49–47 poll", "83¢ market", "$107.6M vs $6.4M committees" over the Old Capitol hero | "Three ways to measure Florida's governor race. They do not agree." | F-08 F-09 F-10 | hero `fl-capitol.jpg` (credit DXR, CC BY-SA 4.0) |
| 0:03 to 0:12 | The board | 30 tiles, one per contest, names and party letters (governor, Senate, 28 districts), pulses once | "Florida votes November 3 on thirty contests: governor, one Senate seat and 28 House districts. Here is what we can check." | F-01 F-02 | State Board component (`/elections/2026/florida/`), screen-recorded or re-rendered from `candidates.json` |
| 0:12 to 0:32 | Governor | the three chips, one at a time, each with a label saying what it measures and what it does not | "A University of North Florida poll has Byron Donalds ahead of David Jolly, 49 to 47. The margin of error is nearly three points, so that is a close race, not a lead. Kalshi's contract on a Republican win last traded at 83 cents, a trader's price, not a vote share. And one committee backing Donalds reported 107.6 million dollars, against 6.4 million for the committee backing Jolly, as of September 11. That includes transfers, so it is not ad spending." | F-08 F-09 F-10 F-11 | `poll_unf`-style bars for governor; market card; two-bar money comparison labeled "reported, Sept 11" |
| 0:32 to 0:52 | Senate | portraits of Moody and Nixon; poll bars 49 and 45; "declined to debate" card; Vindman line | "In the Senate special election, the newest poll has Ashley Moody at 49 and Angie Nixon at 45. Moody has declined to debate. Nixon won her primary over Alex Vindman, who had reported raising about 14.5 million dollars through June." | F-12 F-13 F-14 F-15 F-16 | `ig-fl-senate-poll.png` redone as motion; portraits 89119.jpg and 90009.jpg |
| 0:52 to 1:12 | House | map with five numbered pins; Trump margins as two split bars; three result bars | "Florida redrew 21 of its 28 House districts. Reporters put the 2024 presidential vote at 55 to 44 for Trump in Kathy Castor's new district. Three August primaries followed: Moskowitz, Fine and Wasserman Schultz won theirs." | F-18 F-19 F-20 F-21 F-22 | `ig-fl-house-map.png` as motion; `result_bars` |
| 1:12 to 1:24 | The six issues | one profile's six slots fill in, four slots stay as dashes with the caption "not graded is not a zero" | "Every candidate has a profile on The Issues Party with six issue grades, where they have a congressional record. A dash means not graded. It does not mean zero." | F-23 F-24 | `ig-fl-house-tip.png` or `ig-fl-senate-tip.png`; one candidate zoomed |
| 1:24 to 1:30 | Close | end card: "Every race, every candidate, every grade. Link in bio." plus "Early voting: Oct 24 to 31" plus credits | "Early voting runs October 24 through 31. Every contest and every grade is linked below." | F-25 F-26 | end card; credits list |

If the cut runs long, drop the issues beat to 6 seconds and keep the board and the three measurement chips.

## 4. Visual system
Colors: paper #f5f2eb, ink #1c1d1b, teal #145b5d, annotation yellow #dfca00. No party colors. Type: serif headlines (the site's Newsreader family or Georgia), sans labels. Every number appears as a chip with its source in small text beneath (for example "UNF, Oct 12–19, n=1,471, ±2.81"). Motion: counters tick up, bars grow left to right, pins drop on the map; one transition type only (a hard cut on the beat). Audio: the brass-techno bed ducked under narration; a single percussive hit on each chip entry; nothing else. Graphics are drawn from data, never generated imagery. Portraits: public domain, credits in the end card (see `fl_assets.csv`: Moody, Nixon, Castor, Fine and Moskowitz are licensed; the rest use a monogram). If any AI visual transition is used, label it in the caption and never imply it is footage.

## 5. Fact callout sheet (everything the video may state)
Status: VERIFIED = read in a primary or two independent sources; ATTRIBUTED = stated "according to <source>"; REFRESH = must be re-read the day of publication. "Say" is the wording limit; the "Never say" column is binding.

| ID | Fact | Say | Source (opened) | Status | Never say |
|---|---|---|---|---|---|
| F-01 | Florida has 30 contests in scope: governor, one Senate seat, 28 House districts; general election Nov 3 2026 | "thirty contests" | Division of Elections roster | VERIFIED | "all of Florida's races" (many others exist: state offices, ballot measures) |
| F-02 | 10 governor tickets, 3 Senate candidates, 83 House candidates on the November ballot | "ten governor tickets, three Senate candidates, 83 House candidates" | Division of Elections roster, captured Oct 23 | VERIFIED, REFRESH | any count after a withdrawal without re-checking |
| F-08 | UNF poll, governor: Donalds 49, Jolly 47, 4 undecided; 1,471 likely voters; Oct 12 to 19; margin ±2.81 | "49 to 47", "a close race, not a lead" | Action News Jax Oct 21 (opened: confirms Donalds' lead fell from five points in July to two, same sample and margin); the 49 and 47 toplines are in the published LLF governor article and a search summary of the same coverage, not yet in a page I opened in full | ATTRIBUTED, REFRESH | "Donalds leads"; "Jolly is closing" (the July comparison is single-sourced) |
| F-09 | Kalshi governor contract on the Republican party last traded 83 cents (Democratic 19 cents) at 22:40Z Oct 23 | "a trader's price, not a vote share" | Kalshi GOVPARTYFL-26, captured Oct 23 | REFRESH | "83% chance"; "the market says Donalds will win"; any link between the price and the poll |
| F-10 | Committee money as of Sept 11 reported by the News Service of Florida: Friends of Byron Donalds $107.6M raised; Florida 2026 (backing Jolly) $6.4M received | "reported, as of September 11", "about 17 to 1" (107.6 / 6.4 = 16.8) | News Service of Florida via CBS12, Sept 21 (cited in the LLF governor article; not retrievable directly from the state database) | ATTRIBUTED | "spent on ads"; "Donalds has $107 million"; any current total |
| F-11 | The committee figure includes transfers and cannot be read as advertising | "includes transfers, so it is not ad spending" | LLF governor article | VERIFIED as a caveat | omit the caveat |
| F-12 | Senate special election: Moody (R, appointed Jan 2025), Nixon (D, state Rep.), Gillespie (no party); winner serves the rest of Rubio's term, about two years | "special election", "appointed in January 2025" | WUSF/News Service of Florida Oct 1; Division of Elections | VERIFIED | "Moody was elected" |
| F-13 | UNF Senate poll: Moody 49, Nixon 45, 5 undecided; same poll as F-08 | "49 to 45" | WLRN and Action News Jax, both Oct 21 (both opened) | VERIFIED | "Moody leads by four" without the margin of error ±2.81 |
| F-14 | Moody declined to debate Nixon (told Action News Jax, reported by the News Service of Florida) | "has declined to debate" | WUSF Oct 1 | ATTRIBUTED | "refuses", "dodges", "hides" |
| F-15 | Nixon won the Aug 18 Democratic primary over Alex Vindman | "won her primary" | Division of Elections roster; Algemeiner Aug 19 (no shares) | VERIFIED | any vote share until the Division of Elections count is read |
| F-16 | Vindman had raised roughly $14.5 million through June (as cited by WFLX) | "had reported raising about 14.5 million dollars through June" | WFLX Aug 11 | ATTRIBUTED | "outspent"; "Nixon raised less" (no Nixon figure in the source) |
| F-17 | Three September polls: tie 47 to 47 (Change Research), Moody +7 (Quantus), 45.2 to 44.8 (St. Pete Polls) | optional: "earlier polls ranged from a tie to seven points" | Newsweek (page undated) | ATTRIBUTED | averaging the polls |
| F-18 | 21 of 28 House districts reworked; districts 1 to 7 unchanged | "redrew 21 of its 28 districts" | WLRN May 5; WUSF Jun 15 (WUSF attributes it to the News Service of Florida) | ATTRIBUTED | "gerrymander" or any motive claim |
| F-19 | Florida Supreme Court declined an emergency request to block the map; a suit is in Leon County court | "courts have let it stand for 2026" | WUSF Jun 15; WLRN May 5 | ATTRIBUTED | "the map is legal" |
| F-20 | Reported 2024 vote on the new lines: FL-14 Trump 55, Harris 44; FL-9 Trump 58, Harris 41 | "reporters put it at 55 to 44" | WLRN May 5 | ATTRIBUTED (reporters' figures; LLF did not recompute) | "Castor's seat is Republican"; any forecast |
| F-21 | Castor said she would run in the new FL-14; she faces Republican Mike Beltran | "Castor is running in the new 14th" | WLRN May 5; Division of Elections | VERIFIED | |
| F-22 | Aug 18 primaries: Moskowitz (FL-25) beat DSA-backed Larkin; Fine (FL-6) beat Bilzerian; Wasserman Schultz moved to FL-20 and won the nomination | "won their primaries" | Reuters via GV Wire Aug 18; Division of Elections roster; Ballotpedia Jun 23 | VERIFIED (winners); shares ATTRIBUTED | shares (63.5, 56.9, 45.6) only as "reported by Algemeiner" or after the Division of Elections count is read; no indictment or criminal claim |
| F-23 | TIP grades six issues, only where a candidate has recorded congressional acts; not graded is not a zero | "a dash means not graded" | TIP methodology; LLF methods page | VERIFIED | "TIP rates candidates as good or bad" |
| F-24 | Example: Moody has two graded issues (war-crime accountability F-, universal healthcare F-; 0 of 9 and 0 of 3 recorded acts aligned); Nixon has none graded | use one profile only, on screen, with the TIP date Oct 21 | TIP candidate records, computed Oct 21 | VERIFIED, REFRESH | endorsing or condemning a grade; inferring a position from a missing grade |
| F-25 | Early voting runs October 24 to 31 in all 67 counties, and some counties offer extra days | "Early voting runs October 24 through 31" | Florida Department of State press release, Oct 19 (opened) | VERIFIED | "mandatory period" (the release does not use that word); county hours |
| F-26 | Vote-by-mail request deadline was Oct 22 | omit from the video | same release | VERIFIED | stating it as upcoming |

Do not use: Hope Florida claims, the Cherfilus-McCormick indictment, the Bilzerian characterizations, any AIPAC or UDP claim, any outside-spending total, any win probability or "chance". None has a source that has been read to the standard this video needs.

## 6. Why this could travel (and what we are not promising)
Nobody can promise virality; distribution is decided by the platform. The design makes the video easy to watch to the end, easy to save and easy to share without making a partisan claim:
1. **Specific, verifiable tension in two seconds.** "Three numbers that do not agree" and "21 of 28 districts" are concrete and unusual; they promise a resolution inside 90 seconds.
2. **A saveable reference.** The 30-tile board is a utility: people save a "know your Florida ballot" frame. Saves and shares are the strongest signals for non-follower reach.
3. **A reason to send it.** The line "which number should you trust?" invites a send to someone who follows Florida politics without telling them what to think.
4. **Trust as the edge.** In a feed full of confident predictions, a video that says what each number does not prove is distinctive and gives local reporters, teachers and civic groups a reason to repost it. The cost is lower outrage-driven sharing; we accept that.
5. **Retention mechanics.** Short beats, one visual change every 2 to 3 seconds, counters and bars that resolve, a payoff for the open loop at 0:30, captions for sound-off viewing, a 90-second length that loops cleanly to the hook.
6. **Timing.** Early voting starts today and runs through October 31, so the video is useful now; it loses most value after November 3.

**Measure, do not assume.** Upload the three hook cuts on different days or to a split audience; judge by 3-second hold, average watch percentage, shares per reach and saves per reach; stop a cut that falls under half the best cut's 3-second hold after 24 hours. Pin a neutral comment ("Which of the three numbers do you find most useful?"). Reply to corrections within the hour and log them in the article's corrections block.

## 7. Before it is cut (refresh list)
Re-read the Kalshi governor and Senate quotes (F-09, F-24 context) and rebuild the market chips; check for a newer UNF or other public poll (`tools/qa/freshness_check.py`); confirm the Division of Elections counts for the three primaries so shares can move from ATTRIBUTED to VERIFIED; open the News Service of Florida committee-finance report or the state database for anything newer than Sept 11 (F-10); confirm early voting dates have not changed (F-25); have an independent reviewer sign the claims file (`CLAIMS_ARTICLE_FL_*.csv` cover the article versions of these facts).

## 8. Series and cuts
Same visual system, three follow-ups: Senate (hook C, with the TIP issue card), House map (hook B, with Castor, Soto and the FL-20 move), and an election-eve "what changed since" using the daily Kalshi and poll snapshots for same-contract movement only. Vertical cutdowns of 20 to 30 seconds per hook for Stories. Cover frame: the three chips on the Old Capitol.

## 9. Production notes for the storyboard
Frames to produce (all deterministic, from data): F01 hook chips; F02 board (30 tiles); F03 to F05 the three governor chips; F06 Senate poll bars with portraits; F07 debate card (quote cards only from the attributed sentence in F-14); F08 Vindman line; F09 map with pins; F10 Trump split bars; F11 result bars; F12 six-slot TIP strip; F13 end card with credits. Credits: Old Florida State Capitol photo by DXR (CC BY-SA 4.0); portraits public domain (U.S. Senate Photography Service, Florida House of Representatives, U.S. Congress, House Creative Services and others as listed in `fl_assets.csv`). Narration disclosure on the end card: "Narration is synthetic." Music license: Artlist, personal-use terms to be re-read for brand use before publishing.
