# `openspec_code_refs`

OpenSpec task-to-code references resolved against the repository git tree at the anchoring commit.

- **Rows:** 435,401
- **Columns:** 8
- **Used for:** RQ1, RQ2, RQ3: every file path named in a task, and whether that file exists

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `id` | BIGINT |  | 100% | 435,401 | 1; 2; 3 |
| `repo_name` | VARCHAR | owner/repo slug (join key to every other layer). | 100% | 7,076 | UndiFineD/obsidian-AI-assistant; BlackBeltTechnology/pi-agent-dashboard; langoai/lango |
| `artifact_path` | VARCHAR | The tasks.md file the path was found in. Its folder is the 'change'. | 100% | 61,295 | openspec/changes/archive/2026-02-12-frontend-react-migration/tasks.md; openspec/changes/bootstrap-project-skeleton/tasks.md; openspec/changes/archive/2025-11-06-add-shell-completions/tasks.md |
| `code_path` | VARCHAR | The file path written in the task text. | 100% | 262,508 | App.tsx; index.html; Next.js |
| `task_done` | BIGINT | 1 = the task's checkbox is ticked [x], 0 = not ticked [ ]. | 100% | 2 | 1; 0 |
| `anchor_sha` | VARCHAR | The commit whose file list was used to check the path. Empty = no anchor commit. | 95% | 42,552 | 6a8e0bc9d828f011623abb8c70eacbbb0b7d3d8e; 1b5ebc00c7e68529c99ad6b46fbeb9f7e991c79e; 208e108fb39d1eaa2a75120165653103aebb2a55 |
| `exists_at_anchor` | BIGINT | 1 = the file exists at the anchor commit; 0 = it does not (a 'missing' file, the RQ1 outcome); 2 = undocumented; empty = no anchor commit. | 95% | 3 | 1; 0; 2 |
| `resolved_path` | VARCHAR | The real file the path matched. Differs from code_path when it was matched by file name only. | 76% | 180,594 | index.html; src/main.rs; src/App.tsx |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `id` | 8131 | 9206 | 11775 |
| `repo_name` | adriangmrraa/clinicforge | AfoD3V/poke-hub | akatzmann/headmesh |
| `artifact_path` | openspec/changes/odontogram-v2-complete/tasks.md | openspec/changes/series-drill-down-search/tasks.md | openspec/changes/archive/2026-04-11-myopenceo-full-reimplementation/tasks.md |
| `code_path` | SurfacePath.tsx | LanguageSelector.svelte | tests/unit/test_employee.py |
| `task_done` | 1 | 1 | 1 |
| `anchor_sha` | ca4c35c2b50b0eb0f2765337e470f69a7bebb0ce | 6d0d781e896e0f24eeb0ac5595e006dd7cfcd9ee | d8f4389b5bd8127e263f86baf851e8a5ec20479f |
| `exists_at_anchor` | 1 | 1 | 0 |
| `resolved_path` | frontend_react/src/components/odontogram/SurfacePath.tsx | ui/src/lib/components/LanguageSelector.svelte | (empty) |
