"""Step 2 of exploring SpecMine: a small CSV sample of every table.

Writes data/sample_csv/<table>.csv with 50 random rows from each of the 10
tables (the same rows every run, thanks to the seed in config.yaml), so you
can open them in Excel, Numbers or VS Code and look around.

To keep the files readable, long text (spec text, commit messages) is cut to
300 characters and line breaks are shown as " ⏎ ". Each table is sampled on
its own, so rows in different files do not belong to the same repositories;
for a connected sample, see rq_sample.py.

Run:  python run.py explore     (or: python src/explore/sample_csv.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

from lib.db import connect  # noqa: E402
from lib.io import DATA, TABLES, load_config, write_csv  # noqa: E402

ROWS_PER_TABLE = 50
MAX_TEXT = 300


def readable(value):
    """Cut long text and show line breaks as ⏎ so each row stays on one line."""
    if isinstance(value, str):
        value = value.replace("\r", "").replace("\n", " ⏎ ")
        if len(value) > MAX_TEXT:
            value = value[:MAX_TEXT] + " …"
    return value


def main():
    seed = load_config()["seed"]
    con = connect()
    out = DATA / "sample_csv"
    out.mkdir(parents=True, exist_ok=True)

    for table in TABLES:
        rows = con.execute(
            f"select * from {table} using sample reservoir({ROWS_PER_TABLE} rows) repeatable ({seed})").df()
        rows = rows.map(readable)
        write_csv(rows, out / f"{table}.csv")
        print(f"{table:25s} {len(rows)} rows x {len(rows.columns)} columns -> data/sample_csv/{table}.csv")


if __name__ == "__main__":
    main()
