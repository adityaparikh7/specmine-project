"""Small statistics helpers shared by the analysis scripts.

Refs in one repository are not independent (one sloppy repository produces many
missing files at once), so every interval here resamples REPOSITORIES, not refs.
"""
import numpy as np
import pandas as pd


def repo_totals(df, by, outcome="missing"):
    """Per (repository, group) sums: n refs and n with the outcome."""
    g = df.groupby(["repo_name", *by], observed=True)[outcome].agg(["size", "sum"]).reset_index()
    return g.rename(columns={"size": "n", "sum": "k"})


def bootstrap_draws(repos, draws, seed):
    """A (draws x repos) matrix of how many times each repository is picked in each resample."""
    rng = np.random.default_rng(seed)
    n = len(repos)
    return np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(draws)])


def cell_rates(totals, by, weights, repos):
    """Bootstrap rate for every group: matrix (draws x groups) plus the group labels."""
    index = {r: i for i, r in enumerate(repos)}
    groups = totals[by].drop_duplicates().sort_values(by).reset_index(drop=True)
    out = np.empty((weights.shape[0], len(groups)))
    for j, key in enumerate(groups.itertuples(index=False)):
        sel = totals
        for col, val in zip(by, key):
            sel = sel[sel[col] == val]
        idx = sel["repo_name"].map(index).to_numpy()
        w = weights[:, idx]
        with np.errstate(invalid="ignore", divide="ignore"):
            out[:, j] = (w * sel["k"].to_numpy()).sum(1) / (w * sel["n"].to_numpy()).sum(1)
    return out, groups


def ci(x, level=0.95):
    lo, hi = np.nanpercentile(x, [(1 - level) / 2 * 100, (1 + level) / 2 * 100], axis=0)
    return lo, hi


def per_repo_median(df, by, outcome="missing", min_refs=5):
    """Median over repositories (with at least min_refs refs in the group) of each repository's rate."""
    g = df.groupby([*by, "repo_name"], observed=True)[outcome].agg(["mean", "size"]).reset_index()
    g = g[g["size"] >= min_refs]
    return g.groupby(by, observed=True)["mean"].agg(median="median", repos="size").reset_index()


def fmt_pct(x, digits=1):
    return "" if pd.isna(x) else f"{100 * x:.{digits}f}%"
