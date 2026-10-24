---
name: llf-article-format
description: Apply LookLearnFind's approved election article schemas (State of the Race, Delta, Spending, Dark Horse vs party, Dark Horse vs AIPAC/UDP-supported, AIPAC-supported candidates still running) and the state and race guide modules, with voice rules and TIP integration. Use when drafting or reviewing any LLF election article.
---

# llf-article-format

**Version** 1.3.0 · **Owner** LLF editorial (ChatGPT drafts, Claude Code checks fit) · **Type** instruction skill. It carries no script; the checks are `llf-factcheck-finalize` and `llf-publication-qa`.

## Canonical schema pages
`docs/schemas/01_STATE_OF_THE_RACE.md` · `02_DELTA_REPORT.md` · `03_SPENDING_REPORT.md` · `04_DARK_HORSE_PARTY.md` · `05_DARK_HORSE_AIPAC.md` · `06_AIPAC_CANDIDATES_STILL_RUNNING.md` · `07_STATE_AND_RACE_ARTICLE_REQUIREMENTS.md` (the guide and race modules). The index is `docs/election-build/INDEX.md`. Do not create a second schema: map every article to one of these.

## Lean standard (owner reset 2026-10-24)
Story first, proof enough. A finance table, market chart or poll is included only if the story uses it; FEC fields are optional everywhere, and a reported spending figure is cited and attributed to the original report, never presented as audited. Embed one to three useful graphics and the TIP deep links. Headline: a real tension or a surprising, sourced observation; attribute opinion; cite the original reporting.

## Audit additions (2026-10-24)
- **Headline test.** Every word of the headline must be supported by a ledger row, and "tightens", "surges", "slips" need a same-source comparison (same pollster, same question). If the comparison rests on one report, the body says so.
- **Figures-as-of line.** Time-sensitive articles state the as-of date in the body and the dek avoids numbers that will be stale within a week.
- **Update cadence.** Race articles are re-checked with `tools/qa/freshness_check.py` before publishing, then on Oct 31 and Nov 2 (and any day a newer poll appears in the feed). A change is logged in `<!--corrections-->` with the date.
- **Image kit per article.** Hero (credited), OG image (1200x630) via the front-matter `og:` key, one 4:5 social card per hook, TIP grade card; made by `tools/social/render_cards.py` from the same data the page uses.
- **Alt text and captions.** Every chart is an SVG with `role="img"` and a plain-language `aria-label`; every figure has a caption with source, date and what the number is not.
- **Neutral color.** Do not code candidates by party color in charts; label with name and party letter.

## After the articles
When a state's articles are DRAFTED, `llf-video-storyboard` turns their claims into the video pack. Keep each article's claims file: it is the only source of facts for the video.

## Rules every article follows
Scope: Governor, U.S. Senate, U.S. House. Neutral reporting: no win probabilities, no causal claims about spending or price moves, no rankings or endorsements. R1: first mention of a featured candidate links to their TIP profile. R2: every mentioned race links to that race. TIP shows six issues; "not graded" is never zero; a grade is cited only from the profile that shows it. Numbers come from `[[v:name]]` macros where data exists; sources are `[[s:n]]`. Style: no Oxford comma.

## Input and output
Input: the schema page and the exchange pair `STORY_BRIEF.md` (from the Research agent, see `llf-story-scout`) and, going back, `CLAIMS.csv`. The state packet and its 14 files are supplementary references only. Output: `content/learn/<slug>.html` with front matter `layout: report` and the blocks `<!--openfile-->`, `<!--sources-->`, `<!--corrections-->`.

## Fixtures and QA gate
Existing reports (`florida-governor-fundraising-polling-2026`, `florida-house-independent-spending-october-2026`, `michigan-senate-delta-october-2026`) are the reference fixtures. Gate: `python3 build.py --strict` and `tools/qa/factcheck_gate.py`.

## Failure semantics
A draft that needs a figure the brief does not contain stops with the gap named; it is never filled from memory.

## Changelog
1.3.0 (2026-10-24) pointer to the video skill. 1.2.0 (2026-10-24) audit additions: headline test, as-of line, update cadence, image kit, alt text, neutral color. 1.1.0 (2026-10-24) lean standard; finance optional; brief and claims exchange. 1.0.0 (2026-10-23) first version; schemas imported from the Round 1 package into `docs/schemas/`.
