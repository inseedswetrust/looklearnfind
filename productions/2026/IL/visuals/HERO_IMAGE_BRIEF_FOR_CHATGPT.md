# Prompt for ChatGPT: hero images for the Illinois and Michigan reported features

Attach before sending: `docs/BRAND.md`, one of the existing hero photos (`static/img/elections/il-capitol.jpg`) for tone, and `reference/homepage/assets/overlap-hero.png` and the six reference photos named in `docs/CHATGPT_ASSET_PROMPT.md`.

---

You are the creative director and copy lead for **LookLearnFind** (LLF), an editorial site that shows its sources. Make **four hero images** (plus one optional) for four reported features about money in 2026 elections, and write the on-page copy that sits on them. Treat this as an art-direction brief: deliver finished images, the exact prompts you used and a copy deck.

## 1. What is being made and where it goes

The pages already exist or are in draft. The Illinois governor, Senate, House and district pages need **no new art** (they use public-domain or licensed photographs and a district map). Only the reported features need heroes.

| ID | File | Feature | Subject of the piece |
| --- | --- | --- | --- |
| H1 | `il-ford.jpg` | Illinois 7th District | Outside spending in the primary for Danny Davis's seat and how it ended |
| H2 | `il-stratton.jpg` | Illinois U.S. Senate | Three different kinds of money in a Senate primary |
| H3 | `il-garcia.jpg` | Illinois 4th District | How the ballot was set: 697 signatures to run in a Democratic primary, 10,816 as an independent |
| H4 | `mi-udp.jpg` | Michigan U.S. Senate | What one super PAC's filings show around an October announcement |
| H5 (optional) | `og-illinois-state-of-the-race.jpg` | Illinois hub share card | General Illinois election art |

## 2. Hard rules (any breach fails the image)

1. **No faces and no real people.** No candidates, no politicians, no lookalikes, no crowds with readable faces. Hands are allowed only if anatomically perfect; prefer none. Real candidate portraits will be real, licensed photographs used elsewhere on the page; never generate or imply one.
2. **No readable text anywhere in the image.** No signs, ballots, mailers, screens, license plates or logos. Anything that would carry text must be blurred, turned away, out of frame or abstract shapes. LLF adds every word in HTML. **No fonts are used in the artwork.**
3. **No campaign branding, party symbols, flags or slogans.** No party colors used as signals (no red/blue pairing).
4. **No numbers or data in the art.** The page shows the figures. Do not draw bars, stacks sized to a real ratio, dollar signs, money piles or cash. Nothing should read as a chart.
5. **Illustrative, not evidentiary.** These are labeled AI illustrations of a concept. They must not look like documentary photos of a real event, a real mailer, a real office or a real person's property.
6. **No clichés from the brand's avoid list:** magnifying glasses, detective boards, fake newspaper clippings, neon gradients, glossy corporate stock, generic AI-tech imagery, scales of justice, ballot-box icons, eagles.

## 3. Look and feel

- **Genre:** illustrative concept photography. Candid, lived-in, specific. Natural light, material texture, subtle film grain, shallow depth of field. 35 mm look, f/2.8, eye-level or slightly low.
- **Mood:** calm, observant, slightly quiet. A place where a civic thing is about to happen or has just happened. Never ominous, never sinister, never partisan, never glib. The pieces are about money and ballots; the image should invite a reader to look closer, not tell them what to conclude.
- **Palette** (match site tokens): warm ivory paper `#F5F2EB` and `#FFFDF8`, ink `#1C1D1B`, petrol teal `#145B5D` (dark `#0F4145`) as the dominant cool accent, warm gray `#EEE9DF`, and **one** small yellow `#DFCA00` accent object per image at most (a pencil, a sticky tab, a dry-erase marker cap). Keep saturation low. Autumn light (late October).
- **Variety across the four:** different rooms, different light, different camera distance, so a reader seeing two on the Politics page does not think they are a set of clones.

## 4. Technical specs

- **Master:** 3600 × 2400 px (3:2), sRGB, JPEG quality 90. **Also deliver** a 1800 × 1200 export at quality 80 (target 350 KB or less; the site recompresses).
- **Display:** the site shows the image inside a bordered panel, cropped with `object-fit: cover` between about 1.2:1 and 2:1 depending on screen width. Keep everything important inside the **central 70 % × 70 %**.
- **Overlay quiet zones (keep low-detail, mid-to-dark tones, no focal objects):**
  - **Bottom-left 70 % wide × 28 % tall:** a cream caption card covers this on desktop.
  - **Bottom-right 55 % wide × 8 % tall:** a small white credit line is printed here. Keep it darker than the rest.
- **Social crop:** a **1200 × 630** (1.91:1) crop will also be taken from the centre. The focal subject must survive a crop to the **central 78 % of the height** at full width. State the focal point in the manifest.
- **Mobile:** the image is shown at roughly 4:3 with the caption below; the centre-weighted composition must still read at 390 px wide.
- **Delivery:** one file per image, named as in the table, no embedded watermark, no C2PA-stripping tricks, no signature.

## 5. The four concepts

