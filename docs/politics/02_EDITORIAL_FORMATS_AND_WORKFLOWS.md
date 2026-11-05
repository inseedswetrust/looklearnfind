# 02 — Editorial series and execution workflows

## Core formats
| Series | Cadence | Primary output | Reuse |
|---|---|---|---|
| The Daily Signal | Each publishing morning | Dated brief: top 3–5 verified developments, evidence, why it matters, what's unknown | 2 short-form video pitches, 1+ story briefs, social derivatives after actual links |
| State Election Report | Initial post-election and material updates | Living hub with timestamped results and corrections | 7 state hubs, office/district templates |
| State of the Record | Post-election, update on evidence | Distinct long-tail state postmortem and evolving governing record | Result snapshots + TIP records, state hero assets |
| Election Signals | On verified changes | Three evidence-backed interpretations, clear limitations | Existing claim verification and source system |
| Follow the Money | When FEC/IE change materially | Report with spending totals, time windows, sources and causation cautions | Existing 9 money articles, existing FEC tools |
| Accountability Desk | When position/decision changes | Dated evidence card and change history | TIP candidate profiles and Action Party separation |
| Go to the Source | Always | Links to primary documents and explanation of limitations | Existing Open File and `[[s:n]]` footnote pipeline |

## Daily editorial lane (human-in-the-loop)
1. **Morning commissioning:** source feed + verified results delta + FEC/spending watch + official leadership records -> 5-10 candidate stories, each with original source, UTC and local timestamps, what changed, uncertainty, attribution.
2. **Priority triage:** editor selects 3–5 Daily Signal items and up to two video angles; do not equate popularity with importance or make unverified claims. Editorial decision recorded.
3. **Report and fact check:** `llf-story-scout` -> STORY_BRIEF.md + CLAIMS.csv -> separate independent `llf-factcheck-finalize` review. Unsupported claims blocked.
4. **Daily article:** versioned date under `/politics/daily/YYYY-MM-DD/`; archive rather than overwriting yesterday. Lead status may change but revision history remains.
5. **Videos:** two scripts derived from approved claims only; ElevenLabs narration script with intonation, Remotion shot plan/assets; voice recorded and renders by user/Claude; publish only after media QA and owner approval. Link video to specific source-rich LLF article.
6. **Social:** only after user supplies published video URLs, produce platform-specific X/Bluesky descriptions and accurate links. No fake published URL; preserve source/claim mapping.
7. **Publish:** owner -> Claude file ingest -> build strict -> independent QA -> owner sign-off -> manual deploy (existing process). New automated posting must have explicit separate approval.

## Standard article/brief handoff
`STORY_BRIEF.md`, `CLAIMS.csv`, `SOURCE_REGISTER.csv`, `EDITORIAL_NOTES.md`, `VIDEO_A_SCRIPT.md`, `VIDEO_B_SCRIPT.md`, `ASSET_MANIFEST.csv`, `PUBLICATION_RETURN.md` as applicable. Claims states VERIFIED / ATTRIBUTED / NEEDS_CONTEXT; sources marked opened/discovered. Use a stable `story_id` across article/video/social derivatives.

## Workload discipline
Do not demand 2 videos from low-news days; queue evergreen explainers with documented source freshness, or explicitly produce fewer. Reuse master assets and metadata, not duplicate original render files. Keep user manual editorial gateway intact.
