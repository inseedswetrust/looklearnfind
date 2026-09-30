# Prompt for ChatGPT: art direction + copy pass for looklearnfind.com

Attach these files as style references before sending: `reference/homepage/LookLearnFind-homepage-preview.png`, `reference/homepage/assets/overlap-hero.png`, `logo-01.png`, the six photos in `reference/homepage/assets/`, and `topic-icons.svg`.

---

You are the art director and editorial copy lead for **LookLearnFind**, an editorial discovery site. **Look** = short video posts worth a second look. **Learn** = reported deep dives with numbered footnotes to original sources. **Find** = real-world people, places, guides and products that hold up. The tone is relaxed, visually engaging, extremely informed, open to other perspectives, and willing to show receipts. It is not a hot-take feed, a verdict machine, or generic lifestyle content.

Attached are the approved homepage, hero, logo, six photos and icon sheet. Match them. Do not redraw or alter the logo.

## Brand rules (apply to everything)
- **Palette:** paper `#f5f2eb`, ink `#1c1d1b`, petrol teal `#145b5d` (dark `#0f4145`), yellow `#dfca00` used sparingly as a single notation mark, warm gray `#eee9df`, rules `#c9c4b9`.
- **Type feeling:** expressive editorial serif for headlines (tight spacing) + precise small-caps-style sans for utility labels. No rounded, techy or luxury-fashion lettering.
- **Photography:** candid, lived-in, specific. People listening, making, reading, working, cooking, moving, meeting in real places. Natural window or golden light, material texture, warm ivory / ink / petrol teal, subtle film grain, shallow depth of field. Varied ages, body types and backgrounds, natural not model-perfect.
- **Never:** glossy corporate stock, magnifying glasses, fake newspaper clippings, detective boards, pseudo-scientific diagrams, generic AI-tech imagery, neon gradients, logos or brand names, **any legible text in images** (signs, documents, maps, screens must be blurred, out of frame or illegible), real public figures or recognizable politicians, distorted hands or faces, fake video frames that could pass as a real creator's clip.
- **Voice:** curious, clear, observant, calm, lightly distinctive. Concrete verbs ("Read the record", "Open the source", "Try it"). Lead with something worth noticing. Confident about what was checked, candid about what is open. Never glib about civic, health or financial topics.
- **Banned phrases:** "unlock insights", "game-changing", "we give you the truth", "both sides", "do your own research", "from signal to decision", hype, clickbait, jargon, cultish exclusivity.
- **Four categories** (Politics, Economy, Society, Everyday Life) and **twelve topics:** Politics, Candidates, Businesses, Home improvement, Self improvement, Side projects, Working out, Cooking, Supplements, Skincare, Self care, Money.

## PART A: Photographs (generate each; return a filename, the prompt you used, and alt text)
Generate at the stated size. Single subject, clear focal point, leave calm negative space in the lower third for overlaid headline text (tiles darken at the bottom). JPG quality ~80 when exported. All are *illustrative concept photography*; label them as such in the manifest.

**Homepage tiles (replace placeholders)**
1. `society-conversation.jpg`, 1200×1600 portrait. Two people of different generations talking on a city stoop or bench, one listening intently, autumn light.
2. `society-public-space.jpg`, 1200×1600 portrait. Inside a community bookshop-café, people mingling, plants, tall windows, warm practical lighting.
3. `society-common-ground.jpg`, 1600×1200. A long shared table, a mixed group mid-conversation, jars of flowers, bread, mugs; a moment of real disagreement handled warmly.
4. `politics-receipts.jpg`, 1600×1067. Over-the-shoulder of someone reading printed mailers and papers at a wooden table with coffee, notebook and pencil. All paper text illegible.
5. `economy-prices.jpg`, 1200×1600 portrait. Hands weighing vegetables on a brass scale at a market stall, paper bag, a small receipt.
6. `economy-work.jpg`, 1200×1600 portrait. Two makers reviewing a packaged product and samples at a workshop table, laptop open, shelves behind.

**Section and page banners** (all 2100×900, 7:3, focal point in the left 60%)
7. `banner-politics.jpg`: a community meeting hall as chairs are set out, morning light. 8. `banner-economy.jpg`: a shop counter at opening time. 9. `banner-society.jpg`: neighbors on a street at dusk. 10. `banner-everyday-life.jpg`: a home kitchen with a project in progress.
11. `story-tartary-maps.jpg`, 2100×900: hands carefully turning the page of a large old atlas in a reading room; map detail only as abstract engraved texture, no legible words.
12. `find-map-room.jpg`, 1600×700: a university map-library reading room, flat map cabinets, empty table, daylight.
13. `look-desk.jpg`, 1600×1067: editorial still life of index cards, pins, a pencil and a phone lying face-down on a desk. Screen dark.
14. `about-hero.jpg`, 2100×900: a shared worktable with annotated printouts, a cup, hands pointing at one detail (no legible text). (For real people on the About page we will use real photographs; do not generate team portraits.)

**Topic cards** (12 images, 1200×675, named `topic-<slug>.jpg`, slugs: politics, candidates, businesses, home-improvement, self-improvement, side-projects, working-out, cooking, supplements, skincare, self-care, money). One quiet, specific, human moment per topic; no product branding; supplements and skincare show labels only as blurred shapes.

