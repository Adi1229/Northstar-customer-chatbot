
-- DATABASE_SCHEMA.sql
-- SQLite schema for assignment

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS recommendation_rules;

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_name TEXT,
    status TEXT NOT NULL,
    estimated_delivery TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    product_name TEXT NOT NULL
);

CREATE TABLE recommendation_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity TEXT,
    weather TEXT,
    experience TEXT,
    category TEXT
);

INSERT INTO orders VALUES
('111','Demo Customer','Shipped','Arriving Tomorrow'),
('222','Demo Customer','Processing','Ships in 24 Hours'),
('333','Demo Customer','Delivered','Delivered');

INSERT INTO products(category,product_name) VALUES
('Tent','4-Season Tent'),
('Sleeping','Insulated Sleeping Bag'),
('Clothing','Insulated Jacket'),
('Backpack','60L Hiking Backpack');

INSERT INTO recommendation_rules(activity,weather,experience,category) VALUES
('Camping','Cold','Beginner','Sleeping'),
('Camping','Cold','Beginner','Clothing'),
('Camping','Cold','Beginner','Tent'),
('Hiking','Warm','Intermediate','Backpack');
