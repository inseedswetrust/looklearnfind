# INSTALL_REPORT: LLF Canonical Local Workflow & Skills Lock v2.0

Installed 2026-10-28 into the existing LookLearnFind repository (`C:\Users\Red Right Hand\Desktop\Issues Party\looklearnfind`, branch `claude/funny-shannon-dg9qoe`, local commits, nothing pushed). The package was `LLF_CANONICAL_LOCAL_WORKFLOW_AND_SKILLS_LOCK_2026-10-24.zip`, followed per `04_CLAUDE_INSTALL_AND_TESTS.md`. Installation commit: the one titled "Install LLF Production Lock v2.0" (see `git log`).

**Result: PASS** for the install and the nine acceptance tests; **PARTIAL** on three items listed under "Limits". Not done, by instruction: no Michigan production, no pages published or uploaded, no video rendered, no new research.

## 1. What was audited first (and preserved)
Root `CLAUDE.md`, `docs/election-build/INDEX.md`, `AGENT_RUNBOOK.md`, `PUBLISHING_RULES.md`, the eleven installed skills, `tools/video/*` (Florida builders, footage tools), the workflow ledger and transitions tool, the story and fact-check gates, the build and the site tests. Nothing newer was downgraded: the article skills (`llf-story-scout`, `llf-article-format`, `llf-factcheck-finalize`, `llf-election-render`) kept their content (only a pointer line in `llf-article-format`), the page templates, `elections.py`, `build.py` and the QA scripts are unchanged, and the Illinois discovery files are byte-for-byte as returned (`git diff` on `docs/illinois` and `data/elections/IL` shows only one new file).

## 2. Installed paths
| Path | What |
|---|---|
| `docs/production/00_READ_FIRST.md` to `07_STARTER_PROMPT_FOR_CLAUDE.md`, `ROOT_CLAUDE_POINTER.txt` | the package text, verbatim (06 has install decisions appended) |
| `docs/production/templates/` | `SCENES.csv`, `TRANSITIONS.csv`, `ASSETS.csv` (package; ASSETS gained a last column `aspect_ratio`), `FACTS.csv` (new) |
| `docs/production/skills/llf-video-director.PACKAGE_ORIGINAL.md` | the skill as packaged |
| `docs/production/README.md`, `INSTALL_REPORT.md`, `DATA_ACCESS_LIMITATIONS.md`, `WORKFLOW_LOG.md` | index and precedence, this report, the register of unreadable sources, the log |
| `docs/production/SKILL_MANIFEST.json` and `.md` | shared skill version manifest (generated; `tools/qa/skill_manifest.py --check` fails if stale) |
| `.claude/skills/llf-video-director/SKILL.md` | the single canonical video skill, 2.0.0 |
| `tools/video/scene_pack.py` | asset-first pack scaffolder and checker (`init`, `check`, `production`); assets only |
| `tools/qa/skill_manifest.py` | manifest generator and checker |
| `tools/workflow/transitions.py` | new lanes `production:` and `render:`, authorization and independent-reviewer gates |
| `productions/2026/IL/` | the folder tree and a README pointing at the Illinois material that stays where it was produced (not moved) |
| `tests/test_production_lock.py` | 23 tests: the nine acceptance tests and install checks |
| `docs/illinois/DATA_ACCESS_LIMITATIONS.md` | the Illinois State Board of Elections limitation (new file; the returned files are untouched) |
| `CLAUDE.md` (top block), `docs/election-build/INDEX.md` ("Production lock" section first), `AGENT_RUNBOOK.md` (sections 4 and 5 rewritten), `PUBLISHING_RULES.md` (R11 to R15) | startup pointers and updated commands |

## 3. Skill inventory (12; generated manifest in `SKILL_MANIFEST.md`)
`llf-story-scout` 1.0.0 · `llf-article-format` 1.3.1 · `llf-factcheck-finalize` 2.2.0 · `llf-election-render` 1.1.0 · `llf-publication-qa` 1.4.0 · **`llf-video-director` 2.0.0 (new)** · `llf-footage-scout` 1.1.0 · `llf-video-storyboard` 2.0.0 (legacy alias) · `election-state-packet` 1.0.2 · `darkhorse-source-monitor` 1.1.1 · `llf-delta-editorial` 1.0.0 · `workflow-retrospective` 1.0.0. The last three gained a header version line (they carried it only in a Contract section).

## 4. How the video skills were integrated (no duplication)
One entry point, `llf-video-director`. `llf-video-storyboard` keeps its Florida procedure text under a "Legacy procedure (Florida example only)" heading, its scripts and its tests, with a notice at the top and a description that begins "LEGACY ALIAS". `llf-footage-scout` is now the REAL_CLIP search sub-procedure and no longer downloads or cuts clips unless the owner explicitly asks for a specific `CLEARED` clip. `llf-publication-qa`'s video section now runs `scene_pack.py check`.

