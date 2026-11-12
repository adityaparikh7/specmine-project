"""Phase 1, step 5: recompute every known caveat and put its count next to its decision.

Covers the plan's caveat table, the "What Phase 1 checks" column, and a few
new caveats found while profiling. Writes reports/caveats.csv with one row
per caveat: what the plan expected, what we observe, a status, the decision.

Status: reproduced (equal, or within 1% where the plan says "about"),
close (within 10%), differs (the note explains why), new (not in the plan),
info (descriptive only).
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

import pandas as pd  # noqa: E402

from lib import checks  # noqa: E402
from lib.db import connect  # noqa: E402
from lib.io import is_sample, load_config, output_dir, write_log  # noqa: E402
from lib.rules.openspec_paths import change_dir, is_archived  # noqa: E402
from lib.rules.ref_noise import noise_rule  # noqa: E402

# PROVISIONAL pattern for "Co-authored-by: <agent>" trailers. Phase 3's
# lib/rules/agent_rules.py (the port of the pilot's classify.py) replaces it.
AGENT_TRAILER = (r"(?im)^\s*co-authored-by:.*(anthropic\.com|\bclaude\b|copilot|cursoragent|"
                 r"cursor\.com|openai\.com|\bcodex\b|jules|gemini|opencode|devin|aider|"
                 r"windsurf|codeium|kiro|sisyphus|oh-my-codex|caffeine|\bcline\b|junie|kilo)")
CAFFEINE_TRAILER = r"(?im)^\s*co-authored-by:.*caffeine"
CLAUDE_TRAILER = r"(?im)^\s*co-authored-by:.*(anthropic\.com|\bclaude\b)"

caveats = []


def add(cid, table, caveat, expected, observed, decision, status, note=""):
    caveats.append({"id": cid, "area": table, "caveat": caveat, "expected": expected,
                    "observed": observed, "status": status, "decision": decision, "note": note})


def compare(expected, observed, about=False):
    """Status of an observed number against the plan's expected number."""
    if observed == expected or (about and abs(observed - expected) <= 0.01 * expected):
        return "reproduced"
    if abs(observed - expected) <= 0.10 * expected:
        return "close"
    return "differs"


def pct(x):
    return "n/a" if x is None or pd.isna(x) else f"{100 * x:.1f}%"


def one(con, sql):
    """Run a query that returns one row."""
    return con.execute(sql).fetchone()


