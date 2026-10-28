# Returning an article to Claude Code

Return **three files** per article, named with the story ID and slug:

1. `MI-A1_<slug>.html`: the article in the published source form (copy the shape of the files in `examples/published_pieces/` (or the pieces already in this chat)).
2. `MI-A1_CLAIMS.csv`: every checkable claim in the draft (format below).
3. `MI-A1_NOTES.md`: what you changed from the brief, what you were unsure of, any data requests and the hero copy lines.

## 1. The article file
```
---
kind: story
layout: report
title: <headline: every word supportable by a claims row>
dek: <one or two sentences; no numbers that go stale within a week>
date: 2026-10-29          (Claude sets the real date)
updated: 2026-10-29
author: LookLearnFind
category: politics
format: Reported Feature   (a public label: Reported Feature, Delta Report, Spending Report; never a schema name)
topics: politics,candidates
threads:
hero: mi-duggan            (the key given in the hero brief)
hero_alt: <125 characters or fewer, describes the image>
hero_title: Michigan governor
hero_text: <one line shown on the hero, 110 characters or fewer>
---
<!--openfile
question: <the question this piece answers>
checked: <what was checked and in which sources, with dates>
supported: <what the evidence supports>
other: <other accounts or responses>
open: <what remains unknown>
-->
<h2 id="short-anchor">Section heading</h2>
<p>Body text.[[s:1]] First mention of a candidate: <a href="https://theissuesparty.org/candidates/GOV-MI-BENSON">Jocelyn Benson</a>. First mention of a race: <a href="https://theissuesparty.org/races/2026-GOV-MI">Michigan governor race</a>.</p>
...
<h2 id="not">What this does not show</h2>
<ul><li>...</li></ul>
<!--sources
1 | Title | Publisher | Date | URL | What this source supports
2 | ...
-->
<!--corrections
-->
```
Rules for the body: plain HTML paragraphs, `h2` with ids, lists; no inline styles; no images (Claude adds the hero and any chart). `[[s:n]]` points to the numbered line in the sources block and goes after the sentence it supports. Where a number comes from the data files, write the number out and note the data file in the claims `evidence_ref`; Claude converts to `[[v:name]]` macros where they exist. Use exact URLs from `inputs/<task id>/LINK_MAP.md`; do not invent URLs.

## 2. The claims file
Header: `claim,text_location,source_url,source_date,checked_date,status,type,evidence_ref`

- `claim`: the sentence's checkable content in one line, including the number and the unit.
- `text_location`: lede, h2 id, or sentence number.
- `source_url`, `source_date`: where it comes from. Use the brief's sources; for anything else, `NEW`.
- `checked_date`: leave blank; the independent reviewer fills it.
- `status`: `VERIFIED` (primary document read by Claude, in the brief), `ATTRIBUTED` (reported by an outlet or poll, in the brief), `UNVERIFIED` (not opened), `NEW` (you added it), `OPINION` (attributed view).
- `type`: `number`, `quote`, `date`, `name`, `status`, `explainer`.
- `evidence_ref`: the file or section in this package.

Every sentence containing a number, a date, a quote, a name or a status must have a row. Rows from the brief may be reused unchanged.

## 3. The notes file
Four short sections: **Changes from the brief**, **Doubts** (sentences you are least sure of), **Data requests** (use `DATA_REQUEST.md`), **Hero copy** (alt, title, text, the caption you would like).
