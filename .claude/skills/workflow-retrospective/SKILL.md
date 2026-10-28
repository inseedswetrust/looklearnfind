---
name: workflow-retrospective
description: After each state, story or daily-monitor incident, record what worked, what failed and why, and propose skill or script improvements with a regression fixture. Does not change rules or skills on its own.
---

# workflow-retrospective

**Version** 1.0.0 (header added 2026-10-28; the Contract section below carries the same number)

## Inputs
`docs/election-build/WORKFLOW_LOG.md`, `data/elections/dark_horse/status.json`, run manifests, reviewer notes, corrections.

## Output
1. A dated entry in the workflow log: stage, tool, action, result, decision, obstacle.
2. For each failure cause (blocked source, wrong match, date/timezone bug, duplicate data): a proposed change and a regression fixture added to `tests/` before the change is made.
3. An owner approval request. Skills and thresholds (for example the 3-point change threshold in `daily.py`) change only after approval and with a changelog line.

## Never
rewrite an approved skill, alter a truth standard or loosen a publishing rule automatically.

## Contract (v1.0.0)
**Owner** LLF production. **Type** instruction skill; proposes changes, never edits a skill or threshold itself. **Input** the workflow ledger (`data/elections/workflow_ledger.jsonl`), the fact-check ledger and the correction log of a shipped article. **Output** a dated entry in `docs/election-build/WORKFLOW_LOG.md` plus a separate proposal list for owner approval. **Fixtures** none yet (first retrospective is due after the first Phase C article ships). **Failure semantics** a missing ledger is reported as a gap, not reconstructed.
## Video additions (2026-10-24)
For a shipped video also record: segments changed after QA and why, facts that went stale between spec and posting, generated plates rejected and the reason (text, faces, artifacts), hours spent on image generation versus assembly, and hook performance (3-second hold, average watch percentage, shares and saves per reach) for each hook cut. Propose spec or validator changes separately for owner approval.

## Changelog
1.0.0 (2026-10-23) first version.
