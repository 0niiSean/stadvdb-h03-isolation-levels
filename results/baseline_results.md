# Baseline results

| Isolation level | Anomaly | What B saw | Anomaly occurred | Blocked (s) |
|---|---|---|---|---|
| READ UNCOMMITTED | Dirty read | read1=0, read2=10 | YES | 0.0 |
| READ COMMITTED | Dirty read | read1=10, read2=10 | NO | 0.0 |
| REPEATABLE READ | Dirty read | read1=10, read2=10 | NO | 0.0 |
| SERIALIZABLE | Dirty read | read1=10, read2=10 | NO | 2.0 |
| READ UNCOMMITTED | Non-repeatable read | read1=10, read2=15 | YES | 0.0 |
| READ COMMITTED | Non-repeatable read | read1=10, read2=15 | YES | 0.0 |
| REPEATABLE READ | Non-repeatable read | read1=10, read2=10 | NO | 0.0 |
| SERIALIZABLE | Non-repeatable read | read1=10, read2=10 | NO | 2.5 |
| READ UNCOMMITTED | Phantom read (plain SELECT) | count1=4, count2=5, count3=5 | YES | 0.0 |
| READ UNCOMMITTED | Phantom read (after UPDATE) | count1=4, count2=5, count3=5 | YES | 0.0 |
| READ COMMITTED | Phantom read (plain SELECT) | count1=4, count2=5, count3=5 | YES | 0.0 |
| READ COMMITTED | Phantom read (after UPDATE) | count1=4, count2=5, count3=5 | YES | 0.0 |
| REPEATABLE READ | Phantom read (plain SELECT) | count1=4, count2=4, count3=5 | NO | 0.0 |
| REPEATABLE READ | Phantom read (after UPDATE) | count1=4, count2=4, count3=5 | YES | 0.0 |
| SERIALIZABLE | Phantom read (plain SELECT) | count1=4, count2=4, count3=4 | NO | 2.51 |
| SERIALIZABLE | Phantom read (after UPDATE) | count1=4, count2=4, count3=4 | NO | 2.51 |

## Textbook comparison

| Isolation level | Dirty | Non-repeatable | Phantom |
|---|---|---|---|
| SERIALIZABLE | textbook X, got X | textbook X, got X | textbook X, got X |
| REPEATABLE READ | textbook X, got X | textbook X, got X | textbook V, got V |
| READ COMMITTED | textbook X, got X | textbook V, got V | textbook V, got V |
| READ UNCOMMITTED | textbook V, got V | textbook V, got V | textbook V, got V |

### Differences from the textbook
- None.
