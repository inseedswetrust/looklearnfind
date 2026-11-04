# LookLearnFind — brand, voice, and design guide

Purpose: write and design new LookLearnFind pages in the established voice and visual system. Approved mockups and assets in `reference/` are the visual source of truth; this file explains the thinking behind them.

## The brand in one paragraph

The world is full of fascinating people, claims, practices, places, and things to make or try. Opinions about them are plentiful; the material behind those opinions is often harder to find. LookLearnFind makes curiosity easier to pursue. **Look** offers short social posts that introduce an idea worth the scroll. **Learn** opens it up through long-form reporting and deep dives with numbered footnotes to original material. **Find** identifies strong real-world expressions of an idea so a visitor can visit, try, make, attend, or otherwise experience it. Visitors should feel welcome to form their own view. The brand is relaxed, visually engaging, extremely informed, open to relevant perspectives, and willing to show its receipts.

Positioning: an editorial discovery system and a community of people who enjoy looking closer. It has a lifestyle dimension because ideas should lead into real life, but it is not a generic lifestyle publication, a hot-take feed, or a verdict machine.

The feeling to create: "These people notice interesting things, know how to investigate them, and will show me enough to think for myself." Let the design and the work convey this; avoid explaining the brand through repeated slogans.

## The reader and the subject map

The reader enjoys following a thread, testing an idea, hearing a perspective they had not considered, and finding something useful in the world. They may only watch a short post, or read every footnote. Both are legitimate ways in. Participation should feel like contributing an observation or a source to a shared investigation, not joining a fan club.

Four main editorial categories, in navigation and homepage order: **Politics, Economy, Society, Everyday Life.** Other main navigation: **Topics, Latest, Find, About**, with search available. Politics opened the homepage with a 2026 midterms concept; it is not the permanent center of the brand.

Twelve topics: Politics, Candidates, Businesses, Home improvement, Self improvement, Side projects, Working out, Cooking, Supplements, Skincare, Self care, Money. Topics are cross-category paths into stories and finds, not a replacement for the four categories. Cannabis is outside the current focus.

Use subjects expansively but concretely: a candidate's record, a small business, a home estimate, a weeknight cooking technique, a movement routine, a supplement label, a skincare claim, a side project. The connecting idea: notice something, understand its basis, see whether it holds up in life.

## Approved identity

- **Logo:** stacked cream LOOK / LEARN / FIND wordmark on charcoal, fine rule, small `01` footnote. Use `reference/homepage/assets/logo-01.png` (served as `/img/logo-cream.png`). Do not redraw it or sprinkle the 01 as decoration. In the rail and mobile bar the original artwork is used as an alpha mask, one clip per word, and the word of the current **mode** is lit yellow (see Navigation below).
- **Homepage opening:** keep the split-portrait overlap hero, yellow overlap, `SOURCE 01` notation, and the exact copy "where signal meets source." Artwork: `overlap-hero.png`. On small screens, art-direct the crop and use live text if embedded words would become illegible.
- **Underlying idea:** overlapping viewpoints, a marginal note, and a footnote that lets the viewer go beneath the surface. An intelligent editorial system, not a detective board or bureaucratic dossier.
- **Notation:** small indexes, fine rules, arrows, source markers, margin-like annotations. Make them functional where possible.

## Color and type

**Design tokens v1** (2026-11-04, owner-approved direction; source of truth is the `:root` block of `static/css/site.css`, names `--llf-*`; legacy names such as `--teal` and `--paper` resolve to these values). Specification and rules: `docs/design/LLF_GLOBAL_SHELL.md`.

| Role | Token | Value |
| --- | --- | --- |
| Rail, mast and mobile bar | `--llf-night` | `#1d1e20` (neutral charcoal, no longer dark green) |
| Rail secondary surfaces | `--llf-night-soft` | `#292a2d` |
| Main paper | `--llf-paper` | `#f8f6f0` (with `#fbfaf6` and `#fffdf9` for raised surfaces) |
| Ink | `--llf-ink` | `#222326` |
| Muted text | `--llf-muted` | `#646b70` (5.0:1 on paper) |
| Editorial blue: links, labels, source cues | `--llf-blue` | `#28636c` (6.3:1 on paper) |
| Deeper blue: actions, emphasis | `--llf-blue-dark` | `#173e47` |
| Fine rules | `--llf-line` | `#d7d3c9` |
| Brand yellow | `--llf-yellow` | `#f0d800` |
| Rail width (desktop, 901px and up) | `--llf-rail-width` | `236px` |
| Display / editorial text | `--serif` | Newsreader Variable (self-hosted) with Iowan Old Style / Baskerville / Palatino / Georgia fallbacks; tight headline spacing |
| Navigation / utility | `--sans` | Arial / Helvetica-style sans; small uppercase, letterspaced |

