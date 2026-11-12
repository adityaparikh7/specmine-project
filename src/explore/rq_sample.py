"""Step 3 of exploring SpecMine: a small, connected CSV sample with only what the RQs use.

We pick 300 OpenSpec repositories that name code files in their tasks: 75
from each star band (0, 1-9, 10-99 and 100+ stars; config rq_sample.repos_per_band)
and keep only the tables and columns that RQ1, RQ2 and RQ3 need, for those
repositories only. Equal bands mean popular repositories are well represented,
so remember to weight by band (or report per band) before quoting overall rates. Because every file covers the same repositories,
the files join to each other on repo_name, just like the full data.

Files written to data/rq_sample/:
  code_refs.csv     RQ1-3  every file path named in a task, ticked or not, and whether the file exists
  task_lines.csv    RQ1    every checkbox line of every tasks.md, one per row (to read the task's verb)
  repo_trees.csv    RQ1    whether each repository's file list is complete
  repos.csv         RQ2    one row per repository: stars, forks, language, size, age, ...
  spec_commits.csv  RQ3    commits on spec files, with author and message (agent credit)
  README.md                what each file and column is

Run:  python run.py explore     (or: python src/explore/rq_sample.py)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

import pandas as pd  # noqa: E402

from lib.db import connect  # noqa: E402
from lib.io import DATA, load_config, write_csv, write_text  # noqa: E402

CHECKBOX_LINE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*\[([ xX])\]\s*(.*)$")  # "- [x] Create src/app.ts"


def star_band(stars):
    if stars == 0:
        return "0"
    if stars < 10:
        return "1-9"
    if stars < 100:
        return "10-99"
    return "100+"


def one_line(text):
    """Show line breaks as ⏎ so each row of the CSV stays on one line."""
    return text.replace("\r", "").replace("\n", " ⏎ ") if isinstance(text, str) else text


def main():
    config = load_config()
    seed, per_band = config["seed"], config["rq_sample"]["repos_per_band"]
    con = connect()
    out = DATA / "rq_sample"
    out.mkdir(parents=True, exist_ok=True)

    # 1. Pick the repositories: OpenSpec repositories that name code files in their tasks,
    #    the same number from every star band.
    repos = con.execute("""
        select repo_name, max(repo_stars) as stars from spec_files
        where repo_name in (select repo_name from openspec_code_refs)
        group by 1 order by 1""").df()
    repos["star_band"] = repos["stars"].map(star_band)
    picked = repos.groupby("star_band").sample(n=per_band, random_state=seed)
    con.register("picked", picked[["repo_name"]])
    in_picked = "repo_name in (select repo_name from picked)"

    # 2. RQ1-3: the task-to-code references (all 8 columns).
    code_refs = con.execute(f"select * from openspec_code_refs where {in_picked} order by repo_name, id").df()

    # 3. RQ1: every checkbox line of every tasks.md, one row per line.
    tasks = con.execute(f"""select repo_name, file_path, content from openspec_artifact_files
                            where kind = 'tasks.md' and content is not null and {in_picked}""").df()
    task_lines = []
    for t in tasks.itertuples():
        for number, line in enumerate(t.content.split("\n"), start=1):
            match = CHECKBOX_LINE.match(line)
            if match:
                task_lines.append({"repo_name": t.repo_name, "tasks_file": t.file_path, "line_number": number,
                                   "ticked": int(match.group(1) in "xX"), "task_text": match.group(2)})
    task_lines = pd.DataFrame(task_lines).sort_values(["repo_name", "tasks_file", "line_number"])

    # 4. RQ1: is each repository's file list complete?
    repo_trees = con.execute(f"select repo_name, status, truncated, n_entries from repo_trees where {in_picked} order by repo_name").df()

    # 5. RQ2: one row per repository with the facts we compare across repositories.
    repo_facts = con.execute(f"""
        select repo_name, any_value(repo_stars) as stars, any_value(repo_forks) as forks,
               any_value(repo_language) as language, any_value(repo_size_kb) as size_kb,
               any_value(repo_created_at) as created_at, any_value(repo_pushed_at) as last_push_at,
               any_value(owner_type) as owner_type, any_value(repo_fork) as is_fork,
               any_value(repo_archived) as is_archived, count(*) as spec_files,
               string_agg(distinct spec_tool, ', ' order by spec_tool) as spec_tools
        from spec_files where {in_picked} group by 1 order by 1""").df()
    repo_facts = repo_facts.merge(picked[["repo_name", "star_band"]])

    # 6. RQ3: commits on spec files that are in spec_files (the inner join the plan asks for).
    spec_commits = con.execute(f"""
        select distinct c.repo_name, c.file_path, c.commit_sha, c.committed_at,
               c.author_login, c.author_type, c.message
        from spec_file_commits c join spec_files s using (file_url_sha16)
        where c.{in_picked} order by all""").df()
    spec_commits["message"] = spec_commits["message"].map(one_line)

    # 7. Save everything.
    files = {"code_refs": code_refs, "task_lines": task_lines, "repo_trees": repo_trees,
             "repos": repo_facts, "spec_commits": spec_commits}
    for name, df in files.items():
        write_csv(df, out / f"{name}.csv")
        print(f"{name + '.csv':18s} {len(df):>6,} rows")
    write_csv(picked.sort_values(["star_band", "repo_name"]), out / "repositories.csv")
    write_text(out / "README.md", readme(picked, files, repos))
    print(f"\n{len(picked)} repositories:", picked["star_band"].value_counts().sort_index().to_dict())


def readme(picked, files, eligible):
    counts = {name: f"{len(df):,}" for name, df in files.items()}
    bands = "\n".join(f"| {band} | {(picked['star_band'] == band).sum()} | {(eligible['star_band'] == band).sum():,} |"
                      for band in ["0", "1-9", "10-99", "100+"])
    return f"""# RQ sample

