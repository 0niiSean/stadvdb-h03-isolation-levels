# Manual Runbook (two PowerShell windows)

Use this to repeat three cases by hand and take screenshots.

## Setup

Open **two** PowerShell windows. In each one run (it asks for the password):

```
mysql -u root -p isolation_lab
```

- **Window A** = Session A (writer)
- **Window B** = Session B (reader)

Wait for the `mysql>` prompt. **All SQL in this file goes at the `mysql>` prompt, not at the plain `PS C:\...>` prompt.** Pasting SQL into plain PowerShell gives a parser error such as "Missing argument in parameter list". If you see `PS C:\...>`, you are not inside mysql yet; run the command above first. (Type `exit` to leave mysql.)

Rules for every case:
- Do the steps **in the numbered order**, switching windows as labelled.
- Run the **reset** first. Before resetting, make sure no transaction is still open in either window (run `ROLLBACK;` in both if unsure).
- Set the isolation level **before** `START TRANSACTION`, and check it with the `SELECT @@transaction_isolation;` line (good for a screenshot).

## Reset (before EVERY case)

**Easiest option:** from a plain PowerShell prompt (`PS C:\...>`, not inside mysql), in the project folder:

```
python reset_data.py
```

It prints `film_inventory reset: 10 rows`. Make sure no transaction is open in either mysql window first.

**Or inside mysql:** paste this at the `mysql>` prompt in Window A:

```sql
DELETE FROM film_inventory;
INSERT INTO film_inventory (film_id, title, stock, price)
SELECT film_id, title, 10, rental_rate FROM sakila.film WHERE film_id BETWEEN 1 AND 10;
SELECT film_id, stock, price FROM film_inventory;
```

Expect: 10 rows, all with stock 10. Films 2, 7, 8, 10 have price 4.99 (so `price > 3` matches 4 rows).

---

## Case 1: Dirty read at READ UNCOMMITTED

| Step | Window | SQL |
|---|---|---|
| 1 | A | `SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;` |
| 2 | B | `SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;` |
| 3 | A | `SELECT @@transaction_isolation;` |
| 4 | B | `SELECT @@transaction_isolation;` |
| 5 | A | `START TRANSACTION;` |
| 6 | A | `UPDATE film_inventory SET stock = 0 WHERE film_id = 1;` |
| 7 | B | `START TRANSACTION;` |
| 8 | B | `SELECT stock FROM film_inventory WHERE film_id = 1;` |
| 9 | A | `ROLLBACK;` |
| 10 | B | `SELECT stock FROM film_inventory WHERE film_id = 1;` |
| 11 | B | `COMMIT;` |

Copy-paste blocks:

Window A, steps 1, 3, 5, 6:
```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SELECT @@transaction_isolation;
START TRANSACTION;
UPDATE film_inventory SET stock = 0 WHERE film_id = 1;
```
Window B, steps 2, 4, 7, 8:
```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SELECT @@transaction_isolation;
START TRANSACTION;
SELECT stock FROM film_inventory WHERE film_id = 1;
```
Window A, step 9:
```sql
ROLLBACK;
```
Window B, steps 10, 11:
```sql
SELECT stock FROM film_inventory WHERE film_id = 1;
COMMIT;
```

Expect: step 8 returns **0** (A's uncommitted value, a dirty read). Step 10 returns **10**.

---

## Case 2: Non-repeatable read at READ COMMITTED

| Step | Window | SQL |
|---|---|---|
| 1 | A | `SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;` |
| 2 | B | `SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;` |
| 3 | A | `SELECT @@transaction_isolation;` |
| 4 | B | `SELECT @@transaction_isolation;` |
| 5 | B | `START TRANSACTION;` |
| 6 | B | `SELECT stock FROM film_inventory WHERE film_id = 1;` |
| 7 | A | `START TRANSACTION;` |
| 8 | A | `UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1;` |
| 9 | A | `COMMIT;` |
| 10 | B | `SELECT stock FROM film_inventory WHERE film_id = 1;` |
| 11 | B | `COMMIT;` |

Copy-paste blocks:

Window A, steps 1, 3:
```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT @@transaction_isolation;
```
Window B, steps 2, 4, 5, 6:
```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT @@transaction_isolation;
START TRANSACTION;
SELECT stock FROM film_inventory WHERE film_id = 1;
```
Window A, steps 7 to 9:
```sql
START TRANSACTION;
UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1;
COMMIT;
```
Window B, steps 10, 11:
```sql
SELECT stock FROM film_inventory WHERE film_id = 1;
COMMIT;
```

Expect: step 6 returns **10**, step 10 returns **15** (same transaction, two different answers).

---

## Case 3: Phantom read at REPEATABLE READ (plain count, then count after UPDATE)

| Step | Window | SQL |
|---|---|---|
| 1 | A | `SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;` |
| 2 | B | `SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;` |
| 3 | A | `SELECT @@transaction_isolation;` |
| 4 | B | `SELECT @@transaction_isolation;` |
| 5 | B | `START TRANSACTION;` |
| 6 | B | `SELECT COUNT(*) FROM film_inventory WHERE price > 3;` (count1) |
| 7 | A | `START TRANSACTION;` |
| 8 | A | `INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99);` |
| 9 | A | `COMMIT;` |
| 10 | B | `SELECT COUNT(*) FROM film_inventory WHERE price > 3;` (count2, plain SELECT) |
| 11 | B | `UPDATE film_inventory SET stock = stock + 1 WHERE price > 3;` |
| 12 | B | `SELECT COUNT(*) FROM film_inventory WHERE price > 3;` (count3) |
| 13 | B | `COMMIT;` |

Copy-paste blocks:

Window A, steps 1, 3:
```sql
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT @@transaction_isolation;
```
Window B, steps 2, 4, 5, 6:
```sql
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT @@transaction_isolation;
START TRANSACTION;
SELECT COUNT(*) FROM film_inventory WHERE price > 3;
```
Window A, steps 7 to 9:
```sql
START TRANSACTION;
INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99);
COMMIT;
```
Window B, steps 10 to 13:
```sql
SELECT COUNT(*) FROM film_inventory WHERE price > 3;
UPDATE film_inventory SET stock = stock + 1 WHERE price > 3;
SELECT COUNT(*) FROM film_inventory WHERE price > 3;
COMMIT;
```

Expect: count1 = **4**, count2 = **4** (the plain SELECT does not show the new row), the UPDATE reports **5 rows matched/changed** (it touches the new row), and count3 = **5** (the phantom appears after the UPDATE).
