# Timelines

## DIRTY @ READ UNCOMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.04 | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | -- sleep 1s |
| 0.07 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.08 | UPDATE film_inventory SET stock = 0 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.08 | -- sleep 3s |  |
| 1.08 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 1.08 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(0,)] |
| 3.08 | ROLLBACK  ->  OK, 0 row(s) affected |  |
| 3.08 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |

## DIRTY @ READ COMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.04 | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | -- sleep 1s |
| 0.07 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.07 | UPDATE film_inventory SET stock = 0 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.07 | -- sleep 3s |  |
| 1.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 1.08 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 3.08 | ROLLBACK  ->  OK, 0 row(s) affected |  |
| 3.08 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |

## DIRTY @ REPEATABLE READ

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |
| 0.07 |  | -- sleep 1s |
| 0.07 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.07 | UPDATE film_inventory SET stock = 0 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.07 | -- sleep 3s |  |
| 1.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 1.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 3.08 | ROLLBACK  ->  OK, 0 row(s) affected |  |
| 3.08 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |

## DIRTY @ SERIALIZABLE

| Time (s) | Session A | Session B |
|---|---|---|
| 0.04 | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |
| 0.07 |  | -- sleep 1s |
| 0.07 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.07 | UPDATE film_inventory SET stock = 0 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.07 | -- sleep 3s |  |
| 1.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 1.58 |  |    ... waiting (blocked) on: SELECT stock FROM film_inventory WHERE film_id = 1 |
| 3.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)]  [BLOCKED 2.00s] |
| 3.08 | ROLLBACK  ->  OK, 0 row(s) affected |  |
| 3.08 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |

## NONREPEATABLE @ READ UNCOMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.57 | UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.58 | COMMIT  ->  OK, 0 row(s) affected |  |
| 3.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(15,)] |
| 3.07 |  | COMMIT  ->  OK, 0 row(s) affected |

## NONREPEATABLE @ READ COMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.57 | UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.58 | COMMIT  ->  OK, 0 row(s) affected |  |
| 3.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(15,)] |
| 3.07 |  | COMMIT  ->  OK, 0 row(s) affected |

## NONREPEATABLE @ REPEATABLE READ

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.57 | UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.58 | COMMIT  ->  OK, 0 row(s) affected |  |
| 3.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 3.07 |  | COMMIT  ->  OK, 0 row(s) affected |

## NONREPEATABLE @ SERIALIZABLE

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 1.07 |    ... waiting (blocked) on: UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1 |  |
| 3.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 3.07 |  | COMMIT  ->  OK, 0 row(s) affected |
| 3.07 | UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1  ->  OK, 1 row(s) affected  [BLOCKED 2.50s] |  |
| 3.08 | COMMIT  ->  OK, 0 row(s) affected |  |

## PHANTOM @ READ UNCOMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(4,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.57 | INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99)  ->  OK, 1 row(s) affected |  |
| 0.58 | COMMIT  ->  OK, 0 row(s) affected |  |
| 3.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(5,)] |
| 3.07 |  | UPDATE film_inventory SET stock = stock + 1 WHERE price > 3  ->  OK, 5 row(s) affected |
| 3.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(5,)] |
| 3.09 |  | COMMIT  ->  OK, 0 row(s) affected |

## PHANTOM @ READ COMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(4,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.57 | INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99)  ->  OK, 1 row(s) affected |  |
| 0.58 | COMMIT  ->  OK, 0 row(s) affected |  |
| 3.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(5,)] |
| 3.07 |  | UPDATE film_inventory SET stock = stock + 1 WHERE price > 3  ->  OK, 5 row(s) affected |
| 3.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(5,)] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |

## PHANTOM @ REPEATABLE READ

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(4,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.57 | INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99)  ->  OK, 1 row(s) affected |  |
| 0.58 | COMMIT  ->  OK, 0 row(s) affected |  |
| 3.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(4,)] |
| 3.07 |  | UPDATE film_inventory SET stock = stock + 1 WHERE price > 3  ->  OK, 5 row(s) affected |
| 3.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(5,)] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |

## PHANTOM @ SERIALIZABLE

| Time (s) | Session A | Session B |
|---|---|---|
| 0.04 | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(4,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 1.08 |    ... waiting (blocked) on: INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99) |  |
| 3.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(4,)] |
| 3.07 |  | UPDATE film_inventory SET stock = stock + 1 WHERE price > 3  ->  OK, 4 row(s) affected |
| 3.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(4,)] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |
| 3.08 | INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99)  ->  OK, 1 row(s) affected  [BLOCKED 2.51s] |  |
| 3.09 | COMMIT  ->  OK, 0 row(s) affected |  |

## Exp1 READ UNCOMMITTED lock=False

