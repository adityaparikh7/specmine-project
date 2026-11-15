"""Checkbox reliability (part of RQ1): does a ticked box mean the file is there?

1. 2 x 2 per intent and status: ticked vs unticked against present vs missing.
     over-claim  = ticked but the file is missing   (share of ticked refs)
     under-claim = unticked but the file is present (share of unticked refs)
2. Within-change comparison: in every change that has BOTH ticked and unticked
   create tasks, compare their missing rates. Both sides share one anchor commit
   and one repository, so timing and repository effects cancel. 95% interval
   from repository bootstrap resamples. Repeated for modify tasks as a baseline.
3. Archived changes with no box ticked at all, as their own row: the work was
   archived, yet nothing was ticked. How often are their files missing?

Writes tables/checkbox_2x2.csv, tables/checkbox_within_change.csv,
tables/checkbox_no_box_ticked.csv, tables/checkbox.md, logs/07_checkbox.json.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `import lib` works

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from lib import stats  # noqa: E402
from lib.db import connect  # noqa: E402
from lib.io import load_config, output_dir, read_derived, write_csv, write_log, write_text  # noqa: E402
from lib.rules.openspec_paths import is_archived  # noqa: E402

INTENTS = ["create", "modify"]


def two_by_two(refs):
    rows = []
    for (status, intent), d in refs[refs["intent"].isin(INTENTS)].groupby(["status", "intent"]):
        t, u = d[d["task_done"] == 1], d[d["task_done"] == 0]
        rows.append({
            "status": status, "intent": intent,
            "ticked_present": int((t["missing"] == 0).sum()), "ticked_missing": int(t["missing"].sum()),
            "unticked_present": int((u["missing"] == 0).sum()), "unticked_missing": int(u["missing"].sum()),
            "over_claim": t["missing"].mean(), "under_claim": (u["missing"] == 0).mean(),
        })
    return pd.DataFrame(rows)


def within_change(refs, intent, weights, repos):
    d = refs[refs["intent"] == intent]
    both = d.groupby(["repo_name", "change_dir"])["task_done"].agg(["min", "max"]).reset_index()
    both = both[(both["min"] == 0) & (both["max"] == 1)][["repo_name", "change_dir"]]
    d = d.merge(both)
    d["side"] = np.where(d["task_done"] == 1, "ticked", "unticked")
    rows = []
    for status, ds in d.groupby("status"):
        totals = stats.repo_totals(ds, ["side"])
        boot, groups = stats.cell_rates(totals, ["side"], weights, repos)
        i_t = groups.index[groups.side == "ticked"][0]
        i_u = groups.index[groups.side == "unticked"][0]
        diff = boot[:, i_u] - boot[:, i_t]
        lo, hi = stats.ci(diff)
        rt = ds.loc[ds.side == "ticked", "missing"].mean()
        ru = ds.loc[ds.side == "unticked", "missing"].mean()
        rows.append({
            "intent": intent, "status": status,
            "changes": len(ds[["repo_name", "change_dir"]].drop_duplicates()),
            "repos": ds["repo_name"].nunique(),
            "ticked_refs": int((ds.side == "ticked").sum()), "unticked_refs": int((ds.side == "unticked").sum()),
            "ticked_missing_rate": rt, "unticked_missing_rate": ru,
            "gap_pts": 100 * (ru - rt), "gap_ci_lo": 100 * lo, "gap_ci_hi": 100 * hi,
        })
    return rows


def no_box_ticked(refs):
    con = connect()
    arts = con.execute("""select repo_name, file_path as artifact_path, n_tasks, n_tasks_done
                          from openspec_artifact_files where kind = 'tasks.md'""").df()
    arts = arts[arts["artifact_path"].map(is_archived) & (arts["n_tasks_done"] == 0)]
    d = refs.merge(arts[["repo_name", "artifact_path"]])
    rows = [{"group": "archived tasks.md with no box ticked (any task count)",
             "tasks_md_files": len(arts), "with_tasks": int((arts["n_tasks"] > 0).sum()),
             "with_refs": d["artifact_path"].nunique() if len(d) else 0}]
    for intent, di in d[d["intent"].isin(INTENTS)].groupby("intent"):
        rows.append({"group": f"  refs, {intent}", "refs": len(di), "repos": di["repo_name"].nunique(),
                     "missing_rate": di["missing"].mean()})
    return pd.DataFrame(rows), len(arts)


def main():
    started = time.time()
    config = load_config()
    refs = read_derived("refs_with_intent")
    refs = refs[refs["analyzable"]].copy()
    refs["status"] = np.where(refs["archived"], "archived", "in progress")
    repos = np.array(sorted(refs["repo_name"].unique()))
    weights = stats.bootstrap_draws(repos, config["bootstrap_draws"], config["seed"])

    t22 = two_by_two(refs)
    wc = pd.DataFrame([r for i in INTENTS for r in within_change(refs, i, weights, repos)])
    nb, n_nobox = no_box_ticked(refs)

    out = output_dir("tables")
    write_csv(t22, out / "checkbox_2x2.csv")
    write_csv(wc, out / "checkbox_within_change.csv")
    write_csv(nb, out / "checkbox_no_box_ticked.csv")

    md = ["# Checkbox reliability (RQ1)\n", "## Ticked vs unticked, present vs missing\n",
          "| status | intent | ticked: missing / total | over-claim | unticked: present / total | under-claim |",
          "|---|---|---|---:|---|---:|"]
    for r in t22.itertuples():
        nt, nu = r.ticked_present + r.ticked_missing, r.unticked_present + r.unticked_missing
        md.append(f"| {r.status} | {r.intent} | {r.ticked_missing:,} / {nt:,} | {stats.fmt_pct(r.over_claim)} | "
                  f"{r.unticked_present:,} / {nu:,} | {stats.fmt_pct(r.under_claim)} |")
    md += ["\n## Within-change: changes with both ticked and unticked tasks of one intent\n",
           "| intent | status | changes | repos | ticked missing | unticked missing | gap (95% CI) |",
           "|---|---|---:|---:|---:|---:|---|"]
    for r in wc.itertuples():
        md.append(f"| {r.intent} | {r.status} | {r.changes:,} | {r.repos:,} | {stats.fmt_pct(r.ticked_missing_rate)} | "
                  f"{stats.fmt_pct(r.unticked_missing_rate)} | {r.gap_pts:+.1f} pts ({r.gap_ci_lo:+.1f} to {r.gap_ci_hi:+.1f}) |")
    md += ["\n## Archived changes with no box ticked\n", nb.to_markdown(index=False, floatfmt=".3f")]
    write_text(out / "checkbox.md", "\n".join(md) + "\n")

    a = wc[(wc.intent == "create") & (wc.status == "archived")]
    counts = {"archived_no_box_ticked_tasks_md": n_nobox}
    if len(a):
        a = a.iloc[0]
        counts.update({"within_change_create_archived_changes": int(a.changes),
                       "ticked_missing_rate": round(a.ticked_missing_rate, 4),
                       "unticked_missing_rate": round(a.unticked_missing_rate, 4)})
    write_log("07_checkbox", counts, started)
    print("\n".join(md))


if __name__ == "__main__":
    main()
