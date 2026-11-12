"""Phase 1: answer the three questions the plan sets for RQ3.

Q1 Change coverage: how many changes with a checked "create" task have at
   least one commit on a spec delta in their folder? (spec_file_commits only
   covers spec.md files, so a change's commits are those on its spec deltas.)
Q2 Anchor commits: how many anchor_sha values are commits in spec_file_commits?
Q3 Config files: can agent config files (CLAUDE.md, AGENTS.md, .cursor/...)
   be found anywhere, given that repo_trees has no file names?

Q1 needs each ref's task line and its leading verb. Phase 2 owns the real line
finder and the ten-language intent rules, so this script uses a PROVISIONAL
English-only version and reports coverage for a strict and a broad verb list.

Writes reports/rq3_questions.json and reports/rq3_coverage.csv.
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

import pandas as pd  # noqa: E402

from lib import checks  # noqa: E402
from lib.db import connect  # noqa: E402
from lib.io import load_config, output_dir, write_log, write_text  # noqa: E402
from lib.rules.openspec_paths import change_dir, delta_change_dir, is_archived  # noqa: E402

# A task line: "- [ ] ...", "* [x] ...", "1. [x] ..."
CHECKBOX = re.compile(r"^\s*([-*+]|\d+[.)])\s*\[[ xX]\]")
# The first word after the checkbox, skipping task numbers ("1.2"), bold and backticks.
VERB = re.compile(r"\]\s*[*_`]*\s*(?:\d+(?:\.\d+)*\.?\s*)?[*_`]*\s*([a-z]+)")
CREATE_STRICT = {"create", "creates", "scaffold", "generate", "introduce", "new",
                 "initialize", "initialise", "init", "bootstrap"}
CREATE_BROAD = CREATE_STRICT | {"add", "implement", "write", "build", "setup", "set",
                                "define", "make", "extract", "port"}

# Agent config files that sit in a repository (not spec files).
CONFIG_FILE = (r"(^|/)(claude\.md|agents\.md|gemini\.md|\.cursorrules|\.windsurfrules|"
               r"copilot-instructions\.md|\.clinerules|\.cursor/rules/|\.kiro/steering/|"
               r"\.github/instructions/|\.junie/guidelines\.md)")
# Agent folders (specs often live inside these, e.g. .claude/specs/).
AGENT_FOLDER = r"(^|/)\.(claude|cursor|codex|gemini|windsurf|roo|junie|kiro|cline|opencode|github/agents)/"


def matches(texts, pattern):
    """True for each text (lower-cased) that matches the regular expression."""
    return texts.str.lower().map(lambda text: re.search(pattern, text) is not None)


def find_task_line(lines, code_path):
    """The first checkbox line that names the path, or None."""
    for line in lines:
        if code_path in line and CHECKBOX.match(line):
            return line
    return None


def leading_verb(line):
    match = VERB.search(line.lower())
    return match.group(1) if match else ""


def load_refs_with_task_lines(con):
    """openspec_code_refs plus each ref's task line, checkbox and verb."""
    refs = con.execute("select id, repo_name, artifact_path, code_path, task_done, anchor_sha "
                       "from openspec_code_refs").df()
    texts = con.execute("""select repo_name, file_path as artifact_path, content from openspec_artifact_files
                           where kind = 'tasks.md' and content is not null""").df()
    texts = texts.merge(refs[["repo_name", "artifact_path"]].drop_duplicates())
    lines_of = {(r.repo_name, r.artifact_path): r.content.split("\n") for r in texts.itertuples()}

    refs["line"] = [find_task_line(lines_of.get((r.repo_name, r.artifact_path), []), r.code_path)
                    for r in refs.itertuples()]
    found = refs["line"].notna()
    refs["line_checked"] = refs["line"].str.contains(r"\[[xX]\]", regex=True)
    refs["verb"] = refs["line"].map(lambda line: leading_verb(line) if isinstance(line, str) else "")
    refs["change_dir"] = refs["artifact_path"].map(change_dir)
    refs["archived"] = refs["artifact_path"].map(is_archived)
    refs["checked_create_strict"] = (refs["task_done"] == 1) & refs["verb"].isin(CREATE_STRICT)
    refs["checked_create_broad"] = (refs["task_done"] == 1) & refs["verb"].isin(CREATE_BROAD)

    agree = (refs.loc[found, "line_checked"] == (refs.loc[found, "task_done"] == 1)).mean()
    line_finder = {
        "refs": len(refs),
        "line_found": int(found.sum()),
        "line_found_share": round(found.mean(), 4),
        "checkbox_agrees_with_task_done": round(agree, 4),
        "top_verbs": refs.loc[found, "verb"].value_counts().head(25).to_dict(),
    }
    return refs, line_finder


