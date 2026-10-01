-- data/seed.sql
-- Demo seed data for the NorthStar AI Customer Support Chatbot.
--
-- NOTE: The application seeds the database via Python (SQLAlchemy) at
-- startup — this file is a reference only and is not executed directly.

-- ---------------------------------------------------------------------------
-- Orders (assignment-required data)
-- ---------------------------------------------------------------------------
INSERT INTO orders (order_id, customer_name, status, estimated_delivery) VALUES
    ('111', 'Demo Customer', 'Shipped',    'Arriving Tomorrow'),
    ('222', 'Demo Customer', 'Processing', 'Ships in 24 Hours'),
    ('333', 'Demo Customer', 'Delivered',  'Delivered');

-- ---------------------------------------------------------------------------
-- Products
-- ---------------------------------------------------------------------------
INSERT INTO products (category, product_name) VALUES
    ('Tent',        '4-Season Tent'),
    ('Sleeping',    'Insulated Sleeping Bag'),
    ('Clothing',    'Insulated Jacket'),
    ('Backpack',    '60L Hiking Backpack'),
    ('Footwear',    'Waterproof Hiking Boots'),
    ('Rain Jacket', 'Packable Rain Jacket');

-- ---------------------------------------------------------------------------
-- Recommendation Rules
-- ---------------------------------------------------------------------------
INSERT INTO recommendation_rules (activity, weather, experience, category) VALUES
    ('Camping', 'Cold', 'Beginner',     'Sleeping'),
    ('Camping', 'Cold', 'Beginner',     'Clothing'),
    ('Camping', 'Cold', 'Beginner',     'Tent'),
    ('Camping', 'Cold', 'Intermediate', 'Tent'),
    ('Camping', 'Cold', 'Intermediate', 'Sleeping'),
    ('Camping', 'Warm', NULL,           'Tent'),
    ('Camping', 'Warm', NULL,           'Backpack'),
    ('Hiking',  'Warm', 'Intermediate', 'Backpack'),
    ('Hiking',  'Warm', 'Intermediate', 'Footwear'),
    ('Hiking',  'Rainy', NULL,          'Rain Jacket'),
    ('Hiking',  'Rainy', NULL,          'Footwear');
