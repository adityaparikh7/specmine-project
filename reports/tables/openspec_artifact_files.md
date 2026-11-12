# `openspec_artifact_files`

OpenSpec change proposals, designs, and task lists with parsed task counts and raw content.

- **Rows:** 266,230
- **Columns:** 12
- **Used for:** RQ1, RQ2: the text of each tasks.md (to read the task line and its verb)

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `id` | BIGINT |  | 100% | 266,230 | 1; 2; 3 |
| `repo_name` | VARCHAR | owner/repo slug (join key to every other layer). | 100% | 8,366 | langoai/lango; UndiFineD/obsidian-AI-assistant; BlackBeltTechnology/pi-agent-dashboard |
| `file_path` | VARCHAR | path within its repository. | 100% | 260,708 | openspec/changes/archive/2025-01-11-add-update-command/design.md; openspec/changes/archive/2025-01-11-add-update-command/proposal.md; openspec/changes/archive/2025-01-11-add-update-command/tasks.md |
| `kind` | VARCHAR | Which document: proposal.md, design.md or tasks.md. | 100% | 7 | proposal.md; tasks.md; design.md |
| `content` | VARCHAR | The full Markdown text of the document. | 99% | ~236,285 | # Proposal: Workflow Improvements (Fast Lanes, Parallelization, Validation Hooks) ⏎  ⏎ **Change ID**: `workflow-improvem … |
| `content_sha` | VARCHAR |  | 99% | 256,134 | 49ccab2cca7144b8e1c8f2b536575c91db65bf606bd2e90eee7872a9e36b8975; 0da9d6607488b594b97f43ad211449b3283d28b95f3c8df16e0eaeee1313b7ad; 12daef9207d1009693e41d65836f8b29d740961a884db6a60c9fd8b994e2e1c0 |
| `n_bytes` | BIGINT |  | 99% | 20,269 | 44392; 67317; 1903 |
| `n_tasks` | BIGINT | Number of checkbox tasks in a tasks.md. | 35% | 334 | 9; 12; 8 |
| `n_tasks_done` | BIGINT | Number of those tasks that are ticked. | 35% | 284 | 0; 9; 12 |
| `n_code_refs` | BIGINT | code paths named in tasks.md. | 35% | 61 | 0; 1; 2 |
| `fetch_status` | VARCHAR | done = text downloaded; missing = could not be downloaded. | 100% | 2 | done; missing |
| `fetched_at` | VARCHAR |  | 100% | 3,783 | 2026-07-20T22:57:01Z; 2026-07-20T22:57:00Z; 2026-07-20T23:49:53Z |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `id` | 8130 | 9205 | 11774 |
| `repo_name` | aladrocMatiner/compose-traeffik | alexei-lexx/budget | alxgalache/kuadrat |
| `file_path` | openspec/changes/archive/2026-03-03-add-observability-stack-for-traefik-ctfd/proposal.md | openspec/changes/archive/2026-03-18-show-agent-trace-on-failure/proposal.md | openspec/changes/archive/2026-05-24-multi-image-products/tasks.md |
| `kind` | proposal.md | proposal.md | tasks.md |
| `content` | # Change: Add reusable observability stack for Traefik-based deployments (Prometheus + Grafana + Loki) ⏎  ⏎ ## Why ⏎ The … | ## Why ⏎  ⏎ When an AI-powered operation fails, the agent trace is discarded before it reaches the frontend — the agent  … | ## 1. Database schema ⏎  ⏎ - [x] 1.1 In `api/config/database.js`, remove the `basename TEXT NOT NULL` (and `basename TEX … |
| `content_sha` | f3107e899a0775ef0ade5ea72ec65f54986723d43c5dc48c08270e17fd078d3e | d43f9ec4ed64bcd9ece2ae8403b818c10bdfb859ae40414b6e80fed87672223c | e11aca224d1978ac49784f2556e8c52a5a2c88e114b07660ccd157caaf48a449 |
| `n_bytes` | 4394 | 3039 | 19190 |
| `n_tasks` | <NA> | <NA> | 108 |
| `n_tasks_done` | <NA> | <NA> | 108 |
| `n_code_refs` | <NA> | <NA> | 44 |
| `fetch_status` | done | done | done |
| `fetched_at` | 2026-07-20T22:48:59Z | 2026-07-20T22:49:23Z | 2026-07-20T22:49:42Z |