**H1 `il-ford.jpg` : Illinois 7th District (Chicago's West Side and western suburbs).**
Concept: *the weight of paper that arrives at a front door.* A quiet block of brick and greystone two-flats at first light, seen from across the street at a slight low angle; on the nearest front step, an untidy stack of glossy unmarked mailers (blank backs, no print) held by a rubber band beside a closed front door with a brass mail slot. Fall leaves on the sidewalk, one bare tree. Teal door, ivory stone, ink-dark shadows. No signs. Focal point: the stack on the step, right of centre. Lower left: sidewalk and shadow (quiet). Do not show a specific real address or landmark.

**H2 `il-stratton.jpg` : Illinois U.S. Senate, three kinds of money.**
Concept: *three different kinds of paper on one counter.* A long, worn wooden counter in a county clerk or election office, mid-morning window light: three separate, clearly distinct trays or document boxes in a row, each holding a different material (bound ledger pages, glossy folded mailers, a thin pile of printed receipts), all blank and unreadable. Blurred filing shelves behind. The row is evenly lit, deliberately not a ranked or ascending arrangement (no staircase, no tallest-to-shortest). Focal point: the middle tray. Yellow accent: a pencil laid across the counter.

**H3 `il-garcia.jpg` : Illinois 4th District, how the ballot was set.**
Concept: *a petition table in a storefront.* A folding table in a Southwest Side storefront window (Chicago bungalow-belt street outside, softly out of focus), with two stacks of clipboarded petition sheets: one thin, one noticeably taller, both with illegible scribbled lines. Late-afternoon side light through the window, a thermos and a pen. No people. The size difference of the stacks should be gentle and natural, not a diagram, and must not be the picture's only idea (the room and light carry it). Focal point: between the stacks, slightly left of centre.

**H4 `mi-udp.jpg` : Michigan U.S. Senate, one committee's filings.**
Concept: *political mail and a text on an ordinary evening.* A kitchen table in an older Michigan brick bungalow, early evening, lamp on, a small stack of unopened glossy mail beside a coffee mug and a phone lying face-up with a blurred, unreadable lock-screen notification. Window behind shows maple trees in late-October colour and a dusk sky. Different light and distance from H1 (interior, warm lamp light, closer). Focal point: mail and phone, centre-right. Yellow accent: the phone case edge or a sticky note (blank).

**H5 (optional) `og-illinois-state-of-the-race.jpg` : share card.**
Concept: *a quiet polling place the morning before an election.* A school gymnasium with empty folding voting booths with the privacy curtains and privacy flaps in teal and ivory, wood floor, high windows, nobody present. No signs or flags. Keep the left third calmer for a wordmark that LLF composites.

## 6. Copy deck (copywriter pass)

The words sit in HTML on the page, **not in the art**. Typography is fixed by the site:

- **Kicker (the small label above the caption):** Arial/Helvetica sans, bold, 10 px, uppercase, letter-spacing .1 em, petrol teal `#145B5D`.
- **Caption text:** Newsreader Variable (serif; fallbacks Iowan Old Style, Baskerville, Georgia), regular, 15 px / 1.35, ink `#1C1D1B`, on a cream card at 94 % opacity.
- **Credit line:** Arial, 10 px, white with shadow over the image (on mobile it moves below in muted gray).

Write for these fields. Limits are firm because the card is small.

| Field | Limit | Notes |
| --- | --- | --- |
| Kicker (`hero_title`) | 28 characters | Place or office only |
| Caption (`hero_text`) | 110 characters | One sentence, plain, concrete |
| Alt text | 125 characters | Describe the picture; start with the subject; no "image of" |
| Credit line | 80 characters | Must say the image is an AI illustration |

**Starting drafts for you to tighten (keep facts as given; add none):**

- H1 kicker `Illinois 7th District` · caption "Who spent what in the primary for Danny Davis's seat, and how it ended." · credit "Illustration generated with AI. Not a photo of a real place."
- H2 kicker `Illinois U.S. Senate` · caption "Who paid for what in the Illinois Senate primary, and why the totals differ by source." · same credit. *(The earlier phrase "most expensive Senate primary in Illinois history" is unverified; do not use it.)*
- H3 kicker `Illinois 4th District` · caption "How the ballot was set in a district where the incumbent did not run." · same credit.
- H4 kicker `Michigan U.S. Senate` · caption "What one super PAC's filings show about the weeks around an October announcement." · same credit.

**Copy rules.** Neutral and attributed. No Oxford comma in any list. No rankings, endorsements, win probabilities or claims that spending caused a result. Do not name or characterize any candidate or committee in alt text beyond the office and place. No exclamation marks, no slogans, no banned phrases ("unlock insights", "game-changing", "both sides", "do your own research"). Voice: curious, clear, calm, concrete verbs. If a fact is needed that the table above does not give, insert a `[BRACKETED PLACEHOLDER]` and ask; do not invent figures, quotes or sources.

## 7. What to return

1. The images, named as in the table, in both sizes.
2. A manifest table: file, the exact prompt used, the tool and version, the seed if available, focal point, the confirmed quiet zones and any known flaws.
3. The copy deck table filled in (kicker, caption, alt, credit) for each image.
4. A self-check against Section 2 (one line per rule, per image) and a note of anything you could not do faithfully. If an image shows a face, legible text or a brand mark, regenerate it; do not send it with a note.

Do not add a logo, a border or a vignette. LLF adds the frame.
