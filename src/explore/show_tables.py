"""Step 1 of exploring SpecMine: what is in each table?

For every one of the 10 tables this writes one easy-to-read Markdown page,
reports/tables/<table>.md, with:
  - what the table is and how many rows it has,
  - every column: its type, what it means, how often it is filled in,
    and a few example values,
  - three sample rows, shown column by column.

It also writes reports/tables/README.md, a one-page overview of all tables.

Run:  python run.py explore     (or: python src/explore/show_tables.py)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

from lib.db import connect  # noqa: E402
from lib.io import TABLES, find_doc, output_dir, read_text, write_text  # noqa: E402

# Which research question uses each table (from the Implementation Plan).
USED_FOR = {
    "openspec_code_refs": "RQ1, RQ2, RQ3: every file path named in a task, and whether that file exists",
    "openspec_artifact_files": "RQ1, RQ2: the text of each tasks.md (to read the task line and its verb)",
    "repo_trees": "RQ1: tells us which repositories have an incomplete file listing",
    "spec_files": "RQ2, RQ3: repository facts (stars, language, age) and which tool made each spec",
    "spec_file_commits": "RQ3: who committed each spec file, and whether an AI agent is credited",
    "spec_links": "Checked for RQ3 (agent config files); not used in the end",
    "spec_content_features": "Not used",
    "kiro_files": "Not used",
    "pull_requests": "One sentence in RQ3 (branch names like claude/...)",
    "pr_files": "Not used",
}

# Plain-English notes for the columns the research questions rely on.
# They add to (or replace) the short descriptions in DATA_DICTIONARY.md.
NOTES = {
    ("openspec_code_refs", "artifact_path"): "The tasks.md file the path was found in. Its folder is the 'change'.",
    ("openspec_code_refs", "code_path"): "The file path written in the task text.",
    ("openspec_code_refs", "task_done"): "1 = the task's checkbox is ticked [x], 0 = not ticked [ ].",
    ("openspec_code_refs", "anchor_sha"): "The commit whose file list was used to check the path. Empty = no anchor commit.",
    ("openspec_code_refs", "exists_at_anchor"): "1 = the file exists at the anchor commit; 0 = it does not (a 'missing' "
                                                "file, the RQ1 outcome); 2 = undocumented; empty = no anchor commit.",
    ("openspec_code_refs", "resolved_path"): "The real file the path matched. Differs from code_path when it was matched "
                                             "by file name only.",
    ("openspec_artifact_files", "kind"): "Which document: proposal.md, design.md or tasks.md.",
    ("openspec_artifact_files", "content"): "The full Markdown text of the document.",
    ("openspec_artifact_files", "n_tasks"): "Number of checkbox tasks in a tasks.md.",
    ("openspec_artifact_files", "n_tasks_done"): "Number of those tasks that are ticked.",
    ("openspec_artifact_files", "fetch_status"): "done = text downloaded; missing = could not be downloaded.",
    ("repo_trees", "status"): "done = file list downloaded; truncated = GitHub cut it short; missing = not downloaded.",
    ("repo_trees", "truncated"): "1 = the file list is incomplete, so 'missing' files there may not really be missing.",
    ("spec_files", "spec_tool"): "Which spec-driven tool made the file (openspec, speckit, kiro, ...), guessed from its path.",
    ("spec_files", "spec_role"): "OpenSpec: living = current spec, change_proposal = change in progress, "
                                 "archived = finished change.",
    ("spec_files", "file_total_commits"): "How many commits changed this file.",
    ("spec_file_commits", "message"): "The commit message. A 'Co-authored-by: Claude ...' line credits an AI agent (RQ3).",
    ("spec_file_commits", "author_type"): "User, Bot or Organization. Empty when no GitHub account matched the commit.",
    ("spec_file_commits", "committed_at"): "When the commit was made (text, ISO format).",
}

LONG_TEXT_LIMIT = 120  # longer values are cut so the pages stay readable


def read_dictionary():
    """DATA_DICTIONARY.md -> ({table: description}, {(table, column): description})."""
    text = read_text(find_doc("DATA_DICTIONARY.md"))
    table_info, column_info = {}, {}
    for block in text.split("\n## `")[1:]:
        table = block.split("`")[0]
        table_info[table] = block.split("\n\n")[1].strip()
        for col, _type, desc in re.findall(r"^\| `(\w+)` \| ([^|]+) \| ([^|]*) \|$", block, re.M):
            column_info[(table, col)] = desc.strip()
    return table_info, column_info


def short(value):
    """Make one value fit on one line of a Markdown table."""
    if value is None:
        return "(empty)"
    text = str(value).replace("\n", " ⏎ ").replace("|", "\\|")
    return text if len(text) <= LONG_TEXT_LIMIT else text[:LONG_TEXT_LIMIT] + " …"


def describe_table(con, table, table_info, column_info):
    n_rows = con.execute(f"select count(*) from {table}").fetchone()[0]
    columns = con.execute(f"select column_name, column_type from (describe {table})").fetchall()

    lines = [f"# `{table}`", "",
             table_info.get(table, ""), "",
             f"- **Rows:** {n_rows:,}",
             f"- **Columns:** {len(columns)}",
             f"- **Used for:** {USED_FOR[table]}", "",
             "## Columns", "",
             "| Column | Type | What it means | Filled in | Different values | Examples |",
             "|---|---|---|---|---|---|"]
    for col, col_type in columns:
        c = f'"{col}"'
        long_text = col == "content" or "message" in col
        # Exact counts, except for long text where an estimate (marked ~) is much faster.
        count_distinct = f"approx_count_distinct({c})" if long_text else f"count(distinct {c})"
        filled, distinct = con.execute(f"select count({c}), {count_distinct} from {table}").fetchone()
        # The three most common values (for long text, one example is enough).
        n_examples = 1 if long_text else 3
        examples = con.execute(f"""select {c} from {table} where {c} is not null
                                   group by 1 order by count(*) desc, 1 limit {n_examples}""").fetchall()
        meaning = NOTES.get((table, col)) or column_info.get((table, col)) or ""
        lines.append(f"| `{col}` | {col_type} | {meaning} | {filled / n_rows:.0%} | {'~' if long_text else ''}{distinct:,} | "
                     + "; ".join(short(v) for (v,) in examples) + " |")

    # Three random rows (the same three every time), shown one column per line.
    sample = con.execute(f"select * from {table} using sample reservoir(3 rows) repeatable (520)").df()
    lines += ["", "## Three sample rows", "",
              "| Column | Row 1 | Row 2 | Row 3 |", "|---|---|---|---|"]
    for col in sample.columns:
        lines.append(f"| `{col}` | " + " | ".join(short(v) for v in sample[col]) + " |")
    return n_rows, len(columns), "\n".join(lines) + "\n"


def main():
    con = connect()
    table_info, column_info = read_dictionary()
    out = output_dir("reports") / "tables"
    out.mkdir(exist_ok=True)

    overview = ["# SpecMine tables at a glance", "",
                "One page per table in this folder. Start with the tables marked RQ.", "",
                "| Table | Rows | Columns | Used for |", "|---|---|---|---|"]
    for table in TABLES:
        n_rows, n_cols, page = describe_table(con, table, table_info, column_info)
        write_text(out / f"{table}.md", page)
        overview.append(f"| [`{table}`]({table}.md) | {n_rows:,} | {n_cols} | {USED_FOR[table]} |")
        print(f"{table:25s} {n_rows:>10,} rows  {n_cols:>3} columns  -> reports/tables/{table}.md")

    overview += ["", "## How the tables connect", "",
                 "- `repo_name` (owner/repo) links every table to every other.",
                 "- `file_url_sha16` links `spec_files`, `spec_file_commits` and `spec_content_features`; "
                 "`spec_links.spec_url_sha16` is the same key.",
                 "- `openspec_code_refs.artifact_path` = `openspec_artifact_files.file_path` (same repo): "
                 "the tasks.md a path came from.",
                 "- `pr_files` joins `pull_requests` on (`tool`, `repo_name`, `pr_number`)."]
    write_text(out / "README.md", "\n".join(overview) + "\n")


if __name__ == "__main__":
    main()