## 5. Code changes
- `tools/video/scene_pack.py` (new): script-led timing (no fixed segment length), `SCENES.csv`, `ASSETS.csv`, `TRANSITIONS.csv`, `FACTS.csv`, clip sources and rights, paired start/end frames with aspect-ratio matching, script-lock gate, hashed assets, no video file allowed in a pack.
- `tools/video/build_video_pack.py` (legacy Florida builder): per-segment `seconds` allowed (the 5-second default is no longer required), `--render-video --authorization` gate (records the request in `docs/production/RENDER_REQUESTS.log`, exits 3, renders nothing, no renderer ships), a guard that fails if its output contains any video file, and a refusal for non-Florida specs. `init_state_spec.py` refuses without `--legacy`. `build_visual_direction.py` follows the per-segment seconds.
- `tools/workflow/transitions.py`: lanes `production:` (12 canonical stages) and `render:` (separately authorized); `ARTICLE_PUBLISHED`, `PUBLISHED`, `DEPLOYED`, `OWNER_PUBLISH_APPROVED` and `VIDEO_RENDER_REQUESTED` need an authorization; `ARTICLE_FACTCHECKED` and `FACT_CHECKED` need a reviewer other than the actor. `seed_backfill.py` passes a backfill authorization and reviewer for its reconstructed entries.

## 6. Acceptance tests (04_CLAUDE_INSTALL_AND_TESTS.md, section 5)
| Test | Result | Evidence |
|---|---|---|
| a Michigan intake has no Florida names or market numbers | PASS | `test_a_michigan_intake_contains_no_florida_entities` (scaffold into a temp folder, 11 Florida terms searched) |
| b default builder produces no MP4 | PASS | `test_b_default_builders_produce_no_video`, `test_b_a_render_needs_the_owners_explicit_words`, `test_b_the_legacy_builder_and_spec_template_are_fenced`, `test_a_video_file_in_a_pack_fails` |
| c every scene has a prompt or a real source | PASS | `test_c_every_scene_has_a_prompt_or_a_real_source` |
| d paired transitions use both IDs and a matching aspect ratio | PASS | `test_d_paired_transitions_use_both_ids_and_a_matching_aspect_ratio` |
| e ungraded issues are not negative | PASS | `test_e_ungraded_tip_records_are_never_shown_as_failing` |
| f rights statuses are explicit | PASS | `test_f_rights_statuses_are_explicit` |
| g the story gate does not require finance | PASS | `test_g_the_story_gate_does_not_require_irrelevant_finance` |
| h no unauthorized publication | PASS | `test_h_nothing_is_published_deployed_or_rendered_without_recorded_authorization` |
| i independent fact-check status recorded | PASS | `test_i_independent_factcheck_status_is_recorded`, `test_script_is_locked_before_scene_art_and_review_is_independent` |
Also covered: script-led timing, dated market and poll facts, numbers and people follow the facts, hashed assets, one video entry point, a current manifest, startup pointers, and the preserved Illinois material.

## 7. Regression results (commands run 2026-10-28)
- Full regression (`python -W ignore -m unittest tests/test_dark_horse.py tests/test_phase_a.py tests/test_factcheck_gate.py tests/test_workflow.py tests/test_story_scout.py tests/test_video_pack.py tests/test_footage_pack.py tests/test_production_lock.py`): **Ran 113 tests, OK**.
- `python build.py --strict`: 0 violations, 113 pages built.
- `python tests/links_test.py`: links ok.
- `python tools/qa/skill_manifest.py --check`: manifest current, 12 skills.

## 8. Conflicts reconciled
| Older instruction | Lock v2.0 | Resolution |
|---|---|---|
| fixed 18 x 5-second storyboard for every state | timing follows the script | Florida kept as a labeled example; the builder refuses other states |
| `llf-video-storyboard` as entry point, footage-first sequence in CLAUDE.md | one entry point, script then storyboard then scene visuals | `llf-video-director` is the entry; the real-people rules from the footage-first order are kept; the sequence follows the Lock |
| `llf-footage-scout` downloads and cuts cleared clips | the owner chooses and captures footage | no download by default; acquisition only on an explicit request for a specific `CLEARED` clip |
| AI only for empty plates and transitions | ChatGPT makes on-brand concept stills; Midjourney animates start/end pairs | both allowed as illustration; never a candidate likeness, never evidence, never exact data |
| lanes `story:` and `video:` | a 12-stage production lane and a separate render lane | new lanes added; old lanes remain valid for existing entries |
| `init_state_spec.py` for new states | `scene_pack.py init` | old tool needs `--legacy` |

## 9. Unresolved conflicts and limits (for the owner)
1. **Florida script.** The Lock says the Florida script is finalized in ChatGPT separately. The Florida spec, script table and pitch in `data/video/` and `docs/video/` are the earlier draft and may disagree with the final; they are marked as the legacy example, not a source of truth.
2. **Midjourney settings.** The contract requires settings checked against Midjourney's current official documentation on production day. That was not researched (the install forbids new research); `setting_verified_date` is required before a transition can be marked ready.
3. **Existing Florida footage files.** Earlier footage selects (git-ignored, `assets/video/florida-2026/`) were created under the older acquisition rule and are left in place; no new download will happen by default.
4. **Lane migration.** Existing `story:` and `video:` ledger entries are not rewritten into the new lanes (the ledger is append-only); future work uses the `production:` lane.
5. **Data access.** The Illinois State Board of Elections list is unreadable to automated access (HTTP 403): the Illinois roster is not official or complete and its `isbe_verified` column is PENDING. Recorded in `docs/production/DATA_ACCESS_LIMITATIONS.md`. The discovery is not repeated.
6. **Asset generation and rendering** need the owner's tools (ChatGPT images, Midjourney, Premiere); none was done or simulated.

## 10. Portable knowledge center for ChatGPT
`release/LLF_KNOWLEDGE_CENTER_2026-10-28.zip` (not committed): `docs/production/`, the twelve skills, `CLAUDE.md`, the index, runbook, publishing rules, article schemas, the templates and the manifest. ChatGPT does not have these skills installed: give it this ZIP at the start of each project.
