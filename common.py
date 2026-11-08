"""
Shared helpers used by reset_data.py, run_baseline.py and run_locks.py.

Main ideas:
  * connect()  - open a MySQL connection (password comes from DB_PASSWORD).
  * Timeline   - collects timestamped log lines (seconds since start) and
                 prints them / saves them to a .txt file.
  * Session    - wraps one connection ("A" or "B"). Every SQL statement it runs
                 is logged with the time, the session name, the SQL and the
                 result. If a statement had to wait (blocked), the wait is logged.
"""
import os
import sys
import threading
import time

import mysql.connector

HOST = "localhost"
USER = "root"
DATABASE = "isolation_lab"

# A statement that takes longer than this many seconds counts as "blocked".
BLOCK_THRESHOLD = 0.5

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def load_env_file():
    """Tiny .env reader: puts KEY=VALUE lines into os.environ (if not already set)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def connect():
    """Open a new connection. Password is read from the environment, never hardcoded."""
    load_env_file()
    password = os.environ.get("DB_PASSWORD")
    if password is None:
        sys.exit("DB_PASSWORD is not set. Set the environment variable or create a .env file "
                 "(see .env.example).")
    # autocommit=True means we control transactions ourselves with START TRANSACTION / COMMIT,
    # so the SQL we log is exactly what MySQL receives.
    return mysql.connector.connect(host=HOST, user=USER, password=password,
                                   database=DATABASE, autocommit=True)


class Timeline:
    """Thread-safe, timestamped log. Time is seconds since the Timeline was created."""

    def __init__(self, title):
        self.start = time.time()
        self.lock = threading.Lock()   # A and B log from different threads
        self.lines = []
        self.add(f"=== {title} ===")

    def elapsed(self):
        return time.time() - self.start

    def add(self, text):
        with self.lock:
            print(text)
            self.lines.append(text)

    def log(self, session, text):
        self.add(f"[{self.elapsed():5.2f}s] {session} | {text}")

    def save(self, filename):
        os.makedirs(RESULTS_DIR, exist_ok=True)
        with open(os.path.join(RESULTS_DIR, filename), "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines) + "\n")


class Session:
    """One database connection with logging. name is 'A' (writer) or 'B' (reader)."""

    def __init__(self, name, timeline, level):
        self.name = name
        self.tl = timeline
        self.conn = connect()
        self.cur = self.conn.cursor()
        self.blocked = 0.0   # total seconds this session spent waiting on locks
        # Quiet setup: give up on a lock wait after 10 s instead of 50 s / forever.
        self.cur.execute("SET SESSION innodb_lock_wait_timeout = 10")
        self.cur.execute("SET SESSION lock_wait_timeout = 10")   # used by LOCK TABLES waits
        # Isolation level is set BEFORE START TRANSACTION (it applies to the next transaction).
        self.run(f"SET SESSION TRANSACTION ISOLATION LEVEL {level}")

    def run(self, sql):
        """Run one statement, log it, return the rows (list) for a SELECT, else None."""
        # If the statement is still running after the threshold, print a "waiting" line.
        waiting = threading.Timer(
            BLOCK_THRESHOLD, lambda: self.tl.log(self.name, f"   ... waiting (blocked) on: {sql}"))
        waiting.start()
        t0 = time.time()
        rows = None
        try:
            self.cur.execute(sql)
            if self.cur.with_rows:
                rows = self.cur.fetchall()
                result = str(rows)
            else:
                result = f"OK, {self.cur.rowcount} row(s) affected"
        except mysql.connector.Error as e:
            result = f"ERROR {e.errno}: {e.msg}"
        finally:
            waiting.cancel()
        took = time.time() - t0
        if took >= BLOCK_THRESHOLD:
            self.blocked += took
            result += f"  [BLOCKED {took:.2f}s]"
        self.tl.log(self.name, f"{sql}  ->  {result}")
        return rows

    def sleep(self, seconds):
        """Sleep to force the interleaving between the two sessions."""
        self.tl.log(self.name, f"-- sleep {seconds}s")
        time.sleep(seconds)

    def close(self):
        try:
            self.conn.close()
        except mysql.connector.Error:
            pass


def first_value(rows):
    """Return the first column of the first row (e.g. the stock or the COUNT), or None."""
    return rows[0][0] if rows else None


def start_thread(func):
    """Run func in its own thread, so a blocked session doesn't freeze the main script."""
    t = threading.Thread(target=func)
    t.start()
    return t
