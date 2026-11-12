# `spec_file_commits`

Complete per-file commit history for the broad census.

- **Rows:** 780,335
- **Columns:** 24
- **Used for:** RQ3: who committed each spec file, and whether an AI agent is credited

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `id` | BIGINT |  | 100% | 780,335 | 1; 2; 3 |
| `file_url_sha16` | VARCHAR | 16-hex digest of the file's GitHub blob URL (primary key of the broad census). | 100% | 476,027 | fb18fdb7ee59c4ef; b4e935d20f854700; ef51eaeba1593bf0 |
| `repo_name` | VARCHAR | owner/repo slug (join key to every other layer). | 100% | 77,351 | docxology/codomyrmex; langoai/lango; smart-data-models/dataModel.EnergyCIM |
| `file_path` | VARCHAR | path within its repository. | 100% | 387,809 | SPEC.md; spec.md; docs/SPEC.md |
| `seq_from_oldest` | BIGINT |  | 100% | 548 | 1; 2; 3 |
| `commit_sha` | VARCHAR | commit hash. | 100% | 377,793 | d8b5f593166517ab81528e525cc960432522bfe1; 0c0aa68b95748b7120b4c71e3fe3a8bcef67fa4d; d0368668d4df1f9126102d0a0b275b0460ea189b |
| `node_id` | VARCHAR |  | 100% | 387,887 | C_kwDOQOR5qNoAKGQ4YjVmNTkzMTY2NTE3YWI4MTUyOGU1MjVjYzk2MDQzMjUyMmJmZTE; C_kwDOOZP2QdoAKDBjMGFhNjhiOTU3NDhiNzEyMGI0YzcxZTNmZTNhOGJjZWY2N2ZhNGQ; C_kwDOSBRG4NoAKGQwMzY4NjY4ZDRkZjFmOTEyNjEwMmQwYTBiMjc1YjA0NjBlYTE4OWI |
| `html_url` | VARCHAR |  | 100% | 387,889 | https://github.com/gesad-lab/baes_berk_20251103/commit/d8b5f593166517ab81528e525cc960432522bfe1; https://github.com/metorial/metorial/commit/0c0aa68b95748b7120b4c71e3fe3a8bcef67fa4d; https://github.com/metorial/integrations/commit/d0368668d4df1f9126102d0a0b275b0460ea189b |
| `message` | VARCHAR | The commit message. A 'Co-authored-by: Claude ...' line credits an AI agent (RQ3). | 100% | ~330,497 | update |
| `comment_count` | BIGINT |  | 100% | 7 | 0; 1; 2 |
| `authored_at` | VARCHAR | author timestamp. | 100% | 372,946 | 2025-11-03T11:48:53Z; 2026-07-02T07:36:38Z; 2026-04-13T09:45:51Z |
| `author_name` | VARCHAR |  | 100% | 65,967 | Alberto Abella; Claude; NewTester |
| `author_login` | VARCHAR | commit author GitHub login. | 87% | 44,942 | docxology; albertoabellagarcia; claude |
| `author_id` | BIGINT |  | 87% | 44,943 | 6911384; 59435267; 81847 |
| `author_type` | VARCHAR | User, Bot or Organization. Empty when no GitHub account matched the commit. | 87% | 3 | User; Bot; Organization |
| `committed_at` | VARCHAR | When the commit was made (text, ISO format). | 100% | 368,749 | 2025-11-03T11:48:53Z; 2026-07-02T07:36:38Z; 2026-04-13T09:45:51Z |
| `committer_name` | VARCHAR |  | 100% | 60,740 | GitHub; Alberto Abella; NewTester |
| `committer_login` | VARCHAR | committer GitHub login. | 87% | 40,827 | web-flow; docxology; albertoabellagarcia |
| `committer_id` | BIGINT |  | 87% | 40,828 | 19864447; 6911384; 59435267 |
| `committer_type` | VARCHAR |  | 87% | 3 | User; Bot; Organization |
| `tree_sha` | VARCHAR |  | 100% | 377,136 | 7ec0ac9e529664d0d3692bb0ac1601242b5c7ef0; 48e04fe910d29b09d4ec140254c46f3c9d356ee1; 03b6465d89dfe76ee394af47bd8bc78f041a67c8 |
| `parents` | VARCHAR |  | 94% | 356,171 | c4c38f74f75a577e4458b4fe38827aa8a13eaad7; 9cd61155576729551dc544b9bcd3d07f0dd60fa6; 322ddf97f3f6500ea28205b52f091cef29d1b728 |
| `verified` | BIGINT |  | 100% | 2 | 0; 1 |
| `verification_reason` | VARCHAR |  | 100% | 10 | unsigned; valid; unknown_key |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `id` | 8333 | 9418 | 12023 |
| `file_url_sha16` | 02b3b3995c934f53 | 03095d7ef0a92197 | 03d37a7aa14ed0da |
| `repo_name` | pabloimrik17/monolab | wongsorn-labs/atlas-lineage | ljoukov/spark |
| `file_path` | openspec/specs/npm-update-apply/spec.md | openspec/specs/person-management/spec.md | docs/SPEC.md |
| `seq_from_oldest` | 4 | 1 | 49 |
| `commit_sha` | a567925da1271394c60a69eb7f3b0324bbcb039c | 6204d3c3a9f4213526c2ec9d6355f51e6ee3ed62 | 70ffa24854a9822acbde80b6006b9aae1a2f018b |
| `node_id` | C_kwDOOYF3TtoAKGE1Njc5MjVkYTEyNzEzOTRjNjBhNjllYjdmM2IwMzI0YmJjYjAzOWM | C_kwDOSCeb39oAKDYyMDRkM2MzYTlmNDIxMzUyNmMyZWM5ZDYzNTVmNTFlNmVlM2VkNjI | C_kwDOPzZTx9oAKDcwZmZhMjQ4NTRhOTgyMmFjYmRlODBiNjAwNmI5YWFlMWEyZjAxOGI |
| `html_url` | https://github.com/pabloimrik17/monolab/commit/a567925da1271394c60a69eb7f3b0324bbcb039c | https://github.com/wongsorn-labs/atlas-lineage/commit/6204d3c3a9f4213526c2ec9d6355f51e6ee3ed62 | https://github.com/ljoukov/spark/commit/70ffa24854a9822acbde80b6006b9aae1a2f018b |
| `message` | Merge pull request #261 from pabloimrik17/feature/233-pnpm-named-catalogs ⏎  ⏎ feat: support pnpm named catalogs in npm- … | docs(shared): set up OpenSpec and baseline capability specs ⏎  ⏎ Initialize OpenSpec (spec-driven development) for Claud … | [fix/llm] generate specs with tests in ideas stage |
| `comment_count` | 0 | 0 | 0 |
| `authored_at` | 2026-07-09T17:47:32Z | 2026-07-03T17:39:08Z | 2025-11-27T14:29:27Z |
| `author_name` | Pablo F. Guerra | Claude | Liudmila Joukovskaya |
| `author_login` | pabloimrik17 | claude | ljoukov |
| `author_id` | 5611863 | 81847 | 22657507 |
| `author_type` | User | User | User |
| `committed_at` | 2026-07-09T17:47:32Z | 2026-07-03T17:39:08Z | 2025-11-27T14:29:27Z |
| `committer_name` | GitHub | Claude | Liudmila Joukovskaya |
| `committer_login` | web-flow | claude | ljoukov |
| `committer_id` | 19864447 | 81847 | 22657507 |
| `committer_type` | User | User | User |
| `tree_sha` | 19fb0519f71a2904b007778bc14ef6fe2ab376bb | 9d777dc90442f633cf1fa73378f680033a9a2e0f | 709f7b622237278a7189e2d0d5dc9f9fbe5a2eee |
| `parents` | c56f1f5bb562e0164dd300c19e07aded3229def8 | 48b3e72a71625bb109865d85dcbb975257923404 | 480c484957ed6b2b949cea299db88b691777d5ba |
| `verified` | 1 | 1 | 0 |
| `verification_reason` | valid | valid | unsigned |