**Find type headers** (5 images, 1200×675): `find-candidates.jpg`, `find-businesses.jpg`, `find-guides.jpg`, `find-products.jpg`, `find-places.jpg`.

**Hero variants.** If you can edit the attached hero, return: `overlap-hero-textless.jpg` (2400×845, identical art with the words "where signal meets source" and "SOURCE 01" removed) and `overlap-hero-mobile.jpg` (1080×1350 portrait, art-directed crop keeping both faces and the yellow overlap). If you cannot edit it faithfully, say so instead of approximating.

**Social/share:** `og-default.jpg`, `og-look.jpg`, `og-learn.jpg`, `og-find.jpg` (1200×630). Use the hero art or a matching photo, leaving the lower-left clear for the wordmark, which we will composite ourselves.

## PART B: Vector assets (return SVG code in code blocks, one per file)
Extend the attached icon family exactly: 64×64 viewBox, ~2.2 rounded strokes in `currentColor`, **one** yellow `#dfca00` dot, no enclosing badge.
- Categories: `cat-politics.svg`, `cat-economy.svg`, `cat-society.svg`, `cat-everyday-life.svg`.
- Find types: `find-candidates.svg`, `find-businesses.svg`, `find-guides.svg`, `find-products.svg`, `find-places.svg`.
- Look / Learn / Find: `step-look.svg`, `step-learn.svg`, `step-find.svg`.
- Ledger UI (same style, 24×24 also acceptable): `ui-save-tab.svg` (a small yellow bookmark/ledger-tab), `ui-shuffle.svg`, `ui-filter.svg`, `ui-open-out.svg`, `ui-play.svg`, `ui-follow.svg`, `ui-collection.svg`, `ui-report.svg`.
- Motifs: `motif-overlap.svg` (two overlapping circles, yellow intersection, for section dividers), `motif-leader.svg` (a thin leader line ending in a small dot, for "SOURCE 01" style annotations; shapes only, no text), `rule-notation.svg`.
- Also: `paper-grain.png` 600×600 seamless, very subtle warm grain with transparent background.
- **Logo:** I need clean vector or high-res transparent versions of the approved wordmark (cream on transparent, ink on transparent, and on charcoal) and three *concept* options for a square favicon/app-icon mark derived from its letterforms. Propose only; do not replace the approved logo.

## PART C: Copy (return as plain text, clearly headed)
**Hard rule: never invent facts, people, funding, quotes, statistics, studies, sources, URLs or legal claims. Where a real fact is needed, insert a `[BRACKETED PLACEHOLDER]` and ask me the question.**
1. **Alt text** for every image above (concise, descriptive, no "image of").
2. **Topic intros:** for each of the 12 topics, a 50-70 word intro in brand voice, plus three "questions to bring" as short bullet questions.
3. **Category intros:** for each of the four categories, an 80-100 word intro and three suggested threads (subjects to follow) with one-line summaries.
4. **Microcopy polish:** give two on-voice variants each for: empty Following shelf; no results; unavailable original post; signed-out save prompt; private vs public save explanation; "profile will become public" consent; submission-under-review confirmation; duplicate video found; report-a-problem confirmation; password reset email subject and body; newsletter confirmation and welcome email; 404.
5. **Policies in plain English** (mark each "DRAFT FOR LEGAL REVIEW"): Privacy, Terms of use, Community and contribution guidelines, Commercial-relationship and disclosure policy, Corrections policy. Facts to assume: accounts store email, hashed password, handle, display name; saves are private by default; public saves are opt-in and reviewed by editors before they appear; users can export and delete their saves; only a session cookie is used; newsletter and contact emails are stored; videos are never hosted, only linked with provider thumbnails; editors may correct tags, merge duplicates, add context or remove entries with an audit trail. Leave `[BRACKETED]` fields for company name, address, jurisdiction and contact.
6. **Ledger guidelines** (150 words): what makes a good save, what is not allowed, how "Why was this worth keeping?" should be answered, and the plain statement that a save is a recommendation to look, not a verification.
7. **About page:** draft structure and copy for "Who we are" with `[BRACKETED]` fields, plus a short interview questionnaire (10 questions) I can answer so you can fill the real facts in next turn (maker, editors, ownership, funding, affiliations, why this exists).
8. **Editorial planning (no articles):** three story briefs, each with the question, why it is worth asking now, the *types* of primary sources to seek (not specific citations), which Finds could follow, suggested threads, and what would make it fail. Suggested subjects: a first-time voter's local ballot; what goes into a grocery price; how to compare two home-renovation quotes.
9. **SEO:** a meta title (≤60 characters) and meta description (≤155 characters) for each: Home, four categories, Topics index, Latest, Learn, Find and its five subpages, Look, Search, About, Who we are, How we work, Corrections, Contribute, Contact.

## Output format
Finish with a manifest table: `filename | type | size | status (done / needs real photo / needs my input) | alt text`. Put anything you could not do faithfully under "Needs a human". Keep all assets consistent with each other and with the attached references, and ask me before changing any rule above.
