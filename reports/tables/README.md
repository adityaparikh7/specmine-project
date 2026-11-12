# SpecMine tables at a glance

One page per table in this folder. Start with the tables marked RQ.

| Table | Rows | Columns | Used for |
|---|---|---|---|
| [`openspec_code_refs`](openspec_code_refs.md) | 435,401 | 8 | RQ1, RQ2, RQ3: every file path named in a task, and whether that file exists |
| [`openspec_artifact_files`](openspec_artifact_files.md) | 266,230 | 12 | RQ1, RQ2: the text of each tasks.md (to read the task line and its verb) |
| [`repo_trees`](repo_trees.md) | 73,030 | 5 | RQ1: tells us which repositories have an incomplete file listing |
| [`spec_files`](spec_files.md) | 470,795 | 124 | RQ2, RQ3: repository facts (stars, language, age) and which tool made each spec |
| [`spec_file_commits`](spec_file_commits.md) | 780,335 | 24 | RQ3: who committed each spec file, and whether an AI agent is credited |
| [`spec_links`](spec_links.md) | 2,421,323 | 5 | Checked for RQ3 (agent config files); not used in the end |
| [`spec_content_features`](spec_content_features.md) | 468,307 | 40 | Not used |
| [`kiro_files`](kiro_files.md) | 98,574 | 12 | Not used |
| [`pull_requests`](pull_requests.md) | 5,992 | 25 | One sentence in RQ3 (branch names like claude/...) |
| [`pr_files`](pr_files.md) | 348,141 | 12 | Not used |

## How the tables connect

- `repo_name` (owner/repo) links every table to every other.
- `file_url_sha16` links `spec_files`, `spec_file_commits` and `spec_content_features`; `spec_links.spec_url_sha16` is the same key.
- `openspec_code_refs.artifact_path` = `openspec_artifact_files.file_path` (same repo): the tasks.md a path came from.
- `pr_files` joins `pull_requests` on (`tool`, `repo_name`, `pr_number`).
