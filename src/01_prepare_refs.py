"""Stage 1: clean the task-to-code references (openspec_code_refs).

Keeps the refs RQ1-RQ3 can use, and tags each one with the flags the analyses need.

Dropped (counted in the log):
  - no anchor commit (anchor_sha null)            -> nothing to check the file against
  - exists_at_anchor = 2 (undocumented value)
  - repository listing truncated (repo_trees)     -> "missing" is unreliable there
Tagged, not dropped (column `noise_rule`, from lib/rules/ref_noise.py):
  - parser noise such as Next.js, .ts, globs, placeholders, task numbers, URLs
  `analyzable` = not noise. Later stages use only analyzable refs.

Flags added:
  missing        1 if the named file is absent at the anchor commit (exists_at_anchor = 0)
  change_dir     the change folder (repo-unique with repo_name)
  archived       the change sits under an archive/ folder (finished)
  archive_date   date prefix of the archived folder (2026-04-25-add-login -> 2026-04-25), if any
  full_path      the code path names a folder (has '/'), not a bare file name
  exact_match    the file was found at exactly the named path (True / False / NA)
                 NA when the file exists but resolved_path is null (Phase 1 caveat N1)
  is_test        the path looks like a test file

Writes data/derived/refs_annotated.parquet.
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `import lib` works

import pandas as pd  # noqa: E402

from lib import checks  # noqa: E402
from lib.db import connect  # noqa: E402
from lib.io import is_sample, write_derived, write_log  # noqa: E402
from lib.rules.openspec_paths import change_dir, is_archived  # noqa: E402
from lib.rules.ref_noise import noise_rule  # noqa: E402

ARCHIVE_DATE = re.compile(r"(?:^|/)archive/(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
TEST_FILE = re.compile(
    r"(^|/)(tests?|__tests__|spec|specs|e2e|testing)/"      # a test folder
    r"|(^|/)test_[^/]+$|_test\.[a-z0-9]+$"                   # test_x.py, x_test.go
    r"|\.(test|spec)\.[a-z0-9]+$"                            # x.test.ts, x.spec.js
    r"|(Test|Tests|Spec|IT)\.(java|kt|cs|scala|swift)$",     # FooTest.java, BarSpec.scala
    re.IGNORECASE)


def archive_date(path):
    match = ARCHIVE_DATE.search(path)
    return match.group(1) if match else None


def main():
    started = time.time()
    con = connect()
    refs = con.execute("""select r.*, t.truncated
                          from openspec_code_refs r left join repo_trees t using (repo_name)""").df()
    n_all = len(refs)

    no_anchor = refs["anchor_sha"].isna()
    exists_two = refs["exists_at_anchor"] == 2
    truncated = refs["truncated"] == 1
    refs = refs[~no_anchor & ~exists_two & ~truncated].copy()
    checks.check("every kept ref has exists_at_anchor 0 or 1",
                 refs["exists_at_anchor"].isin([0, 1]).all())

    refs["noise_rule"] = refs["code_path"].map(noise_rule)
    refs["analyzable"] = refs["noise_rule"].isna()
    refs["missing"] = (refs["exists_at_anchor"] == 0).astype("int8")
    refs["change_dir"] = refs["artifact_path"].map(change_dir)
    refs["archived"] = refs["artifact_path"].map(is_archived)
    refs["archive_date"] = pd.to_datetime(refs["artifact_path"].map(archive_date), errors="coerce")
    refs["full_path"] = refs["code_path"].str.contains("/", regex=False)
    refs["is_test"] = refs["code_path"].str.contains(TEST_FILE)
    exact = pd.Series(pd.NA, index=refs.index, dtype="boolean")
    exact[refs["missing"] == 1] = False  # nothing was found, so no match of any kind
    found = refs["resolved_path"].notna()
    exact[found] = refs.loc[found, "resolved_path"] == refs.loc[found, "code_path"]
    refs["exact_match"] = exact
    refs = refs.drop(columns=["truncated"])

    kept = refs[refs["analyzable"]]
    n_changes = len(kept[["repo_name", "change_dir"]].drop_duplicates())
    counts = {
        "refs_in": n_all,
        "dropped_no_anchor": int(no_anchor.sum()),
        "dropped_exists_2": int(exists_two.sum()),
        "dropped_truncated_listing": int((truncated & ~no_anchor & ~exists_two).sum()),
        "refs_out": len(refs),
        "noise": int((~refs["analyzable"]).sum()),
        "noise_by_rule": refs["noise_rule"].value_counts().to_dict(),
        "analyzable": len(kept),
        "analyzable_repos": kept["repo_name"].nunique(),
        "analyzable_changes": n_changes,
        "analyzable_archived_share": round(kept["archived"].mean(), 4),
        "analyzable_missing_share": round(kept["missing"].mean(), 4),
        "exact_match_unknown": int(kept["exact_match"].isna().sum()),
    }
    if not is_sample():
        # Phase 1 (check_caveats R7) found 405,368 refs in 6,802 repositories and 59,965 changes.
        checks.expect_range("analyzable refs match Phase 1 (R7)", len(kept), lo=405_368, hi=405_368)
        checks.expect_range("analyzable repos match Phase 1 (R7)", counts["analyzable_repos"], lo=6_802, hi=6_802)

    write_derived(refs, "refs_annotated")
    write_log("01_prepare_refs", counts, started)
    for k, v in counts.items():
        print(f"{k:28} {v:,}" if isinstance(v, int) else f"{k:28} {v}")


if __name__ == "__main__":
    main()
