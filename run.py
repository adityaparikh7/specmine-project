"""Run the project's steps the same way on Windows and macOS.

    conda activate specmine
    python run.py check-data        check the dataset you dragged into data/
    python run.py explore           table pages, CSV samples, RQ sample
    python run.py checks            deeper checks and reports/data_report.md
    python run.py test              unit tests
    python run.py all               all of the above, in order

Add --sample to `checks` to run it on the small committed sample in data/sample/.
Each step runs its scripts one after another and stops at the first failure.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STEPS = {
    "check-data": ["src/explore/check_data.py"],
    "explore": ["src/explore/show_tables.py",
                "src/explore/sample_csv.py",
                "src/explore/rq_sample.py"],
    "checks": ["src/checks/profile_tables.py",
               "src/checks/check_joins.py",
               "src/checks/check_caveats.py",
               "src/checks/rq3_questions.py",
               "src/checks/make_sample.py",     # skipped with --sample
               "src/checks/data_report.py"],
    "test": ["-m", "pytest", "-q", "tests"],
}


def run(args, sample):
    env = dict(os.environ, SAMPLE="1" if sample else "0", PYTHONUTF8="1")
    print(f"\n>>> python {' '.join(args)}", flush=True)
    if subprocess.run([sys.executable, *args], cwd=ROOT, env=env).returncode != 0:
        sys.exit(f"\nStopped: {' '.join(args)} failed (see the error above).")


def main():
    words = [a for a in sys.argv[1:] if a != "--sample"]
    sample = "--sample" in sys.argv
    if len(words) != 1 or words[0] not in [*STEPS, "all"]:
        sys.exit(__doc__)
    steps = list(STEPS) if words[0] == "all" else words
    for step in steps:
        if step == "test":
            run(STEPS["test"], sample=False)
            continue
        for script in STEPS[step]:
            if sample and script.endswith("make_sample.py"):
                continue  # the sample is built from the full data, never from itself
            run([script], sample)
    print("\nDone.")


if __name__ == "__main__":
    main()
