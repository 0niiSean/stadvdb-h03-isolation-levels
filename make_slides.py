"""
Build the presentation material in results/slides/ from the EXISTING results
(the .txt logs and the two results .md tables). Nothing is hardcoded about outcomes.

Creates:
  matrix.png                 4x3 grid: Occurred / Prevented per isolation level and anomaly
  swimlane_<run>.png         one per run (12 baseline + 4 lock runs "with lock")
  lock_waits.png             wait time with vs without lock
  slide_tables.md            timelines with short labels (SET SESSION and sleep rows removed)
  facts_for_script.md        one raw-facts line per run (16 lines)

Usage:  python make_slides.py     (after run_baseline.py and run_locks.py)
"""
import os
import re

import matplotlib
matplotlib.use("Agg")                      # draw to files, no window
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common import RESULTS_DIR
from timeline_tables import ordered_logs

SLIDES_DIR = os.path.join(RESULTS_DIR, "slides")
GREEN, GREEN_BG = "#1a7f37", "#dcf3e2"     # prevented
RED, RED_BG = "#c62828", "#fde3e3"         # occurred
GREY = "#444444"
LEVELS = ["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"]
ANOMALIES = ["Dirty read", "Non-repeatable read", "Phantom read"]
SIZE = (19.2, 10.8)                        # inches; at dpi=100 -> 1920x1080 pixels

plt.rcParams.update({"font.size": 20, "font.family": "DejaVu Sans"})


# ------------------------------------------------------------------ reading the results .md tables

