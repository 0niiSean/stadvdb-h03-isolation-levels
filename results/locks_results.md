# Locking experiment results

| # | Isolation level | Problem | Lock used | Run | Waiting session | Wait time (s) | Observed |
|---|---|---|---|---|---|---|---|
| 1 | READ UNCOMMITTED | Dirty read | SELECT ... FOR SHARE | baseline (no lock) | B | 0.00 | B read stock=0 (committed value is 10) |
| 1 | READ UNCOMMITTED | Dirty read | SELECT ... FOR SHARE | with lock | B | 2.00 | B read stock=10 (committed value is 10) |
| 2 | READ COMMITTED | Non-repeatable read | SELECT ... FOR SHARE | baseline (no lock) | A | 0.00 | B read1=10, read2=15 |
| 2 | READ COMMITTED | Non-repeatable read | SELECT ... FOR SHARE | with lock | A | 2.50 | B read1=10, read2=10 |
| 3 | REPEATABLE READ | Phantom read | SELECT ... WHERE price > 3 FOR UPDATE | baseline (no lock) | A | 0.00 | B count1=4, count2=5 |
| 3 | REPEATABLE READ | Phantom read | SELECT ... WHERE price > 3 FOR UPDATE | with lock | A | 2.50 | B count1=4, count2=4 |
| 4 | SERIALIZABLE | Reader blocked by table lock | LOCK TABLES film_inventory WRITE | baseline (no lock) | A | 0.00 | A's read ran immediately |
| 4 | SERIALIZABLE | Reader blocked by table lock | LOCK TABLES film_inventory WRITE | with lock | A | 2.00 | A's read had to wait for UNLOCK TABLES |
