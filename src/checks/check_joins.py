"""Phase 1, step 4: check every join the pipeline uses.

For each join we count how many left-hand rows find a match on the right,
and whether the right-hand key is unique (if it is not, the join would
duplicate rows). Writes reports/joins.csv.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

import pandas as pd  # noqa: E402

from lib import checks  # noqa: E402
from lib.db import connect  # noqa: E402
from lib.io import output_dir, write_log  # noqa: E402

SPEC_REPOS = "(select distinct repo_name from spec_files)"
TASKS_MD = """(select repo_name, file_path as artifact_path from openspec_artifact_files
               where kind = 'tasks.md' and fetch_status = 'done' and content is not null)"""

# (name, left table, right table, join columns, which phase uses it)
JOINS = [
    ("code refs -> tasks.md text", "openspec_code_refs", TASKS_MD, ["repo_name", "artifact_path"], "Phase 2"),
    ("code refs -> repo_trees", "openspec_code_refs", "repo_trees", ["repo_name"], "Phase 2"),
    ("code refs -> spec_files repos", "openspec_code_refs", SPEC_REPOS, ["repo_name"], "Phase 3"),
    ("artifact files -> spec_files repos", "openspec_artifact_files", SPEC_REPOS, ["repo_name"], "Phase 3"),
    ("spec_file_commits -> spec_files", "spec_file_commits", "spec_files", ["file_url_sha16"], "Phase 3"),
    ("spec_content_features -> spec_files", "spec_content_features", "spec_files", ["file_url_sha16"], "not used"),
    ("spec_files -> spec_content_features", "spec_files", "spec_content_features", ["file_url_sha16"], "not used"),
    ("spec_links -> spec_files", "spec_links",
     "(select file_url_sha16 as spec_url_sha16 from spec_files)", ["spec_url_sha16"], "Phase 3, if useful"),
    ("pr_files -> pull_requests", "pr_files", "pull_requests", ["tool", "repo_name", "pr_number"], "one RQ3 sentence"),
    ("pull_requests -> spec_files repos", "pull_requests", SPEC_REPOS, ["repo_name"], "one RQ3 sentence"),
    ("kiro_files -> spec_files repos", "kiro_files", SPEC_REPOS, ["repo_name"], "not used"),
    ("repo_trees -> spec_files repos", "repo_trees", SPEC_REPOS, ["repo_name"], "Phase 2"),
    ("spec_files repos -> repo_trees", SPEC_REPOS, "repo_trees", ["repo_name"], "Phase 2"),
]


def main():
    started = time.time()
    con = connect()
    rows = []
    for name, left, right, keys, used_by in JOINS:
        key = ", ".join(keys)
        match = " and ".join(f"l.{k} = r.{k}" for k in keys)
        left_rows = con.execute(f"select count(*) from {left}").fetchone()[0]
        matched = con.execute(
            f"select count(*) from {left} l where exists (select 1 from {right} r where {match})").fetchone()[0]
        right_duplicates = con.execute(f"select count(*) - count(distinct ({key})) from {right}").fetchone()[0]
        checks.check(f"right key unique: {name}", right_duplicates == 0, f"duplicates={right_duplicates:,}")
        rows.append({"join": name, "keys": "+".join(keys), "used_by": used_by, "left_rows": left_rows,
                     "left_rows_matched": matched, "match_share": round(matched / left_rows, 6)})
        print(f"{name:40s} {matched / left_rows:8.2%} matched")

    # A commit row's repo and path should equal those of its spec_files row.
    disagree = con.execute("""
        select count(*) from spec_file_commits c join spec_files s using (file_url_sha16)
        where c.repo_name <> s.repo_name or c.file_path <> s.file_path""").fetchone()[0]
    checks.check("spec_file_commits repo and path agree with spec_files", disagree == 0, f"rows={disagree}")

    joins = pd.DataFrame(rows)
    joins.to_csv(output_dir("reports") / "joins.csv", index=False)
    write_log("check_joins", {r["join"]: r["left_rows_matched"] for r in rows}, started)


if __name__ == "__main__":
    main()
