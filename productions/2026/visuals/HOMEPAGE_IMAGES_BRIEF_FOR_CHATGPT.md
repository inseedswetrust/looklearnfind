# Homepage image brief for ChatGPT (LookLearnFind, 2026-10-28)

Paste everything below the line into ChatGPT. It continues the same four-hero system (IL-07 stoop, IL Senate trays, IL-04 clipboards, MI kitchen table).

---

You are art director and image maker for LookLearnFind, a reported-journalism site on U.S. midterm elections. Make **three** new illustrated images for the homepage. They sit beside four heroes you already made (a stone stoop with mailers at dawn, three wooden trays with a ledger, clipboards on a teal table, mail and a phone on a kitchen table at dusk). Match that look exactly: photographic, shallow depth of field, warm natural light, muted teal and amber palette, no people, calm and observational.

## Deliverables
| ID | Use | Scene | Master | Web | Social |
|---|---|---|---|---|---|
| S1 | "The state files" tile: Florida | A county elections office counter in morning light, blank stickers on a roll, a pen and a stack of unmarked envelopes, louvered window shutters behind, soft green leaf shadows on the wall | 3600x2400 JPEG q90 | 1800x1200 JPEG q80, 350 KB or less | 1200x630 centered crop |
| S2 | "The state files" tile: Illinois | A folding table in a brick church hall in winter light: blank sign-in sheets, a cup of pencils, a steel thermos, a radiator under a frosted window | same | same | same |
| S3 | Homepage social card (og:image) for the "Election 2026 reporting" block | A long wooden desk seen from slightly above with four small stacks: letters, a ledger, a clipboard and a folded map with no readable detail, arranged left to right with even gaps | 2400x1260 JPEG q90 | 1200x630 JPEG q80 | none |

All three: sRGB, 4:2:0, progressive JPEG. Generate at the largest size the tool allows, then resample with Lanczos and say so. Do not invent native resolution.

## Composition rules
- Subject sits in the central 70 percent width and 78 percent height. The page crops these at 3:2, 4:3, 1.91:1 and 1.2:1, so nothing important may touch an edge.
- Keep the bottom-left and bottom-right 22 percent of S1 and S2 quiet (defocused surface, no objects). The site places a credit chip bottom-right and a caption card bottom-left.
- S3 is cropped hard to 1.91:1: keep all four stacks within the central 60 percent of the height.
- Eye-level to slightly high camera. 35 to 50 mm look. Aperture around f/2.8. Natural light only.

## Hard rules (a miss on any one is a reject)
1. No faces, hands, silhouettes or people of any kind.
2. No readable text, numerals, letters, logos or signatures anywhere. Paper has blank surfaces or indistinct non-letter rules. Stickers are blank.
3. No campaign branding: no flags, party colors used as signals, slogans, buttons, yard signs or stars and stripes.
4. No numbers, charts, cash, dollar signs, maps with labels or measured ratios.
5. These are invented scenes, not evidence about any real place, person or event. They will carry the credit "AI illustration. Not a photograph of a real place or event." Do not imitate a specific real building, office or landmark.
6. No clichés: no ballot-box-with-flag, no hand dropping a ballot, no capitol dome, no eagle, no gavel, no voting booth silhouettes, no "I Voted" sticker, no handshake, no megaphone.

## Copy deck (the page adds text in HTML; do not paint it into the art)
| ID | Kicker (28 characters max) | Caption (110 max) | Alt text (125 max) |
|---|---|---|---|
| S1 | Florida | Governor, U.S. Senate and 28 House races, with the money and the record. | A roll of blank stickers, a pen and unmarked envelopes on a counter beside louvered shutters in morning light. |
| S2 | Illinois | Governor, U.S. Senate and 17 House races, with the primary money and the ballot rules. | A folding table in a brick hall holds blank sign-in sheets, a cup of pencils and a thermos beside a radiator. |
| S3 | Election 2026 reporting | What the filings and the ballots show, and what they do not. | Four small stacks of letters, a ledger, a clipboard and a folded map on a long wooden desk. |

Copywriting check: no Oxford commas, no hype words, no verbs that imply cause or a forecast. If you change a line, keep it under the limits and tell me what you changed.

## What to return in one ZIP
- masters/, web/, social/ folders (named s1-florida, s2-illinois, s3-election-card)
- originals/ untouched generator files
- prompts/ with the exact prompt for each image
- manifest.json (size, bytes, focal point as percentages, quiet-zone check) and a README with a pass or fail line for each of the six hard rules per image. State honestly anything you could not verify.
