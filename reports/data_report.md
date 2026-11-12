# SpecMine data report (Phase 1)

Generated 2026-11-12 17:22 by `src/checks/data_report.py` on the full dataset. Do not edit by hand: rerun `python run.py checks`.

## Summary

- **Tables.** All 10 tables load through `lib/db.py`; every row count matches the SpecMine README and every column matches `schema.sql`.
- **Caveats.** 28 checks: 17 reproduced, 3 close, 2 differ (each explained), 4 new, 2 descriptive.
- **RQ3 change coverage.** 99.9% of 16,342 changes with a checked create task (strict verbs) have a commit on a spec delta in their folder (99.9% with broad verbs), well above the 50.0% threshold, so change-level credit is usable. But 95.0% of covered changes have exactly one such commit, often the archive commit (decision 7).
- **RQ3 anchor commits.** 99.8% of 43,028 anchor commits are spec commits, and for 60,710 of 60,837 changes the anchor is a commit on that change's own spec delta. Keep the anchor-commit measure; it is nearly the same commit as the change-level one.
- **RQ3 config files.** Not answerable corpus-wide: `spec_links` names a root config file in 0 repositories, and code refs never hold `.md` paths. The PR layer shows config files changed in 331 of 581 repositories, a lower bound for that subsample only. Cite the undercount from the git-history pilot.
- **Sample.** 200 repositories, 191,945 rows across 10 tables, 28.5 MB in `data/sample/`.

## Decisions for Phases 2 and 3

1. Inner-join `spec_file_commits` to `spec_files`, then deduplicate on `(repo_name, commit_sha)`: the joined rows are commit-file pairs, roughly two per commit.
2. Deduplicate `spec_files` on `(repo_name, file_path)` before any file-level count (caveat N2: the same file captured at two commits).
3. Key the PR tables on `(tool, id)` or `(tool, repo_name, pr_number)`; `id` alone repeats across tools (N3).
4. Treat refs with `exists_at_anchor = 1` and no `resolved_path` as existing, with `exact_match` unknown (N1).
5. Report agent-trailer shares with and without Caffeine's `forge@caffeine.ai` trailer (C3); October's 22% is the share without it.
6. Use `min(col || '')` for min/max of text columns read straight from Parquet: DuckDB otherwise answers from truncated Parquet statistics (e.g. `2009-03-`).
7. RQ3 can use change-level credit and the anchor commit, but 95.0% of changes have a single spec-delta commit. For archived changes that commit's message mentions archiving 53.0% of the time, and 14.5% of change commits touch several changes at once. Credit therefore means 'an agent is credited on the commit that wrote or archived the change's spec', not 'an agent wrote its code'. Say so in the paper.

## 1. Tables

| Table | Rows | README | Columns | Repos | Key | Duplicate keys | Columns with nulls |
|---|---|---|---|---|---|---|---|
| openspec_code_refs | 435,401 | 435,401 | 8 | 7,076 | id | 0 | 3 |
| openspec_artifact_files | 266,230 | 266,230 | 12 | 8,366 | id | 0 | 6 |
| repo_trees | 73,030 | 73,030 | 5 | 73,030 | repo_name | 0 | 0 |
| spec_files | 470,795 | 470,795 | 124 | 73,031 | file_url_sha16 | 0 | 58 |
| spec_file_commits | 780,335 | 780,335 | 24 | 77,351 | id | 0 | 7 |
| spec_links | 2,421,323 | 2,421,323 | 5 |  | id | 0 | 0 |
| spec_content_features | 468,307 | 468,307 | 40 |  | file_url_sha16 | 0 | 0 |
| kiro_files | 98,574 | 98,574 | 12 | 12,910 | id | 0 | 0 |
| pull_requests | 5,992 | 5,992 | 25 | 581 | tool+repo_name+pr_number | 0 | 0 |
| pr_files | 348,141 | 348,141 | 12 | 581 | tool+id | 0 | 0 |

Per-column profiles (null share, distinct values, min/max, top values) are in `reports/profile/<table>.csv`. Schema check against `schema.sql`: no differences.

## 2. Joins

