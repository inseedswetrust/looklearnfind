# LookLearnFind — voice and design brief for Claude

Use this document with the approved visual references and the assets in this package. The approved hero and wordmark are the strongest source of truth. Keep the site's editorial system coherent across the home page, search, stories, Find, About, and the Ledger.

## The idea

LookLearnFind is a place for people who enjoy discovering an idea and then seeing how it holds up. **Look** links to short video posts that preview an idea worth the scroll. **Learn** offers a longer account with numbered notes that lead to original material. **Find** identifies useful real-world manifestations: people, places, guides, businesses, and products that visitors can explore or experience. The path is an invitation, not a compulsory funnel. A save recommends a second look; it does not certify a claim.

People should feel relaxed in the interface and well equipped by the reporting. Avoid a grading or verdict interface. Let other perspectives enter when they clarify the question, while distinguishing a claim from a source and an inference. Be specific about what was checked and what is still open.

## Identity and visual thesis

The logo is the approved LookLearnFind wordmark with its tiny **01 footnote**. That annotation is the essential clue: even the identity points outward to a source. Do not redraw or replace it. The approved hero places two overlapping faces in charcoal and petrol teal with a restrained yellow intersection and the words **“where signal meets source.”** It communicates proximity, differing points of view, and a point of shared inquiry. The intersection is an accent, not a universal yellow fill.

The overall look combines editorial margin notes, a textured paper surface, modern newspaper scale, and candid lifestyle photography. It should feel like a thoughtful cultural publication someone wants to spend time with. The atmosphere is welcoming and lived in; the information architecture is exact.

| Token | Value | Use |
|---|---|---|
| Paper | `#f5f2eb` | Primary canvas |
| Ink | `#1c1d1b` | Headlines, body, rules at full strength |
| Petrol teal | `#145b5d` | Links, key accents, image toning |
| Dark teal | `#0f4145` | Occasional solid section or button |
| Yellow | `#dfca00` | A single dot, source mark, active notation |
| Warm gray | `#eee9df` | Quiet alternate fields |
| Rule | `#c9c4b9` | Table lines and dividers |

Typography in the approved homepage uses an expressive serif stack: `'Iowan Old Style', Baskerville, 'Palatino Linotype', Georgia, serif`. The utility sans stack is `Arial, Helvetica, sans-serif`. Keep serif headlines large, tight, and light in weight. Use small uppercase sans labels with controlled tracking for section numbers, dates, source notes, filters, and navigation. Body copy is clear and comfortably spaced. Avoid rounded tech UI and luxury-fashion display lettering.

The approved homepage preview and `llf_homepage/index.html` can guide desktop scale. Photography should be candid and specific: people listening, working, cooking, making, moving, and meeting in actual-feeling spaces. Warm window or golden light, tactile surfaces, restrained grain, mixed ages and backgrounds. New assets are concept illustrations only. Do not attribute them to actual events or use them as reporting evidence. Use actual photographs and permissions for real team members, candidates, businesses, and quoted subjects.

Icons are thin, rounded 64×64 line drawings using `currentColor`, approximately 2.2 stroke width, with one yellow dot. The supplied standalone SVGs extend the approved sheet. They are wayfinding, not decorative stickers.

## Sitemap and template responsibilities

| Route family | Template purpose |
|---|---|
| Home | Approved hero at top, then Politics, Economy, Society, Everyday Life, Topics, Latest, Find, About. Politics leads with a timely midterm-related question only after real election facts and links are supplied. |
| /politics, /economy, /society, /everyday-life | Category landing pages with distinct photographic banners, a concise orientation, featured Look/Learn/Find paths, and three followable threads. |
| /topics and /topics/[slug] | Index and 12 topic pages: Politics, Candidates, Businesses, Home improvement, Self improvement, Side projects, Working out, Cooking, Supplements, Skincare, Self care, Money. |
| /look and /look/[entry] | Short-post discovery and individual context; open the original at its provider. Never present a synthetic video frame as a creator's post. |
| /learn and /learn/[story] | Long-form reading with numbered footnotes, source list, clear dates, updates, and related Finds. |
| /find and /find/[type] | People, candidates, businesses, guides, products, places, with editorial context and disclosures where applicable. |
| /ledger, /ledger/[entry], /[profile] | Dense, filterable, user-curated table of linked short posts; detail and saved-profile views. |
| /latest, /search | Chronological discovery and functional cross-format search. |
| /about, /about/who-we-are, /about/how-we-work, /about/corrections | Identity, real people and ownership, editorial process, and visible correction path. |
| /contribute, /contact, /privacy, /terms, /community, /disclosures | Participation, contact, and reviewed policy pages. |

