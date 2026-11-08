"""
Locking experiments: one fix per isolation level, each run twice
(without the lock = baseline, then with the lock). We measure how many seconds
the "waiting session" was blocked.

Session A = writer, Session B = reader (same as run_baseline.py).
"""
import os

from common import RESULTS_DIR, Session, Timeline, first_value, start_thread
from reset_data import reset

READ_STOCK = "SELECT stock FROM film_inventory WHERE film_id = 1"


def setup(title, level):
    """Fresh data, a fresh timeline and two sessions at the given isolation level."""
    reset()
    tl = Timeline(title)
    return tl, Session("A", tl, level), Session("B", tl, level)


# ---- 1. READ UNCOMMITTED: dirty read fixed by SELECT ... FOR SHARE (waiting session = B)
def exp1(use_lock):
    level = "READ UNCOMMITTED"
    tl, A, B = setup(f"Exp1 {level} lock={use_lock}", level)

    def a_work():
        A.run("START TRANSACTION")
        A.run("UPDATE film_inventory SET stock = 0 WHERE film_id = 1")   # uncommitted
        A.sleep(3)
        A.run("ROLLBACK")

    t = start_thread(a_work)
    B.sleep(1)
    B.run("START TRANSACTION")
    # FOR SHARE needs a shared lock on the row, so B must wait until A's lock is gone.
    stock = first_value(B.run(READ_STOCK + (" FOR SHARE" if use_lock else "")))
    B.run("COMMIT")
    t.join()
    return tl, A, B, B, f"B read stock={stock} (committed value is 10)"


# ---- 2. READ COMMITTED: non-repeatable read fixed by FOR SHARE (waiting session = A)
def exp2(use_lock):
    level = "READ COMMITTED"
    tl, A, B = setup(f"Exp2 {level} lock={use_lock}", level)

    def a_work():
        A.sleep(0.5)
        A.run("START TRANSACTION")
        A.run("UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1")  # waits if locked
        A.run("COMMIT")

    B.run("START TRANSACTION")
    read1 = first_value(B.run(READ_STOCK + (" FOR SHARE" if use_lock else "")))
    t = start_thread(a_work)
    B.sleep(3)
    read2 = first_value(B.run(READ_STOCK))
    B.run("COMMIT")
    t.join()
    return tl, A, B, A, f"B read1={read1}, read2={read2}"


# ---- 3. REPEATABLE READ: phantom fixed by FOR UPDATE on the range (waiting session = A)
def exp3(use_lock):
    level = "REPEATABLE READ"
    tl, A, B = setup(f"Exp3 {level} lock={use_lock}", level)

    def a_work():
        A.sleep(0.5)
        A.run("START TRANSACTION")
        A.run("INSERT INTO film_inventory (film_id, title, stock, price) "
              "VALUES (11, 'PHANTOM FILM', 10, 4.99)")                    # waits if locked
        A.run("COMMIT")

    count = "SELECT COUNT(*) FROM film_inventory WHERE price > 3"
    B.run("START TRANSACTION")
    count1 = first_value(B.run(count + (" FOR UPDATE" if use_lock else "")))
    t = start_thread(a_work)
    B.sleep(3)
    # The 2nd read is always a "current read" (FOR UPDATE) so it shows the newest committed
    # data. (A plain SELECT in REPEATABLE READ would hide the phantom either way.)
    count2 = first_value(B.run(count + " FOR UPDATE"))
    B.run("COMMIT")
    t.join()
    return tl, A, B, A, f"B count1={count1}, count2={count2}"


# ---- 4. SERIALIZABLE: LOCK TABLES ... WRITE in B (waiting session = A)
def exp4(use_lock):
    level = "SERIALIZABLE"
    tl, A, B = setup(f"Exp4 {level} lock={use_lock}", level)

    def a_work():
        A.sleep(1)
        A.run("START TRANSACTION")
        # With B's table lock, this read has to wait until B runs UNLOCK TABLES.
        A.run(READ_STOCK)
        A.run("COMMIT")

    if use_lock:
        B.run("LOCK TABLES film_inventory WRITE")
    else:
        B.run("START TRANSACTION")      # no table lock: B just does a normal read
        B.run(READ_STOCK)
    t = start_thread(a_work)
    B.sleep(3)
    B.run("UNLOCK TABLES" if use_lock else "COMMIT")
    t.join()
    return tl, A, B, A, ("A's read had to wait for UNLOCK TABLES" if use_lock
                         else "A's read ran immediately")


# number, isolation level, problem, lock used, experiment function
EXPERIMENTS = [
    ("1", "READ UNCOMMITTED", "Dirty read", "SELECT ... FOR SHARE", exp1),
    ("2", "READ COMMITTED", "Non-repeatable read", "SELECT ... FOR SHARE", exp2),
    ("3", "REPEATABLE READ", "Phantom read", "SELECT ... WHERE price > 3 FOR UPDATE", exp3),
    ("4", "SERIALIZABLE", "Reader blocked by table lock", "LOCK TABLES film_inventory WRITE", exp4),
]


def main():
    out = ["# Locking experiment results", "",
           "| # | Isolation level | Problem | Lock used | Run | Waiting session | Wait time (s) | Observed |",
           "|---|---|---|---|---|---|---|---|"]
    for num, level, problem, lock, func in EXPERIMENTS:
        for use_lock in (False, True):
            tl, A, B, waiter, observed = func(use_lock)
            A.close()
            B.close()
            tl.save(f"locks_exp{num}_{'with' if use_lock else 'without'}_lock.txt")
            out.append(f"| {num} | {level} | {problem} | {lock} | "
                       f"{'with lock' if use_lock else 'baseline (no lock)'} | {waiter.name} | "
                       f"{waiter.blocked:.2f} | {observed} |")

    text = "\n".join(out)
    print("\n" + text)
    with open(os.path.join(RESULTS_DIR, "locks_results.md"), "w", encoding="utf-8") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
