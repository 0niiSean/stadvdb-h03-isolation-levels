# Facts for script

- Dirty read | READ UNCOMMITTED | read1=0, read2=10 | occurred=YES | blocked=0.0s
- Dirty read | READ COMMITTED | read1=10, read2=10 | occurred=NO | blocked=0.0s
- Dirty read | REPEATABLE READ | read1=10, read2=10 | occurred=NO | blocked=0.0s
- Dirty read | SERIALIZABLE | read1=10, read2=10 | occurred=NO | blocked=2.0s
- Non-repeatable read | READ UNCOMMITTED | read1=10, read2=15 | occurred=YES | blocked=0.0s
- Non-repeatable read | READ COMMITTED | read1=10, read2=15 | occurred=YES | blocked=0.0s
- Non-repeatable read | REPEATABLE READ | read1=10, read2=10 | occurred=NO | blocked=0.0s
- Non-repeatable read | SERIALIZABLE | read1=10, read2=10 | occurred=NO | blocked=2.5s
- Phantom read | READ UNCOMMITTED | count1=4, count2=5, count3=5 | plain SELECT=YES, after UPDATE=YES | blocked=0.0s
- Phantom read | READ COMMITTED | count1=4, count2=5, count3=5 | plain SELECT=YES, after UPDATE=YES | blocked=0.0s
- Phantom read | REPEATABLE READ | count1=4, count2=4, count3=5 | plain SELECT=NO, after UPDATE=YES | blocked=0.0s
- Phantom read | SERIALIZABLE | count1=4, count2=4, count3=4 | plain SELECT=NO, after UPDATE=NO | blocked=2.51s
- Lock exp 1 | READ UNCOMMITTED | SELECT ... FOR SHARE | B read 10 | B blocked=2.00s (without lock: 0.00s)
- Lock exp 2 | READ COMMITTED | SELECT ... FOR SHARE | B read 10, B read 10 | A blocked=2.50s (without lock: 0.00s)
- Lock exp 3 | REPEATABLE READ | SELECT ... WHERE price > 3 FOR UPDATE | B read 4, B read 4 | A blocked=2.50s (without lock: 0.00s)
- Lock exp 4 | SERIALIZABLE | LOCK TABLES film_inventory WRITE | A read 10 | A blocked=2.00s (without lock: 0.00s)
