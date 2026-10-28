# Michigan: UDP spending around the AIPAC announcement (story brief)

Lane `production:mi-2026`. Written 2026-10-28 from ChatGPT's editorial brief plus LLF's own FEC check. Draft not started. Scope: U.S. Senate (Michigan).

## What the story is
On October 21, 2026 AIPAC said it would stop endorsements, direct PAC contributions and earmarked fundraising, and that its super PAC, the United Democracy Project (UDP, C00799031), would keep operating. The reportable question is narrow and factual: what do UDP's filings show it spent against Abdul El-Sayed (D) in the Michigan Senate race on and around that date, and what is still unknown.

It is not "AIPAC secretly spent $9.4 million after announcing a change." The announcement was forward-looking and said UDP would continue.

## Working headline (neutral)
"What AIPAC said it would stop, what it kept and what UDP's filings show" (alternate: "UDP's October filings in the Michigan Senate race"). Not "Kept Spending": it implies a contradiction the announcement did not make.

## Verified by LLF on 2026-10-28 (FEC Schedule E, committee C00799031, opposing El-Sayed)
| Date | Amount | Payee | What |
| --- | --- | --- | --- |
| Oct 7 | $94,620.36 | Riviera LLC | direct mail |
| Oct 13 | $94,620.36 | Riviera LLC | direct mail |
| Oct 15 | $94,620.36 | Riviera LLC | direct mail |
| Oct 19 | $94,620.36 | Riviera LLC | direct mail |
| Oct 21 | $94,620.36 | Riviera LLC | direct mail (filed Oct 22) |
| Oct 21 | $20,202.00 | Apex Strategies LLC | text messaging (filed Oct 22) |
| Oct 23 | $94,620.36 | Riviera LLC | direct mail (filed Oct 23) |

- On or after Oct 21: $209,442.72. Before: $378,481.44 (four mailers). Seven expenditures from Oct 7 to Oct 23 total $587,924.16.
- ChatGPT's brief lists the series from Oct 13; our October 23 capture shows an Oct 7 mailer too. ChatGPT's "$493,303.80 across six" is correct for what it counted and is a subset.
- FEC rows carry dates, not times. We cannot say whether Oct 21 spending came before or after the announcement. Say so.
- The mailers' content is not in the filings. Describe them as "direct mail opposing El-Sayed", nothing more.

## Not verified yet
- **The $398,684 delta** ($53,603,927 to about $54,002,611). Two trackers, two cutoffs, one unnamed. Rebuilding it from FEC rows needs the full Schedule E pull (1,265 rows for UDP in the 2026 cycle). The public DEMO_KEY rate limit stopped the pull at row 700. Needs an OpenFEC key from the owner (free at api.data.gov; never stored in the repo) or a pause until the limit resets. Until rebuilt, the delta is attributed ("a tracker reported") or left out. The $209,442.72 stands without it.
- **The $9 million for Great Lakes Conservatives Fund** (Washington Post, per the brief). Not read by us; not in the FEC data we hold. Keep it separate from independent expenditures and never add it to anything. Read the Post story and the recipient committee's filings before writing about it.
- **AIPAC's announcement** (Jewish Insider, NPR/OPB). The drafter must read the originals. The "$90 million" figure is the organization's claim about member giving, not an FEC total.

## Context LLF holds (our capture, deduped Schedule E through the Oct 21 filings)
UDP opposing El-Sayed about $20.1 million and supporting Haley Stevens about $10.5 million. These are LLF computations that include adjustments; label them so. Do not conflate with the Post's "$30 million AIPAC-linked" figure.

## Structure
1. What AIPAC said it would stop and what it said would continue (two sentences, attributed).
2. What the filings show: the table above, with the date-not-time limit.
3. The two numbers we cannot yet stand behind: the tracker delta and the $9 million, each labelled with why.
4. The kinds of money (UDP independent expenditures, transfers to other committees, the recipient's own spending, individual giving) and what each FEC record can and cannot show.
5. What we will do next.

## Rules for this piece
- Linking: first mention of Abdul El-Sayed and Mike Rogers links to their TIP profiles; the Michigan Senate race links to its TIP race page. Both profiles exist in our Michigan data.
- No motive claims ("less recognizable to voters" is speculation unless a named person says it, attributed). No causal claims about spending and results. No win probabilities.
- Do not add $9 million to $398,684 or to any FEC total. Do not add independent expenditures, contributions to other committees and total disbursements.
- UDP "AIPAC-aligned" is the outlets' description; the filings show a committee name and ID.
- The drafter does not fact-check their own article. Owner fact-checks. Nothing published without approval.

## Open items
1. Owner decision 2026-10-28: no OpenFEC key will be provided. The $398,684 delta is not rebuilt; the draft either attributes it to the trackers that reported it (with their different cutoffs) or leaves it out. The $209,442.72 and the Oct 7 to 23 table stand on FEC rows. (The fetch tool, `tools/dark_horse/fetch_udp_ie.py`, reads FEC_API_KEY at run time; no key is stored in the repo.)
2. Read the Washington Post, Jewish Insider and NPR/OPB originals.
3. Links to use (from `data/elections/MI/candidates.json`): El-Sayed https://theissuesparty.org/candidates/S6MI00418, Rogers https://theissuesparty.org/candidates/S4MI00595, race https://theissuesparty.org/races/2026-S-MI (confirm the race page returns 200 before publishing).