| Join | Keys | Used by | Left rows | Matched | Match |
|---|---|---|---|---|---|
| code refs -> tasks.md text | repo_name+artifact_path | Phase 2 | 435,401 | 435,401 | 100.00% |
| code refs -> repo_trees | repo_name | Phase 2 | 435,401 | 435,401 | 100.00% |
| code refs -> spec_files repos | repo_name | Phase 3 | 435,401 | 435,401 | 100.00% |
| artifact files -> spec_files repos | repo_name | Phase 3 | 266,230 | 266,230 | 100.00% |
| spec_file_commits -> spec_files | file_url_sha16 | Phase 3 | 780,335 | 739,165 | 94.72% |
| spec_content_features -> spec_files | file_url_sha16 | not used | 468,307 | 468,307 | 100.00% |
| spec_files -> spec_content_features | file_url_sha16 | not used | 470,795 | 468,307 | 99.47% |
| spec_links -> spec_files | spec_url_sha16 | Phase 3, if useful | 2,421,323 | 2,421,323 | 100.00% |
| pr_files -> pull_requests | tool+repo_name+pr_number | one RQ3 sentence | 348,141 | 348,141 | 100.00% |
| pull_requests -> spec_files repos | repo_name | one RQ3 sentence | 5,992 | 5,992 | 100.00% |
| kiro_files -> spec_files repos | repo_name | not used | 98,574 | 6,148 | 6.24% |
| repo_trees -> spec_files repos | repo_name | Phase 2 | 73,030 | 73,030 | 100.00% |
| spec_files repos -> repo_trees | repo_name | Phase 2 | 73,031 | 73,030 | 100.00% |

No right-hand key has duplicates, so no join adds rows, and every `spec_file_commits` row's repository and path agree with its `spec_files` row. Unmatched `spec_file_commits` rows are the filtered pre-2024 files (caveat C1). Kiro repositories are mostly outside the `spec.md` census by design (N4).

## 3. Caveats

Status: reproduced (equal, or within 1% where the plan says 'about'), close (within 10%), differs (explained in the note), new (not in the plan), info (descriptive).

