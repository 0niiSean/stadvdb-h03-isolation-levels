"""
Lock evidence: while Session A is blocked, a THIRD connection reads
performance_schema.data_locks and performance_schema.data_lock_waits.

Two cases (same interleaving as run_locks.py exp3 / run_baseline.py phantom):
  exp3_with_lock        REPEATABLE READ, B: SELECT COUNT(*) ... WHERE price > 3 FOR UPDATE; A: INSERT blocks
  phantom_serializable  SERIALIZABLE,    B: plain SELECT COUNT(*) ... WHERE price > 3;       A: INSERT blocks

Writes (in results/):
  lock_evidence_<case>.txt   raw output of both queries
  lock_evidence_<case>.md    small table: lock_type, lock_mode, index_name, lock_data
"""
import os
import time

from common import RESULTS_DIR, Session, Timeline, connect, first_value, start_thread
from reset_data import reset

COUNT = "SELECT COUNT(*) FROM film_inventory WHERE price > 3"

# data_locks joined with threads so we can say which session (A or B) owns each lock.
LOCKS_SQL = """
SELECT t.PROCESSLIST_ID AS connection_id, dl.ENGINE_TRANSACTION_ID, dl.OBJECT_NAME, dl.INDEX_NAME,
       dl.LOCK_TYPE, dl.LOCK_MODE, dl.LOCK_STATUS, dl.LOCK_DATA
FROM performance_schema.data_locks dl
LEFT JOIN performance_schema.threads t ON t.THREAD_ID = dl.THREAD_ID
WHERE dl.OBJECT_SCHEMA = 'isolation_lab'
ORDER BY dl.ENGINE_TRANSACTION_ID, dl.LOCK_TYPE, dl.INDEX_NAME, dl.LOCK_DATA
"""
WAITS_SQL = """
SELECT REQUESTING_ENGINE_TRANSACTION_ID, BLOCKING_ENGINE_TRANSACTION_ID,
       REQUESTING_ENGINE_LOCK_ID, BLOCKING_ENGINE_LOCK_ID
FROM performance_schema.data_lock_waits
"""


def raw_text(title, cols, rows):
    """Plain tab-separated dump of a query result."""
    out = [title, "\t".join(cols)]
    out += ["\t".join(str(v) for v in r) for r in rows] or ["(no rows)"]
    return "\n".join(out)


def run_case(case, level, b_lock_sql):
    reset()
    tl = Timeline(f"Lock evidence: {case}")
    A = Session("A", tl, level)
    B = Session("B", tl, level)
    owner = {A.conn.connection_id: "A", B.conn.connection_id: "B"}

    def a_work():
        A.sleep(0.5)
        A.run("START TRANSACTION")
        A.run("INSERT INTO film_inventory (film_id, title, stock, price) "
              "VALUES (11, 'PHANTOM FILM', 10, 4.99)")          # blocks until B commits
        A.run("COMMIT")

    B.run("START TRANSACTION")
    B.run(b_lock_sql)
    t = start_thread(a_work)
    B.sleep(2)                                                  # A is blocked by now

    # ---- third connection: look at the locks while A is blocked
    spy = connect()
    cur = spy.cursor()
    snapshot_time = tl.elapsed()
    cur.execute(LOCKS_SQL)
    lock_cols = [d[0] for d in cur.description]
    lock_rows = cur.fetchall()
    cur.execute(WAITS_SQL)
    wait_cols = [d[0] for d in cur.description]
    wait_rows = cur.fetchall()
    spy.close()
    tl.add(f"[{snapshot_time:5.2f}s] spy | queried performance_schema while A is blocked "
           f"({len(lock_rows)} lock rows, {len(wait_rows)} wait rows)")

    B.sleep(1)
    B.run("COMMIT")
    t.join()
    A.close()
    B.close()

    # ---- raw file
    raw = [f"Case: {case}  (isolation level {level})",
           f"Snapshot taken at {snapshot_time:.2f}s, while Session A's INSERT was blocked.",
           f"connection ids: {owner}", "",
           raw_text("performance_schema.data_locks (joined with threads)", lock_cols, lock_rows), "",
           raw_text("performance_schema.data_lock_waits", wait_cols, wait_rows), "",
           "---- session timeline ----"] + tl.lines
    with open(os.path.join(RESULTS_DIR, f"lock_evidence_{case}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(raw) + "\n")

    # ---- small table
    i = {c: n for n, c in enumerate(lock_cols)}
    md = [f"# Lock evidence: {case}", "", f"Isolation level: {level}. Snapshot while Session A was blocked.", "",
          "| Session | lock_type | lock_mode | index_name | lock_data | lock_status |", "|---|---|---|---|---|---|"]
    for r in lock_rows:
        md.append(f"| {owner.get(r[i['connection_id']], '?')} | {r[i['LOCK_TYPE']]} | {r[i['LOCK_MODE']]} | "
                  f"{r[i['INDEX_NAME']] or ''} | {r[i['LOCK_DATA']] or ''} | {r[i['LOCK_STATUS']]} |")
    with open(os.path.join(RESULTS_DIR, f"lock_evidence_{case}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


def main():
    run_case("exp3_with_lock", "REPEATABLE READ", COUNT + " FOR UPDATE")
    run_case("phantom_serializable", "SERIALIZABLE", COUNT)


if __name__ == "__main__":
    main()
