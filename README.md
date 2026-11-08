# STADVDB H03: Isolation Levels Experiments

Hands-on tests of dirty reads, non-repeatable reads and phantom reads on MySQL 8.0 (InnoDB),
plus locking fixes. Two connections per test: Session A (writer) and Session B (reader).

## Requirements
- MySQL 8.0 on localhost, user `root`, with the `sakila` sample database installed
- Python 3 and `pip install mysql-connector-python`

## Setup
1. Provide the password (never commit it). Either:
   - PowerShell: `$env:DB_PASSWORD = "your_password"`, or
   - copy `.env.example` to `.env` and edit it (`.env` is git-ignored).
2. Create the database/table (needs the password for the mysql client):
   `mysql -u root -p -e "source schema.sql"`

## Run
```
python reset_data.py     # optional: restore the 10 base rows
python run_baseline.py   # 12 cases: 3 anomalies x 4 isolation levels (~1 minute)
python run_locks.py      # 4 locking experiments, each with and without the lock
```

## Output (in `results/`)
- `baseline_results.md` - results table + comparison with the textbook table
- `baseline_<anomaly>_<level>.txt` - timestamped timeline of each baseline case
- `locks_results.md` - lock wait times table
- `locks_exp<N>_with(out)_lock.txt` - timestamped timeline of each locking run

## Files
- `schema.sql` - creates `isolation_lab.film_inventory`
- `common.py` - shared helpers (connection, timestamped logging, Session class)
- `reset_data.py` - restores the base data
- `run_baseline.py`, `run_locks.py` - the experiments
- `AI_USAGE_LOG.md` - record of AI assistance
