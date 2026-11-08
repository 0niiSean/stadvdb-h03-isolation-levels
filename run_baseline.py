"""
Baseline test: 3 anomalies x 4 isolation levels = 12 cases.

Session A = writer, Session B = reader. A runs in its own thread so it can block
(e.g. wait for B's lock) without freezing the script. sleep() calls force the
order of events. Nothing is hardcoded about the outcome: we print what happened.
"""
import os

from common import RESULTS_DIR, Session, Timeline, first_value, start_thread
from reset_data import reset

LEVELS = ["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"]

# Textbook table: True = anomaly CAN occur (V), False = cannot occur (X).
# Order of each tuple: (dirty read, non-repeatable read, phantom read)
TEXTBOOK = {
    "SERIALIZABLE":     (False, False, False),
    "REPEATABLE READ":  (False, False, True),
    "READ COMMITTED":   (False, True,  True),
    "READ UNCOMMITTED": (True,  True,  True),
}
COLUMN_NAMES = ["Dirty read", "Non-repeatable read", "Phantom read"]

READ_STOCK = "SELECT stock FROM film_inventory WHERE film_id = 1"
COUNT_ROWS = "SELECT COUNT(*) FROM film_inventory WHERE price > 3"


def yes_no(flag):
    return "YES" if flag else "NO"


# ---------------------------------------------------------------- the 3 anomaly cases
# Each case returns a list of result dicts (one per anomaly check).

def dirty_read(A, B):
    """A updates but does not commit; B reads; A rolls back."""
    def a_work():
        A.run("START TRANSACTION")
        A.run("UPDATE film_inventory SET stock = 0 WHERE film_id = 1")   # uncommitted!
        A.sleep(3)                      # keep the change uncommitted for a while
        A.run("ROLLBACK")

    t = start_thread(a_work)
    B.sleep(1)                          # make sure A's UPDATE has happened
    B.run("START TRANSACTION")
    read1 = first_value(B.run(READ_STOCK))   # may block (SERIALIZABLE) until A rolls back
    t.join()                            # A has rolled back now
    read2 = first_value(B.run(READ_STOCK))
    B.run("COMMIT")
    return [{"col": 0, "anomaly": "Dirty read",
             "saw": f"read1={read1}, read2={read2}",
             "occurred": read1 == 0}]    # B saw A's uncommitted 0


def non_repeatable_read(A, B):
    """B reads twice; A updates and commits in between."""
    def a_work():
        A.sleep(0.5)
        A.run("START TRANSACTION")
        A.run("UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1")  # may block
        A.run("COMMIT")

    B.run("START TRANSACTION")
    read1 = first_value(B.run(READ_STOCK))
    t = start_thread(a_work)
    B.sleep(3)                          # give A time to update (and commit, if not blocked)
    read2 = first_value(B.run(READ_STOCK))
    B.run("COMMIT")
    t.join()
    return [{"col": 1, "anomaly": "Non-repeatable read",
             "saw": f"read1={read1}, read2={read2}",
             "occurred": read1 != read2}]


def phantom_read(A, B):
    """B counts rows twice (and once after an UPDATE); A inserts a new row in between."""
    def a_work():
        A.sleep(0.5)
        A.run("START TRANSACTION")
        A.run("INSERT INTO film_inventory (film_id, title, stock, price) "
              "VALUES (11, 'PHANTOM FILM', 10, 4.99)")                   # may block
        A.run("COMMIT")

    B.run("START TRANSACTION")
    count1 = first_value(B.run(COUNT_ROWS))
    t = start_thread(a_work)
    B.sleep(3)
    count2 = first_value(B.run(COUNT_ROWS))                  # plain SELECT
    B.run("UPDATE film_inventory SET stock = stock + 1 WHERE price > 3")
    count3 = first_value(B.run(COUNT_ROWS))                  # after B's own UPDATE
    B.run("COMMIT")
    t.join()
    saw = f"count1={count1}, count2={count2}, count3={count3}"
    return [{"col": 2, "anomaly": "Phantom read (plain SELECT)", "saw": saw,
             "occurred": count2 != count1},
            {"col": 2, "anomaly": "Phantom read (after UPDATE)", "saw": saw,
             "occurred": count3 != count1}]


CASES = [("dirty", dirty_read), ("nonrepeatable", non_repeatable_read), ("phantom", phantom_read)]


# ---------------------------------------------------------------- main loop

def run_case(key, func, level):
    reset()                                             # fresh data before every case
    tl = Timeline(f"{key.upper()} @ {level}")
    A = Session("A", tl, level)                         # level is set on BOTH sessions
    B = Session("B", tl, level)                         # (before START TRANSACTION)
    try:
        rows = func(A, B)
    finally:
        A.close()
        B.close()
    blocked = round(A.blocked + B.blocked, 2)
    for r in rows:
        r.update(level=level, blocked=blocked)
    tl.save(f"baseline_{key}_{level.lower().replace(' ', '_')}.txt")
    return rows


def main():
    results = []
    for key, func in CASES:
        for level in LEVELS:
            results.extend(run_case(key, func, level))

    # ---- results table (one row per anomaly check per level)
    out = ["# Baseline results", "",
           "| Isolation level | Anomaly | What B saw | Anomaly occurred | Blocked (s) |",
           "|---|---|---|---|---|"]
    for r in results:
        out.append(f"| {r['level']} | {r['anomaly']} | {r['saw']} | "
                   f"{yes_no(r['occurred'])} | {r['blocked']} |")

    # ---- compare with the textbook table
    # Phantom counts as "occurred" if EITHER the plain or the after-UPDATE check showed it.
    actual = {}   # (level, column) -> bool
    for r in results:
        key = (r["level"], r["col"])
        actual[key] = actual.get(key, False) or r["occurred"]

    out += ["", "## Textbook comparison", "",
            "| Isolation level | Dirty | Non-repeatable | Phantom |", "|---|---|---|---|"]
    diffs = []
    for level in LEVELS[::-1]:
        cells = []
        for col in range(3):
            expected, got = TEXTBOOK[level][col], actual[(level, col)]
            cells.append(f"textbook {'V' if expected else 'X'}, got {'V' if got else 'X'}"
                         + ("" if expected == got else " **(DIFFERENT)**"))
            if expected != got:
                diffs.append(f"- {level} / {COLUMN_NAMES[col]}: textbook says "
                             f"{'can occur' if expected else 'cannot occur'}, "
                             f"but it {'occurred' if got else 'did NOT occur'}.")
        out.append(f"| {level} | " + " | ".join(cells) + " |")
    out += ["", "### Differences from the textbook"]
    out += diffs if diffs else ["- None."]

    text = "\n".join(out)
    print("\n" + text)
    with open(os.path.join(RESULTS_DIR, "baseline_results.md"), "w", encoding="utf-8") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
