"""Stage 2: find the task line behind each reference and label its intent.

For every ref from stage 1, open its tasks.md (openspec_artifact_files.content),
find the checkbox line that names the file, and classify that line with
lib/rules/intent_rules.py as create / modify / delete / move / other.

Line finding:
  - a task can wrap onto indented continuation lines; they are folded in
  - the full code path is searched first, then its file name
  - among matching lines, one whose checkbox agrees with task_done is preferred
Refs whose path appears only outside checkbox lines (notes, code blocks) get
intent 'not_task' and line_match 'none'.

Writes data/derived/refs_with_intent.parquet (stage 1 columns plus
task_line, line_match, verb, intent, move_role).
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `import lib` works

import pandas as pd  # noqa: E402

from lib import checks  # noqa: E402
from lib.db import connect  # noqa: E402
from lib.io import read_derived, write_derived, write_log  # noqa: E402
from lib.rules.intent_rules import classify, parse_checkbox  # noqa: E402


def task_items(content):
    """[(checked, text)] for each checkbox item, continuation lines folded in."""
    items, current = [], None
    for line in (content or "").splitlines():
        box = parse_checkbox(line)
        if box:
            current = [box[0], box[1].strip()]
            items.append(current)
        elif current and line[:1] in (" ", "\t") and line.strip() and not line.lstrip().startswith(("-", "*", "#", "```", "|")):
            current[1] += " " + line.strip()
        else:
            current = None
    return items


def find_line(items, code_path, done):
    """(text, how) of the task naming the path: exact path first, then file name."""
    base = code_path.rsplit("/", 1)[-1]
    for needle, how in ((code_path, "path"), (base, "file_name")):
        hits = [(checked, text) for checked, text in items if needle in text]
        if hits:
            agree = [text for checked, text in hits if checked == bool(done)]
            return (agree or [hits[0][1]])[0], how
    return None, "none"


def main():
    started = time.time()
    refs = read_derived("refs_annotated")
    con = connect()
    texts = con.execute("""select repo_name, file_path as artifact_path, content from openspec_artifact_files
                           where content is not null""").df()
    texts = texts.merge(refs[["repo_name", "artifact_path"]].drop_duplicates())
    items_of = {(r.repo_name, r.artifact_path): task_items(r.content) for r in texts.itertuples()}

    lines, how = [], []
    for r in refs[["repo_name", "artifact_path", "code_path", "task_done"]].itertuples(index=False):
        text, h = find_line(items_of.get((r.repo_name, r.artifact_path), []), r.code_path, r.task_done)
        lines.append(text)
        how.append(h)
    refs["task_line"] = lines
    refs["line_match"] = how
    labels = [classify(t, c) if isinstance(t, str) else ("not_task", "", "")
              for t, c in zip(refs["task_line"], refs["code_path"])]
    refs["intent"] = [x[0] for x in labels]
    refs["verb"] = [x[1] for x in labels]
    refs["move_role"] = [x[2] for x in labels]

    a = refs[refs["analyzable"]]
    found = a["line_match"] != "none"
    checks.expect_range("task line found for most analyzable refs", found.mean(), lo=0.85)
    intent_share = a["intent"].value_counts(normalize=True).round(4).to_dict()
    counts = {
        "analyzable": len(a),
        "line_found_share": round(found.mean(), 4),
        "line_match": a["line_match"].value_counts().to_dict(),
        "intent_share": intent_share,
        "intent_share_checked": a[a["task_done"] == 1]["intent"].value_counts(normalize=True).round(4).to_dict(),
        "top_other_verbs": a.loc[a["intent"] == "other", "verb"].value_counts().head(30).to_dict(),
    }
    write_derived(refs, "refs_with_intent")
    write_log("02_classify_intent", counts, started)
    for k, v in counts.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
