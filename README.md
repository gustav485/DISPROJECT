# Football shirt webshop

This version is rebuilt using the same idea as GreenGroceries:

- `models.py` contains small model classes.
- `queries.py` contains SQL insert/select/update/delete functions.
- `utils/users.sql` and `utils/products.sql` create the schema.
- `init_db.py` imports the dataset from `shirts.csv` into PostgreSQL.
- Flask routes use SQL data instead of hardcoded Python lists.

## AI declaration

See `AI_DECLARATION.md`.

## Regular expression matching

The app uses Python regular expressions to validate user input:

- Signup usernames must match `^[A-Za-z0-9_]{3,30}$`, so usernames only contain letters, numbers, and underscores.
- Checkout postal codes must match `^\d{4}$`, so postal codes are exactly four digits.

## Recommended setup with Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d
cp .env.example .env
```

Then edit `.env` so it contains:

```env
SECRET_KEY=dev-secret-key
DB_HOST=localhost
DB_NAME=football_shop
DB_USERNAME=postgres
DB_PASSWORD=UIS
DB_PORT=5432
```

Initialize the database:

```bash
python init_db.py
python app.py
```

Open: `http://127.0.0.1:5000`

## Login users

After `python init_db.py`, these users exist:

| Username | Password | Role |
|---|---|---|
| admin | 123 | Admin |
| customer | pass | Customer |

You can also create new users through `/signup`.

## Mac/Homebrew setup instead of Docker

If you do not use Docker:

```bash
brew install postgresql@16
brew services start postgresql@16
createdb football_shop
cp .env.example .env
python init_db.py
python app.py
```

For Homebrew PostgreSQL, your database user is often your Mac username, not `postgres`. You can leave `DB_USERNAME=` empty in `.env`; the code will use your Mac username automatically.

## How the dataset works

`init_db.py` reads `shirts.csv` and inserts every row into the `Products` table.

CSV columns used:

```text
pid, name, price, team, season, condition, size
```

The image is generated from the `pid` like this:

```text
/pictures/pid0.png
/pictures/pid1.png
...
```

## Add more products through the dataset

1. Add a new row in `shirts.csv`.
2. Add the matching image in `pictures/`, for example `pid12.png`.
3. Run:

```bash
python init_db.py
```

Important: `init_db.py` resets and reimports the database, just like GreenGroceries does.

## Add products without resetting the database

Log in as:

```text
admin / 123
```

Go to:

```text
/admin/products
```

Fill in the form and press **Add product**.

## Remove or hide products

Log in as admin and go to:

```text
/admin/products
```

- **Toggle** changes `available` true/false.
- **Delete** removes the product from SQL.

Checkout also sets bought products to unavailable.

## Add users to the database

### Option 1: Through the website

Go to `/signup` and create a user.

### Option 2: SQL manually

```sql
INSERT INTO Users(username, full_name, password, is_admin)
VALUES ('newuser', 'New User', 'pass', false);
```

To make an admin:

```sql
INSERT INTO Users(username, full_name, password, is_admin)
VALUES ('newadmin', 'New Admin', '123', true);
```

## Main SQL tables

- `Users`: login and role data.
- `Products`: shirts from the dataset.
- `Orders`: one row per checkout.
- `OrderItems`: products inside each order.

## Useful commands

Check the DB connection:

```bash
python check_db.py
```

Reset/import database:

```bash
python init_db.py
```

Start website:

```bash
python app.py
```


## Checkout flow

The cart page only shows the cart. Pressing **Checkout** opens `/checkout`, where the customer must fill out name and address and confirm: “Are you sure you want to purchase this order?” The order is only inserted into PostgreSQL after that confirmation. Clicking the logo or **Products** always goes back to the product page and does not create an order.
