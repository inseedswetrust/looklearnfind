# Agent/skill map (no duplicate machinery)

Skill = tested, versioned institutional procedure. Tool = deterministic operation/API. Agent = autonomous role using skills/tools. Workflow = ordered stages. Knowledge center = durable local files and source/asset/decision ledgers.

| Role | Operator | Skills & tools | Required output |
|---|---|---|---|
| Research | Claude agent | `llf-story-scout`, optional `election-state-packet`, `darkhorse-source-monitor`; official rosters, existing TIP export, news search | STORY_BRIEF, CLAIMS, source/candidate mapping |
| Editorial | ChatGPT | `llf-article-format`, `llf-delta-editorial` when appropriate, editorial source packet | Full article drafts, script, narrative/hook decisions |
| Standards | Independent Claude/reviewer distinct from author | `llf-factcheck-finalize`, `llf-publication-qa` | verified claims and rights flags, approval exceptions |
| Web production | Claude agent | `llf-election-render`, site tools, manifests | implemented pages, CSS, site images, QA, publish package and URLs |
| Video direction | ChatGPT working with Claude's installed portable `llf-video-director` | current brand/stills, validated storyboard spec, Midjourney guide | scene prompts, on-brand stills, transition pairs, capture instructions, Premiere notes |
| Operational | Claude agent | `workflow-retrospective`, data feeds, state ledger | status, time, decisions, improvements, version history |
| Human | Owner | Midjourney, Premiere Pro, footage capture, editorial approval | approved motion clips/edit, explicit publication/render authorizations |

Keep existing article and QA skills, six concept schemas and market/poll collectors. Add/upgrade ONE video director skill and adjust builder to **no-render default**. Use repo-stored markdown and templates to pass identical skills to ChatGPT; cross-model skills must be loaded, not merely assumed to exist.
