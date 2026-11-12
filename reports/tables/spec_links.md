# `spec_links`

Census-wide traceability index: typed references from each spec to code, sibling docs, PRs, issues, and branches.

- **Rows:** 2,421,323
- **Columns:** 5
- **Used for:** Checked for RQ3 (agent config files); not used in the end

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `id` | BIGINT |  | 100% | 2,421,323 | 1; 2; 3 |
| `spec_url_sha16` | VARCHAR | file_url_sha16 of the spec this reference belongs to (FK to spec_files). | 100% | 349,653 | 0ac6ec30d2ac0a5e; 0b905ae58dfe28c4; 0fce4b6f0f164da5 |
| `rel` | VARCHAR | reference target type: code / sibling / pr / ref / branch / issue / anchor. | 100% | 7 | code; sibling; pr |
| `target` | VARCHAR | the referenced value (path, PR number, issue, branch, ...). | 100% | 859,322 | build.sh; #1; deploy.sh |
| `provenance` | VARCHAR | how the reference was found: tasks / tree / commit_msg / branch_header / content. | 100% | 5 | tasks; tree; commit_msg |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `id` | 1283056 | 1283675 | 1284772 |
| `spec_url_sha16` | 00cd113305a677e9 | 00e83b72d7714b83 | 01337db7ab7dfcc3 |
| `rel` | code | code | code |
| `target` | app/agent/tools.py | test/features/accounting/usage/decorators/test_x_ai_usage_tracking_decorator.py | lib/set_orch/issues/manager.py |
| `provenance` | tasks | tasks | tasks |
