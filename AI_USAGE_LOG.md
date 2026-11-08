# AI Usage Log

Tool: Claude Code (Claude Sonnet 5.5), used on 2026-11-08.
The student gave the specification (setup, test scenarios, expected outputs); the AI wrote the code.
No report text was written by the AI. The student should read and be able to explain every file.

| # | What was built | What the AI did | Student's check |
|---|---|---|---|
| 1 | `schema.sql` | Wrote the CREATE DATABASE/TABLE and the INSERT ... SELECT from `sakila.film` (film_id 1-10, stock 10, price = rental_rate). | Verify the table and 10 rows in MySQL. |
| 2 | `common.py` | Wrote shared helpers: connection from `DB_PASSWORD`, timestamped `Timeline` log, `Session` class that logs SQL/result and measures blocked time, thread helper. | Understand how blocked time is measured (statement took >= 0.5 s). |
| 3 | `reset_data.py` | Wrote the reset (delete all rows, re-insert the 10 base rows from sakila). | Run it and check the row count. |
| 4 | `run_baseline.py` | Wrote the 12 test cases (dirty / non-repeatable / phantom x 4 isolation levels), results table and textbook comparison. | Follow the sleeps/threads and confirm the interleavings match the assignment. |
| 5 | `run_locks.py` | Wrote the 4 locking experiments (FOR SHARE, FOR SHARE, FOR UPDATE, LOCK TABLES), each with/without the lock, and the wait-time table. | Understand why each lock makes the other session wait. |
| 6 | `.gitignore`, `.env.example`, `README.md` | Wrote the ignore rules, password template and run instructions. | Confirm `.env` is never committed. |
| 7 | `AI_USAGE_LOG.md` | Wrote this log. | Add anything else you used AI for. |
| 8 | `timeline_tables.py` | Wrote a script that reads each `.txt` log in `results/` and writes `results/timelines.md` (one Time / Session A / Session B table per run). Ran it to generate the file. | Check a few tables against the original `.txt` logs. |
| 9 | `MANUAL_RUNBOOK.md` | Wrote copy-paste SQL, window labels, step order, expected results and a reset command for the dirty read, non-repeatable read and phantom (REPEATABLE READ) cases. | Run it by hand in two mysql windows and confirm the expected values (esp. the UPDATE row count in case 3). |
| 10 | `make_slides.py` -> `results/slides/matrix.png` | Wrote code that builds the Occurred/Prevented grid from `results/baseline_results.md` (not hardcoded); REPEATABLE READ phantom shows "plain SELECT no / after UPDATE yes". Used matplotlib. | Check each cell against the baseline table. |
| 11 | `make_slides.py` -> `results/slides/swimlane_*.png` | Wrote code that draws a two-lane swimlane (A top, B bottom, red bar = blocked) for the 12 baseline logs and the 4 "with lock" logs; generated 16 PNGs. | Check a few against the `.txt` logs. |
| 12 | `make_slides.py` -> `results/slides/lock_waits.png` | Wrote the with vs without lock bar chart, read from `results/locks_results.md`. | Compare the values with the table. |
| 13 | `make_slides.py` -> `results/slides/slide_tables.md` | Wrote the short-label timelines (SET SESSION and sleep rows removed, blocked rows kept). | Spot-check labels against the logs. |
| 14 | `lock_evidence.py` -> `results/lock_evidence_*.txt/.md` | Wrote a script that opens a third connection while Session A is blocked and queries `performance_schema.data_locks` and `data_lock_waits` for lock exp 3 (with lock) and the SERIALIZABLE phantom case. Ran it. | Understand what each lock row means (S / X / INSERT_INTENTION, supremum). |
| 15 | Stability check (`results/stability/`) | Ran `run_baseline.py` three times, saved each results table, and compared the outcomes with a shell/awk diff. | Re-run if you want to see it yourself. |
| 16 | `make_slides.py` -> `results/slides/facts_for_script.md` | Wrote the one-line-per-run raw facts (12 baseline + 4 lock runs), generated from the results files. | Check numbers against the tables. |
