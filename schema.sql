-- Run once:  mysql -u root -p -e "source schema.sql"
-- Requires the sakila sample database (we copy the first 10 films from it).

CREATE DATABASE IF NOT EXISTS isolation_lab;
USE isolation_lab;

DROP TABLE IF EXISTS film_inventory;

CREATE TABLE film_inventory (
    film_id      INT          PRIMARY KEY,
    title        VARCHAR(100) NOT NULL,
    stock        INT          NOT NULL,
    price        DECIMAL(5,2) NOT NULL,
    -- refreshed automatically whenever the row changes
    last_updated TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                              ON UPDATE CURRENT_TIMESTAMP
) ENGINE = InnoDB;

-- Base data: films 1..10, stock 10, price = rental_rate
INSERT INTO film_inventory (film_id, title, stock, price)
SELECT film_id, title, 10, rental_rate
FROM sakila.film
WHERE film_id BETWEEN 1 AND 10;
