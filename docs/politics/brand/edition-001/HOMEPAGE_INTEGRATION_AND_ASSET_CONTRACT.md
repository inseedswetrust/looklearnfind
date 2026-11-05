# POLITICS HOMEPAGE — EDITION 001 INTEGRATION CONTRACT

**Purpose:** Give Claude the approved visual mockup, precise placement copy and extracted illustration reference plates without asking Claude to invent or recreate the artwork.

## Design authority

1. `LLF_POLITICS_CREATIVE_LOCK/01_POLITICS_BRAND_IDENTITY_CREATIVE_BRIEF.md`
2. `LLF_POLITICS_CREATIVE_LOCK/02_POLITICS_HOMEPAGE_COPY_AND_CONTENT_SPEC.md`
3. This package's approved-direction mockup image under `preview/`
4. This package's Edition 001 briefing and image manifest.

**Immutable shared shell:** `build.shell()` supplies the 236px charcoal desktop rail and mobile slide-in drawer. Reuse it exactly. No new second column. The Politics landing highlights LEARN as approved in reference art, unless this conflicts with the global accessible mode contract — report a conflict before altering core behavior.

## Final above-the-fold copy

- Breadcrumb: `HOME / POLITICS`
- Eyebrow: `01 / POLITICS`
- H1: `Less noise. More evidence.`
- Deck: `The daily briefing, the original records and what they reveal about power, money and what comes next.`
- Daily Signal eyebrow: `THE DAILY SIGNAL`
- Daily Signal title: `Today's political briefing`
- Live edition headline: `The voters changed Congress. Now comes the fight over what changes next.`
- Date: `NOV 5, 2026 / EDITION 001` (publication timestamp replaces this only upon actual publication)
- CTA: `READ THE BRIEFING` -> `/politics/daily/2026-11-05/`, only after edition status is approved.
- Accountability eyebrow: `THE ACCOUNTABILITY DESK`
- Accountability H2: `A new majority. The same leaders?`
- Deck: `Hakeem Jeffries is seeking the speakership. Chuck Schumer expects to become Senate majority leader. Their colleagues will decide whether to keep the party's current leadership or chart another course.`
- CTA: `FOLLOW THE LEADERSHIP RECORD` -> the future verified tracker route, otherwise a source-linked article, not a 404.

## Daily briefing navigation

The homepage offers a compact **Five signals today** link list that points to internal IDs of the new Daily Signal page, not five copies of the story on the homepage. Order: Leadership / Electoral map / Voter priorities / Campaign money / State power. Show these links only if the briefing URL exists and has approved status.

## Lower homepage sequence

1. Election 2026 — `The election is over. The record isn't.` -> verified live state hubs, no fictional results.
2. Follow the Money — `The money behind the message.` -> existing outside-money thread if new topic route unavailable.
3. State of the Record — `Promises made. Decisions pending.` -> existing source-backed articles while tracker is unbuilt.
4. Election Signals — `What the numbers reveal — and what they don't.` -> the full Edition 001 geography analysis or a verified existing article.
5. Current Reporting — three editorially selected, truly existing linked stories, each with publication date and pre/post-election context.
6. Go to the Source — `Don't take our word for it.` -> methodology, official documents and correction policies.

## Visual asset treatment

- Hero: monochrome real photograph of the U.S. Capitol with precise mask, cream canvas and a single muted-teal directional plane. Use supplied extracted reference plate for composition only unless original photographic rights/provenance have been cleared.
- Jeffries/Schumer feature: distinct, actual, documented photographs of both people. Paper-cut masks with subtle irregular edges, no fictional shared event. Supplied cropped composite image is **reference**, not source photography.
- Lower images: mixed real-color documentary photography, muted/monochrome and one duochrome graphic intervention; do not duotone every image.
- No whole new nav redesign. Do not rasterize the page's body copy from the mockup. Render headlines and labels as HTML text.
- Never treat generated visual placeholders as verified source photography.

## Responsive layouts

Desktop: one main editorial content pane to the right of fixed charcoal rail. Tablet 901–1100px: major editorial columns collapse before typography becomes illegible. Mobile <=900px: global drawer from shared shell and full-width modules; daily signal list becomes stacked anchor rows. 44px touch targets and accessible focus behaviors.

## Required checks

- Verify all internal links and headings.
- Do not expose a `SAMPLE` scoreboard or unverified results on the live site.
- No text underlaid with unlicensed images on production pages.
- Maintain provenance records for source photographs, cutout masks and derivative works.
- Run strict build, 191+ unit tests, shell parity, responsive screens and visual diff against approved mockup.
- Publish nothing without owner approval and editor sign-off.
