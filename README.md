# specmine-phantoms

Code for the CS520 SpecMine project: do OpenSpec tasks that are ticked "done"
name files that never appear, and how does that vary with the repository and
with agent credit? Only Phase 1 (getting to know the data) is built so far.

Everything runs the same way on Windows and macOS.

## Setup (once)

1. **Python environment.** Install Miniconda or Anaconda, then from this folder:

   ```bash
   conda env create -f environment.yml
   conda activate specmine
   ```

2. **The dataset.** Download SpecMine v1.0 from Zenodo, unzip it, and drag the
   whole folder into this repository's `data/` folder. The folder name does not
   matter, and dragging only the 10 `.parquet` files (into, say, `data/raw/`)
   works too. You need the `.parquet` files; the CSVs, `specs.jsonl.gz` and the
   MySQL dump are not used. The dataset is never committed to git.

   ```text
   data/
     SpecMine-v1.0/            <- the folder you dragged in (any name)
       data/spec_files.parquet ... (the 10 tables)
       schema.sql, DATA_DICTIONARY.md
     MANIFEST.csv              <- committed: fingerprints of the 10 tables
     sample/                   <- committed: a small slice for tests
   ```

3. **Check it.**

   ```bash
   python run.py check-data
   ```

   This finds the tables, checks their row counts, and compares them with
   `data/MANIFEST.csv`, so the whole team knows it has identical data.

## Exploring the data (start here)

```bash
python run.py explore     # about 15 seconds
```

| Script | What it makes | Open this |
|---|---|---|
| `src/explore/show_tables.py` | One page per table: what it holds, every column with its meaning, how often it is filled in, example values, and 3 sample rows | `reports/tables/README.md` |
| `src/explore/sample_csv.py` | 50 random rows of every table as CSV (long text cut to 300 characters) | `data/sample_csv/` |
| `src/explore/rq_sample.py` | A connected sample of 300 repositories (75 per star band) with only the tables and columns RQ1-RQ3 use | `data/rq_sample/README.md` |

Suggested order: read `reports/tables/README.md`, then the pages for
`openspec_code_refs`, `openspec_artifact_files`, `repo_trees`, `spec_files` and
`spec_file_commits` (the tables the RQs use), then open the CSVs in
`data/rq_sample/` to see real rows side by side. The CSVs open directly in Excel.

## Deeper checks and tests

```bash
python run.py checks            # profiles, joins, known caveats, RQ3 feasibility, data report
python run.py checks --sample   # the same on the small committed sample (a few seconds)
python run.py test              # unit tests
python run.py all               # everything above, in order
```

The checks (in `src/checks/`) confirm the counts and caveats the later phases
rely on, and write `reports/data_report.md`. On macOS the `Makefile` offers the
same steps as shortcuts (`make explore`, `make checks`, ...).

## Layout

```text
run.py             runs the steps: check-data, explore, checks, test, all
config.yaml        settings: seed, star bands, expected row counts, sample sizes
src/lib/io.py      finds the dataset in data/, paths, UTF-8 file helpers, write_log
src/lib/db.py      connect(): DuckDB with one view per table (queries read the Parquet files)
src/lib/checks.py  small checks that stop a script and say what failed
src/lib/rules/     ref_noise.py (paths that are not files), openspec_paths.py (which change a file is in)
src/explore/       check_data.py and the three exploration scripts
src/checks/        the deeper checks and the data report
tests/             unit tests
```

## How the scripts are written

This is a student project, so the code stays plain and easy to follow:

- One script per step, with a docstring saying what it reads and writes, and
  numbered comments for its steps. No classes and no command-line arguments;
  settings live in `config.yaml`. Any script also runs on its own:
  `python src/explore/show_tables.py`.
- `con = connect()` gives DuckDB views over the Parquet files. Use SQL to pick
  columns and filter the big tables, then plain pandas once the data is small.
- Use `pathlib` paths, and the `write_text` / `write_csv` helpers in `lib/io.py`,
  so files are saved as UTF-8 on Windows too.
- Each rule is one Python function with a unit test.

## Notes for Phases 2 and 3

- `lib/rules/ref_noise.py`, the task-line finder in `checks/rq3_questions.py`
  and the trailer pattern in `checks/check_caveats.py` are provisional
  stand-ins for October's `direction1/` and `rq3-ai-authorship/` code.
- Read `reports/data_report.md`, section "Decisions for Phases 2 and 3",
  before writing any Phase 2 or 3 script.