def read_md_table(filename, first_header):
    """Return the rows (lists of cell strings) of the first table that starts with first_header."""
    rows, inside = [], False
    with open(os.path.join(RESULTS_DIR, filename), encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("|") and first_header in line and not inside:
                inside = True
                continue
            if inside:
                if not line.startswith("|"):
                    break
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if not set(cells[0]) <= set("-"):          # skip the |---| line
                    rows.append(cells)
    return rows


def baseline_rows():
    """[(level, anomaly, saw, occurred_bool, blocked_str)] from baseline_results.md."""
    return [(r[0], r[1], r[2], r[3] == "YES", r[4])
            for r in read_md_table("baseline_results.md", "Isolation level")]


def lock_rows():
    """[(num, level, lock, run, waiter, wait_str)] from locks_results.md."""
    return [(r[0], r[1], r[3], r[4], r[5], r[6])
            for r in read_md_table("locks_results.md", "Waiting session")]


# ------------------------------------------------------------------ reading a .txt log

LINE = re.compile(r"^\[\s*([\d.]+)s\] ([AB]) \| (.*)$")
BLOCKED = re.compile(r"\s+\[BLOCKED ([\d.]+)s\]$")


def parse_log(path):
    """Return (raw_title, events). Each event: session, t (end time), start, sql, result, blocked, kind."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    title = lines[0].strip("= ").strip()
    events = []
    for line in lines[1:]:
        m = LINE.match(line)
        if not m:
            continue
        t, session, body = float(m.group(1)), m.group(2), m.group(3)
        if body.startswith("-- sleep"):
            continue
        if "... waiting" in body:
            sql = body.split("on: ", 1)[1]
            events.append(dict(session=session, t=t, start=t, sql=sql, result="", blocked=0.0,
                               kind="waiting"))
            continue
        sql, _, result = body.partition("  ->  ")
        blocked = 0.0
        mb = BLOCKED.search(result)
        if mb:
            blocked = float(mb.group(1))
            result = result[:mb.start()]
        events.append(dict(session=session, t=t, start=t - blocked, sql=sql.strip(),
                           result=result.strip(), blocked=blocked, kind="done"))
    return title, events


def pretty_title(raw):
    """'DIRTY @ READ COMMITTED' -> 'Dirty read @ READ COMMITTED'; 'Exp3 REPEATABLE READ lock=True' -> ..."""
    m = re.match(r"(DIRTY|NONREPEATABLE|PHANTOM) @ (.*)", raw)
    if m:
        name = {"DIRTY": "Dirty read", "NONREPEATABLE": "Non-repeatable read",
                "PHANTOM": "Phantom read"}[m.group(1)]
        return f"{name} @ {m.group(2)}"
    m = re.match(r"Exp(\d) (.*) lock=(True|False)", raw)
    if m:
        return f"Lock experiment {m.group(1)} @ {m.group(2)} ({'with' if m.group(3) == 'True' else 'without'} lock)"
    return raw


def short_sql(sql):
    """Short slide label for a statement."""
    u = sql.upper()
    if u.startswith("START TRANSACTION"):
        return "BEGIN"
    if u in ("COMMIT", "ROLLBACK", "UNLOCK TABLES"):
        return u
    if u.startswith("LOCK TABLES"):
        return "LOCK TABLES WRITE"
    if u.startswith("SET SESSION"):
        return "SET SESSION"
    if u.startswith("INSERT"):
        return "INSERT film 11"
    lock = " FOR SHARE" if u.endswith("FOR SHARE") else " FOR UPDATE" if u.endswith("FOR UPDATE") else ""
    if u.startswith("UPDATE"):
        m = re.search(r"SET stock = (.+?) WHERE (.+)$", sql)
        what = m.group(1).replace(" ", "")              # "0" or "stock+5"
        where = " (price>3)" if "price" in m.group(2) else ""
        return f"UPDATE stock={what}{where}" if what.isdigit() else f"UPDATE {what}{where}"
    if u.startswith("SELECT COUNT"):
        return "COUNT price>3" + lock
    if u.startswith("SELECT"):
        return "SELECT stock" + lock
    return sql[:25]


def short_result(ev):
    """Short result text: the value for a SELECT, 'OK' / 'N row' otherwise."""
    r = ev["result"]
    m = re.match(r"\[\((.*?),\)\]", r)
    if m:
        return m.group(1)
    if r.startswith("ERROR"):
        return r.split(":")[0]
    m = re.match(r"OK, (\d+) row", r)
    u = ev["sql"].upper()
    if m and u.startswith(("UPDATE", "INSERT")):
        return f"{m.group(1)} row" + ("" if m.group(1) == "1" else "s")
    return "OK"


def is_select(ev):
    return ev["sql"].upper().startswith("SELECT")


# ------------------------------------------------------------------ 1. matrix.png

def make_matrix():
    rows = baseline_rows()
    # cell[(level, column)] = list of (anomaly check name, occurred)
    cell = {}
    for level, anomaly, _saw, occurred, _b in rows:
        col = 0 if anomaly.startswith("Dirty") else 1 if anomaly.startswith("Non") else 2
        cell.setdefault((level, col), []).append((anomaly, occurred))

    fig, ax = plt.subplots(figsize=SIZE, dpi=100)
    ax.set_xlim(0, 5.6)
    ax.set_ylim(0, 5.5)
    ax.axis("off")
    x0, w, h = 1.7, 1.2, 1.0
    for c, name in enumerate(ANOMALIES):
        ax.text(x0 + c * w + w / 2, 4.85, name.replace(" ", "\n", 1) if "-" in name else name, ha="center",
                va="center", fontsize=28, weight="bold", linespacing=1.2)
    for r, level in enumerate(LEVELS):
        y = 3.5 - r * h
        ax.text(x0 - 0.1, y + h / 2 - 0.05, level.title(), ha="right", va="center", fontsize=26, weight="bold")
        for c in range(3):
            checks = cell[(level, c)]
            any_occ = any(o for _, o in checks)
            if len(checks) == 2 and checks[0][1] != checks[1][1]:
                # phantom with different answers: show both checks
                text = "\n".join(f"{'plain SELECT' if 'plain' in a else 'after UPDATE'}: "
                                 f"{'yes' if o else 'no'}" for a, o in checks)
                size = 22
            else:
                text, size = ("Occurred" if any_occ else "Prevented"), 30
            ax.add_patch(Rectangle((x0 + c * w, y), w, h, facecolor=RED_BG if any_occ else GREEN_BG,
                                   edgecolor="white", linewidth=6))
            ax.text(x0 + c * w + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
                    weight="bold", color=RED if any_occ else GREEN, linespacing=1.5)
    fig.savefig(os.path.join(SLIDES_DIR, "matrix.png"), facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ 2. swimlanes

def make_swimlane(path, outname):
    raw, events = parse_log(path)
    events = [e for e in events if e["kind"] == "done" and not e["sql"].upper().startswith("SET SESSION")]
    xmax = max(e["t"] for e in events)
    fig, ax = plt.subplots(figsize=SIZE, dpi=100)
    lane_y = {"A": 5.0, "B": 1.0}
    ax.set_xlim(-1.2, xmax + 0.6)
    ax.set_ylim(-0.6, 8.6)
    for s, y in lane_y.items():
        ax.axhline(y, color="#bbbbbb", linewidth=3, zorder=1)
        ax.text(-1.15, y + 0.1, f"Session {s}", fontsize=26, weight="bold", ha="left", va="bottom")
        ax.text(-1.15, y - 0.1, "writer" if s == "A" else "reader", fontsize=18, color=GREY, ha="left", va="top")

    for s, y in lane_y.items():
        evs = sorted((e for e in events if e["session"] == s), key=lambda e: e["t"])
        level, prev_t = 0, None
        for e in evs:
            # red bar for the blocked period
            if e["blocked"] > 0:
                ax.add_patch(Rectangle((e["start"], y - 0.18), e["blocked"], 0.36, facecolor=RED,
                                       edgecolor="none", zorder=3))
                ax.text(e["start"] + e["blocked"] / 2, y - 0.45, f"blocked {e['blocked']:.2f}s",
                        ha="center", va="top", fontsize=20, color=RED, weight="bold")
            # stagger labels that are close in time so they don't overlap
            level = level + 1 if prev_t is not None and e["t"] - prev_t < 0.6 else 0
            prev_t = e["t"]
            label = short_sql(e["sql"])
            if is_select(e):
                label += f"  →  {short_result(e)}"
            ty = y + 0.45 + 0.62 * level
            ax.plot([e["t"], e["t"]], [y, ty], color=GREY, linewidth=1.5, zorder=2)
            ax.plot(e["t"], y, "o", color="#1f4e79", markersize=13, zorder=4)
            right = e["t"] > xmax * 0.7
            ax.text(e["t"] + (-0.04 if right else 0.04), ty, label, ha="right" if right else "left",
                    va="bottom", fontsize=19, weight="bold" if is_select(e) else "normal")
    ax.set_xlabel("seconds since start", fontsize=22)
    ax.set_yticks([])
    ax.set_xticks(range(0, int(xmax) + 2))      # no negative ticks (left margin holds the lane names)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="x", labelsize=20)
    ax.set_title(pretty_title(raw), fontsize=30, weight="bold", loc="left")
    fig.savefig(os.path.join(SLIDES_DIR, outname), facecolor="white")
    plt.close(fig)


def make_all_swimlanes():
    names = []
    for path in ordered_logs():
        base = os.path.basename(path)
        if base.startswith("baseline_") or base.endswith("_with_lock.txt") and base.startswith("locks_"):
            out = "swimlane_" + base.replace(".txt", ".png")
            make_swimlane(path, out)
            names.append(out)
    return names


# ------------------------------------------------------------------ 3. lock_waits.png

def make_lock_waits():
    rows = lock_rows()
    exps = sorted({r[0] for r in rows})
    labels = {r[0]: f"Exp {r[0]}\n{r[1].title()}" for r in rows}
    no_lock = [float(next(r[5] for r in rows if r[0] == e and r[3].startswith("baseline"))) for e in exps]
    with_lock = [float(next(r[5] for r in rows if r[0] == e and r[3] == "with lock")) for e in exps]
    fig, ax = plt.subplots(figsize=SIZE, dpi=100)
    xs = range(len(exps))
    bw = 0.36
    b1 = ax.bar([x - bw / 2 for x in xs], no_lock, bw, label="Without lock", color="#9aa5b1")
    b2 = ax.bar([x + bw / 2 for x in xs], with_lock, bw, label="With lock", color="#1f4e79")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.04, f"{b.get_height():.2f}s",
                    ha="center", va="bottom", fontsize=24, weight="bold")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([labels[e] for e in exps], fontsize=22)
    ax.set_ylabel("Wait time of the waiting session (s)", fontsize=24)
    ax.set_ylim(0, max(with_lock + no_lock) * 1.2 + 0.1)
    ax.tick_params(axis="y", labelsize=20)
    ax.legend(fontsize=24, frameon=False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_title("Lock wait time: with vs without lock", fontsize=30, weight="bold", loc="left")
    fig.savefig(os.path.join(SLIDES_DIR, "lock_waits.png"), facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ 4. slide_tables.md

def make_slide_tables():
    out = ["# Slide timelines", "",
           "(SET SESSION and sleep rows removed. `→` shows the result; blocked statements are marked.)", ""]
    for path in ordered_logs():
        raw, events = parse_log(path)
        out += [f"## {pretty_title(raw)}", "", "| Time (s) | Session A | Session B |", "|---|---|---|"]
        for e in events:
            if e["sql"].upper().startswith("SET SESSION"):
                continue
            if e["kind"] == "waiting":
                text = f"*waiting: {short_sql(e['sql'])}*"
            else:
                text = f"{short_sql(e['sql'])} → {short_result(e)}"
                if e["blocked"] > 0:
                    text += f" **(blocked {e['blocked']:.2f}s)**"
            a, b = (text, "") if e["session"] == "A" else ("", text)
            out.append(f"| {e['t']:.2f} | {a} | {b} |")
        out.append("")
    with open(os.path.join(SLIDES_DIR, "slide_tables.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


# ------------------------------------------------------------------ 7. facts_for_script.md

def make_facts():
    out = ["# Facts for script", ""]
    # 12 baseline runs, from baseline_results.md (the phantom checks share one run)
    runs = {}
    for level, anomaly, saw, occurred, blocked in baseline_rows():
        key = (anomaly.split(" (")[0], level)
        runs.setdefault(key, dict(saw=saw, blocked=blocked, checks=[]))["checks"].append((anomaly, occurred))
    for a in ANOMALIES:
        for level in LEVELS:
            r = runs[(a, level)]
            if a == "Phantom read":
                occ = ", ".join(f"{'plain SELECT' if 'plain' in n else 'after UPDATE'}={'YES' if o else 'NO'}"
                                for n, o in r["checks"])
            else:
                occ = f"occurred={'YES' if r['checks'][0][1] else 'NO'}"
            out.append(f"- {a} | {level} | {r['saw']} | {occ} | blocked={r['blocked']}s")
    # 4 lock runs (with lock), reads taken from the logs, wait times from locks_results.md
    rows = lock_rows()
    for num in ("1", "2", "3", "4"):
        path = os.path.join(RESULTS_DIR, f"locks_exp{num}_with_lock.txt")
        _t, events = parse_log(path)
        reads = ", ".join(f"{e['session']} read {short_result(e)}" for e in events
                          if e["kind"] == "done" and is_select(e))
        with_row = next(r for r in rows if r[0] == num and r[3] == "with lock")
        base_row = next(r for r in rows if r[0] == num and r[3].startswith("baseline"))
        out.append(f"- Lock exp {num} | {with_row[1]} | {with_row[2]} | {reads} | "
                   f"{with_row[4]} blocked={with_row[5]}s (without lock: {base_row[5]}s)")
    with open(os.path.join(SLIDES_DIR, "facts_for_script.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def main():
    os.makedirs(SLIDES_DIR, exist_ok=True)
    make_matrix()
    names = make_all_swimlanes()
    make_lock_waits()
    make_slide_tables()
    make_facts()
    print(f"Wrote matrix.png, {len(names)} swimlanes, lock_waits.png, slide_tables.md, "
          f"facts_for_script.md to results/slides/")


if __name__ == "__main__":
    main()
