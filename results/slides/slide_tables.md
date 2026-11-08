# Slide timelines

(SET SESSION and sleep rows removed. `→` shows the result; blocked statements are marked.)

## Dirty read @ READ UNCOMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 | BEGIN → OK |  |
| 0.07 | UPDATE stock=0 → 1 row |  |
| 1.07 |  | BEGIN → OK |
| 1.07 |  | SELECT stock → 0 |
| 3.07 | ROLLBACK → OK |  |
| 3.07 |  | SELECT stock → 10 |
| 3.07 |  | COMMIT → OK |

## Dirty read @ READ COMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 | BEGIN → OK |  |
| 0.07 | UPDATE stock=0 → 1 row |  |
| 1.07 |  | BEGIN → OK |
| 1.07 |  | SELECT stock → 10 |
| 3.07 | ROLLBACK → OK |  |
| 3.08 |  | SELECT stock → 10 |
| 3.08 |  | COMMIT → OK |

## Dirty read @ REPEATABLE READ

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 | BEGIN → OK |  |
| 0.07 | UPDATE stock=0 → 1 row |  |
| 1.07 |  | BEGIN → OK |
| 1.07 |  | SELECT stock → 10 |
| 3.08 | ROLLBACK → OK |  |
| 3.08 |  | SELECT stock → 10 |
| 3.08 |  | COMMIT → OK |

## Dirty read @ SERIALIZABLE

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 | BEGIN → OK |  |
| 0.07 | UPDATE stock=0 → 1 row |  |
| 1.07 |  | BEGIN → OK |
| 1.58 |  | *waiting: SELECT stock* |
| 3.07 |  | SELECT stock → 10 **(blocked 2.00s)** |
| 3.08 | ROLLBACK → OK |  |
| 3.08 |  | SELECT stock → 10 |
| 3.08 |  | COMMIT → OK |

## Non-repeatable read @ READ UNCOMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | SELECT stock → 10 |
| 0.57 | BEGIN → OK |  |
| 0.57 | UPDATE stock+5 → 1 row |  |
| 0.58 | COMMIT → OK |  |
| 3.07 |  | SELECT stock → 15 |
| 3.07 |  | COMMIT → OK |

## Non-repeatable read @ READ COMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | SELECT stock → 10 |
| 0.57 | BEGIN → OK |  |
| 0.57 | UPDATE stock+5 → 1 row |  |
| 0.58 | COMMIT → OK |  |
| 3.07 |  | SELECT stock → 15 |
| 3.07 |  | COMMIT → OK |

## Non-repeatable read @ REPEATABLE READ

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | SELECT stock → 10 |
| 0.57 | BEGIN → OK |  |
| 0.57 | UPDATE stock+5 → 1 row |  |
| 0.58 | COMMIT → OK |  |
| 3.07 |  | SELECT stock → 10 |
| 3.07 |  | COMMIT → OK |

## Non-repeatable read @ SERIALIZABLE

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | SELECT stock → 10 |
| 0.57 | BEGIN → OK |  |
| 1.08 | *waiting: UPDATE stock+5* |  |
| 3.07 |  | SELECT stock → 10 |
| 3.07 |  | COMMIT → OK |
| 3.07 | UPDATE stock+5 → 1 row **(blocked 2.50s)** |  |
| 3.08 | COMMIT → OK |  |

## Phantom read @ READ UNCOMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | COUNT price>3 → 4 |
| 0.57 | BEGIN → OK |  |
| 0.57 | INSERT film 11 → 1 row |  |
| 0.58 | COMMIT → OK |  |
| 3.07 |  | COUNT price>3 → 5 |
| 3.07 |  | UPDATE stock+1 (price>3) → 5 rows |
| 3.07 |  | COUNT price>3 → 5 |
| 3.08 |  | COMMIT → OK |

## Phantom read @ READ COMMITTED

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | COUNT price>3 → 4 |
| 0.57 | BEGIN → OK |  |
| 0.57 | INSERT film 11 → 1 row |  |
| 0.59 | COMMIT → OK |  |
| 3.07 |  | COUNT price>3 → 5 |
| 3.07 |  | UPDATE stock+1 (price>3) → 5 rows |
| 3.07 |  | COUNT price>3 → 5 |
| 3.08 |  | COMMIT → OK |

## Phantom read @ REPEATABLE READ

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | COUNT price>3 → 4 |
| 0.57 | BEGIN → OK |  |
| 0.57 | INSERT film 11 → 1 row |  |
| 0.58 | COMMIT → OK |  |
| 3.07 |  | COUNT price>3 → 4 |
| 3.07 |  | UPDATE stock+1 (price>3) → 5 rows |
| 3.07 |  | COUNT price>3 → 5 |
| 3.08 |  | COMMIT → OK |

