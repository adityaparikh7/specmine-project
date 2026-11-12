# `repo_trees`

Metadata of the repository git tree that tree-provenance references resolve against.

- **Rows:** 73,030
- **Columns:** 5
- **Used for:** RQ1: tells us which repositories have an incomplete file listing

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `repo_name` | VARCHAR | owner/repo slug (join key to every other layer). | 100% | 73,030 | 0-CYBERDYNE-SYSTEMS-0/FFT_nano; 0-CYBERDYNE-SYSTEMS-0/expert-prompting-eval; 0-CYBERDYNE-SYSTEMS-0/generative-cockpit |
| `status` | VARCHAR | done = file list downloaded; truncated = GitHub cut it short; missing = not downloaded. | 100% | 4 | done; missing; truncated |
| `n_entries` | BIGINT | entries in the repository git tree. | 100% | 5,076 | 0; 120; 106 |
| `truncated` | BIGINT | 1 = the file list is incomplete, so 'missing' files there may not really be missing. | 100% | 2 | 0; 1 |
| `fetched_at` | VARCHAR |  | 100% | 10,745 | 2026-07-17T16:36:15Z; 2026-07-17T16:37:05Z; 2026-07-17T16:37:07Z |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `repo_name` | breez/passkey-login | caffeinepub/ai-chatbot_3 | caffeinepub/cybercase-manager |
| `status` | done | done | done |
| `n_entries` | 2 | 127 | 122 |
| `truncated` | 0 | 0 | 0 |
| `fetched_at` | 2026-07-17T18:32:18Z | 2026-07-17T17:53:59Z | 2026-07-17T17:23:03Z |
