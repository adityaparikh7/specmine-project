"""Checks a script runs on its own results.

Every check is recorded in `results` (write_log saves them to logs/).
A failed check raises CheckFailed, which stops the script and `make`,
and the error message names the check.
"""


class CheckFailed(AssertionError):
    pass


results = []


def check(name, ok, detail=""):
    """Record one check; stop the script if it failed."""
    results.append({"check": name, "ok": bool(ok), "detail": detail})
    if not ok:
        raise CheckFailed(f"[{name}] {detail}")


def expect_rows(name, n, expected=None, min=None, max=None):  # noqa: A002
    ok = ((expected is None or n == expected)
          and (min is None or n >= min)
          and (max is None or n <= max))
    check(name, ok, f"rows={n:,}, expected={expected}, min={min}, max={max}")


def expect_unique(con, table, columns):
    """No two rows of `table` share the same values in `columns`."""
    key = ", ".join(columns)
    duplicates = con.execute(f"select count(*) - count(distinct ({key})) from {table}").fetchone()[0]
    check(f"{table} unique on {key}", duplicates == 0, f"duplicate rows={duplicates:,}")


def expect_null_share(name, share, max_share):
    check(name, share <= max_share, f"null share={share:.4f}, max={max_share}")


def expect_range(name, value, lo=None, hi=None):
    check(name, (lo is None or value >= lo) and (hi is None or value <= hi),
          f"value={value}, range=[{lo}, {hi}]")