**Yellow is for mode, status and navigation focus only: the lit LOOK, LEARN or FIND word, the current-section marker, focus rings and the small notation dot. It is never a party color, a chart series or a wash, and never text on paper (1.3:1).** Charts use neutral colors, labels and patterns, not party colors.

**Deprecated palette (kept for migration only):** the earlier green set. Main paper `#f5f2eb`, ink `#1c1d1b`, rules `#c9c4b9`, teal-green `#145b5d` with darker `#0f4145`, yellow `#dfca00`, masthead `#1d1d1d`, rail background petrol image `sidebar-politics.webp`. `static/css/sidebar.css` and `static/js/sidebar.js` still carry the old rail and load only when the rollback flag turns the global shell off. Do not use the deprecated values in new work. Article HTML and data files contain none of them.

Prototypes use system font stacks. Preserve the contrast between expressive serif reading and precise sans utility text when choosing production fonts. Do not switch to a tech-product sans, rounded playful font, or luxury fashion lettering.

## Photography and graphics

Candid, lived-in, specific: people listening, making, reading, working, cooking, moving, meeting in real places. Natural light, material texture, warm ivory, ink, petrol teal, restrained yellow, subtle grain. Avoid glossy corporate stock, literal magnifying glasses, fake newspaper clippings, pseudo-scientific diagrams, generic AI-tech imagery.

The twelve topic icons (`topic-icons.svg`) are a line-drawing family: 64×64 viewBox, ~2.2 rounded strokes, one yellow notation dot, no badge. Reuse them; don't mix emoji or other icon packs.

Generated concept photographs illustrate a layout; they are not documentary evidence or frames of anyone's video. In production, credit real images and use an actual provider thumbnail or an explicit fallback.

## Layout grammar

Homepage: spacious and chaptered — image-led top, large serif headlines, thin rules, contrasting paper surfaces. A site-wide component system carries masthead, icons, notation, metadata, and source behavior into interior pages without forcing the homepage's dramatic scale.

- **Story Reader:** comfortable measure, generous line height. Inline numbered footnotes open original records at the claim they support. Show author, dates, update/correction history, disclosure. An "Open file" summary can frame the question, what was checked, what is supported, other views, what remains open.
- **Search:** query field, result-type tabs, precise filters, readable mixed results, visible source/disclosure cues, a clear empty state.
- **About:** one example moving through Look, Learn, Find. Real people and a source trail. Name the maker, editorial decision makers, ownership/funding, affiliations before publication; never invent these.
- **Find:** pages for people, businesses, guides, products, opportunities explain why included, what was checked, limits, commercial relationships. "Best" is a judgment with inspectable criteria.
- **Find Ledger:** dense scannable table of short video links with true 9:16 previews. Each row shows title, human note, category/topic, post kind, duration, platform, original creator, saver, and actions without expanding. One featured clip may sit above. Warm paper, light alternating rows, green as accent/button only. Follow `reference/ledger/` v2 mockups; do not revive the rejected gallery or large green windows. See `FIND_LEDGER_PROPOSAL.md`.

## Writing voice

Curious, clear, observant, calm, lightly distinctive. A smart friend who has done the reading, has good taste, and makes space for the reader's judgment. Witty or warm when the subject warrants; never glib about civic, health, or financial consequences. Confident about what was checked, candid about what remains unsettled.

1. Lead with something worth noticing — a specific question, tension, or detail beats an abstract claim.
2. Invite rather than instruct the conclusion. Show what a source supports, competing interpretations, and limits. Don't imply all positions have equal evidence.
3. Move between pleasure and rigor. Avoid relentless academic, activist, or corporate language.
4. Ordinary words, concrete verbs: "Read the record," "See what changed," "Try it," "Visit the shop," "Open the source."
5. Keep the reader's agency. Make an editorial case, show why, allow inspection.
6. Vary cadence. Don't make every heading a fragment or every sentence a slogan.

