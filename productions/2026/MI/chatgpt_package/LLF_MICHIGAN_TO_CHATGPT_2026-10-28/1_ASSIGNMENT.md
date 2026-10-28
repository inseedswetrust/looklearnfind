# Assignment

## Write MI-A1 now; MI-A2 only if confirmed
| ID | Working title | Type (schema) | Target length |
|---|---|---|---|
| MI-A1 | The independent who left: Duggan is off the ballot but still has a market price | Reported Feature (`07_STATE_AND_RACE_ARTICLE_REQUIREMENTS`) | 700 to 1,000 words |
| MI-A2 | Senate: a two-point poll and a 69-cent contract, side by side | Delta Report (`02_DELTA_REPORT`) with a poll comparison | **ON HOLD**: overlaps a live piece, see the warning at the top of its brief; write only if the owner confirms |

Use the facts and the sources in each `STORY_BRIEF.md`. Every factual sentence must trace to a row in that story's `CLAIMS.csv`. If you want to use a fact that is not in the claims, add it as a new row with its source and mark it `NEW`; Claude Code will open the source.

## Hard rules (owner's, in force for all LLF content)
1. **No Oxford comma.** "first, second and third."
2. **Neutral.** No win probabilities, no forecasts, no rankings, no endorsements, no causal claims ("because", "led to", "drove") linking spending, polls or markets to results. A market price is not a forecast. A poll is not a vote share.
3. **Attribute every number** to its source and date. Never call a figure audited or official unless the source is the official record.
4. **Grades:** none of these two stories uses a TIP grade. Do not cite one. "Not graded" is never zero.
5. **Links (enforced by the build):** the first mention of each named candidate links to their TIP profile (URLs in `5_DATA/LINK_MAP.md`); the first mention of the Senate race and the governor race links to the race. Do not invent URLs.
6. **Kalshi:** name the exact contract, the side (last, bid or ask) and the UTC timestamp. Do not state a price as current without that timestamp. The capture is 2026-10-28 20:21 UTC.
7. **No fact-checking your own draft.** Claude Code and the owner check it separately. Flag doubts instead of resolving them by assumption.
8. **Do not repeat** the money delta piece or the Kalshi El-Sayed delta piece (both live; see `4_VOICE_SAMPLES/`). MI-A2 should link to them, not restate them.
9. **Do not use** anything in `6_OPEN_ITEMS.md` as a fact. Where the answer is unknown, say "we could not find" or "the page does not say".
10. Images: the site uses AI illustrations for heroes with a disclosure credit. Do not describe a hero as a photograph. Do not ask for AI portraits of real candidates.

## Front matter for the draft (Claude Code will finalize)
```
kind: story
layout: report
title: ...
dek: ...
date: 2026-10-29        (leave; Claude Code sets the publish date)
category: politics
format: Reported Feature        (MI-A1)   |   Delta Report  (MI-A2)
topics: politics,candidates
hero: (leave blank; hero images are a separate brief)
```
Use `[[s:1]]`, `[[s:2]]` ... style source markers only if you have seen them in `4_VOICE_SAMPLES/`; otherwise write sources as a numbered list at the end and Claude Code will convert them.

## Do not
- Publish, post or send anything.
- Draft MI-A3 or MI-A4.
- Change the ready/not-ready status of an angle.