| Time (s) | Session A | Session B |
|---|---|---|
| 0.04 | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | -- sleep 1s |
| 0.07 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.07 | UPDATE film_inventory SET stock = 0 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.07 | -- sleep 3s |  |
| 1.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 1.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(0,)] |
| 1.07 |  | COMMIT  ->  OK, 0 row(s) affected |
| 3.08 | ROLLBACK  ->  OK, 0 row(s) affected |  |

## Exp1 READ UNCOMMITTED lock=True

| Time (s) | Session A | Session B |
|---|---|---|
| 0.04 | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | -- sleep 1s |
| 0.07 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.08 | UPDATE film_inventory SET stock = 0 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.08 | -- sleep 3s |  |
| 1.08 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 1.58 |  |    ... waiting (blocked) on: SELECT stock FROM film_inventory WHERE film_id = 1 FOR SHARE |
| 3.08 |  | SELECT stock FROM film_inventory WHERE film_id = 1 FOR SHARE  ->  [(10,)]  [BLOCKED 2.00s] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |
| 3.08 | ROLLBACK  ->  OK, 0 row(s) affected |  |

## Exp2 READ COMMITTED lock=False

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.57 | UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1  ->  OK, 1 row(s) affected |  |
| 0.58 | COMMIT  ->  OK, 0 row(s) affected |  |
| 3.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(15,)] |
| 3.07 |  | COMMIT  ->  OK, 0 row(s) affected |

## Exp2 READ COMMITTED lock=True

| Time (s) | Session A | Session B |
|---|---|---|
| 0.04 | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1 FOR SHARE  ->  [(10,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 1.09 |    ... waiting (blocked) on: UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1 |  |
| 3.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |
| 3.08 | UPDATE film_inventory SET stock = stock + 5 WHERE film_id = 1  ->  OK, 1 row(s) affected  [BLOCKED 2.50s] |  |
| 3.08 | COMMIT  ->  OK, 0 row(s) affected |  |

## Exp3 REPEATABLE READ lock=False

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3  ->  [(4,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.58 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 0.58 | INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99)  ->  OK, 1 row(s) affected |  |
| 0.58 | COMMIT  ->  OK, 0 row(s) affected |  |
| 3.08 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3 FOR UPDATE  ->  [(5,)] |
| 3.08 |  | COMMIT  ->  OK, 0 row(s) affected |

## Exp3 REPEATABLE READ lock=True

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3 FOR UPDATE  ->  [(4,)] |
| 0.07 | -- sleep 0.5s |  |
| 0.07 |  | -- sleep 3s |
| 0.57 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 1.08 |    ... waiting (blocked) on: INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99) |  |
| 3.07 |  | SELECT COUNT(*) FROM film_inventory WHERE price > 3 FOR UPDATE  ->  [(4,)] |
| 3.07 |  | COMMIT  ->  OK, 0 row(s) affected |
| 3.07 | INSERT INTO film_inventory (film_id, title, stock, price) VALUES (11, 'PHANTOM FILM', 10, 4.99)  ->  OK, 1 row(s) affected  [BLOCKED 2.50s] |  |
| 3.08 | COMMIT  ->  OK, 0 row(s) affected |  |

## Exp4 SERIALIZABLE lock=False

| Time (s) | Session A | Session B |
|---|---|---|
| 0.03 | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |
| 0.07 |  | START TRANSACTION  ->  OK, 0 row(s) affected |
| 0.07 |  | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |
| 0.07 | -- sleep 1s |  |
| 0.07 |  | -- sleep 3s |
| 1.07 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 1.07 | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)] |  |
| 1.07 | COMMIT  ->  OK, 0 row(s) affected |  |
| 3.07 |  | COMMIT  ->  OK, 0 row(s) affected |

## Exp4 SERIALIZABLE lock=True

| Time (s) | Session A | Session B |
|---|---|---|
| 0.04 | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |  |
| 0.07 |  | SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE  ->  OK, 0 row(s) affected |
| 0.08 |  | LOCK TABLES film_inventory WRITE  ->  OK, 0 row(s) affected |
| 0.08 | -- sleep 1s |  |
| 0.08 |  | -- sleep 3s |
| 1.08 | START TRANSACTION  ->  OK, 0 row(s) affected |  |
| 1.58 |    ... waiting (blocked) on: SELECT stock FROM film_inventory WHERE film_id = 1 |  |
| 3.08 |  | UNLOCK TABLES  ->  OK, 0 row(s) affected |
| 3.08 | SELECT stock FROM film_inventory WHERE film_id = 1  ->  [(10,)]  [BLOCKED 2.00s] |  |
| 3.08 | COMMIT  ->  OK, 0 row(s) affected |  |