| Situation | In-voice approach |
| --- | --- |
| Hero | "where signal meets source" — exactly, in the approved hero |
| About | "Curiosity should lead somewhere." |
| Search | "Follow a thread." / "What are you looking into?" |
| Ledger | "A feed you can steer." / "Why was this worth keeping?" |
| Story | "What does the record show?" followed by the actual material |
| Real-world Find | "Why it made the list," "What we checked," "What to know before you go/try/buy" |
| Community | "Bring a question. Bring a source. Tell us what held up." |

These are tone examples, not lines to repeat everywhere. "From signal to decision" is not a central tagline.

## Avoid

- "We give you the truth," "both sides," "do your own research," and other lazy claims. Name the source, finding, disagreement, or uncertainty.
- Turning every post into a debunk, sales funnel, score, or verdict.
- Hype, clickbait, jargon, self-congratulation, faux rebellion, cultish exclusivity, identity-assigning language.
- Treating a clip, a submitted note, a sourced article, and an endorsed Find as carrying the same authority.
- Fabricated testimonials, metrics, handles, findings, source labels, affiliations, rankings. Label design examples as illustrative.

## Evidence, trust, participation

Footnotes are an interface. In Learn, `SOURCE 01`, `SOURCE 02` point to original material for the associated claim, each with title, publisher/author, date, and why it matters. Corrections and updates stay visible. Disclosures sit near recommendations and in a full policy.

`L / 042` indexes a Ledger link, distinct from `SOURCE 01`. Label **Reader-added**, **Editor-added**, **Deep dive attached** precisely; neither addition is a fact-check. Present firsthand experience as firsthand; report what was actually verified.

Contributions sharpen the work: a question, an original source, a video worth keeping, a report on trying a Find. Credit contributors, review claims before elevating them, explain corrections. Public saves are opt-in; private stay private. A shared annotated shelf, not a follower-count contest.

## Pre-ship test

Can a visitor tell what caught our eye, what the claim or recommendation rests on, who contributed it, what remains open, and what to explore or try next? Does the page still feel like the homepage when the topic shifts from midterms to cooking or skincare? Is the treatment right for the task: spacious for chapters, readable for stories, fast to scan for the Ledger?

Conflict rule: follow the latest approved decisions — locked logo and hero; four-category, twelve-topic map; About's Look → Learn → Find; v2 table-format Ledger with 9:16 previews and light surfaces.

## Navigation and the global shell (approved 2026-11-04)

Approved directions: a persistent dark charcoal sidebar, the original LLF logo, a yellow active-word indicator for Look / Learn / Find, global search and cross-category browsing. Full specification, route-to-mode matrix, accessibility rules and authoring steps: `docs/design/LLF_GLOBAL_SHELL.md`.

- **One shell for every page.** `build.shell()` is the only function that writes a page, and it renders the shell (`shared_nav.py`) into all of them: homepage, categories, topics, threads, articles, Find, Look, search, About, legal, account, 404 and every election page. No template carries navigation markup. A build assertion and `tests/test_global_shell.py` fail a page that lacks exactly one shell root.
- **Desktop (901px and up):** a fixed 236px rail (logo, Look / Learn / Find modes, global search, Browse, a contextual block, About links). The mast stays on top for the brand navigation and is offset by the rail. One content canvas; no second permanent column.
- **Mobile (900px and under):** a persistent compact bar (logo, modes, Explore). The Explore sheet holds the same destinations as the rail. Nothing overlays the content.
- **Modes are editorial state, not site sections.** The lit word comes from the page model: `/look/` and `/u/` light LOOK, `/find/` lights FIND, `/learn/` and `/elections/` light LEARN. Home, category, topic, thread, About, legal, search and error pages light none. Browsing Politics never makes Politics the shell.
- **Contextual block (below the global links, never replacing them):** on a story, the state lens and recommendations; on political and election pages, a state picker; on any page with `<h2 id>` headings, an "On this page" outline; otherwise nothing.
- **Search** is global (`/search/?q=`); `/` focuses it unless the reader is typing in a field. Every link works without JavaScript.
- **Rules:** no Oxford comma in any shell copy; do not add a ninth top-level nav item without owner approval (`data/site.json` is the nav source); the shell never states a result and never calls a race.

Conflict rule (addendum 2026-11-04): where this file and `docs/design/LLF_GLOBAL_SHELL.md` differ on navigation, palette or the shell, the design file governs.
