# LookLearnFind (LLF) election desk: instructions for any agent session

Static site built by `build.py` (stdlib Python) with election pages from `elections.py`. Companion project: The Issues Party (TIP), a separate Next.js repo that holds candidate profiles and issue grades; LLF only reads and links to it.

**Start here:** `docs/election-build/AGENT_RUNBOOK.md` (end to end, with commands), then `docs/election-build/INDEX.md` (where everything is). Skills are in `.claude/skills/`: `llf-story-scout`, `llf-article-format`, `llf-election-render`, `llf-factcheck-finalize`, `llf-publication-qa`, `llf-video-storyboard`, `election-state-packet`, `darkhorse-source-monitor`, `llf-delta-editorial`, `workflow-retrospective`.

## Rules that never change
- Scope: Governor, U.S. Senate, U.S. House. Neutral reporting; no win probabilities; no causal claims about spending or prices; no rankings or endorsements.
- R1 the first mention of a featured candidate links to their TIP profile; R2 every mentioned race links to that race; a grade is cited only from the profile that shows it; "not graded" is never zero.
- Reported numbers are attributed ("according to <outlet>") and never called audited. A search snippet is not reporting: open the article.
- The drafter does not check their own article. Nothing is published, posted, uploaded or written to a production database without the owner's approval.
- Finance data (FEC) is optional and never a gate. Story first, proof enough.
- Style: no Oxford comma ("first, second and third"). Plain, precise, no hype.
- No synthetic footage of real people or events. Generated images carry no information, people, text or numbers; AI visuals and the synthetic narrator are disclosed.

## Commands you will use
`python3 build.py --strict` (must say 0 violations) · `python3 -m unittest tests/test_dark_horse.py tests/test_phase_a.py tests/test_factcheck_gate.py tests/test_workflow.py tests/test_story_scout.py tests/test_video_pack.py` · `python3 tools/qa/factcheck_gate.py <claims.csv> --article <file>` · `python3 tools/video/build_video_pack.py <spec.json>`.

## Windows notes
Use `PYTHONUTF8=1`; prefix `MSYS_NO_PATHCONV=1` when passing a URL path starting with `/` from Git Bash; stop the local server (`python -m http.server 8091` in `dist/`) before running `build.py`; write files that contain quotes with the editor tool, not shell heredocs.

## Do not
Overwrite an installed skill without reading it; upload `release/looklearnfind-site.zip` (older build, overwrites the live robots.txt); store or print keys; re-run the removed FEC Schedule B pull.