| ID | Table | Caveat | Expected | Observed | Status | Decision | Note |
|---|---|---|---|---|---|---|---|
| R1 | openspec_code_refs | exists_at_anchor counts | 1: 361,083; 0: 51,979; 2: 130; null: 22,209 | 0: 51,979; 1: 361,083; 2: 130; null: 22,209 | reproduced | Analyzable refs need 0 or 1 |  |
| R2 | openspec_code_refs | No anchor commit | 22,209 refs | 22,209 refs in 427 repositories | reproduced | Dropped | Every null exists_at_anchor row is a null anchor_sha row |
| R3 | openspec_code_refs | exists_at_anchor = 2 (undocumented) | 130 refs in 5 repositories | 130 refs in 5 repositories | reproduced | Dropped |  |
| R4 | openspec_code_refs | Parser noise such as Next.js, .ts, globs | About 8,900 refs | 7,642 refs (glob 3,040, tech_name 2,101, bare_extension 1,830, placeholder 504, task_number 95, url 72) | differs | Tagged as noise and dropped | Provisional rules in lib/rules/ref_noise.py, deliberately narrow (elided paths like a/.../b.kt are kept); October's direction1 rules were not available to compare. Phase 2's port should reconcile them |
| R5 | openspec_code_refs | Matched by file name or suffix, not exact path | About 128,000 refs | 127,893 refs with resolved_path different from code_path | reproduced | Kept; exact-match and full-path versions reported beside them |  |
| N1 | openspec_code_refs | exists_at_anchor = 1 but resolved_path is null | Not in plan | 28,978 refs | new | Treat as existing; exact_match is unknown for them (not false). Phase 2 should count them separately in the exact-match version |  |
| T1 | repo_trees | Repository listing truncated or missing | 142 truncated and 848 missing repositories | 142 truncated, 848 missing, 1 error; refs affected: 1,021 refs in 3 truncated repositories, 0 in missing ones | reproduced | Drop refs in truncated listings (only these few) | No ref sits in a missing listing; every ref's repository has a repo_trees row |
| R6 | openspec_code_refs | Refs per repository | Descriptive | 7,076 repositories; median 18, 90th percentile 140, max 6,590 | info | Repository bootstrap and per-repository medians (Phase 2) |  |
| R7 | openspec_code_refs | Analyzable refs (Phase 2 expected count) | About 405,196 refs in 6,807 repositories and 60,095 changes | 405,368 refs in 6,802 repositories and 59,965 changes | reproduced | Phase 2's 01_prepare_refs must reproduce this or explain the gap | Uses the provisional noise rules; the gap to October is the noise-rule difference |
| A1 | openspec_artifact_files | Counts by kind; failed fetches | 1,689 failed fetches | proposal.md 93,307; tasks.md 93,061; design.md 79,459; plan.md 245; research.md 78; data-model.md 41; failed 1,689 | reproduced | Failed rows have no text; refs never point at them (see joins) |  |
| A2 | openspec_artifact_files | n_tasks_done never above n_tasks | 0 rows | 0 rows; 2,306,367 tasks, 1,925,372 ticked (83.5%) | reproduced | Safe to use the counts |  |
| A3 | openspec_artifact_files | Every artifact_path in the refs has its tasks.md text | All refs | 435,401 of 435,401 refs | reproduced | Line finder can run on every ref |  |
| A4 | openspec_artifact_files | Archived change with no box ticked | 4,333 changes | 4,426 archived tasks.md files with no box ticked (3,733 of them list at least one task; 2,677 have code refs, with 30,248 refs, 84.4% of which exist) | close | Own row in the checkbox analysis | Archived = any path with an archive/ folder (OpenSpec/changes/archive, openspec/archive). The exact October filter is unknown; 'at least one task' is the stricter reading |
| S1 | spec_files | file_url_sha16 unique | Unique | 470,795 rows, 470,795 distinct | reproduced | Safe key |  |
| S2 | spec_files | Repository columns agree across a repository's rows | Agree | all agree | reproduced | Take one row per repository (latest updated_at) in 04_features | Count of repositories whose rows disagree, per column |
| N2 | spec_files | Same repository and path captured twice (two blob commits in file_url) | Not in plan | 20,328 paths in 1,965 repositories have 20,383 extra rows; 19,876 of the paths have identical content | new | Deduplicate on (repo_name, file_path) before file-level counts; commits on both copies are deduplicated by (repo_name, commit_sha) anyway |  |
| S3 | spec_files | spec_tool and spec_role counts | openspec 274,955 specs in 8,926 repos; archived 156,936, living 73,253, change_proposal 41,806 | openspec 274,955 specs in 8,926 repos; archived 156,936, na 137,779, living 73,253, feature 49,370, change_proposal 41,806, config 11,651 | reproduced | Full counts in reports/profile/spec_files.csv |  |
| S4 | spec_files | Spec file committed only once | 96% of archived, 63% of living | 96.4% of archived, 62.5% of living, 89.2% of change proposals (OpenSpec, file_total_commits = 1) | reproduced | Archiving restarts a file's history, so archived changes mostly show only the archive commit |  |
| F1 | spec_content_features | Task text not in English | About 9% of specs | 8.9% of 468,307 specs (es 11,156, pt 6,939, ja 4,770, vi 3,732, de 2,366, no 2,075) | reproduced | Intent rules cover ten languages; 'other' reported by language | Measured on spec.md text; tasks.md language is not labelled in SpecMine |
| C1 | spec_file_commits | Commit rows for files outside spec_files | About 5,000 files | 6,705 files, 41,170 rows; 100.0% of these files were first committed before 2024 | differs | Inner join before any use | 6,705 equals the paper's count of files removed for a pre-2024 first commit, and every one of them was first committed before 2024: they are the filtered files, not missing ones |
| C2 | spec_file_commits | Commit dates out of range | Author dates 2009 to 2032 | whole table authored 2009-03-08 to 2032-02-16; after the inner join authored 2024-01-02 to 2032-02-16, committed 2024-01-02 to 2032-02-16. Outside 2024-01-01 to 2026-07-14: committed 0 before, 6 after; authored 0 before, 6 after (of 739,165 joined rows) | reproduced | Use committed_at, clipped to the config window | The pre-2024 dates belong to the files outside spec_files (C1); after the inner join only the future dates remain |
| C3 | spec_file_commits | Commits with an agent Co-authored-by trailer | 22% of commits (20% Claude) | 31.3% any agent, 22.7% excluding Caffeine, 20.4% Claude (of 349,159 distinct commits) | close | Phase 3 agent-credit labels (trailer is one of three signals) | October's 22% matches the share without Caffeine's forge@caffeine.ai trailer, which alone adds about 9 points. The 739,165 joined rows are commit-file pairs; deduplicate on (repo_name, commit_sha). Pattern is provisional; agent_rules.py owns the real one |
| C4 | spec_file_commits | author_type counts | Descriptive | User 634,992; null 99,556; Bot 4,591; Organization 26 | info | null author_type means no GitHub account matched the commit email: author unknown, not human |  |
| L1 | spec_links | Links that point to code | 1.28M of 2.4M | 1,278,828 of 2,421,323 (52.8%) | reproduced | Config-file question uses all rel types (see rq3_questions) |  |
| P1 | pull_requests | PR layer is merged-only | All 5,992 PRs | 5,992 of 5,992 merged | reproduced | Not used for inference |  |
| P2 | pull_requests | Head-branch prefixes | claude/ 186, codex/ 140, copilot/ 14 | prefix: claude/ 177, codex/ 139, copilot/ 14; anywhere in the name: claude 238, codex 165, copilot 24 | close | One RQ3 sentence; quote the prefix counts |  |
| N3 | pr_files | id restarts per tool | Not in plan | 132,145 duplicate ids; 0 duplicate (tool, id) | new | Key PR tables on (tool, id) or (tool, repo_name, pr_number) |  |
| N4 | kiro_files | Kiro repositories outside the spec.md census | Not in plan | 12,910 repositories, 239 of them in spec_files | new | Not used; a Kiro feature is not a spec_files row |  |

