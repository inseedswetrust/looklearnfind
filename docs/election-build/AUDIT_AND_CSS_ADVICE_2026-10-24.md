# Audit, design notes and CSS advice (2026-10-24)

Written as an outside auditor would: look for what is missing, say what was fixed and what was not. "Applied" means it is in the repository and the strict build passes; "Recommended" means it is not done.

## A. Gaps found in the process documents and skills
| # | Gap | Action | Status |
|---|---|---|---|
| 1 | Skills still required finance data and a 14-file packet after the lean reset | `llf-factcheck-finalize` 2.1.0, `llf-article-format` 1.2.0, `llf-publication-qa` 1.2.0, `election-state-packet` 1.0.1 (optional); old handoff and skills proposal marked SUPERSEDED | Applied |
| 2 | No rule for who checks a draft the same session wrote | Independence rule (R5) in `PUBLISHING_RULES.md` and the fact-check skill; both Florida articles are held at DRAFTED in the story board until a different reader signs `reviewer` | Applied; **review itself still needed** |
| 3 | Time-sensitive numbers had no refresh rule; the governor article had "82¢" typed while the capture read 83¢ | `tools/qa/freshness_check.py` (+2 tests); R7 (check before publishing, Oct 31, Nov 2); governor article now reads the market value from data | Applied |
| 4 | "Tightens" style headlines need a same-source comparison | Headline test and single-source disclosure added to `llf-article-format`; the Senate article states that the July +8 rests on one report | Applied |
| 5 | New articles were not linked from the guide pages, so readers of `/elections/2026/florida/` could not find them | "Latest reporting" band on the state landing, Senate and House pages | Applied |
| 6 | No per-article OG image (every report used the generic Learn image) and JSON-LD had no `image` | `og:` front-matter key wired through `render_report`; six images from `tools/social/render_cards.py`; JSON-LD gets `image` and `mainEntityOfPage` | Applied |
| 7 | Charts had no accessible names | every new chart is `role="img"` with a sentence-long `aria-label` and a captioned source | Applied |
| 8 | Windows tooling traps: leading `/` rewritten by Git Bash, a stale local server holding `dist/` | noted in `llf-publication-qa`; the server must be stopped before `build.py` | Applied (documented) |
| 9 | No skill for the video, the next project | not warranted until the concept is approved; concept and fact sheet are in `docs/video/FLORIDA_VIDEO_CONCEPT.md`. Recommend a `llf-video-script` skill after the first video ships, once the real edit steps are known | Recommended |
| 10 | No analytics events, so LLF-to-TIP click-through (a stated goal) cannot be measured | Recommend one custom event on every `a[href^="https://theissuesparty.org"]` click and one on the share-image downloads; no new service | Recommended |
| 11 | The packet and daily collector are not tied to the story board | story entities link to briefs, claims, candidates, race, images and (later) article and social | Applied |
| 12 | `docs` accumulate superseded files | each superseded file now carries a banner; `INDEX.md` is the canonical map | Applied |

## B. Content audit of the two articles (what an auditor will ask)
- **Every central claim has a ledger row** (`docs/story-briefs/CLAIMS_ARTICLE_FL_SENATE.csv`, `..._HOUSE.csv`); the gate returns READY including typed checks on the TIP grades and Kalshi tickets against the packet. READY is not approval.
- **Weakest points, stated in the articles:** the July +8 (one outlet); the three primary shares (one outlet, framing is the author's); the 21-of-28 count and the Trump margins (reporters' figures, WUSF attributes the count to the News Service of Florida, LLF did not recompute); Newsweek's September poll listing (undated page, pollsters' releases unopened).
- **Left out on purpose:** the Hope Florida grand jury findings, the Cherfilus-McCormick indictment, the characterization of Bilzerian's rhetoric, every AIPAC and UDP claim, every outside-spending total, any win probability.
- **Not verified in this pass:** the Division of Elections vote counts; UNF's own release (sponsor not named in either report); the Leon County plaintiff.
- **Kalshi cards** show candidate names as labels on party-winner contracts; the surrounding text says so, but a reader who skips it could misread them as candidate odds. Applied: the card now says "Party-winner contracts: each resolves on the winning party and the name shown is only a label."
- **The candidate cards still print FEC receipts** (an existing component). That is accurate and dated on the card, but the lean standard makes it optional; Applied: `candidate_card(..., finance=False)` is used for the Florida Senate and House articles.

## C. CSS advice (applied in `static/css/elections.css` unless marked)
1. **Keyboard focus:** a 3 px yellow outline with offset for body links, `.btn-o`, the on-page contents and race links. Applied.
2. **Reduced motion:** `prefers-reduced-motion` turns off transitions and animation. Applied.
3. **Type floor:** labels and footnote chips were 9 to 10 px; raised to 10.5 to 12 px. Applied.
4. **Links in body copy** underline (not color alone); footnote chips stay un-underlined. Applied.
5. **Tables:** `.num` right-aligned with tabular figures; scroll container with a 520 px minimum so the September poll table never squashes on a phone. Applied.
6. **Charts:** SVG text classes (`.rl .rv .rn`) with the site tokens; inverted labels for bars; the map pins are 24 px circles with leader lines so districts 20 and 25 (side by side on the coast) do not overlap. Applied.
7. **Phones at 400 px or less:** the stat row goes to one column, the six-slot issue strip to three columns, the side padding to 16 px. Applied.
8. **Race links** do not wrap mid-name (`white-space: nowrap`). Applied. Plain-text "FL-14" can still break at the hyphen; Recommended: wrap in `<span class="nb">` in prose or use a non-breaking hyphen.
9. **Print:** hides the rail, contents, nav and footer, prints URLs after links. Applied.
10. **Tap targets:** the screenshot check reports 19 to 20 targets under 24 px on every page. They are site-wide (nav and footer links), not from these articles. Recommended: raise `nav a` and footer link padding to a 24 px minimum height in `site.css`.
11. **Hero and portraits:** `loading="lazy"` on portraits above the fold makes first paint show empty boxes in full-page captures and hurts LCP. Recommended: `loading="eager"` for the first four portraits and explicit `width`/`height` on the hero image to prevent layout shift.
12. **Fonts:** the serif stack falls back to Georgia if Newsreader fails; the share-image renderer uses Georgia. Recommended: embed Newsreader in the renderer for exact brand parity (or accept Georgia for social).
13. **Color:** charts avoid party color on purpose (ink and teal only, with names and party letters). Keep it.
14. **Dark mode:** not supported site-wide; do not add it for these pages alone.

## D. Design notes (what the pages do)
Order: open-file box (question, what we checked, what the sources support, other views, what is open) → "race at a glance" with four stat chips → the poll or the map with its chart → what the other measurements say (market card) → candidate cards with TIP grades → what we do not know → numbered sources → corrections. Rail: contents, race on TIP, latest poll or the five-district list. Visual rule: every number has its source and date within one screen, every chart says what it does not show. Share kit: OG 1200 x 630 per article; 4:5 cards for the Senate poll, Senate TIP grades, House map and House TIP grades (`static/img/elections/social/`).

## E. Still needed from a person
Independent reader for both ledgers; Division of Elections counts for the three primaries and the Senate primary; the owner's upload of the release zip; the first unattended run of the daily collector (12:00 UTC today) to be observed.
