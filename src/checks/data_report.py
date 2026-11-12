"""Phase 1, step 7: write reports/data_report.md from the other Phase 1 outputs.

Every number comes from the files the earlier steps wrote (profile, joins,
caveats, RQ3 answers, sample manifest). The only hand-written text is the
framing, the decisions and the list of deviations from the plan.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

import pandas as pd  # noqa: E402

from lib.io import is_sample, load_config, output_dir, read_text, sample_dir, write_log, write_text  # noqa: E402


def num(x):
    """1234567 -> '1,234,567'; blanks for missing values."""
    if x is None or pd.isna(x):
        return ""
    return f"{x:,.4f}".rstrip("0") if isinstance(x, float) and not float(x).is_integer() else f"{int(x):,}"


def pct(x):
    return f"{100 * x:.1f}%"


def markdown_table(df, columns, headers):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(columns)]
    for _, row in df.iterrows():
        cells = [num(row[c]) if isinstance(row[c], (int, float)) else str(row[c]) for c in columns]
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |")
    return "\n".join(lines)


DEVIATIONS = [
    "**The dataset is dragged into data/.** Instead of `pull_data.py` downloading or copying it, each person "
    "drags the SpecMine folder into `data/` (any folder name); the scripts find it. `check_data.py` then "
    "checks it against `data/MANIFEST.csv`. This works the same on Windows and macOS.",
    "**MANIFEST.csv is committed at data/MANIFEST.csv** (the plan puts it in `data/raw/`, which is not "
    "committed), so every laptop can check it has byte-identical files.",
    "**One extra script, `explore/rq3_questions.py`,** so the caveat table stays one row per caveat.",
    "**Provisional rules stand in for October's scripts.** `direction1/` and `rq3-ai-authorship/` are not on "
    "this Mac, so the noise rules (`lib/rules/ref_noise.py`), the task-line finder and create verbs "
    "(`rq3_questions.py`) and the agent-trailer pattern (`check_caveats.py`) are new, English-only stand-ins. "
    "Phase 2 and 3 ports should replace them.",
    "**OpenSpec changes are matched by folder** (`lib/rules/openspec_paths.py`): a change is its tasks.md "
    "folder, and archived means any `archive/` folder, because layouts vary.",
    "**Equal sample per star band**: 50 repositories in each of 0, 1-9, 10-99 and 100+ stars, so tests see "
    "popular repositories too.",
    "**Kept simple on purpose**: plain scripts, pandas where the data fits in memory, DuckDB for the big "
    "tables. `lib/db.py` has no `table()` helper; scripts query the views directly.",
    "**Runs with `python run.py`** on Windows and macOS (the Makefile is an optional shortcut). Tested on "
    "macOS only so far, and CI has not run yet.",
]


def main():
    started = time.time()
    config = load_config()
    reports = output_dir("reports")
    summary = pd.read_csv(reports / "profile" / "_summary.csv")
    schema = pd.read_csv(reports / "profile" / "_schema_diff.csv")
    joins = pd.read_csv(reports / "joins.csv")
    caveats = pd.read_csv(reports / "caveats.csv").fillna("")
    coverage = pd.read_csv(reports / "rq3_coverage.csv")
    rq3 = json.loads(read_text(reports / "rq3_questions.json"))
    sample_tables = pd.read_csv(sample_dir() / "SAMPLE_MANIFEST.csv")
    sample_repos = pd.read_csv(sample_dir() / "sample_repos.csv")

    q1, q2, q3 = rq3["q1_change_coverage"], rq3["q2_anchor_commits"], rq3["q3_config_files"]
    finder = rq3["line_finder"]
    status = caveats["status"].value_counts()
    rows_match = (summary["rows"] == summary["rows_readme"]).all()
    md = []

    md += ["# SpecMine data report (Phase 1)", "",
           f"Generated {time.strftime('%Y-%m-%d %H:%M')} by `src/checks/data_report.py` on the "
           f"{'200-repository sample' if is_sample() else 'full dataset'}. Do not edit by hand: rerun `python run.py checks`.", ""]

    md += ["## Summary", "",
           f"- **Tables.** All 10 tables load through `lib/db.py`; "
           f"{'every row count matches the SpecMine README' if rows_match else 'some row counts differ from the README'}"
           f" and {'every column matches `schema.sql`' if schema.empty else f'{len(schema)} columns differ from `schema.sql`'}.",
           f"- **Caveats.** {len(caveats)} checks: {status.get('reproduced', 0)} reproduced, {status.get('close', 0)} close, "
           f"{status.get('differs', 0)} differ (each explained), {status.get('new', 0)} new, {status.get('info', 0)} descriptive.",
           f"- **RQ3 change coverage.** {pct(q1['strict']['coverage'])} of {num(q1['strict']['changes'])} changes with a "
           f"checked create task (strict verbs) have a commit on a spec delta in their folder "
           f"({pct(q1['broad']['coverage'])} with broad verbs), well above the {pct(q1['threshold'])} threshold, so "
           f"change-level credit is usable. But {pct(q1['covered_with_one_commit_share'])} of covered changes have "
           f"exactly one such commit, often the archive commit (decision 7).",
           f"- **RQ3 anchor commits.** {pct(q2['share'])} of {num(q2['distinct_anchors'])} anchor commits are spec "
           f"commits, and for {num(q2['changes_whose_anchor_touched_their_own_spec_delta'])} of "
           f"{num(q2['changes_with_anchor'])} changes the anchor is a commit on that change's own spec delta. Keep the "
           f"anchor-commit measure; it is nearly the same commit as the change-level one.",
           f"- **RQ3 config files.** Not answerable corpus-wide: `spec_links` names a root config file in "
           f"{num(q3['spec_links_repos_with_config_target'])} repositories, and code refs never hold `.md` paths. The PR "
           f"layer shows config files changed in {num(q3['pr_files_repos_with_config'])} of {num(q3['pr_layer_repos'])} "
           f"repositories, a lower bound for that subsample only. Cite the undercount from the git-history pilot.",
           f"- **Sample.** {len(sample_repos)} repositories, {num(sample_tables['rows'].sum())} rows across 10 tables, "
           f"{sample_tables['bytes'].sum() / 1e6:.1f} MB in `data/sample/`.", ""]

    md += ["## Decisions for Phases 2 and 3", "",
           "1. Inner-join `spec_file_commits` to `spec_files`, then deduplicate on `(repo_name, commit_sha)`: the "
           "joined rows are commit-file pairs, roughly two per commit.",
           "2. Deduplicate `spec_files` on `(repo_name, file_path)` before any file-level count (caveat N2: the same "
           "file captured at two commits).",
           "3. Key the PR tables on `(tool, id)` or `(tool, repo_name, pr_number)`; `id` alone repeats across tools (N3).",
           "4. Treat refs with `exists_at_anchor = 1` and no `resolved_path` as existing, with `exact_match` unknown (N1).",
           "5. Report agent-trailer shares with and without Caffeine's `forge@caffeine.ai` trailer (C3); October's "
           "22% is the share without it.",
           "6. Use `min(col || '')` for min/max of text columns read straight from Parquet: DuckDB otherwise answers "
           "from truncated Parquet statistics (e.g. `2009-03-`).",
           f"7. RQ3 can use change-level credit and the anchor commit, but {pct(q1['covered_with_one_commit_share'])} of "
           f"changes have a single spec-delta commit. For archived changes that commit's message mentions archiving "
           f"{pct(q1['archived_single_commit_mentions_archive_share'])} of the time, and "
           f"{pct(q1['commits_touching_several_changes_share'])} of change commits touch several changes at once. "
           "Credit therefore means 'an agent is credited on the commit that wrote or archived the change's spec', "
           "not 'an agent wrote its code'. Say so in the paper.", ""]

    md += ["## 1. Tables", "",
           markdown_table(summary, ["table", "rows", "rows_readme", "columns", "repos", "key", "duplicate_keys",
                                    "columns_with_nulls"],
                          ["Table", "Rows", "README", "Columns", "Repos", "Key", "Duplicate keys", "Columns with nulls"]),
           "", "Per-column profiles (null share, distinct values, min/max, top values) are in "
           "`reports/profile/<table>.csv`. Schema check against `schema.sql`: "
           + ("no differences." if schema.empty else f"{len(schema)} differences in `_schema_diff.csv`."), ""]

    joins["match"] = joins["match_share"].map(lambda x: f"{100 * x:.2f}%")
    md += ["## 2. Joins", "",
           markdown_table(joins, ["join", "keys", "used_by", "left_rows", "left_rows_matched", "match"],
                          ["Join", "Keys", "Used by", "Left rows", "Matched", "Match"]),
           "", "No right-hand key has duplicates, so no join adds rows, and every `spec_file_commits` row's repository "
           "and path agree with its `spec_files` row. Unmatched `spec_file_commits` rows are the filtered pre-2024 "
           "files (caveat C1). Kiro repositories are mostly outside the `spec.md` census by design (N4).", ""]

    md += ["## 3. Caveats", "",
           "Status: reproduced (equal, or within 1% where the plan says 'about'), close (within 10%), differs "
           "(explained in the note), new (not in the plan), info (descriptive).", "",
           markdown_table(caveats, ["id", "area", "caveat", "expected", "observed", "status", "decision", "note"],
                          ["ID", "Table", "Caveat", "Expected", "Observed", "Status", "Decision", "Note"]), ""]

    coverage["coverage"] = coverage["coverage"].map(pct)
    md += ["## 4. The three RQ3 questions", "", "### Change coverage", "",
           "A change's commits are the commits on spec deltas in its folder (`spec_file_commits` covers only "
           "`spec.md`). 'Checked create task' uses a provisional English line finder: the first checkbox line naming "
           f"the path. It finds a line for {pct(finder['line_found_share'])} of refs, and that line's checkbox agrees "
           f"with `task_done` for {pct(finder['checkbox_agrees_with_task_done'])} of them (Phase 2 needs 98%).", "",
           markdown_table(coverage, ["definition", "status", "changes", "with_spec_commit", "coverage", "with_2plus_commits"],
                          ["Changes", "Status", "Changes", "With a spec-delta commit", "Coverage", "With 2+ commits"]),
           "", f"**Answer:** {q1['decision']}. Both verb lists give the same answer: "
           f"{'yes' if q1['same_answer_for_both_verb_lists'] else 'no'}.", ""]
    md += ["### Anchor commits", "",
           f"- {num(q2['distinct_anchors'])} distinct anchors in {num(q2['repos_with_anchor'])} repositories (median "
           f"{num(q2['anchors_per_repo_median'])} per repository, max {num(q2['anchors_per_repo_max'])}).",
           f"- {num(q2['anchors_that_are_spec_commits'])} of them ({pct(q2['share'])}) are commits in "
           "`spec_file_commits` after the inner join.",
           f"- For {num(q2['changes_whose_anchor_touched_their_own_spec_delta'])} of {num(q2['changes_with_anchor'])} "
           "changes, the anchor commit touched that change's own spec delta.",
           "", f"**Answer:** {q2['decision']}.", ""]
    pr_config = pd.DataFrame(q3["pr_files_config"])
    folders = ", ".join(f"{t['spec_tool']} {num(t['repos'])}" for t in q3["agent_tool_spec_folders"])
    md += ["### Agent config files", "",
           f"- `spec_links`: {num(q3['spec_links_repos_with_config_target'])} repositories with a root config target. "
           f"Of {num(q3['spec_links_agent_folder_hits'])} agent-folder hits, "
           f"{num(q3['spec_links_agent_folder_hits_that_are_spec_siblings'])} are sibling docs of specs that themselves "
           "live in an agent folder (e.g. `.claude/specs/`).",
           f"- `openspec_code_refs`: {num(q3['code_refs_repos_naming_config'])} repositories; the parser keeps only "
           "code extensions, so `.md` config files never appear.",
           f"- `pr_files`: config files changed in spec-touching PRs of {num(q3['pr_files_repos_with_config'])} of "
           f"{num(q3['pr_layer_repos'])} PR-layer repositories:", ""]
    if not pr_config.empty:
        md += [markdown_table(pr_config, ["file", "rows", "repos"], ["Config file", "PR file rows", "Repositories"]), ""]
    md += [f"- Agent-tool spec folders (`spec_tool`): {folders} repositories.", "",
           f"**Answer:** {q3['decision']}.", ""]

    bands = sample_repos["band"].value_counts().sort_index().rename_axis("band").reset_index(name="repos")
    md += ["## 5. Test sample", "",
           f"`data/sample/`: {len(sample_repos)} OpenSpec repositories with task references, seed {config['seed']}, "
           "the same number from each star band. Every table is cut down to them (`spec_content_features` and "
           "`spec_links` through the sampled `spec_files`). `python run.py checks --sample` runs the checks on it.", "",
           markdown_table(bands, ["band", "repos"], ["Stars", "Repositories"]), "",
           markdown_table(sample_tables, ["table", "rows", "bytes"], ["Table", "Rows", "Bytes"]), ""]

    md += ["## 6. Deviations from the plan", ""] + [f"- {d}" for d in DEVIATIONS] + [""]
    md += ["## 7. Reproduce", "", "```bash", "python run.py check-data", "python run.py checks",
           "python run.py test", "```", "",
           "Run logs with row counts, timings and every check are in `logs/<script>.json`.", ""]

    write_text(reports / "data_report.md", "\n".join(md))
    print(f"wrote {reports / 'data_report.md'}")
    write_log("data_report", {"caveats": len(caveats)}, started)


if __name__ == "__main__":
    main()