A connected slice of SpecMine with only the tables and columns the research
questions use. Made by `src/explore/rq_sample.py`. All files cover the same
{len(picked)} OpenSpec repositories, so they join on `repo_name`
(the list is in `repositories.csv`).

| Stars | Repositories in the sample | Eligible repositories |
|---|---|---|
{bands}

Every band gets the same number of repositories, so popular repositories are
over-represented compared with the full data. Report results per band, or weight
each band by its share of eligible repositories, before quoting an overall rate.

| File | Rows | Used for | One row is |
|---|---|---|---|
| `repositories.csv` | {len(picked)} | all | a sampled repository and its star band |
| `code_refs.csv` | {counts['code_refs']} | RQ1, RQ2, RQ3 | a file path named in a task |
| `task_lines.csv` | {counts['task_lines']} | RQ1 | one checkbox line of a tasks.md |
| `repo_trees.csv` | {counts['repo_trees']} | RQ1 | a repository's file list status |
| `repos.csv` | {counts['repos']} | RQ2 | a repository |
| `spec_commits.csv` | {counts['spec_commits']} | RQ3 | a commit that changed a spec file |

## Columns

**code_refs.csv** (all columns of `openspec_code_refs`)
- `artifact_path`: the tasks.md the path came from; its folder is the change.
  `.../changes/archive/...` means the change is finished (archived).
- `code_path`: the path written in the task. `task_done`: 1 if the task is ticked.
- `exists_at_anchor`: 1 = the file exists, 0 = it is missing (the RQ1 outcome),
  2 = undocumented, empty = no anchor commit. `anchor_sha`: the commit checked.
- `resolved_path`: the real file matched (differs from `code_path` when matched by name only).

**task_lines.csv**: `tasks_file` matches `code_refs.artifact_path`. `ticked` is 1 for `[x]`.
`task_text` is the line after the checkbox; its first word (Create, Add, Update, ...) is the
task's intent. Find a ref's line by looking for its `code_path` in `task_text`.

**repo_trees.csv**: `truncated` = 1 means GitHub cut the file list short, so "missing"
files in that repository are not reliable.

**repos.csv**: repository facts from `spec_files` (stars, forks, language, size,
created and last-push dates, owner type, fork/archived flags, number of spec files, SDD tools).

**spec_commits.csv**: `author_type` is User, Bot or empty (no GitHub account matched).
`message` is the full commit message with line breaks shown as ⏎; a
`Co-authored-by: Claude ...` (or Copilot, Cursor, Codex, ...) line credits an AI agent.
"""


if __name__ == "__main__":
    main()
