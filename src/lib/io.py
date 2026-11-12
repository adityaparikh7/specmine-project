"""Paths, config and small file helpers that every script shares.

Where is the data? Drag the SpecMine dataset folder (or just its .parquet
files) anywhere inside this repository's data/ folder. find_dataset_dir()
looks through data/ for spec_files.parquet and uses the folder it is in, so
the same scripts work on Windows and macOS whatever the folder is called.

Runs with SAMPLE=1 read data/sample/ instead, and write their outputs to a
`_sample` subfolder (reports/_sample, logs/_sample, ...), so a quick sample
run never overwrites the full-data results.
"""
import json
import os
import time
from pathlib import Path

import pandas as pd
import yaml

# The repository root (this file is src/lib/io.py).
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

# The 10 SpecMine tables, one Parquet file each.
TABLES = [
    "openspec_code_refs",
    "openspec_artifact_files",
    "repo_trees",
    "spec_files",
    "spec_file_commits",
    "spec_links",
    "spec_content_features",
    "kiro_files",
    "pull_requests",
    "pr_files",
]

# Folders inside data/ that our own scripts write; never treated as the dataset.
OUR_FOLDERS = {"sample", "sample_csv", "rq_sample", "derived", "frozen"}


def load_config():
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_sample():
    return os.environ.get("SAMPLE") == "1"


def find_dataset_dir(data_folder=DATA):
    """The folder inside data/ that holds the 10 SpecMine .parquet files."""
    found = []
    for path in sorted(data_folder.rglob("spec_files.parquet")):
        inside = path.relative_to(data_folder).parts
        if inside[0] not in OUR_FOLDERS:
            found.append(path.parent)
    if not found:
        raise FileNotFoundError(
            f"Could not find the SpecMine dataset in {data_folder}.\n"
            "Download it from Zenodo and drag the whole folder (or just its 10 .parquet files) "
            "into the data/ folder of this repository, then run `python run.py check-data`.")
    if len(found) > 1:
        raise RuntimeError("Found more than one copy of the SpecMine dataset; keep only one:\n"
                           + "\n".join(f"  {f}" for f in found))
    folder = found[0]
    missing = [t for t in TABLES if not (folder / f"{t}.parquet").exists()]
    if missing:
        raise FileNotFoundError(f"{folder} is missing these tables: {missing}")
    return folder


def input_dir():
    """Folder the SpecMine tables are read from."""
    return sample_dir() if is_sample() else find_dataset_dir()


def sample_dir():
    return DATA / "sample"


def find_doc(name):
    """schema.sql or DATA_DICTIONARY.md: next to the tables, one folder up, or our copy in data/sample."""
    places = [sample_dir()]
    if not is_sample():
        dataset = find_dataset_dir()
        places = [dataset, dataset.parent, sample_dir()]
    for folder in places:
        if (folder / name).exists():
            return folder / name
    raise FileNotFoundError(f"{name} not found in {places}")


def sql_path(path):
    """A path written the way DuckDB SQL expects it, on Windows too (forward slashes)."""
    return Path(path).as_posix()


def output_dir(name):
    """An output folder such as 'reports', 'logs', 'tables' or 'data/derived'."""
    folder = ROOT / name
    if is_sample():
        folder = folder / "_sample"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def write_text(path, text):
    """Save text as UTF-8 (Windows would otherwise use its own encoding and fail on symbols like ⏎)."""
    Path(path).write_text(text, encoding="utf-8")


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def write_csv(df, path):
    """Save a CSV that Excel on Windows and Mac opens with the right characters."""
    df.to_csv(path, index=False, encoding="utf-8-sig")


def write_derived(df, name):
    """Save a stage's output for later scripts (data/derived/<name>.parquet)."""
    df.to_parquet(output_dir("data/derived") / f"{name}.parquet", index=False)


def read_derived(name):
    return pd.read_parquet(output_dir("data/derived") / f"{name}.parquet")


def write_log(script, counts, started):
    """Write logs/<script>.json: row counts, run time and every check that ran."""
    from lib import checks

    log = {
        "script": script,
        "sample": is_sample(),
        "seconds": round(time.time() - started, 1),
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "counts": counts,
        "checks": checks.results,
    }
    write_text(output_dir("logs") / f"{script}.json", json.dumps(log, indent=2, default=str))
