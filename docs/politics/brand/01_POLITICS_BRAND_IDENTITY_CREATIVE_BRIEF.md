# LOOKLEARNFIND — POLITICS VISUAL IDENTITY & CREATIVE DIRECTION

**Document ID:** `LLF-POLITICS-CREATIVE-001`  
**Version:** 1.0 — November 5, 2026  
**Status:** OWNER-APPROVED DIRECTION FOR CREATIVE DEVELOPMENT; implementation requires normal build, editorial and deployment checks  
**Applies to:** Politics homepage, Daily Signal, elections and state hubs, race pages, articles, video covers, social assets, evidence graphics, related feature templates and new Politics components  
**Companion:** `02_POLITICS_HOMEPAGE_COPY_AND_CONTENT_SPEC.md`

> **Non-negotiable concept:** LLF is a premium independent lifestyle and documentary journalism brand with an investigative edge. Politics is not a different brand. It expresses the same editorial taste through stronger analysis of power, public records and consequences. The design should feel meticulously art-directed, editorially calm and capable of one arresting visual intervention.

## 0. Source of truth and precedence

This is a written design contract, **not a replacement for the site's shared navigation system or its publishing rules**. Claude must read it before creating or modifying Politics creative. Cite it from root `CLAUDE.md`, the production-lock index and the brand/design index. Treat a change as a versioned amendment reviewed by the owner. Never silently overwrite the accepted rules with a new image-generation interpretation.

Precedence on conflicts:
1. Safety, legal rights, factual accuracy, editorial verification and existing Production Lock.
2. Approved locked global shell and authentic LLF brand assets.
3. This Politics-specific brand contract.
4. Page-level design and copy briefs.
5. Aesthetic defaults from a creative tool or an individual designer.

Create or extend regression tests for structural requirements. Visual choices which cannot be tested automatically must have comparison screenshots and owner approval. “Immutable” means **versioned, auditable and change-controlled**, not filesystem read-only. Every later creative task must inherit this document, including tasks started in a new Claude session.

## 1. Brand thesis

**Editorial proposition:** “Less noise. More evidence.”  
**Editorial method:** Look → Learn → Find. Observe an event, establish the record and show readers where the evidence and accountable institutions can be found.  
**Design thesis:** **The Annotated World** — we interrupt photographs, reports and interfaces only where the interruption helps readers see a relationship or detail that matters.  
**Temperament:** curious, independent, unsentimental, culturally aware, confident, precise.  
**Avoid:** institutional public-affairs design, partisan campaign collateral, newsroom control panels, loud activist graphics, youth-oriented illustrations and fashion for its own sake.

An LLF page should resemble an art-directed independent magazine, not a prebuilt landing-page template. Photography, white space, headlines and small editorial metadata should feel part of one considered composition. We prefer documentary specificity over general symbolism: the inside of a chamber rather than another generic Capitol exterior, an archival filing table rather than a random stack of papers, a public hallway with observational depth rather than a generic infographic.

### User-validated reference decisions

- **Locked:** Existing persistent charcoal left rail and slim top mast; authentic stacked logo; yellow highlight on the currently active LOOK, LEARN or FIND word; mobile left slide-in drawer. These must NOT be redesigned for a Politics feature.
- **Approved typography and hero cue:** Signal / Noise's large, elegant serif title “Less noise. More evidence.”, intelligent line breaks, warm-paper negative space, restrained metadata and black-and-white Capitol photo that is **masked out of its background plane**.
- **Approved image composition:** A desaturated photographic subject crosses the edge of an inset, cutout or geometric color field. The geometric color sits *behind, within or across* the documentary image to create a sense of dissection, not decoration.
- **Approved Daily Signal:** Modern Dissident's controlled asymmetric horizontal feature: a small forceful headline territory, concise quieter description, date and purposeful action. Avoid reducing it to a massive yellow advertisement.
- **Approved leadership-feature photography:** Observational and cinematic images from *inside* political institutions, with figures in foreground and believable light, not just a civic-building icon.
- **Approved type-on-image reference:** The train-platform example: one large, condensed, punchy statement integrated with real documentary photography and a naturally dark area that supports it. Text is not a floating generic CTA card.
- **Approved new candidate treatment:** Real photographs of real featured politicians, cut out like clipped newspaper photographs with irregular paper edges, assembled against a separately sourced documentary or geometric background with other relevant politician cutouts.
- **Approved new signature:** **Directional duochrome geometry canvas** — controlled shapes and color planes overlay or interleave with monochrome photographs, suggesting that LLF is interrupting time to analyze the scene.
- **Explicit rejection:** Busy style sheets, excessive yellow strokes, repeated teal blocks, cartoonish or painterly image generation, generic photo grids, identical visual weight for all cards, excessive boxes, faux evidence stamps and prominent unverifiable metrics.

