"""Open DuckDB with one view per SpecMine table.

    from lib.db import connect
    con = connect()
    df = con.execute("select spec_tool, count(*) from spec_files group by 1").df()

Views read the Parquet files wherever the dataset sits inside data/ (or
data/sample/ with SAMPLE=1),
so nothing is loaded until a query asks for it. connect() also checks that
the files are the ones in data/MANIFEST.csv and that every column matches
schema.sql; either problem stops the script.

DuckDB gotcha: min()/max() of a text column read straight from these files
can come back cut short (e.g. '2009-03-'), because DuckDB answers from Parquet
statistics. Write min(col || '') to make it read the real values.
"""
import re

import duckdb
import pandas as pd

from lib.io import ROOT, TABLES, find_doc, input_dir, is_sample, load_config, read_text, sql_path

MANIFEST = ROOT / "data" / "MANIFEST.csv"

# Which DuckDB types fit each MySQL type in schema.sql.
INTEGER_TYPES = {"BIGINT", "INTEGER", "SMALLINT", "TINYINT"}
FITS = {
    "int": INTEGER_TYPES, "bigint": INTEGER_TYPES, "tinyint": INTEGER_TYPES,
    "char": {"VARCHAR"}, "varchar": {"VARCHAR"}, "text": {"VARCHAR"}, "longtext": {"VARCHAR"},
    "timestamp": {"VARCHAR", "TIMESTAMP"},  # SpecMine ships its one timestamp column as text
}


def connect(check=True):
    folder = input_dir()
    con = duckdb.connect()
    con.execute(f"set memory_limit = '{load_config()['duckdb_memory_limit']}'")
    con.execute("set preserve_insertion_order = false")  # lets big queries use less memory
    for table in TABLES:
        path = folder / f"{table}.parquet"
        con.execute(f"create view {table} as select * from read_parquet('{sql_path(path)}')")
    if check:
        if not is_sample():
            check_manifest_sizes()
        problems = schema_problems(con)
        if problems:
            raise RuntimeError("Parquet files do not match schema.sql:\n" + "\n".join(problems))
    return con


def check_manifest_sizes():
    """Quick check that every table still has the size recorded by check_data.py."""
    if not MANIFEST.exists():
        raise FileNotFoundError("data/MANIFEST.csv is missing; run `python run.py check-data` first")
    folder = input_dir()
    for row in pd.read_csv(MANIFEST).itertuples():
        if (folder / row.file).stat().st_size != row.bytes:
            raise RuntimeError(f"{row.file} is not the file listed in data/MANIFEST.csv; "
                               "run `python run.py check-data` to see what changed")


def read_schema_sql(path):
    """schema.sql -> {table: [(column, mysql_type), ...]}"""
    text = read_text(path)
    schema = {}
    for table, body in re.findall(r"CREATE TABLE `(\w+)` \((.*?)\)\s*DEFAULT", text, re.S):
        schema[table] = re.findall(r"^\s*`(\w+)`\s+([a-z]+)", body, re.M)
    return schema


def schema_problems(con):
    """Every way the Parquet views differ from schema.sql, as readable strings."""
    expected = read_schema_sql(find_doc("schema.sql"))
    problems = []
    for table in TABLES:
        actual = dict(con.execute(f"select column_name, column_type from (describe {table})").fetchall())
        wanted = dict(expected.get(table, []))
        for col in wanted.keys() - actual.keys():
            problems.append(f"{table}.{col}: in schema.sql but not in the Parquet file")
        for col in actual.keys() - wanted.keys():
            problems.append(f"{table}.{col}: in the Parquet file but not in schema.sql")
        for col in wanted.keys() & actual.keys():
            if actual[col] not in FITS.get(wanted[col], set()):
                problems.append(f"{table}.{col}: Parquet type {actual[col]} does not fit {wanted[col]}")
    return problems
