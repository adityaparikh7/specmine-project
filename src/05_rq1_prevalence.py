"""RQ1: how often do checked OpenSpec tasks name code files that do not exist?

Population: analyzable refs (stage 1) whose task is ticked (task_done = 1),
with intent create or modify (stage 2). The outcome `missing` = the named
file is absent at the anchor commit.

For each cell of intent (create, modify) x change status (archived, in progress):
  - raw missing rate, n refs, n repositories
  - excess = create rate - modify rate, within the same status.
    Modify tasks are the noise floor: a file a task says to edit should already
    exist, so their missing rate estimates matcher and parser error.
  - three measurement versions side by side:
      all        every ref
      full_path  only refs whose path names a folder (no bare file names)
      exact      drop refs found only by name/suffix matching (exact_match False/NA)
  - pooled rate with a 95% interval from repository bootstrap resamples,
    plus the median of per-repository rates (repositories with >= 5 refs),
    so large repositories do not dominate.
Archived changes are the headline: in-progress rates are inflated by code
written after the anchor commit.

Writes tables/table1_rq1.csv and .md, tables/rq1_all_intents.csv, logs/05_rq1_prevalence.json.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `import lib` works

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from lib import checks, stats  # noqa: E402
from lib.io import load_config, output_dir, read_derived, write_csv, write_log, write_text  # noqa: E402

VERSIONS = {
    "all": lambda d: d,
    "full_path": lambda d: d[d["full_path"]],
    "exact": lambda d: d[(d["missing"] == 1) | (d["exact_match"] == True)],  # noqa: E712
}


def load_population():
    refs = read_derived("refs_with_intent")
    refs = refs[refs["analyzable"] & (refs["task_done"] == 1)].copy()
    refs["status"] = np.where(refs["archived"], "archived", "in progress")
    return refs


def table_for(df, version, weights, repos):
    by = ["status", "intent"]
    totals = stats.repo_totals(df, by)
    boot, groups = stats.cell_rates(totals, by, weights, repos)
    lo, hi = stats.ci(boot)
    point = df.groupby(by)["missing"].agg(n="size", rate="mean").reset_index()
    nrepo = df.groupby(by)["repo_name"].nunique().rename("repos").reset_index()
    med = stats.per_repo_median(df, by).rename(columns={"median": "repo_median", "repos": "median_over_repos"})
    t = groups.assign(ci_lo=lo, ci_hi=hi).merge(point).merge(nrepo).merge(med, how="left")

    # excess over modify, within status, using the same resamples
    rows = []
    for status in ["archived", "in progress"]:
        try:
            jc = groups.index[(groups.status == status) & (groups.intent == "create")][0]
            jm = groups.index[(groups.status == status) & (groups.intent == "modify")][0]
        except IndexError:
            continue
        diff = boot[:, jc] - boot[:, jm]
        dlo, dhi = stats.ci(diff)
        pc = t.loc[(t.status == status) & (t.intent == "create"), "rate"].iloc[0]
        pm = t.loc[(t.status == status) & (t.intent == "modify"), "rate"].iloc[0]
        rows.append({"status": status, "intent": "create", "excess": pc - pm,
                     "excess_ci_lo": dlo, "excess_ci_hi": dhi})
    t = t.merge(pd.DataFrame(rows), how="left")
    t.insert(0, "version", version)
    return t


def markdown(t):
    lines = ["| version | status | intent | n | repos | missing rate (95% CI) | per-repo median | excess over modify (95% CI) |",
             "|---|---|---|---:|---:|---|---:|---|"]
    for r in t.itertuples():
        ex = "" if pd.isna(r.excess) else (f"{100 * r.excess:+.1f} pts "
                                            f"({100 * r.excess_ci_lo:+.1f} to {100 * r.excess_ci_hi:+.1f})")
        lines.append(f"| {r.version} | {r.status} | {r.intent} | {r.n:,} | {r.repos:,} | "
                     f"{stats.fmt_pct(r.rate)} ({stats.fmt_pct(r.ci_lo)}–{stats.fmt_pct(r.ci_hi)}) | "
                     f"{stats.fmt_pct(r.repo_median)} | {ex} |")
    return "\n".join(lines)


def main():
    started = time.time()
    config = load_config()
    refs = load_population()
    repos = np.array(sorted(refs["repo_name"].unique()))
    weights = stats.bootstrap_draws(repos, config["bootstrap_draws"], config["seed"])

    cm = refs[refs["intent"].isin(["create", "modify"])]
    table = pd.concat([table_for(VERSIONS[v](cm), v, weights, repos) for v in VERSIONS], ignore_index=True)
    out = output_dir("tables")
    write_csv(table, out / "table1_rq1.csv")
    write_text(out / "table1_rq1.md", "# Table 1: RQ1 — checked tasks naming a missing file\n\n" + markdown(table) + "\n")

    # every intent (delete/move/other/not_task included), all-refs version, for context
    every = refs.groupby(["status", "intent"])["missing"].agg(n="size", rate="mean").reset_index()
    every["repos"] = refs.groupby(["status", "intent"])["repo_name"].nunique().to_numpy()
    write_csv(every, out / "rq1_all_intents.csv")

    head = table[(table.version == "all") & (table.status == "archived")].set_index("intent")
    # The plan's "passing" condition for the noise floor; recorded, does not stop the run.
    checks.results.append({"check": "modify (noise floor) below create, archived",
                           "ok": bool(head.loc["modify", "rate"] < head.loc["create", "rate"]),
                           "detail": f"modify {head.loc['modify', 'rate']:.4f} vs create {head.loc['create', 'rate']:.4f}"})
    counts = {
        "checked_refs": len(refs),
        "checked_create_modify": len(cm),
        "repos": len(repos),
        "archived_create_rate": round(head.loc["create", "rate"], 4),
        "archived_modify_rate": round(head.loc["modify", "rate"], 4),
        "archived_excess_pts": round(100 * head.loc["create", "excess"], 2),
    }
    write_log("05_rq1_prevalence", counts, started)
    print(markdown(table))
    print("\nAll intents (all refs):\n" + every.to_string(index=False))


if __name__ == "__main__":
    main()