## 2. Locked global shell — do not reinterpret

Desktop:
- Persistent left navigation, charcoal `#1D1E20` or the *existing production token that resolves to the approved charcoal*. Do not invent a teal/green Politics sidebar.
- Original approved LLF logo asset. Never typeset an imitation logo in a new font. The active LOOK / LEARN / FIND word is highlighted in brand yellow according to the page's mode.
- Modes, global search, cross-category Browse, contextual state picker and article outline belong in the common navigation system. The rail must not become Politics-only navigation.
- Slim upper mast remains. No second permanently visible right-hand navigation column.
- Main content starts beyond the rail, fills the available width and uses controlled editorial gutters. Headline and image may form a single spread.

Mobile:
- Persistent narrow header with authentic logo and a clearly labelled menu trigger.
- Left slide-in charcoal navigation drawer, approximately `min(300px, 85vw)`, shares destinations and mode logic with desktop. Dim backdrop; proper focus management, scroll locking, escape/backdrop close and reduced-motion support.
- Do not replace this with a completely separate mobile navigation product or a Politics-only full-screen sheet.

Changes to shell markup or breakpoints require shared-component review and regression testing across all page families, not only the Politics landing.

## 3. Colors, texture and usage hierarchy

Use approved production design tokens where present. The numerical values below are **reference targets**, not instructions to override a different approved token without inspection.

| Role | Reference | Rules |
|---|---|---|
| Charcoal / navigation | `#1D1E20` | Fixed shell, some rare photographic feature panels and ink-dark backgrounds |
| Warm editorial paper | `#F8F6F0` | Primary content canvas, reading areas and calm negative space |
| Editorial ink | `#202122` | Headlines, substantial copy and key rules |
| Muted teal | `#28636C` | Fine indexing, annotations, restrained geometries and data relationships |
| Duochrome teal field | `#16A79B` at controlled opacity | Occasional directional geometry; not a generic full-page background |
| LLF yellow | `#F0D800` or approved brand token | Active logo/navigation state, rare text-over-image declaration and *one* prominent attention marker per viewport |
| Quiet border | `#CBC9C3` | Thin editorial dividers and field boundaries |
| Secondary text | `#5C6160` | Captions, dates, source and method labels |

The yellow is an *attention currency*. Spend it deliberately. A useful guideline: a full desktop viewport should contain at most one visually dominant yellow intervention outside of the active sidebar logo/navigation. Teal is not a second attention color to apply indiscriminately.

Texture: subtle natural paper in light reading surfaces, restrained film grain in photographic assets. Texture must not reduce text legibility or create false documentary authenticity. No grunge splatters, faux-ripped paper backgrounds across entire sections or overprinted random type.

## 4. Typography and title structure

Keep the production-approved editorial serif (Newsreader if present) and the established navigation sans. Don't introduce a new font family just to make a single feature look forceful. Use a **bold, carefully selected sans or condensed face** only for statement-over-image exceptions, matched to the design system and web licensing.

### Hierarchy
1. **Page hero / H1:** One short, declarative editorial claim or promise. High-contrast serif, large enough to set the page's identity. Intentional line breaks at editorially meaningful points, never one or two words stranded by accident.
2. **Hero deck:** One or two readable sentences explaining what the user will find. Smaller serif or high-quality body style, not another competing giant display line.
3. **Primary feature / H2:** One dominant story or current investigation. Can carry a photo-led heading or split editorial spread. Should not compete with the H1.
4. **Section title / H2:** Controlled serif scale with a small sans eyebrow when genuinely helpful. Examples: “The Daily Signal”, “Election 2026”, “The Accountability Desk”. Do not stack multiple markers communicating the same label.
5. **Story title / H3:** Short specific claims, not generalized slogans. Headlines must reflect content actually available.
6. **Metadata:** Compact, tracking-aware sans. Use readable dates, author, source status and update details. Metadata must be genuinely meaningful.
7. **Source footnotes:** Linked, numbered or labeled as appropriate; understated yet discoverable and keyboard accessible.