## 4. The three RQ3 questions

### Change coverage

A change's commits are the commits on spec deltas in its folder (`spec_file_commits` covers only `spec.md`). 'Checked create task' uses a provisional English line finder: the first checkbox line naming the path. It finds a line for 88.7% of refs, and that line's checkbox agrees with `task_done` for 98.3% of them (Phase 2 needs 98%).

| Changes | Status | Changes | With a spec-delta commit | Coverage | With 2+ commits |
|---|---|---|---|---|---|
| all changes with code refs | all | 62,472 | 62,394 | 99.9% | 3,150 |
| all changes with code refs | archived | 50,280 | 50,216 | 99.9% | 1,846 |
| all changes with code refs | in progress | 12,192 | 12,178 | 99.9% | 1,304 |
| changes with a checked task | all | 54,221 | 54,161 | 99.9% | 2,528 |
| changes with a checked task | archived | 45,634 | 45,586 | 99.9% | 1,618 |
| changes with a checked task | in progress | 8,587 | 8,575 | 99.9% | 910 |
| changes with a checked create task (broad verbs) | all | 28,667 | 28,643 | 99.9% | 1,384 |
| changes with a checked create task (broad verbs) | archived | 23,995 | 23,981 | 99.9% | 900 |
| changes with a checked create task (broad verbs) | in progress | 4,672 | 4,662 | 99.8% | 484 |
| changes with a checked create task (strict verbs) | all | 16,342 | 16,330 | 99.9% | 857 |
| changes with a checked create task (strict verbs) | archived | 13,342 | 13,333 | 99.9% | 566 |
| changes with a checked create task (strict verbs) | in progress | 3,000 | 2,997 | 99.9% | 291 |

**Answer:** Change-level credit is usable. Both verb lists give the same answer: yes.

### Anchor commits

- 43,028 distinct anchors in 6,906 repositories (median 2 per repository, max 463).
- 42,954 of them (99.8%) are commits in `spec_file_commits` after the inner join.
- For 60,710 of 60,837 changes, the anchor commit touched that change's own spec delta.

**Answer:** Keep the anchor commit; it carries agent credit for almost every change.

### Agent config files

