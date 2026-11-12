# `pull_requests`

PR layer (the 11 per-tool <tool>_prs tables unioned, 10 non-empty, with a `tool` column): every pull request that touches a spec file, one row per PR.

- **Rows:** 5,992
- **Columns:** 25
- **Used for:** One sentence in RQ3 (branch names like claude/...)

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `tool` | VARCHAR | SDD tool this PR row was discovered under (10 of the 11 swept tools appear; specweave yielded none). | 100% | 10 | openspec; speckit; moai |
| `id` | BIGINT |  | 100% | 4,231 | 1; 2; 3 |
| `repo_name` | VARCHAR | owner/repo slug (join key to every other layer). | 100% | 581 | elastic/terraform-provider-elasticstack; modu-ai/moai-adk; alfredoperez/speckit-companion |
| `pr_number` | BIGINT | pull request number. | 100% | 2,327 | 1; 7; 3 |
| `title` | VARCHAR | PR title. | 100% | 5,918 | Dev; Develop; Feature/cluster |
| `state` | VARCHAR | open/closed. | 100% | 1 | closed |
| `is_merged` | BIGINT | 1 if merged. | 100% | 1 | 1 |
| `merged_at` | VARCHAR | merge timestamp. | 100% | 5,972 | 2026-06-04T09:44:43Z; 2026-06-12T10:39:17Z; 2026-06-11T02:39:28Z |
| `created_at` | VARCHAR | PR creation timestamp. | 100% | 5,974 | 2026-06-04T09:44:32Z; 2026-06-12T10:38:00Z; 2026-06-10T11:16:53Z |
| `closed_at` | VARCHAR |  | 100% | 5,971 | 2026-06-04T09:44:43Z; 2026-06-12T10:39:17Z; 2026-06-11T02:39:28Z |
| `author_login` | VARCHAR | commit author GitHub login. | 100% | 744 | tobio; alfredoperez; GoosLab |
| `head_branch` | VARCHAR | source branch. | 100% | 5,589 | dev; main; master |
| `base_branch` | VARCHAR | target branch. | 100% | 108 | main; master; develop |
| `n_files` | BIGINT | files changed in the PR. | 100% | 398 | 6; 10; 8 |
| `n_specdir_files` | BIGINT |  | 100% | 184 | 6; 8; 5 |
| `n_spec_files` | BIGINT | spec files changed. | 100% | 105 | 1; 2; 4 |
| `n_code_files` | BIGINT | code files changed. | 100% | 279 | 0; 2; 3 |
| `n_md_files` | BIGINT |  | 100% | 133 | 0; 1; 2 |
| `n_other_files` | BIGINT |  | 100% | 142 | 0; 1; 2 |
| `additions` | BIGINT | lines added. | 100% | 3,466 | 0; 18; 21 |
| `deletions` | BIGINT | lines removed. | 100% | 1,394 | 0; 2; 1 |
| `files_status` | VARCHAR |  | 100% | 1 | done |
| `touches_code` | BIGINT | 1 when the PR changes at least one code file outside the spec directory (co-change signal). | 100% | 2 | 1; 0 |
| `n_code_outside` | BIGINT | code files changed outside the spec directory. | 100% | 277 | 0; 2; 3 |
| `n_prs_in_repo` | BIGINT | total spec-touching PRs in the repo. | 100% | 66 | 327; 134; 1 |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `tool` | openspec | openspec | speckit |
| `id` | 2220 | 4989 | 571 |
| `repo_name` | qixing-jk/all-api-hub | kalbasit/ncps | alfredoperez/speckit-companion |
| `pr_number` | 571 | 1288 | 89 |
| `title` | feat(webdav): add selective sync data selection | test(cache,server): assert row counts via Ent | fix(spec-viewer): prevent tab clicks from mutating workflow currentStep |
| `state` | closed | closed | closed |
| `is_merged` | 1 | 1 | 1 |
| `merged_at` | 2026-03-06T16:29:04Z | 2026-05-29T20:01:16Z | 2026-04-14T00:52:49Z |
| `created_at` | 2026-03-06T11:51:23Z | 2026-05-29T17:16:51Z | 2026-04-14T00:43:34Z |
| `closed_at` | 2026-03-06T16:29:04Z | 2026-05-29T20:01:16Z | 2026-04-14T00:52:49Z |
| `author_login` | qixing-jk | kalbasit | alfredoperez |
| `head_branch` | feat/webdav-selective-sync-data | refactor/trim-test-raw-sql-counts | 066-fix-viewer-step-state |
| `base_branch` | main | main | main |
| `n_files` | 26 | 8 | 9 |
| `n_specdir_files` | 6 | 6 | 4 |
| `n_spec_files` | 2 | 2 | 1 |
| `n_code_files` | 16 | 2 | 4 |
| `n_md_files` | 0 | 0 | 1 |
| `n_other_files` | 4 | 0 | 0 |
| `additions` | 3696 | 157 | 458 |
| `deletions` | 245 | 40 | 14 |
| `files_status` | done | done | done |
| `touches_code` | 1 | 1 | 1 |
| `n_code_outside` | 16 | 2 | 4 |
| `n_prs_in_repo` | 65 | 101 | 184 |