Underlining is not the default brand signature. Links can use conventional focus/hover treatment. Do **not** underline every eyebrow, H2 or call to action in yellow. A single rule may distinguish a section when it clarifies flow. Editorial rules are primarily gray/ink or very restrained teal.

### Content style
- Clear, skeptical, lively, professional and sourced. Avoid breathless news clichés.
- Prefer specific verbs and observable claims: “A vote approaches”, “The record shows”, “What changed” over empty adjectives like “shocking”, “explosive”, “game-changing”.
- Use no Oxford comma.
- Distinguish a verified quotation from an original editorial declaration. Never create fabricated quotations.
- All campaign finance, election results and leadership position descriptions must include provenance and as-of status where displayed.

## 5. The signature image grammar

### A. Directional duochrome geometry canvas — REQUIRED SIGNATURE FEATURE

Use **at least one instance on the Politics homepage or on a major Politics feature**, not as wallpaper on every card. This is a composition method, not a filter preset slapped over a whole picture.

**Intent:** A documentary scene is deliberately paused and analyzed. The viewer senses that an image has been separated into layers and that an otherwise hidden relationship or context is being singled out.

**Construction, in order:**
1. Select a strong **real** photograph with licensed or otherwise authorized reuse and recorded provenance. Prefer a recognizably factual scene with natural perspective or architectural rhythm.
2. Convert all or part of the photo to high-quality black-and-white. Preserve facial detail, fine shadow gradations, building texture and truthful outlines. No AI alterations that imply an event did not happen.
3. Create one or two controlled teal geometric planes — rectilinear strips, offset blocks or a stepped directional shape. Use grid and architectural cues to anchor placement. Geometry must imply focus, movement, interruption or comparison.
4. Use a precise subject mask to carry one photographic element **above** a colored plane or beyond a photo boundary, creating genuine foreground/background depth. For architecture, a dome or staircase can cross the field edge. For a person, hair or shoulder contours can cross the field.
5. Permit a tiny amount of natural-looking grain. No cartoon outlines or artificial illustration textures.
6. Compose editorial type **around** the layers with ample clear space, not over essential facial features.
7. Check the image in monochrome, at a laptop viewport and on mobile to make sure contrast and meaningful content remain legible.

**Geometric rules:** Flat or slightly translucent teal; no default gradients, neon glows, 3D bevels, random triangles, confetti or complex pseudo-technical HUD markings. Lines or crop boundaries may align with pillars, doors or a horizon to make the intervention credible. Direction should lead toward the relevant evidence or story. Visual noise is failure.

**Hero example:** A black-and-white Capitol dome masked so its edge rises above an offset muted-teal field. The warm-paper headline and tiny institutional labels occupy the opposing plane. One purposeful teal interruption and no obligatory yellow underline.

### B. Documentary / cinematic image treatment

**Source priority:** (1) actual licensed or use-authorized event photography, (2) official public record photographs under confirmed reuse conditions, (3) original commissioned photography, (4) labelled AI illustration only for conceptual, nonfactual background use. Do not label an AI image as a real photograph and do not depict an invented real-world interaction.

Preferred framing: people viewed from within an actual environment, understated street life, observed legislative spaces, signs of public institutions, original documents and human-scale context. Keep imperfect atmospheric shadows, architectural depth and credible camera height. Avoid repetitive frontal Capitol hero photos, stock-office clichés and fake campaign signage.

**Treatments:**
- `ARCHIVE`: credible monochrome with dark tonal range and restrained film grain.
- `WITNESS`: muted documentary color, warm practical highlights and charcoal shadows.
- `CUTOUT`: isolated real-photo subject with a visible paper edge, composited against another true-to-source image or restrained graphic plane.

Do not impose one filter on every asset. Use consistent tonal contrast and editorial seriousness across the set.

### C. Newspaper-cutout politician compositions — SECOND SIGNATURE

**Mandatory whenever featuring named politicians in a multi-person political collage:** Pull actual photographs of **each** politician being discussed. This means retrieving real photos, checking identity and context, maintaining a source/license manifest and using those pixels as the source. **A text-to-image approximation of a politician is not a substitute for this rule.** If photographs cannot be secured, leave the art in a source-pending state; do not silently fabricate likenesses.