def main():
    started = time.time()
    config = load_config()
    con = connect()

    # ------------------------------------------------------------------
    # 1. openspec_code_refs: small enough (435k rows) to work on in pandas.
    # ------------------------------------------------------------------
    refs = con.execute("""select r.*, t.status as tree_status, t.truncated
                          from openspec_code_refs r left join repo_trees t using (repo_name)""").df()
    refs["noise_rule"] = refs["code_path"].map(noise_rule)
    refs["change_dir"] = refs["artifact_path"].map(change_dir)
    refs["archived"] = refs["artifact_path"].map(is_archived)

    counts = refs["exists_at_anchor"].value_counts(dropna=False)
    counts = {("null" if pd.isna(k) else int(k)): int(v) for k, v in counts.items()}
    observed = "; ".join(f"{k}: {counts.get(k, 0):,}" for k in [0, 1, 2, "null"])
    add("R1", "openspec_code_refs", "exists_at_anchor counts", "1: 361,083; 0: 51,979; 2: 130; null: 22,209",
        observed, "Analyzable refs need 0 or 1",
        "reproduced" if counts == {1: 361083, 0: 51979, 2: 130, "null": 22209} else "differs")

    no_anchor = refs[refs["anchor_sha"].isna()]
    add("R2", "openspec_code_refs", "No anchor commit", "22,209 refs",
        f"{len(no_anchor):,} refs in {no_anchor['repo_name'].nunique():,} repositories", "Dropped",
        compare(22209, len(no_anchor)), "Every null exists_at_anchor row is a null anchor_sha row")

    two = refs[refs["exists_at_anchor"] == 2]
    add("R3", "openspec_code_refs", "exists_at_anchor = 2 (undocumented)", "130 refs in 5 repositories",
        f"{len(two):,} refs in {two['repo_name'].nunique()} repositories", "Dropped", compare(130, len(two)))

    by_rule = refs["noise_rule"].value_counts()
    n_noise = int(by_rule.sum())
    add("R4", "openspec_code_refs", "Parser noise such as Next.js, .ts, globs", "About 8,900 refs",
        f"{n_noise:,} refs (" + ", ".join(f"{rule} {n:,}" for rule, n in by_rule.items()) + ")",
        "Tagged as noise and dropped", compare(8900, n_noise, about=True),
        "Provisional rules in lib/rules/ref_noise.py, deliberately narrow (elided paths like a/.../b.kt "
        "are kept); October's direction1 rules were not available to compare. Phase 2's port should "
        "reconcile them")

    suffix_match = (refs["resolved_path"].notna() & (refs["resolved_path"] != refs["code_path"])).sum()
    add("R5", "openspec_code_refs", "Matched by file name or suffix, not exact path", "About 128,000 refs",
        f"{suffix_match:,} refs with resolved_path different from code_path",
        "Kept; exact-match and full-path versions reported beside them", compare(128000, suffix_match, about=True))

    exists_no_path = ((refs["exists_at_anchor"] == 1) & refs["resolved_path"].isna()).sum()
    add("N1", "openspec_code_refs", "exists_at_anchor = 1 but resolved_path is null", "Not in plan",
        f"{exists_no_path:,} refs", "Treat as existing; exact_match is unknown for them (not false). "
        "Phase 2 should count them separately in the exact-match version", "new")

    trees = one(con, """select count(*) filter (where truncated = 1), count(*) filter (where status = 'missing'),
                               count(*) filter (where status = 'error') from repo_trees""")
    in_truncated = refs[refs["truncated"] == 1]
    in_missing = refs[refs["tree_status"] == "missing"]
    add("T1", "repo_trees", "Repository listing truncated or missing", "142 truncated and 848 missing repositories",
        f"{trees[0]} truncated, {trees[1]} missing, {trees[2]} error; refs affected: {len(in_truncated):,} refs in "
        f"{in_truncated['repo_name'].nunique()} truncated repositories, {len(in_missing)} in missing ones",
        "Drop refs in truncated listings (only these few)",
        "reproduced" if (trees[0], trees[1]) == (142, 848) else "differs",
        "No ref sits in a missing listing; every ref's repository has a repo_trees row")

    per_repo = refs.groupby("repo_name").size()
    add("R6", "openspec_code_refs", "Refs per repository", "Descriptive",
        f"{len(per_repo):,} repositories; median {per_repo.median():.0f}, 90th percentile "
        f"{per_repo.quantile(0.9):.0f}, max {per_repo.max():,}",
        "Repository bootstrap and per-repository medians (Phase 2)", "info")

    analyzable = refs[refs["anchor_sha"].notna() & refs["exists_at_anchor"].isin([0, 1])
                      & refs["noise_rule"].isna() & (refs["truncated"] != 1)]
    n_changes = len(analyzable[["repo_name", "change_dir"]].drop_duplicates())
    add("R7", "openspec_code_refs", "Analyzable refs (Phase 2 expected count)",
        "About 405,196 refs in 6,807 repositories and 60,095 changes",
        f"{len(analyzable):,} refs in {analyzable['repo_name'].nunique():,} repositories and {n_changes:,} changes",
        "Phase 2's 01_prepare_refs must reproduce this or explain the gap",
        compare(405196, len(analyzable), about=True),
        "Uses the provisional noise rules; the gap to October is the noise-rule difference")

    # ------------------------------------------------------------------
    # 2. openspec_artifact_files
    # ------------------------------------------------------------------
    kinds = con.execute("""select kind, count(*) as n, count(*) filter (where fetch_status <> 'done') as failed
                           from openspec_artifact_files group by 1 order by 2 desc""").df()
    failed = int(kinds["failed"].sum())
    add("A1", "openspec_artifact_files", "Counts by kind; failed fetches", "1,689 failed fetches",
        "; ".join(f"{r.kind} {r.n:,}" for r in kinds.head(6).itertuples()) + f"; failed {failed:,}",
        "Failed rows have no text; refs never point at them (see joins)", compare(1689, failed))

    over = one(con, "select count(*) from openspec_artifact_files where n_tasks_done > n_tasks")[0]
    tasks, ticked = one(con, "select sum(n_tasks), sum(n_tasks_done) from openspec_artifact_files where kind = 'tasks.md'")
    checks.expect_rows("n_tasks_done never above n_tasks", over, expected=0)
    add("A2", "openspec_artifact_files", "n_tasks_done never above n_tasks", "0 rows",
        f"{over} rows; {tasks:,} tasks, {ticked:,} ticked ({pct(ticked / tasks)})", "Safe to use the counts",
        compare(0, over))

    with_text = one(con, """select count(*) from openspec_code_refs r join openspec_artifact_files a
                            on r.repo_name = a.repo_name and r.artifact_path = a.file_path
                            where a.kind = 'tasks.md' and a.fetch_status = 'done'""")[0]
    add("A3", "openspec_artifact_files", "Every artifact_path in the refs has its tasks.md text", "All refs",
        f"{with_text:,} of {len(refs):,} refs", "Line finder can run on every ref", compare(len(refs), with_text))

    task_files = con.execute("""select repo_name, file_path, n_tasks, n_tasks_done from openspec_artifact_files
                                where kind = 'tasks.md'""").df()
    none_ticked = task_files[task_files["file_path"].map(is_archived) & (task_files["n_tasks_done"] == 0)]
    has_refs = none_ticked.merge(refs[["repo_name", "artifact_path"]].drop_duplicates(),
                                 left_on=["repo_name", "file_path"], right_on=["repo_name", "artifact_path"])
    # Refs in archived changes where no ref's task is ticked, and how many of their files exist.
    no_tick_changes = refs[refs["archived"]].groupby(["repo_name", "artifact_path"])["task_done"].max()
    no_tick_changes = no_tick_changes[no_tick_changes == 0].reset_index()[["repo_name", "artifact_path"]]
    no_tick_refs = refs.merge(no_tick_changes, on=["repo_name", "artifact_path"])
    exist_share = no_tick_refs.loc[no_tick_refs["exists_at_anchor"].isin([0, 1]), "exists_at_anchor"].mean()
    add("A4", "openspec_artifact_files", "Archived change with no box ticked", "4,333 changes",
        f"{len(none_ticked):,} archived tasks.md files with no box ticked "
        f"({(none_ticked['n_tasks'] > 0).sum():,} of them list at least one task; {len(has_refs):,} have code "
        f"refs, with {len(no_tick_refs):,} refs, {pct(exist_share)} of which exist)",
        "Own row in the checkbox analysis", compare(4333, len(none_ticked)),
        "Archived = any path with an archive/ folder (OpenSpec/changes/archive, openspec/archive). "
        "The exact October filter is unknown; 'at least one task' is the stricter reading")

    # ------------------------------------------------------------------
    # 3. spec_files
    # ------------------------------------------------------------------
    n_files, n_keys = one(con, "select count(*), count(distinct file_url_sha16) from spec_files")
    add("S1", "spec_files", "file_url_sha16 unique", "Unique", f"{n_files:,} rows, {n_keys:,} distinct",
        "Safe key", compare(n_files, n_keys))

    # Repository columns are copied onto every file row; they should agree within a repository.
    disagree = {}
    for col in ["repo_id", "repo_stars", "repo_forks", "repo_size_kb", "repo_language", "repo_created_at",
                "repo_pushed_at", "owner_type", "repo_fork", "repo_license_spdx_id"]:
        disagree[col] = one(con, f"""select count(*) from (select repo_name from spec_files
                                     group by 1 having count(distinct {col}) > 1)""")[0]
    add("S2", "spec_files", "Repository columns agree across a repository's rows", "Agree",
        "; ".join(f"{k}: {v}" for k, v in disagree.items() if v) or "all agree",
        "Take one row per repository (latest updated_at) in 04_features", compare(0, max(disagree.values())),
        "Count of repositories whose rows disagree, per column")

    dup = one(con, """select count(*), sum(k) - count(*), count(distinct repo_name), count(*) filter (where shas = 1)
                      from (select repo_name, file_path, count(*) as k, count(distinct file_sha) as shas
                            from spec_files group by all having count(*) > 1)""")
    add("N2", "spec_files", "Same repository and path captured twice (two blob commits in file_url)", "Not in plan",
        f"{dup[0]:,} paths in {dup[2]:,} repositories have {dup[1]:,} extra rows; {dup[3]:,} of the paths have "
        "identical content",
        "Deduplicate on (repo_name, file_path) before file-level counts; commits on both copies are "
        "deduplicated by (repo_name, commit_sha) anyway", "new")

    openspec = one(con, "select count(*), count(distinct repo_name) from spec_files where spec_tool = 'openspec'")
    roles = con.execute("select spec_role, count(*) as n from spec_files group by 1 order by 2 desc").df()
    add("S3", "spec_files", "spec_tool and spec_role counts",
        "openspec 274,955 specs in 8,926 repos; archived 156,936, living 73,253, change_proposal 41,806",
        f"openspec {openspec[0]:,} specs in {openspec[1]:,} repos; "
        + ", ".join(f"{r.spec_role} {r.n:,}" for r in roles.itertuples()),
        "Full counts in reports/profile/spec_files.csv", compare(274955, openspec[0]))

    once = con.execute("""select spec_role, avg((file_total_commits = 1)::int) as share from spec_files
                          where spec_tool = 'openspec' group by 1""").df().set_index("spec_role")["share"]
    add("S4", "spec_files", "Spec file committed only once", "96% of archived, 63% of living",
        f"{pct(once['archived'])} of archived, {pct(once['living'])} of living, {pct(once['change_proposal'])} "
        "of change proposals (OpenSpec, file_total_commits = 1)",
        "Archiving restarts a file's history, so archived changes mostly show only the archive commit",
        compare(96, round(100 * once["archived"])))

    # ------------------------------------------------------------------
    # 4. spec_content_features
    # ------------------------------------------------------------------
    n_specs, not_english = one(con, "select count(*), count(*) filter (where lang <> 'en') from spec_content_features")
    langs = con.execute("""select lang, count(*) as n from spec_content_features where lang <> 'en'
                           group by 1 order by 2 desc limit 6""").df()
    add("F1", "spec_content_features", "Task text not in English", "About 9% of specs",
        f"{pct(not_english / n_specs)} of {n_specs:,} specs ("
        + ", ".join(f"{r.lang} {r.n:,}" for r in langs.itertuples()) + ")",
        "Intent rules cover ten languages; 'other' reported by language",
        compare(9, round(100 * not_english / n_specs)),
        "Measured on spec.md text; tasks.md language is not labelled in SpecMine")

    # ------------------------------------------------------------------
    # 5. spec_file_commits
    # ------------------------------------------------------------------
    outside = one(con, """select count(distinct file_url_sha16), count(*) from spec_file_commits
                          where file_url_sha16 not in (select file_url_sha16 from spec_files)""")
    outside_pre2024 = one(con, """select avg((first_commit < '2024-01-01')::int) from (
                                    select file_url_sha16, min(authored_at) as first_commit from spec_file_commits
                                    where file_url_sha16 not in (select file_url_sha16 from spec_files) group by 1)""")[0]
    add("C1", "spec_file_commits", "Commit rows for files outside spec_files", "About 5,000 files",
        f"{outside[0]:,} files, {outside[1]:,} rows; {pct(outside_pre2024)} of these files were first committed "
        "before 2024", "Inner join before any use", compare(5000, outside[0]),
        "6,705 equals the paper's count of files removed for a pre-2024 first commit, and every one of them "
        "was first committed before 2024: they are the filtered files, not missing ones")

    # From here on, only commits on files that are in spec_files (the inner join).
    con.execute("""create temp table commits as select * from spec_file_commits
                   where file_url_sha16 in (select file_url_sha16 from spec_files)""")
    w0, w1 = str(config["window"]["start"]), str(config["window"]["end"]) + "T23:59:59Z"
    all_dates = one(con, "select min(authored_at || ''), max(authored_at || '') from spec_file_commits")
    d = one(con, f"""select min(authored_at), max(authored_at), min(committed_at), max(committed_at),
                            count(*) filter (where committed_at < '{w0}'), count(*) filter (where committed_at > '{w1}'),
                            count(*) filter (where authored_at < '{w0}'), count(*) filter (where authored_at > '{w1}'),
                            count(*) from commits""")
    add("C2", "spec_file_commits", "Commit dates out of range", "Author dates 2009 to 2032",
        f"whole table authored {all_dates[0][:10]} to {all_dates[1][:10]}; after the inner join authored "
        f"{d[0][:10]} to {d[1][:10]}, committed {d[2][:10]} to {d[3][:10]}. Outside {w0} to {w1[:10]}: committed "
        f"{d[4]:,} before, {d[5]:,} after; authored {d[6]:,} before, {d[7]:,} after (of {d[8]:,} joined rows)",
        "Use committed_at, clipped to the config window",
        "reproduced" if (all_dates[0][:4], all_dates[1][:4]) == ("2009", "2032") else "differs",
        "The pre-2024 dates belong to the files outside spec_files (C1); after the inner join only the "
        "future dates remain")

    # One commit can touch several spec files, so count each (repo, commit) once.
    rows, n_commits, agent, agent_no_caffeine, claude = one(con, f"""
        select sum(n_rows), count(*), count(*) filter (where agent), count(*) filter (where agent and not caffeine),
               count(*) filter (where claude)
        from (select repo_name, commit_sha, count(*) as n_rows,
                     bool_or(regexp_matches(message, '{AGENT_TRAILER}')) as agent,
                     bool_or(regexp_matches(message, '{CAFFEINE_TRAILER}')) as caffeine,
                     bool_or(regexp_matches(message, '{CLAUDE_TRAILER}')) as claude
              from commits group by all)""")
    add("C3", "spec_file_commits", "Commits with an agent Co-authored-by trailer", "22% of commits (20% Claude)",
        f"{pct(agent / n_commits)} any agent, {pct(agent_no_caffeine / n_commits)} excluding Caffeine, "
        f"{pct(claude / n_commits)} Claude (of {n_commits:,} distinct commits)",
        "Phase 3 agent-credit labels (trailer is one of three signals)",
        compare(22, round(100 * agent_no_caffeine / n_commits)),
        "October's 22% matches the share without Caffeine's forge@caffeine.ai trailer, which alone adds "
        f"about 9 points. The {rows:,} joined rows are commit-file pairs; deduplicate on "
        "(repo_name, commit_sha). Pattern is provisional; agent_rules.py owns the real one")

    author_types = con.execute("""select coalesce(author_type, 'null') as author_type, count(*) as n
                                  from commits group by 1 order by 2 desc""").df()
    add("C4", "spec_file_commits", "author_type counts", "Descriptive",
        "; ".join(f"{r.author_type} {r.n:,}" for r in author_types.itertuples()),
        "null author_type means no GitHub account matched the commit email: author unknown, not human", "info")

    # ------------------------------------------------------------------
    # 6. spec_links and the PR layer
    # ------------------------------------------------------------------
    n_links, n_code = one(con, "select count(*), count(*) filter (where rel = 'code') from spec_links")
    add("L1", "spec_links", "Links that point to code", "1.28M of 2.4M",
        f"{n_code:,} of {n_links:,} ({pct(n_code / n_links)})",
        "Config-file question uses all rel types (see rq3_questions)", compare(1278828, n_code))

    n_prs, merged = one(con, "select count(*), count(*) filter (where is_merged = 1) from pull_requests")
    add("P1", "pull_requests", "PR layer is merged-only", "All 5,992 PRs", f"{merged:,} of {n_prs:,} merged",
        "Not used for inference", compare(5992, merged))

    b = one(con, """select count(*) filter (where lower(head_branch) like 'claude/%'),
                           count(*) filter (where lower(head_branch) like 'codex/%'),
                           count(*) filter (where lower(head_branch) like 'copilot/%'),
                           count(*) filter (where lower(head_branch) like '%claude%'),
                           count(*) filter (where lower(head_branch) like '%codex%'),
                           count(*) filter (where lower(head_branch) like '%copilot%')
                    from pull_requests""")
    add("P2", "pull_requests", "Head-branch prefixes", "claude/ 186, codex/ 140, copilot/ 14",
        f"prefix: claude/ {b[0]}, codex/ {b[1]}, copilot/ {b[2]}; anywhere in the name: claude {b[3]}, "
        f"codex {b[4]}, copilot {b[5]}", "One RQ3 sentence; quote the prefix counts", compare(186, b[0]))

    ids = one(con, "select count(*) - count(distinct id), count(*) - count(distinct (tool, id)) from pr_files")
    add("N3", "pr_files", "id restarts per tool", "Not in plan",
        f"{ids[0]:,} duplicate ids; {ids[1]} duplicate (tool, id)",
        "Key PR tables on (tool, id) or (tool, repo_name, pr_number)", "new")

    kiro = one(con, """select count(distinct repo_name),
                              count(distinct repo_name) filter (where repo_name in (select repo_name from spec_files))
                       from kiro_files""")
    add("N4", "kiro_files", "Kiro repositories outside the spec.md census", "Not in plan",
        f"{kiro[0]:,} repositories, {kiro[1]:,} of them in spec_files",
        "Not used; a Kiro feature is not a spec_files row", "new")

    # ------------------------------------------------------------------
    # 7. Save. Every 'differs' must carry a note explaining it.
    # ------------------------------------------------------------------
    table = pd.DataFrame(caveats)
    table.to_csv(output_dir("reports") / "caveats.csv", index=False)
    print(table[["id", "status", "observed"]].to_string(index=False, max_colwidth=90))
    if not is_sample():
        unexplained = table[(table["status"] == "differs") & (table["note"] == "")]["id"].tolist()
        checks.check("every caveat that differs has a note", not unexplained, f"ids: {unexplained}")
    write_log("check_caveats", {"caveats": len(table), "analyzable_refs": len(analyzable),
                                **table["status"].value_counts().to_dict()}, started)


if __name__ == "__main__":
    main()
