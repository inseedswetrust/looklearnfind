# LookLearnFind × The Issues Party: knowledge package for ChatGPT (Michigan 2026)

Package version `MI-2026-10-28-v1`. Built by Claude Code from the project repository (the repository is the source of truth; this is a portable copy). If anything here conflicts with a later message from the owner, the owner wins; if a file here conflicts with another file here, the one in `02_STANDARDS/` wins.

## 1. The project in six lines
- **LookLearnFind (LLF)**, looklearnfind.com: reported-journalism site. Long-form pieces with numbered sources, plus election "State of the Race" pages.
- **The Issues Party (TIP)**, theissuesparty.org: candidate profiles, races and six issue grades. LLF links to TIP.
- **Scope of the election work:** Governor, U.S. Senate and U.S. House only, 2026. Nothing about ballot measures, the legislature, judges or other offices.
- **Who does what.** *You (ChatGPT)*: write articles, direct and generate images, develop video scripts and storyboards. *Claude Code*: researches, builds the roster and pages, extracts TIP data, fact-checks (never the drafter), builds and publishes. *The owner*: approves everything that is published, deployed or written to a production database, and runs Midjourney and Premiere.
- **Nothing is published by you or without the owner's explicit approval.** Approval for one thing does not carry over to the next.
- **Tone:** plain, specific, neutral, source-linked, willing to say what is not known.

## 2. Where things stand (details in `01_WORKFLOW/STATE_STATUS.md`)
Florida and Illinois are live (state pages plus reported pieces). Michigan: the money delta piece and a Kalshi Senate delta piece are live; the Michigan roster, TIP profiles, portraits, markets and all state pages (hub, governor, Senate, House directory, 13 districts) are built but **not yet live**; nothing is fact-checked beyond Claude's own source checks; no Michigan video work has started.

## 3. What to do first
| # | Task | Brief | Return |
|---|---|---|---|
| 1 | Draft article **MI-A1** (governor: the independent who left; Reported Feature, 700 to 1,000 words) | `05_MICHIGAN/stories/MI-A1/STORY_BRIEF.md` and `CLAIMS.csv` | `07_RETURN_TEMPLATES/ARTICLE_RETURN.md` format |
| 2 | Hero image for MI-A1 (one image, AI illustration) | `04_VISUALS/MI_A1_HERO_BRIEF.md` | PNG or JPEG plus alt text and caption lines |
| 3 | Michigan state tile for the homepage ("The state files") | `04_VISUALS/MICHIGAN_HERO_BRIEF_FOR_CHATGPT.md` | masters, web and social exports as the brief says |

**Not yet assigned:** MI-A2 (Senate poll beside the market) is withdrawn because a live LLF piece already covers it. MI-A3 (MI-13) and MI-A4 (MI-10 outside spending) are being researched by Claude and will come in a later package; see `05_MICHIGAN/stories/MI-A3_A4_RESEARCH_NOTES.md`. **Video:** do not start. The video lane opens only after articles are fact-checked and the owner approves a script direction (`01_WORKFLOW/`).

## 4. Folder map
| Folder | Contents |
|---|---|
| `01_WORKFLOW/` | The production workflow and stage gates (Production Lock v2.0), agent map, the video contract, decision log and `STATE_STATUS.md` (what is live, local, open, per state) |
| `02_STANDARDS/` | House rules (one page), publishing rules R1 and R2, brand and voice guide, the seven article schemas, the six TIP issue definitions and the working skill files as plain markdown (article format, delta editorial, story scout, fact-check, video director) |
| `03_EXAMPLES/` | Brief-to-published examples: Illinois briefs with their claims files and the seven live pieces in their published source form (front matter, blocks and markers) |
| `04_VISUALS/` | Image briefs already used (Illinois and Michigan heroes, homepage tiles), the two new Michigan briefs, hero credits and `reference_images/` (the existing images; match them) |
| `05_MICHIGAN/` | The Michigan data: stories, roster, TIP extract, Kalshi capture, the official Department of State listing, link map |
| `06_OPEN_ITEMS.md` | What is unknown, withdrawn, blocked or pending an owner decision |
| `07_RETURN_TEMPLATES/` | The exact formats for returning an article, a claims file, a hero and a data request |
| `manifest.json` | Every file with size and SHA-256, plus the commit it was built from |

## 5. How the article pipeline works (so you can plan)
1. Claude Code produces `STORY_BRIEF.md` and `CLAIMS.csv` from sources it actually opened (this package contains them).
2. **You** draft the article from the brief and the matching schema, in the voice of the examples. Every factual sentence must trace to a claims row. New facts go in as new rows marked `NEW`; Claude opens the source.
3. An independent reviewer (not you, not the drafter) fact-checks every used claim. Failures are fixed or the sentence is cut.
4. Claude Code builds it into the site (`[[s:n]]` source markers, `[[v:name]]` value macros, the hero, TIP links), runs the strict build and automated checks.
5. The owner approves. Only then is it published.

The `llf-article-format` skill file in `02_STANDARDS/skills/` is the checklist for step 2. The six reports in `03_EXAMPLES/published_pieces/` are the model for the final shape.

## 6. Hard rules (full text: `02_STANDARDS/HOUSE_RULES_ONE_PAGE.md`)
No Oxford comma. Neutral reporting: no win probabilities, no forecasts, no causal claims about spending, polls or markets, no rankings, no endorsements. Every number attributed with date and unit. "Not graded" is never zero. First mention of each candidate links to their TIP profile; first mention of each race links to the race. A Kalshi price is a quotation with an exact contract and UTC timestamp, never a forecast. No faces or people in generated images, no readable text in images, no AI portraits of real candidates, no synthetic footage of real people or events; every AI visual is disclosed.

## 7. How to ask Claude for something
Do not research from memory and do not guess. If you need a fact, a source opened, an FEC pull, a TIP lookup or a file, write it in `07_RETURN_TEMPLATES/DATA_REQUEST.md` format and keep drafting around the gap. The owner passes requests to Claude Code, which has the repository and the disk.
