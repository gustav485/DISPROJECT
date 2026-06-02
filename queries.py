from models import User, Product, Order
from db import get_cursor


# INSERT QUERIES

def insert_user(user: User):
    sql = """
    INSERT INTO Users(username, full_name, password)
    VALUES (%s, %s, %s)
    RETURNING pk
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (user.username, user.full_name, user.password))
        row = cur.fetchone()
        return row.get("pk") if row else None


def insert_order(user_pk, cart_lines, total, customer_name, address, city=None, postal_code=None):
    """Create one order and many order_items from session cart lines."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO Orders(user_pk, customer_name, address, city, postal_code, total)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING pk
            """,
            (user_pk, customer_name, address, city, postal_code, total)
        )
        order_pk = cur.fetchone()["pk"]
        for line in cart_lines:
            cur.execute(
                """
                INSERT INTO OrderItems(order_pk, product_pk, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """,
                (order_pk, line["pk"], line["quantity"], line["price"])
            )
        return order_pk


# SELECT QUERIES

def get_user_by_pk(pk):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM Users WHERE pk = %s", (pk,))
        return User(cur.fetchone()) if cur.rowcount > 0 else None


def get_user_by_username(username):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM Users WHERE username = %s", (username,))
        return User(cur.fetchone()) if cur.rowcount > 0 else None


def verify_user(username, password):
    user = get_user_by_username(username)
    if user and user.password == password:
        return user
    return None


def get_product_by_pk(pk):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM vw_products WHERE pk = %s", (pk,))
        return Product(cur.fetchone()) if cur.rowcount > 0 else None


def get_available_products():
    with get_cursor() as cur:
        cur.execute("SELECT * FROM vw_products WHERE available = true ORDER BY team, name")
        return [Product(row) for row in cur.fetchall()] if cur.rowcount > 0 else []


def get_products_by_filters(team=None, size=None, max_price=None, search=None):
    sql = "SELECT * FROM vw_products WHERE 1=1"
    params = []
    if team:
        sql += " AND team = %s"
        params.append(team)
    if size:
        sql += " AND size = %s"
        params.append(size)
    if max_price:
        sql += " AND price <= %s"
        params.append(max_price)
    if search:
        sql += " AND (LOWER(name) LIKE LOWER(%s) OR LOWER(team) LIKE LOWER(%s) OR LOWER(season) LIKE LOWER(%s))"
        term = f"%{search}%"
        params.extend([term, term, term])
    sql += " ORDER BY available DESC, team, name"
    with get_cursor() as cur:
        cur.execute(sql, tuple(params))
        return [Product(row) for row in cur.fetchall()] if cur.rowcount > 0 else []


def get_filter_options():
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT team FROM Products ORDER BY team")
        teams = [row["team"] for row in cur.fetchall()]
        cur.execute("SELECT DISTINCT size FROM Products ORDER BY size")
        sizes = [row["size"] for row in cur.fetchall()]
    return teams, sizes


def get_orders_by_user_pk(user_pk):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM Orders WHERE user_pk = %s ORDER BY created_at DESC", (user_pk,))
        return [Order(row) for row in cur.fetchall()] if cur.rowcount > 0 else []


def get_order_items(order_pk):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM vw_order_items WHERE order_pk = %s ORDER BY name", (order_pk,))
        return cur.fetchall() if cur.rowcount > 0 else []


# UPDATE QUERIES

def update_product_availability(product_pk, available):
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE Products SET available = %s WHERE pk = %s", (available, product_pk))
