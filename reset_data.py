"""
Restore film_inventory to its 10 base rows (film_id 1-10, stock 10, price = rental_rate).
Deletes any extra rows (e.g. film_id 11 inserted by the phantom tests).

Usage:  python reset_data.py      (also imported and called by the other scripts)
"""
from common import connect


def reset():
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM film_inventory")
    cur.execute("""
        INSERT INTO film_inventory (film_id, title, stock, price)
        SELECT film_id, title, 10, rental_rate
        FROM sakila.film
        WHERE film_id BETWEEN 1 AND 10
    """)
    cur.execute("SELECT COUNT(*) FROM film_inventory")
    count = cur.fetchone()[0]
    conn.close()
    return count


if __name__ == "__main__":
    print(f"film_inventory reset: {reset()} rows")