- `spec_links`: 0 repositories with a root config target. Of 8,717 agent-folder hits, 8,344 are sibling docs of specs that themselves live in an agent folder (e.g. `.claude/specs/`).
- `openspec_code_refs`: 0 repositories; the parser keeps only code extensions, so `.md` config files never appear.
- `pr_files`: config files changed in spec-touching PRs of 331 of 581 PR-layer repositories:

| Config file | PR file rows | Repositories |
|---|---|---|
| agents.md | 926 | 179 |
| claude.md | 886 | 207 |
| copilot-instructions.md | 160 | 44 |
| .cursor/rules/ | 74 | 15 |
| .github/instructions/ | 49 | 11 |
| gemini.md | 19 | 14 |
| .cursorrules | 10 | 7 |
| .clinerules | 9 | 2 |
| .kiro/steering/ | 4 | 2 |
| .windsurfrules | 2 | 2 |

- Agent-tool spec folders (`spec_tool`): claude_code 833, trae 434, codex 69, opencode 66, cursor 65, moai 63, kilocode 3 repositories.

**Answer:** Not answerable corpus-wide. spec_links never names a root config file (its agent-folder hits are spec files living inside .claude/ etc.), and code refs only hold code extensions, never .md. The PR layer is the one trace: config files changed in spec-touching PRs, a lower bound for the >=10-star subsample. Cite the undercount from the git-history pilot; optionally add the PR-layer lower bound in one sentence.

## 5. Test sample

`data/sample/`: 200 OpenSpec repositories with task references, seed 520, the same number from each star band. Every table is cut down to them (`spec_content_features` and `spec_links` through the sampled `spec_files`). `python run.py checks --sample` runs the checks on it.

| Stars | Repositories |
|---|---|
| 0 | 50 |
| 1-9 | 50 |
| 10-99 | 50 |
| 100+ | 50 |

| Table | Rows | Bytes |
|---|---|---|
| openspec_code_refs | 21,320 | 442,733 |
| openspec_artifact_files | 11,831 | 16,982,264 |
| repo_trees | 200 | 5,406 |
| spec_files | 11,866 | 6,429,671 |
| spec_file_commits | 15,919 | 3,291,436 |
| spec_links | 88,979 | 683,918 |
| spec_content_features | 11,866 | 259,509 |
| kiro_files | 21 | 6,002 |
| pull_requests | 637 | 57,482 |
| pr_files | 29,306 | 370,765 |

## 6. Deviations from the plan

- **The dataset is dragged into data/.** Instead of `pull_data.py` downloading or copying it, each person drags the SpecMine folder into `data/` (any folder name); the scripts find it. `check_data.py` then checks it against `data/MANIFEST.csv`. This works the same on Windows and macOS.
- **MANIFEST.csv is committed at data/MANIFEST.csv** (the plan puts it in `data/raw/`, which is not committed), so every laptop can check it has byte-identical files.
- **One extra script, `explore/rq3_questions.py`,** so the caveat table stays one row per caveat.
- **Provisional rules stand in for October's scripts.** `direction1/` and `rq3-ai-authorship/` are not on this Mac, so the noise rules (`lib/rules/ref_noise.py`), the task-line finder and create verbs (`rq3_questions.py`) and the agent-trailer pattern (`check_caveats.py`) are new, English-only stand-ins. Phase 2 and 3 ports should replace them.
- **OpenSpec changes are matched by folder** (`lib/rules/openspec_paths.py`): a change is its tasks.md folder, and archived means any `archive/` folder, because layouts vary.
- **Equal sample per star band**: 50 repositories in each of 0, 1-9, 10-99 and 100+ stars, so tests see popular repositories too.
- **Kept simple on purpose**: plain scripts, pandas where the data fits in memory, DuckDB for the big tables. `lib/db.py` has no `table()` helper; scripts query the views directly.
- **Runs with `python run.py`** on Windows and macOS (the Makefile is an optional shortcut). Tested on macOS only so far, and CI has not run yet.

## 7. Reproduce

```bash
python run.py check-data
python run.py checks
python run.py test
```

Run logs with row counts, timings and every check are in `logs/<script>.json`.
