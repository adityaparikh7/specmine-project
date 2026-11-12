import duckdb
import pandas as pd
import pytest

from lib import checks


def test_passing_checks_are_recorded():
    checks.expect_rows("exact", 10, expected=10)
    checks.expect_rows("range", 5, min=1, max=9)
    assert checks.results[-1]["ok"] and checks.results[-2]["ok"]


def test_failing_check_names_itself():
    with pytest.raises(checks.CheckFailed, match=r"\[too few\]"):
        checks.expect_rows("too few", 3, min=4)


def test_expect_unique():
    con = duckdb.connect()
    con.register("t", pd.DataFrame({"a": [1, 1, 2], "b": ["x", "y", "x"]}))
    checks.expect_unique(con, "t", ["a", "b"])
    with pytest.raises(checks.CheckFailed):
        checks.expect_unique(con, "t", ["a"])


def test_null_share_and_range():
    checks.expect_null_share("nulls", 0.01, 0.05)
    with pytest.raises(checks.CheckFailed):
        checks.expect_range("range", 1.2, lo=0, hi=1)
