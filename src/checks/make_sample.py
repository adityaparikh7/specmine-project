"""Phase 1, step 6: a 200-repository slice of every table, for tests and quick runs.

We draw OpenSpec repositories that have task references, the same number from
each star band (0, 1-9, 10-99, 100+ with the default config), using the config
seed so every laptop gets the same sample. Then every table is cut down to
those repositories and saved to data/sample/.

spec_content_features and spec_links have no repo_name column, so they are
cut through the sampled repositories' spec_files rows (file_url_sha16).
"""
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import lib` works

import pandas as pd  # noqa: E402

from lib import checks  # noqa: E402
from lib.db import connect  # noqa: E402
from lib.io import TABLES, find_doc, is_sample, load_config, sample_dir, sql_path, write_log  # noqa: E402


def star_band(stars, bounds):
    """'0', '1-9', '10-99' or '100+' for bounds [0, 1, 10, 100]."""
    for i in reversed(range(len(bounds))):
        if stars >= bounds[i]:
            if i == len(bounds) - 1:
                return f"{bounds[i]}+"
            high = bounds[i + 1] - 1
            return str(bounds[i]) if high == bounds[i] else f"{bounds[i]}-{high}"


def main():
    if is_sample():
        sys.exit("make_sample.py builds data/sample from the full data; run it without SAMPLE=1")
    started = time.time()
    config = load_config()
    con = connect()

    # 1. Eligible repositories: those with task references, with their star count.
    repos = con.execute("""
        select repo_name, max(repo_stars) as stars from spec_files
        where repo_name in (select repo_name from openspec_code_refs)
        group by 1 order by 1""").df()
    repos["band"] = repos["stars"].map(lambda s: star_band(s, config["star_bands"]))

    # 2. The same number from every band.
    per_band = config["sample"]["n_repos"] // len(config["star_bands"])
    for band, n in repos["band"].value_counts().items():
        checks.check(f"band {band} has enough repositories", n >= per_band, f"{n} < {per_band}")
    sample = repos.groupby("band").sample(n=per_band, random_state=config["seed"])
    sample = sample.sort_values(["band", "repo_name"]).reset_index(drop=True)
    checks.expect_rows("sample size", len(sample), expected=config["sample"]["n_repos"])

    # 3. Cut every table down to the sampled repositories.
    out = sample_dir()
    out.mkdir(parents=True, exist_ok=True)
    sample.to_csv(out / "sample_repos.csv", index=False)
    con.register("sample_repos", sample[["repo_name"]])
    in_sample = "repo_name in (select repo_name from sample_repos)"
    sample_files = f"(select file_url_sha16 from spec_files where {in_sample})"
    where = {table: in_sample for table in TABLES}
    where["spec_content_features"] = f"file_url_sha16 in {sample_files}"
    where["spec_links"] = f"spec_url_sha16 in {sample_files}"

    manifest = []
    for table in TABLES:
        path = out / f"{table}.parquet"
        con.execute(f"copy (select * from {table} where {where[table]} order by all) "
                    f"to '{sql_path(path)}' (format parquet, compression zstd)")
        n = con.execute(f"select count(*) from read_parquet('{sql_path(path)}')").fetchone()[0]
        manifest.append({"table": table, "rows": n, "bytes": path.stat().st_size})
    # Keep copies of the two documents so the sample works on its own.
    for doc in ["schema.sql", "DATA_DICTIONARY.md"]:
        shutil.copy2(find_doc(doc), out / doc)
    manifest = pd.DataFrame(manifest)
    manifest.to_csv(out / "SAMPLE_MANIFEST.csv", index=False)

    megabytes = manifest["bytes"].sum() / 1e6
    checks.expect_range("sample is small enough to commit (MB)", megabytes, hi=50)
    print(sample["band"].value_counts().to_string())
    print(manifest.to_string(index=False), f"\ntotal {megabytes:.1f} MB")
    write_log("make_sample", {**dict(zip(manifest["table"], manifest["rows"])),
                              "eligible_by_band": repos["band"].value_counts().to_dict()}, started)


if __name__ == "__main__":
    main()
