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
