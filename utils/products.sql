DROP VIEW IF EXISTS vw_order_items CASCADE;
DROP VIEW IF EXISTS vw_products CASCADE;
DROP TABLE IF EXISTS OrderItems CASCADE;
DROP TABLE IF EXISTS Orders CASCADE;
DROP TABLE IF EXISTS Products CASCADE;

CREATE TABLE IF NOT EXISTS Products(
    pk serial not null PRIMARY KEY,
    original_pid int UNIQUE,
    name varchar(100) NOT NULL,
    price numeric(10, 2) NOT NULL,
    team varchar(100),
    season varchar(20),
    condition varchar(20),
    size varchar(30),
    image varchar(255),
    available boolean default true
);

CREATE INDEX IF NOT EXISTS products_index
ON Products (team, size, price, available);

CREATE TABLE IF NOT EXISTS Orders(
    pk serial not null PRIMARY KEY,
    user_pk int not null REFERENCES Users(pk) ON DELETE CASCADE,
    customer_name varchar(100) NOT NULL,
    address varchar(255) NOT NULL,
    city varchar(100),
    postal_code varchar(30),
    total numeric(10, 2) not null,
    created_at timestamp not null default current_timestamp
);

CREATE INDEX IF NOT EXISTS orders_index
ON Orders (user_pk, created_at);

CREATE TABLE IF NOT EXISTS OrderItems(
    pk serial not null PRIMARY KEY,
    order_pk int not null REFERENCES Orders(pk) ON DELETE CASCADE,
    product_pk int not null REFERENCES Products(pk) ON DELETE CASCADE,
    quantity int not null default 1,
    unit_price numeric(10, 2) not null
);

CREATE INDEX IF NOT EXISTS order_items_index
ON OrderItems (order_pk, product_pk);

CREATE OR REPLACE VIEW vw_products
AS
SELECT
    pk,
    original_pid,
    name,
    price,
    team,
    season,
    condition,
    size,
    image,
    available,
    CONCAT(INITCAP(REPLACE(team, '_', ' ')), ' ', season, ' shirt in size ', size, '. Condition: ', condition, '.') as description
FROM Products;

CREATE OR REPLACE VIEW vw_order_items
AS
SELECT
    oi.pk,
    oi.order_pk,
    oi.product_pk,
    oi.quantity,
    oi.unit_price,
    p.name,
    p.team,
    p.season,
    p.size,
    p.condition,
    p.image,
    (oi.quantity * oi.unit_price) as subtotal
FROM OrderItems oi
JOIN Products p ON p.pk = oi.product_pk;
