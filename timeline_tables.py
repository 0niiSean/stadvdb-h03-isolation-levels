"""
Turn the timestamped .txt logs in results/ into results/timelines.md.

One markdown table per run, with columns: Time (s) | Session A | Session B.
Each log line becomes its own row, placed in the column of the session that ran it.

Usage:  python timeline_tables.py     (run after run_baseline.py and run_locks.py)
"""
import glob
import os
import re

from common import RESULTS_DIR

# A log line looks like:  [ 1.07s] B | START TRANSACTION  ->  OK, 0 row(s) affected
LINE = re.compile(r"^\[\s*([\d.]+)s\] ([AB]) \| (.*)$")
# The first line of each log is its title:  === DIRTY @ SERIALIZABLE ===
TITLE = re.compile(r"^=== (.*) ===$")

# Order the runs the same way the scripts ran them (dirty, non-repeatable, phantom; then locks).
ANOMALIES = ["dirty", "nonrepeatable", "phantom"]
LEVELS = ["read_uncommitted", "read_committed", "repeatable_read", "serializable"]


def ordered_logs():
    """Baseline logs first (by anomaly, then level), then the locking logs by experiment."""
    names = [f"baseline_{a}_{lvl}.txt" for a in ANOMALIES for lvl in LEVELS]
    names += [f"locks_exp{n}_{kind}_lock.txt" for n in range(1, 5) for kind in ("without", "with")]
    paths = [os.path.join(RESULTS_DIR, n) for n in names]
    # Also pick up any other .txt log we didn't list, so nothing is silently skipped.
    extra = sorted(set(glob.glob(os.path.join(RESULTS_DIR, "*.txt"))) - set(paths))
    return [p for p in paths + extra if os.path.exists(p)]


def cell(text):
    """Make text safe for a markdown table cell (a literal | would split the column)."""
    return text.replace("|", "\\|")


def table_for(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    title_match = TITLE.match(lines[0])
    title = title_match.group(1) if title_match else os.path.basename(path)

    out = [f"## {title}", "", "| Time (s) | Session A | Session B |", "|---|---|---|"]
    for line in lines[1:]:
        m = LINE.match(line)
        if not m:
            continue
        time_s, session, text = m.groups()
        text = cell(text)
        a_cell, b_cell = (text, "") if session == "A" else ("", text)
        out.append(f"| {time_s} | {a_cell} | {b_cell} |")
    return "\n".join(out)


def main():
    parts = ["# Timelines", ""]
    for path in ordered_logs():
        parts.append(table_for(path))
        parts.append("")
    with open(os.path.join(RESULTS_DIR, "timelines.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"Wrote results/timelines.md ({len(ordered_logs())} tables)")


if __name__ == "__main__":
    main()
