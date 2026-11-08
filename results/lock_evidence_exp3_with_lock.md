# Lock evidence: exp3_with_lock

Isolation level: REPEATABLE READ. Snapshot while Session A was blocked.

| Session | lock_type | lock_mode | index_name | lock_data | lock_status |
|---|---|---|---|---|---|
| B | RECORD | X | PRIMARY | 1 | GRANTED |
| B | RECORD | X | PRIMARY | 10 | GRANTED |
| B | RECORD | X | PRIMARY | 2 | GRANTED |
| B | RECORD | X | PRIMARY | 3 | GRANTED |
| B | RECORD | X | PRIMARY | 4 | GRANTED |
| B | RECORD | X | PRIMARY | 5 | GRANTED |
| B | RECORD | X | PRIMARY | 6 | GRANTED |
| B | RECORD | X | PRIMARY | 7 | GRANTED |
| B | RECORD | X | PRIMARY | 8 | GRANTED |
| B | RECORD | X | PRIMARY | 9 | GRANTED |
| B | RECORD | X | PRIMARY | supremum pseudo-record | GRANTED |
| B | TABLE | IX |  |  | GRANTED |
| A | RECORD | X,INSERT_INTENTION | PRIMARY | supremum pseudo-record | WAITING |
| A | TABLE | IX |  |  | GRANTED |
