# LookLearnFind Michigan 2026: package for ChatGPT

Prepared 2026-10-28 by Claude Code (the implementer). You are the writer. This package is everything you need; you should not have to ask for background or repeat basic research. Read this file, then `1_ASSIGNMENT.md`.

## What LookLearnFind is
A reported-journalism site on the 2026 midterms (looklearnfind.com), paired with The Issues Party (TIP, theissuesparty.org), which holds candidate profiles and six issue grades. Scope is **Governor, U.S. Senate and U.S. House only**. Voice: plain, specific, neutral, source-linked. Two live Michigan pieces show the voice (`4_VOICE_SAMPLES/`).

## Folders
| Folder | What it holds |
|---|---|
| `1_ASSIGNMENT.md` | What to write, the format, what to return, what is off limits |
| `2_STORIES/MI-A1`, `MI-A2` | One folder per article: `STORY_BRIEF.md` (the angle and facts) and `CLAIMS.csv` (every checkable claim with source and status) |
| `3_RULES/` | Publishing rules (R1 and R2), the article schemas that apply, the house rules in one page |
| `4_VOICE_SAMPLES/` | Two published Michigan pieces (HTML with front matter) to match tone and structure |
| `5_DATA/` | Michigan data already in hand: roster, TIP profile and race extract for the people named, Kalshi capture, link map |
| `6_OPEN_ITEMS.md` | What is NOT known. Write around these; do not fill them in |

## Two angles are ready. Two are not.
`MI-A1` (the independent who left) and `MI-A2` (Senate poll beside the market) are READY. `MI-A3` (MI-13) and `MI-A4` (MI-10) are NOT READY and are listed in `6_OPEN_ITEMS.md` with the reason. Do not draft them.

## What to return
For each story, one HTML or Markdown draft (see `1_ASSIGNMENT.md` for the front matter), a list of every number and name in it with the source it comes from, and a short note of anything you changed from the brief. Claude Code then implements, runs the build checks and sends the draft to an independent fact-check. **Nothing is published until the owner approves.**
