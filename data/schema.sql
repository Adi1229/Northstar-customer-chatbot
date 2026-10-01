-- data/schema.sql
-- DDL for the NorthStar AI Customer Support Chatbot (SQLite)
--
-- This file contains CREATE TABLE statements only.
-- Seed data lives in data/seed.sql.
-- The application seeds via Python (SQLAlchemy) at startup,
-- so this file serves as a reference schema document.

DROP TABLE IF EXISTS recommendation_rules;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;

-- ---------------------------------------------------------------------------
-- orders
-- Stores customer order status for the demo data set.
-- ---------------------------------------------------------------------------
CREATE TABLE orders (
    order_id            TEXT    PRIMARY KEY,
    customer_name       TEXT,
    status              TEXT    NOT NULL,
    estimated_delivery  TEXT
);

-- ---------------------------------------------------------------------------
-- products
-- Stores the product catalogue (category + name).
-- ---------------------------------------------------------------------------
CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    category     TEXT    NOT NULL,
    product_name TEXT    NOT NULL
);

-- ---------------------------------------------------------------------------
-- recommendation_rules
-- Maps user activity/weather/experience to a product category.
-- experience is nullable — it is an optional filter.
-- ---------------------------------------------------------------------------
CREATE TABLE recommendation_rules (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    activity   TEXT    NOT NULL,
    weather    TEXT    NOT NULL,
    experience TEXT,
    category   TEXT    NOT NULL
);

-- Indexes for expected query patterns
CREATE INDEX IF NOT EXISTS idx_orders_order_id
    ON orders (order_id);

CREATE INDEX IF NOT EXISTS idx_rules_activity_weather
    ON recommendation_rules (activity, weather);