## Phantom read @ SERIALIZABLE

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | COUNT price>3 → 4 |
| 0.57 | BEGIN → OK |  |
| 1.08 | *waiting: INSERT film 11* |  |
| 3.07 |  | COUNT price>3 → 4 |
| 3.07 |  | UPDATE stock+1 (price>3) → 4 rows |
| 3.07 |  | COUNT price>3 → 4 |
| 3.08 |  | COMMIT → OK |
| 3.08 | INSERT film 11 → 1 row **(blocked 2.51s)** |  |
| 3.09 | COMMIT → OK |  |

## Lock experiment 1 @ READ UNCOMMITTED (without lock)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 | BEGIN → OK |  |
| 0.07 | UPDATE stock=0 → 1 row |  |
| 1.07 |  | BEGIN → OK |
| 1.07 |  | SELECT stock → 0 |
| 1.07 |  | COMMIT → OK |
| 3.08 | ROLLBACK → OK |  |

## Lock experiment 1 @ READ UNCOMMITTED (with lock)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 | BEGIN → OK |  |
| 0.08 | UPDATE stock=0 → 1 row |  |
| 1.08 |  | BEGIN → OK |
| 1.58 |  | *waiting: SELECT stock FOR SHARE* |
| 3.08 |  | SELECT stock FOR SHARE → 10 **(blocked 2.00s)** |
| 3.08 |  | COMMIT → OK |
| 3.08 | ROLLBACK → OK |  |

## Lock experiment 2 @ READ COMMITTED (without lock)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | SELECT stock → 10 |
| 0.57 | BEGIN → OK |  |
| 0.57 | UPDATE stock+5 → 1 row |  |
| 0.58 | COMMIT → OK |  |
| 3.07 |  | SELECT stock → 15 |
| 3.07 |  | COMMIT → OK |

## Lock experiment 2 @ READ COMMITTED (with lock)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | SELECT stock FOR SHARE → 10 |
| 0.57 | BEGIN → OK |  |
| 1.09 | *waiting: UPDATE stock+5* |  |
| 3.07 |  | SELECT stock → 10 |
| 3.08 |  | COMMIT → OK |
| 3.08 | UPDATE stock+5 → 1 row **(blocked 2.50s)** |  |
| 3.08 | COMMIT → OK |  |

## Lock experiment 3 @ REPEATABLE READ (without lock)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | COUNT price>3 → 4 |
| 0.58 | BEGIN → OK |  |
| 0.58 | INSERT film 11 → 1 row |  |
| 0.58 | COMMIT → OK |  |
| 3.08 |  | COUNT price>3 FOR UPDATE → 5 |
| 3.08 |  | COMMIT → OK |

## Lock experiment 3 @ REPEATABLE READ (with lock)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | COUNT price>3 FOR UPDATE → 4 |
| 0.57 | BEGIN → OK |  |
| 1.08 | *waiting: INSERT film 11* |  |
| 3.07 |  | COUNT price>3 FOR UPDATE → 4 |
| 3.07 |  | COMMIT → OK |
| 3.07 | INSERT film 11 → 1 row **(blocked 2.50s)** |  |
| 3.08 | COMMIT → OK |  |

## Lock experiment 4 @ SERIALIZABLE (without lock)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | SELECT stock → 10 |
| 1.07 | BEGIN → OK |  |
| 1.07 | SELECT stock → 10 |  |
| 1.07 | COMMIT → OK |  |
| 3.07 |  | COMMIT → OK |

## Lock experiment 4 @ SERIALIZABLE (with lock)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.08 |  | LOCK TABLES WRITE → OK |
| 1.08 | BEGIN → OK |  |
| 1.58 | *waiting: SELECT stock* |  |
| 3.08 |  | UNLOCK TABLES → OK |
| 3.08 | SELECT stock → 10 **(blocked 2.00s)** |  |
| 3.08 | COMMIT → OK |  |

## Case: exp3_with_lock  (isolation level REPEATABLE READ)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | COUNT price>3 FOR UPDATE → 4 |
| 0.57 | BEGIN → OK |  |
| 1.07 | *waiting: INSERT film 11* |  |
| 3.15 |  | COMMIT → OK |
| 3.15 | INSERT film 11 → 1 row **(blocked 2.58s)** |  |
| 3.16 | COMMIT → OK |  |

## Case: phantom_serializable  (isolation level SERIALIZABLE)

| Time (s) | Session A | Session B |
|---|---|---|
| 0.07 |  | BEGIN → OK |
| 0.07 |  | COUNT price>3 → 4 |
| 0.57 | BEGIN → OK |  |
| 1.07 | *waiting: INSERT film 11* |  |
| 3.11 |  | COMMIT → OK |
| 3.11 | INSERT film 11 → 1 row **(blocked 2.54s)** |  |
| 3.12 | COMMIT → OK |  |
