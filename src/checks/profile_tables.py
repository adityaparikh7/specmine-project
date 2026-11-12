"""Phase 1, step 3: profile every table.

For each column: type, null share, number of distinct values, min and max,
average text length, and the most common values when there are only a few.
Writes reports/profile/<table>.csv (one row per column) and
reports/profile/_summary.csv (one row per table).
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

import pandas as pd  # noqa: E402

from lib import checks  # noqa: E402
from lib.db import connect, schema_problems  # noqa: E402
from lib.io import TABLES, is_sample, load_config, output_dir, write_log  # noqa: E402

# The key of each table. pr_files' id restarts for every tool, so its key includes tool.
KEYS = {
    "openspec_code_refs": "id",
    "openspec_artifact_files": "id",
    "repo_trees": "repo_name",
    "spec_files": "file_url_sha16",
    "spec_file_commits": "id",
    "spec_links": "id",
    "spec_content_features": "file_url_sha16",
    "kiro_files": "id",
    "pull_requests": "tool, repo_name, pr_number",
    "pr_files": "tool, id",
}

# Long free text: count distinct values approximately and skip min/max.
LONG_TEXT = {"content", "message", "file_last_commit_message", "file_first_commit_message",
             "repo_description", "title", "repo_topics", "parents", "file_last_commit_parents",
             "file_first_commit_parents"}


def profile_column(con, table, column, col_type, n_rows):
    c = f'"{column}"'
    if column in LONG_TEXT:
        non_null, distinct, mean_len = con.execute(
            f"select count({c}), approx_count_distinct({c}), avg(length({c})) from {table}").fetchone()
        low = high = None
    else:
        # `|| ''` makes DuckDB read real values instead of truncated Parquet statistics.
        v = f"({c} || '')" if col_type == "VARCHAR" else c
        non_null, distinct, low, high = con.execute(
            f"select count({c}), count(distinct {c}), min({v})::varchar, max({v})::varchar from {table}").fetchone()
        mean_len = con.execute(f"select avg(length({c})) from {table}").fetchone()[0] if col_type == "VARCHAR" else None

    top = None
    if column not in LONG_TEXT and 0 < distinct <= 60:  # a category column
        pairs = con.execute(f"select {c}::varchar, count(*) from {table} group by 1 order by 2 desc, 1 limit 8").fetchall()
        top = "; ".join(f"{value}: {count}" for value, count in pairs)

    return {
        "column": column,
        "type": col_type,
        "rows": n_rows,
        "non_null": non_null,
        "null_share": round(1 - non_null / n_rows, 6) if n_rows else None,
        "n_distinct": distinct,
        "min": low[:80] if isinstance(low, str) else low,
        "max": high[:80] if isinstance(high, str) else high,
        "mean_length": round(mean_len, 1) if mean_len is not None else None,
        "top_values": top,
    }


def main():
    started = time.time()
    config = load_config()
    con = connect(check=False)  # we record schema problems below instead of stopping
    out = output_dir("reports") / "profile"
    out.mkdir(exist_ok=True)

    # 1. Compare every column with schema.sql.
    problems = schema_problems(con)
    pd.DataFrame({"problem": problems}).to_csv(out / "_schema_diff.csv", index=False)
    checks.check("Parquet columns and types match schema.sql", not problems, "; ".join(problems))

    # 2. Profile each table, column by column.
    summary = []
    for table in TABLES:
        n_rows = con.execute(f"select count(*) from {table}").fetchone()[0]
        columns = con.execute(f"select column_name, column_type from (describe {table})").fetchall()
        profile = pd.DataFrame([profile_column(con, table, col, typ, n_rows) for col, typ in columns])
        profile.to_csv(out / f"{table}.csv", index=False)

        key = KEYS[table]
        duplicate_keys = con.execute(f"select count(*) - count(distinct ({key})) from {table}").fetchone()[0]
        repos = None
        if "repo_name" in profile["column"].values:
            repos = con.execute(f"select count(distinct repo_name) from {table}").fetchone()[0]
        summary.append({
            "table": table,
            "rows": n_rows,
            "rows_readme": config["expected_rows"][table],
            "columns": len(profile),
            "repos": repos,
            "key": key.replace(", ", "+"),
            "duplicate_keys": duplicate_keys,
            "columns_with_nulls": int((profile["null_share"] > 0).sum()),
        })
        if not is_sample():
            checks.expect_rows(f"{table} rows match README", n_rows, expected=config["expected_rows"][table])
        print(f"profiled {table}: {n_rows:,} rows, {len(profile)} columns")

    summary = pd.DataFrame(summary)
    summary.to_csv(out / "_summary.csv", index=False)
    print(summary.to_string(index=False))
    write_log("profile_tables", dict(zip(summary["table"], summary["rows"])), started)


if __name__ == "__main__":
    main()
