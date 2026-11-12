# `pr_files`

PR layer (the 11 per-tool <tool>_pr_files tables unioned): the per-file changeset of each spec-touching PR (complete up to GitHub's 3,000-file-per-PR cap), each file flagged spec/code.

- **Rows:** 348,141
- **Columns:** 12
- **Used for:** Not used

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `tool` | VARCHAR | SDD tool this PR row was discovered under (10 of the 11 swept tools appear; specweave yielded none). | 100% | 10 | openspec; speckit; claude_code |
| `id` | BIGINT |  | 100% | 215,996 | 1; 2; 3 |
| `repo_name` | VARCHAR | owner/repo slug (join key to every other layer). | 100% | 581 | langoai/lango; carverauto/serviceradar; zhukunpenglinyutong/desktop-cc-gui |
| `pr_number` | BIGINT | pull request number. | 100% | 2,327 | 1; 26; 7 |
| `file_path` | VARCHAR | path within its repository. | 100% | 243,694 | README.md; CLAUDE.md; CHANGELOG.md |
| `change_status` | VARCHAR | per-file status: added / modified / removed. | 100% | 4 | added; modified; removed |
| `additions` | BIGINT | lines added. | 100% | 2,185 | 0; 1; 2 |
| `deletions` | BIGINT | lines removed. | 100% | 1,789 | 0; 1; 2 |
| `is_specdir` | BIGINT | 1 if the file sits under the spec directory. | 100% | 2 | 0; 1 |
| `is_spec` | BIGINT | 1 if the changed file is a spec. | 100% | 2 | 0; 1 |
| `is_code` | BIGINT | 1 if the changed file is source code. | 100% | 2 | 0; 1 |
| `ext` | VARCHAR | file extension. | 100% | 680 | md; ts; go |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `tool` | openspec | openspec | openspec |
| `id` | 8132 | 9207 | 11776 |
| `repo_name` | langoai/lango | igamenovoer/houmao | zhukunpenglinyutong/desktop-cc-gui |
| `pr_number` | 23 | 4 | 613 |
| `file_path` | internal/cli/security/secrets.go | scripts/demo/legacy/houmao-server-agent-api-demo-pack/inputs/project-template/src/mailbox_demo/__init__.py | src/components/ui/RendererContextMenu.tsx |
| `change_status` | modified | renamed | modified |
| `additions` | 26 | 0 | 231 |
| `deletions` | 9 | 0 | 42 |
| `is_specdir` | 0 | 0 | 0 |
| `is_spec` | 0 | 0 | 0 |
| `is_code` | 1 | 1 | 1 |
| `ext` | go | py | tsx |