**Visual construction:**
1. Choose one authentic, high-resolution photo per featured politician. Favor natural expressions, contemporary relevance and good contour separation. Avoid archival age mismatches unless the story is historical.
2. Extract the silhouette precisely, including hair and shoulders. Keep the face unchanged and recognizable. Never regenerate, beautify, alter expression or combine facial identities.
3. Add a narrow, slightly irregular warm-white newspaper-paper perimeter around the cutout (roughly 3–8px at a 1600px-wide artboard, scaled by export size). Slight hand-cut irregularity is acceptable; thick cartoon sticker outlines are not.
4. Maintain believable relative scale and intentional overlap. The collage is an editorial comparison, not a fictional meeting or shared event. Positioning must not imply the people stood together, endorsed one another or made a joint statement.
5. Behind cutouts, use a genuine documentary background or the directional geometry canvas. Black-and-white cutouts can contrast with teal behind-plane fragments. A colored original may be selectively desaturated, but subjects remain faithful to the source.
6. Reserve a clear title field with strong serif editorial typography or one forceful sans statement when using text-over-image. Do not cover eyes with decorative graphics.
7. Optionally include a tiny image-credit/source line and `01` reference marker. The index has an actual collection/thread meaning, not arbitrary decoration.
8. Show a visible or accessible media credit in publication and preserve license/source records in the asset manifest.

**Composition variants:**
- `DUAL`: two principal politicians with equal documentary dignity for contested leadership or contrasting records.
- `CONSTELLATION`: two principals plus one or two smaller secondary figures only when the reporting establishes their relevance.
- `PROFILE`: one principal cutout in front of relevant legislative architecture or documented setting.

**First test story:** “Who Leads Next?” featuring authentic cutouts of Hakeem Jeffries and Chuck Schumer. This is an editorial examination of leadership questions, not visual evidence that they met, are being deposed or agree on an outcome. If the story describes an organized campaign to replace them, attribute the campaign and differentiate its position from LLF's fact reporting. Do not visually imply replacement has already occurred.

### D. Strong text over images

Use on major feature heroes, select investigations and video covers. One bold editorial thought per image. Favor natural dark regions or compositionally quiet areas of the photo. Use bright yellow only when editorial impact justifies it; white can be equally strong. Use no generic opaque banner unless it is an intentional headline plane. Treat actual quotations as quotations, with source and context. No fake text attributed to politicians.

Type should be intentionally set and line-broken, possibly covering about 20–35% of the visual field. Avoid breaking a phrase in a confusing place. The image retains its documentary identity.

## 6. Repeatable editorial marks — hierarchy, not decoration

1. **The footnote/index:** Preserve the small superscript-like mark from the authentic LLF logo. In content, a restrained `01 / POLITICS` may identify a fixed section. Story markers only when tied to real series/thread IDs. No random numeric decoration.
2. **The annotation plane:** one directional teal geometry treatment when the piece calls for analysis or compositing. The plane is architectural, never a generic brand sticker.
3. **The statement intervention:** short, hard-hitting type integrated into an actual photograph. No need for a yellow underline beneath it.
4. **The source breadcrumb:** discreet original-source link, image credit and “as of” metadata wherever a factual or numerical claim is presented.
5. **Editorial tab:** occasional small color field to identify a daily flagship. The Daily Signal may have a single controlled yellow tab; use it nowhere else in the same viewport unless necessary.

**Priority rule:** A single design unit should generally deploy **one** signature device. A flagship hero can combine a cutout with a geometric plane because their relationship is the point, but must not also add multiple highlights, stamps, arrows and oversized badges.

## 7. Homepage composition contract

This is a *single cohesive Politics homepage*, not a sample board.

**First viewport desktop:** locked left rail and mast, one resolved Signal / Noise hero, live-current Daily Signal module and the beginning of one main reporting feature. Preserve the precise interplay of paper, type and photographic cutout. At least one hero/feature image uses directional duochrome geometry.

**Below the fold:** one editorial lead investigation, an Accountability Desk entry, Election 2026/state report entry, controlled photo-led latest reporting and compact source-oriented links. Avoid a repetitive four-card wall. Use different editorial rhythms: split spread, horizontal news strip, ruled story list, cinematic photograph and one carefully chosen quote-over-image feature.

