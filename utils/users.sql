DROP TABLE IF EXISTS OrderItems CASCADE;
DROP TABLE IF EXISTS Orders CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE IF NOT EXISTS Users(
    pk serial not null PRIMARY KEY,
    username varchar(50) UNIQUE NOT NULL,
    full_name varchar(100),
    password varchar(120) NOT NULL,
    is_admin boolean default false
);

CREATE INDEX IF NOT EXISTS users_index
ON Users (pk, username);

INSERT INTO Users(username, full_name, password, is_admin)
VALUES
('admin', 'Admin User', '123', true),
('customer', 'Test Customer', 'pass', false);