def load_change_commits(con):
    """(repo_name, change_dir, commit_sha) for every commit on a file inside a change folder."""
    commits = con.execute("""select distinct repo_name, commit_sha, file_path from spec_file_commits
                             where file_url_sha16 in (select file_url_sha16 from spec_files)""").df()
    # A spec delta (openspec/changes/x/specs/a/spec.md) belongs to the change before '/specs/';
    # a spec.md sitting directly in a change folder belongs to its own folder.
    by_delta = commits.assign(change_dir=commits["file_path"].map(delta_change_dir))
    by_folder = commits.assign(change_dir=commits["file_path"].map(change_dir))
    change_commits = pd.concat([by_delta, by_folder])[["repo_name", "change_dir", "commit_sha"]]
    return change_commits[change_commits["change_dir"] != ""].drop_duplicates()


def q1_change_coverage(con, refs, change_commits, threshold):
    # One row per change, with how many of its refs are checked (create) tasks.
    changes = refs.groupby(["repo_name", "change_dir"]).agg(
        archived=("archived", "any"),
        refs=("id", "size"),
        checked=("task_done", "sum"),
        checked_create_strict=("checked_create_strict", "sum"),
        checked_create_broad=("checked_create_broad", "sum"),
    ).reset_index()
    n_commits = change_commits.groupby(["repo_name", "change_dir"])["commit_sha"].nunique().rename("n_commits")
    changes = changes.merge(n_commits.reset_index(), how="left").fillna({"n_commits": 0})

    rows = []
    definitions = [("all changes with code refs", changes["refs"] > 0),
                   ("changes with a checked task", changes["checked"] > 0),
                   ("changes with a checked create task (broad verbs)", changes["checked_create_broad"] > 0),
                   ("changes with a checked create task (strict verbs)", changes["checked_create_strict"] > 0)]
    for label, chosen in definitions:
        for status, in_status in [("all", True), ("archived", changes["archived"]),
                                  ("in progress", ~changes["archived"])]:
            subset = changes[chosen & in_status]
            covered = subset[subset["n_commits"] > 0]
            rows.append({"definition": label, "status": status, "changes": len(subset),
                         "with_spec_commit": len(covered), "coverage": round(len(covered) / len(subset), 4),
                         "with_2plus_commits": int((subset["n_commits"] > 1).sum())})
    coverage = pd.DataFrame(rows)

    strict = coverage[coverage["definition"].str.contains("strict") & (coverage["status"] == "all")].iloc[0]
    broad = coverage[coverage["definition"].str.contains("broad") & (coverage["status"] == "all")].iloc[0]

    # Most covered changes have exactly one spec-delta commit. What is it?
    covered = changes[changes["n_commits"] > 0]
    single = covered[covered["n_commits"] == 1].merge(change_commits)
    messages = con.execute("""select distinct repo_name, commit_sha, message from spec_file_commits
                              where file_url_sha16 in (select file_url_sha16 from spec_files)""").df()
    single = single.merge(messages.drop_duplicates(["repo_name", "commit_sha"]))
    single["mentions_archive"] = single["message"].str.contains("archiv", case=False)
    in_changes = change_commits.merge(changes[["repo_name", "change_dir"]])
    changes_per_commit = in_changes.groupby(["repo_name", "commit_sha"])["change_dir"].nunique()

    answer = {
        "strict": strict.to_dict(),
        "broad": broad.to_dict(),
        "threshold": threshold,
        "same_answer_for_both_verb_lists": bool((strict.coverage < threshold) == (broad.coverage < threshold)),
        "covered_changes": len(covered),
        "covered_with_one_commit_share": round((covered["n_commits"] == 1).mean(), 4),
        "archived_single_commit_mentions_archive_share": round(single.loc[single["archived"], "mentions_archive"].mean(), 4),
        "commits_touching_several_changes_share": round((changes_per_commit > 1).mean(), 4),
        "decision": ("Use repository-level credit for RQ3's missing-file comparison" if strict.coverage < threshold
                     else "Change-level credit is usable"),
    }
    return answer, coverage


def q2_anchor_commits(refs, change_commits):
    anchors = refs[["repo_name", "anchor_sha"]].dropna().drop_duplicates()
    spec_commits = change_commits[["repo_name", "commit_sha"]].drop_duplicates()
    is_spec_commit = anchors.merge(spec_commits, left_on=["repo_name", "anchor_sha"],
                                   right_on=["repo_name", "commit_sha"], how="left")["commit_sha"].notna()
    per_repo = anchors.groupby("repo_name").size()

    # Does the anchor touch the spec delta of the same change the ref comes from?
    anchored = refs.dropna(subset=["anchor_sha"])[["repo_name", "change_dir", "anchor_sha"]].drop_duplicates()
    same_change = anchored.merge(change_commits, left_on=["repo_name", "change_dir", "anchor_sha"],
                                 right_on=["repo_name", "change_dir", "commit_sha"])
    n_changes = len(anchored[["repo_name", "change_dir"]].drop_duplicates())
    n_same = len(same_change[["repo_name", "change_dir"]].drop_duplicates())
    share = is_spec_commit.mean()
    return {
        "distinct_anchors": len(anchors),
        "anchors_that_are_spec_commits": int(is_spec_commit.sum()),
        "share": round(share, 4),
        "repos_with_anchor": len(per_repo),
        "anchors_per_repo_median": float(per_repo.median()),
        "anchors_per_repo_max": int(per_repo.max()),
        "changes_with_anchor": n_changes,
        "changes_whose_anchor_touched_their_own_spec_delta": n_same,
        "decision": ("Drop the anchor-commit measure" if share < 0.5
                     else "Keep the anchor commit; it carries agent credit for almost every change"),
    }