The first screen of Home retains the approved hero and updated footnote logo. Below it, let four category chapters have their own image rhythm, editorial headline, a useful question, and related reading. Topic cards use the icon family. Latest is concise and date aware. Find introduces tangible people, places, guides, and products. About closes with the worldview and method.

## The Ledger

The Ledger is a place to browse saved links to YouTube Shorts and Instagram-style portrait posts without surrendering discovery to an opaque feed. A table is the main interface. Show enough information to scan quickly: portrait thumbnail, post title or editorial summary, creator and provider, topic, why it was kept, source status or context, contributor, date, and save action. A featured entry is fine, but it should not overwhelm the rows. Use paper and warm gray in table cells; petrol teal belongs in accents and actions rather than filling every window.

Filters should combine topic, format/provider, contributor, post type, recency, and saved/followed state as data permits. Search, sort, clear filters, shuffle, and open-original actions should be legible. In a narrow viewport, adapt each row into a compact card that preserves the metadata and portrait thumbnail. Do not widen vertical clips into cinematic landscape cards. Users can create profiles, save privately by default, opt in to public saves, and follow other profiles' approved public shelves. Editors review public saves and can correct metadata, merge duplicates, add context, or remove an entry with an audit trail.

The contribution prompt asks: **“Why was this worth keeping?”** A good answer identifies a moment or question, not an unearned verdict. A public save is a recommendation to look, not verification. Link directly to the original; videos are not hosted here.

## Functional details across templates

- **Search:** Search across posts, sourced stories, topics, and Finds. Make scope and filters visible; preserve query state in the URL; distinguish no results from an unavailable original.
- **Learn story:** Give the headline and question room; show publication/update dates, author or editor when known, numbered footnotes linked to source entries, context and uncertainty, related Look posts and Finds, and a correction link. Never generate claims or sources from a headline.
- **Find listing/detail:** Explain why an item is here, what someone can actually do with it, when details were checked, and any relevant relationship. Use actual records and permissions before presenting a real candidate or business.
- **About:** Lead with the worldview and Look/Learn/Find use, then name real makers, ownership, funding, and affiliations from founder answers. Do not invent team biographies.
- **Policies:** Use the supplied drafts only after counsel and operator verification. Bracketed fields must not go live.

## Voice

Write like a smart, curious person showing another person the useful part of the record. Start with something observable. Prefer “Read the record,” “Open the source,” “See what changed,” or “Try it” over sweeping promises. Give the reader space to think. Keep civic, health, and financial subjects careful and concrete. A headline may be intriguing, but the body must earn it.

Avoid “unlock insights,” “game-changing,” “we give you the truth,” “both sides,” “do your own research,” “from signal to decision,” insider-club language, and claims of certainty unsupported by sources. Avoid invented people, statistics, studies, citations, quotes, URLs, affiliations, or legal assertions. Insert a bracketed question for the founder when a real-world fact is missing.

## Asset use

Use `MANIFEST.md` for exact dimensions and status, `PHOTO_PROMPTS_AND_ALT.md` for image provenance and alt drafts, and `SVG_SOURCE.md` for standalone vector code. The package includes a contact sheet for visual scanning and the approved originals under `references/`. The two requested hero edits need a layered source to be faithful; a flattened raster should not be approximated. The transparent logo PNGs preserve raster shapes, while an editable outline vector still requires the original file.