**Do not** write unsupported result numbers, leadership vote totals or claims of mandates into concept imagery. Dynamic facts must come from approved published data. Use meaningful empty states, not fictional numbers.

**Photography budget:** A photographic image should exist for the primary hero, the lead investigation and two or more secondary editorial contexts when source assets are available. More real photography is preferred to more iconography. Each image needs `asset_id`, description, source URL, creator, rights status, date, treatment and editorial context.

**Responsive:** At 1024px, reduce the number of columns rather than squeezing headlines. At mobile, the hero collapses to a readable text-first composition plus image; the cutout geometry survives as a subordinate visual, not as a text-obscuring overlay. All core headlines, source links and dates remain accessible.

## 8. Politics content system — recurring series

- **The Daily Signal:** Daily current-politics briefing, owner review and dated archive. A concise editorial summary can commission two videos, but may not claim unsupported facts.
- **State Election Report:** Living state hub with official results where verified, postmortem, race links, campaign-finance context and updates. Preserve existing election URLs.
- **State of the Record:** Distinct recurring reporting series on documented political choices and consequences; old “State of the Race” articles remain historically labeled and linked.
- **Election Signals:** Evidence-based comparisons and meaningful statistical patterns, with methods and limitations.
- **Follow the Money:** Source-linked PAC, FEC and other campaign-finance reporting.
- **The Accountability Desk:** Documented public positions, pending replies, institutional decisions and official actions; show the evidence behind every position.
- **Go to the Source:** Original records and methodology, not just a slogan.

LLF reports and verifies. TIP is a separate advocacy and candidate-response product. Link to TIP records and Action Parties transparently. Do not conflate an advocacy demand with a verified electoral mandate or let a lack of answer imply opposition.

## 9. Video and social continuity

When a news article becomes a Reel, short video or X/Bluesky post, keep the same core title promise, source evidence and image attribution. Use real politician cutouts and the `CUTOUT` variant when named politicians are visually represented. The vertical cover should be separately composed, not a squeezed crop of a landscape hero. Essential type and faces stay clear of platform UI zones. ElevenLabs narration, Remotion layering and owner-reviewed production remain under existing production rules. Do not change the script, invent dialogue or fictionalize an encounter to make artwork easier.

## 10. Creative production checklist — mandatory for Claude and collaborators

**Before creative work:**
- [ ] Read this document and the locked shell/Production Lock rules.
- [ ] Identify exact output medium, route and intended editorial fact/claim.
- [ ] Read the page-copy brief and identify the one strongest title/deck.
- [ ] Inventory existing real photos and select only relevant ones; verify subject names, source and rights.
- [ ] Select one visual signature, not every signature.
- [ ] Identify the mobile crop and text-safe zone.

**Before approval:**
- [ ] Actual LLF logo and existing shell unchanged.
- [ ] Natural, documentary visual tone; no cartoon/painterly regeneration.
- [ ] Photo cutouts from real sourced politician photographs, not invented likenesses.
- [ ] Source/license provenance preserved.
- [ ] All pictured people represent actual article subjects; collage doesn't imply a fabricated meeting.
- [ ] A directional duochrome geometry composition appears at least once on the Politics homepage or designated feature.
- [ ] Typography and whitespace remain elegant, no decorative accent overuse.
- [ ] No unsupported statistics, race calls, quotations or public-position classifications.
- [ ] Desktop and mobile visual checks against the approved reference shell.
- [ ] Any production change to these rules is versioned and approved rather than silently introduced.

## 11. Deliverable standard for each new creative request

Return a compositional mockup plus an implementation-ready source manifest. When possible supply separate authentic image layers, masks, background, text and typography specifications. Do not deliver flattened concept art as if it were an authentic-photo source package. Include `ASSET_MANIFEST.csv` fields: `asset_id,subject,origin_url,creator,rights_basis,date_downloaded,context,transform,credit_required,usage_status`. If rights or identity are unverified, use `usage_status=pending` and keep the artwork unpublished.

No image generation prompt, tool default or third-party designer may override this brand document without written owner approval.

---

**Change control:** Maintain the document in `docs/brand/politics/` (or the equivalent existing brand directory). Create a root pointer in `CLAUDE.md`; list the file in the production manifest; commit revisions with a clear date, rationale and visual diff. The original approved shell and source-first editorial constraints are permanent requirements unless the owner changes them explicitly.