def q3_config_files(con, refs):
    # spec_links: targets that name a config file, and agent-folder targets.
    links = con.execute(f"""
        select s.repo_name, s.file_path as spec_path, l.rel, l.target from spec_links l
        join spec_files s on l.spec_url_sha16 = s.file_url_sha16
        where regexp_matches(lower(l.target), '{CONFIG_FILE}') or regexp_matches(lower(l.target), '{AGENT_FOLDER}')""").df()
    config_targets = links[matches(links["target"], CONFIG_FILE)]
    folder_siblings = links[(links["rel"] == "sibling") & matches(links["spec_path"], AGENT_FOLDER)]

    # Code refs: a task that names a config file would show the file exists.
    refs_naming_config = refs[matches(refs["code_path"], CONFIG_FILE)]

    # PR layer: config files changed in spec-touching PRs.
    pr_config = con.execute(f"""
        select regexp_extract(lower(file_path), '{CONFIG_FILE}', 2) as file, count(*) as rows,
               count(distinct repo_name) as repos
        from pr_files where regexp_matches(lower(file_path), '{CONFIG_FILE}') group by 1 order by 2 desc""").df()
    pr_repos = con.execute(f"""select count(distinct repo_name) from pr_files
                               where regexp_matches(lower(file_path), '{CONFIG_FILE}')""").fetchone()[0]
    pr_layer_repos = con.execute("select count(distinct repo_name) from pull_requests").fetchone()[0]
    tool_folders = con.execute("""
        select spec_tool, count(distinct repo_name) as repos from spec_files
        where spec_tool in ('claude_code', 'cursor', 'codex', 'opencode', 'kilocode', 'trae', 'moai')
        group by 1 order by 2 desc""").df()

    return {
        "spec_links_repos_with_config_target": int(config_targets["repo_name"].nunique()),
        "spec_links_agent_folder_hits": len(links),
        "spec_links_agent_folder_hits_that_are_spec_siblings": len(folder_siblings),
        "code_refs_repos_naming_config": int(refs_naming_config["repo_name"].nunique()),
        "pr_files_config": pr_config.to_dict("records"),
        "pr_files_repos_with_config": pr_repos,
        "pr_layer_repos": pr_layer_repos,
        "agent_tool_spec_folders": tool_folders.to_dict("records"),
        "decision": ("Not answerable corpus-wide. spec_links never names a root config file (its agent-folder "
                     "hits are spec files living inside .claude/ etc.), and code refs only hold code "
                     "extensions, never .md. The PR layer is the one trace: config files changed in "
                     "spec-touching PRs, a lower bound for the >=10-star subsample. Cite the undercount "
                     "from the git-history pilot; optionally add the PR-layer lower bound in one sentence"),
    }


def main():
    started = time.time()
    config = load_config()
    con = connect()

    refs, line_finder = load_refs_with_task_lines(con)
    change_commits = load_change_commits(con)
    q1, coverage = q1_change_coverage(con, refs, change_commits, config["rq3"]["coverage_threshold"])
    q2 = q2_anchor_commits(refs, change_commits)
    q3 = q3_config_files(con, refs)

    answers = {"line_finder": line_finder, "q1_change_coverage": q1, "q2_anchor_commits": q2,
               "q3_config_files": q3}
    reports = output_dir("reports")
    coverage.to_csv(reports / "rq3_coverage.csv", index=False)
    write_text(reports / "rq3_questions.json", json.dumps(answers, indent=2, default=str))

    checks.expect_range("line finder finds a task line for most refs", line_finder["line_found_share"], lo=0.8)
    print(coverage.to_string(index=False))
    print(json.dumps({k: v["decision"] for k, v in answers.items() if "decision" in v}, indent=1))
    write_log("rq3_questions", {"changes": len(refs[["repo_name", "change_dir"]].drop_duplicates()),
                                "coverage_strict": q1["strict"]["coverage"], "anchors": q2["distinct_anchors"]},
              started)


if __name__ == "__main__":
    main()
