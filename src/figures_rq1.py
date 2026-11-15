"""Figures 1 and 2 of the paper (RQ1), drawn from the tables 05 and 07 wrote.

Figure 1  missing rate per cell (create / modify x archived / in progress) with 95%
          intervals, the three measurement versions (all refs, full paths, exact
          matches) side by side.
Figure 2  within-change comparison: ticked vs unticked create tasks in the same
          changes, archived and in progress, with modify tasks as the baseline.

Writes figures/fig1_rq1_rates.png/.pdf and figures/fig2_checkbox_within_change.png/.pdf.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `import lib` works

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from lib.io import output_dir  # noqa: E402

COLORS = {"create": "#3B6EA8", "modify": "#A7B4C2", "ticked": "#3B6EA8", "unticked": "#D08C3B"}
VERSION_LABEL = {"all": "All refs", "full_path": "Full paths only", "exact": "Exact matches only"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    out = output_dir("figures")
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote figures/{name}.png/.pdf")


def figure1(t):
    versions = [v for v in VERSION_LABEL if v in set(t.version)]
    fig, axes = plt.subplots(1, len(versions), figsize=(2.4 * len(versions), 2.6), sharey=True)
    axes = np.atleast_1d(axes)
    statuses = ["archived", "in progress"]
    for ax, v in zip(axes, versions):
        d = t[t.version == v]
        for k, intent in enumerate(["create", "modify"]):
            x = np.arange(len(statuses)) + (k - 0.5) * 0.36
            rows = [d[(d.status == s) & (d.intent == intent)].iloc[0] for s in statuses]
            rate = np.array([r.rate for r in rows]) * 100
            err = np.array([[r.rate - r.ci_lo for r in rows], [r.ci_hi - r.rate for r in rows]]) * 100
            ax.bar(x, rate, 0.34, yerr=err, color=COLORS[intent], capsize=2, label=intent,
                   error_kw={"elinewidth": 0.8})
            top = rate + err[1]
            for xi, ri, ti in zip(x, rate, top):
                ax.text(xi, ti + 0.6, f"{ri:.1f}", ha="center", va="bottom", fontsize=7)
        ax.set_xticks(range(len(statuses)), statuses)
        ax.set_title(VERSION_LABEL[v], fontsize=9)
    axes[0].set_ylabel("Checked refs naming a missing file (%)")
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    save(fig, "fig1_rq1_rates")


def figure2(w):
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    groups = [(i, s) for i in ["create", "modify"] for s in ["archived", "in progress"]
              if len(w[(w.intent == i) & (w.status == s)])]
    x = np.arange(len(groups))
    for k, side in enumerate(["ticked", "unticked"]):
        vals = [w[(w.intent == i) & (w.status == s)][f"{side}_missing_rate"].iloc[0] * 100 for i, s in groups]
        xs = x + (k - 0.5) * 0.36
        ax.bar(xs, vals, 0.34, color=COLORS[side], label=f"{side} tasks")
        for xi, vi in zip(xs, vals):
            ax.text(xi, vi + 0.6, f"{vi:.1f}", ha="center", va="bottom", fontsize=7)
    labels = []
    for i, s in groups:
        r = w[(w.intent == i) & (w.status == s)].iloc[0]
        labels.append(f"{i}\n{s}\n({r.changes:,} changes)")
    ax.set_xticks(x, labels, fontsize=7.5)
    ax.set_ylabel("Missing (%)")
    ax.set_title("Same change, ticked vs unticked tasks", fontsize=9)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    save(fig, "fig2_checkbox_within_change")


def main():
    tables = output_dir("tables")
    figure1(pd.read_csv(tables / "table1_rq1.csv"))
    figure2(pd.read_csv(tables / "checkbox_within_change.csv"))


if __name__ == "__main__":
    main()
