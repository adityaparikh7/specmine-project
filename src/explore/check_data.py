"""Step 0: check that the SpecMine dataset is in place and is the same for everyone.

Before running anything, download the SpecMine v1.0 dataset from Zenodo and
drag the whole folder (or just its 10 .parquet files) into this repository's
data/ folder. The folder name does not matter, on Windows or macOS.

This script then:
  1. finds the folder inside data/ that holds the 10 tables,
  2. checks each table's row count against the SpecMine README,
  3. fingerprints every table (size + SHA-256) and compares with data/MANIFEST.csv,
     which is committed, so the whole team can see they have identical files.
     The first person to run it writes the manifest. If your files differ, the
     script stops; set ACCEPT_NEW_DATA=1 to overwrite the manifest on purpose.

Run:  python run.py check-data     (or: python src/explore/check_data.py)
"""
import hashlib
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

import duckdb  # noqa: E402
import pandas as pd  # noqa: E402

from lib import checks  # noqa: E402
from lib.io import DATA, ROOT, TABLES, find_dataset_dir, find_doc, load_config, sql_path, write_log  # noqa: E402

MANIFEST = DATA / "MANIFEST.csv"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    started = time.time()
    config = load_config()

    # 1. Find the dataset inside data/.
    folder = find_dataset_dir()
    print(f"Found the SpecMine tables in {folder.relative_to(ROOT)}")
    for doc in ["schema.sql", "DATA_DICTIONARY.md"]:
        print(f"  {doc}: {find_doc(doc).relative_to(ROOT)}")

    # 2. Row counts must match the SpecMine README.
    counts = {}
    for table in TABLES:
        path = sql_path(folder / f"{table}.parquet")
        counts[table] = duckdb.sql(f"select count(*) from read_parquet('{path}')").fetchone()[0]
        checks.expect_rows(f"{table} rows match README", counts[table], expected=config["expected_rows"][table])

    # 3. Fingerprint every table and compare with the committed manifest.
    manifest = pd.DataFrame([{"file": f"{t}.parquet",
                              "bytes": (folder / f"{t}.parquet").stat().st_size,
                              "sha256": sha256(folder / f"{t}.parquet")} for t in TABLES])
    if MANIFEST.exists() and os.environ.get("ACCEPT_NEW_DATA") != "1":
        expected = pd.read_csv(MANIFEST).set_index("file")["sha256"]
        different = [r.file for r in manifest.itertuples() if expected.get(r.file) != r.sha256]
        checks.check("tables match data/MANIFEST.csv", not different,
                     f"these files differ from the team's copy: {different}")
        print("All 10 tables match data/MANIFEST.csv.")
    else:
        manifest.to_csv(MANIFEST, index=False)
        print("Wrote data/MANIFEST.csv; commit it so the team can compare.")

    print(manifest.assign(rows=[counts[t] for t in TABLES])[["file", "rows", "bytes"]].to_string(index=False))
    write_log("check_data", counts, started)


if __name__ == "__main__":
    main()
