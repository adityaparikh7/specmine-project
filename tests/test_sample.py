"""The committed 200-repository sample loads and is consistent."""
import pandas as pd
import pytest

from lib.io import TABLES, load_config, sample_dir


@pytest.fixture(scope="module")
def con():
    mp = pytest.MonkeyPatch()
    mp.setenv("SAMPLE", "1")
    from lib.db import connect
    yield connect()  # connect() also checks every column against schema.sql
    mp.undo()


def test_tables_match_sample_manifest(con):
    manifest = pd.read_csv(sample_dir() / "SAMPLE_MANIFEST.csv").set_index("table")["rows"]
    for table in TABLES:
        assert con.execute(f"select count(*) from {table}").fetchone()[0] == manifest[table]


def test_sample_repositories(con):
    repos = pd.read_csv(sample_dir() / "sample_repos.csv")
    assert len(repos) == repos["repo_name"].nunique() == load_config()["sample"]["n_repos"]
    assert repos["band"].value_counts().nunique() == 1  # the same number per star band
    n = con.execute("select count(distinct repo_name) from openspec_code_refs").fetchone()[0]
    assert n == len(repos)


def test_star_bands():
    import sys
    sys.path.insert(0, "src/checks")
    from make_sample import star_band
    bounds = [0, 1, 10, 100]
    assert [star_band(s, bounds) for s in [0, 1, 9, 10, 99, 100, 5000]] == \
        ["0", "1-9", "1-9", "10-99", "10-99", "100+", "100+"]
