# Lock evidence: phantom_serializable

Isolation level: SERIALIZABLE. Snapshot while Session A was blocked.

| Session | lock_type | lock_mode | index_name | lock_data | lock_status |
|---|---|---|---|---|---|
| A | RECORD | X,INSERT_INTENTION | PRIMARY | supremum pseudo-record | WAITING |
| A | TABLE | IX |  |  | GRANTED |
| B | RECORD | S | PRIMARY | 1 | GRANTED |
| B | RECORD | S | PRIMARY | 10 | GRANTED |
| B | RECORD | S | PRIMARY | 2 | GRANTED |
| B | RECORD | S | PRIMARY | 3 | GRANTED |
| B | RECORD | S | PRIMARY | 4 | GRANTED |
| B | RECORD | S | PRIMARY | 5 | GRANTED |
| B | RECORD | S | PRIMARY | 6 | GRANTED |
| B | RECORD | S | PRIMARY | 7 | GRANTED |
| B | RECORD | S | PRIMARY | 8 | GRANTED |
| B | RECORD | S | PRIMARY | 9 | GRANTED |
| B | RECORD | S | PRIMARY | supremum pseudo-record | GRANTED |
| B | TABLE | IS |  |  | GRANTED |
