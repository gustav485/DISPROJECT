from functools import wraps
import os

from flask import Flask, render_template, abort, redirect, url_for, request, session, flash, send_from_directory
from psycopg2 import OperationalError

from models import User, Product
from queries import (
    verify_user, get_user_by_username, insert_user,
    get_product_by_pk, get_available_products, get_products_by_filters, get_filter_options,
    insert_order, get_orders_by_user_pk, get_order_items,
    insert_product, update_product_availability, delete_product
)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


@app.errorhandler(OperationalError)
def database_error(error):
    return render_template("db_error.html", error=error), 500


@app.route("/pictures/<path:filename>")
def pictures(filename):
    return send_from_directory("pictures", filename)


# ---------------------------------------------------------------------------
# Cart helpers — cart stays in session, products/orders come from SQL.
# ---------------------------------------------------------------------------

def cart_get():
    return session.get("cart", {})


def cart_save(cart):
    session["cart"] = cart
    session.modified = True


def cart_add(product_id, quantity=1):
    cart = cart_get()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + quantity
    cart_save(cart)


def cart_remove(product_id):
    cart = cart_get()
    cart.pop(str(product_id), None)
    cart_save(cart)


def cart_update_quantity(product_id, quantity):
    if quantity <= 0:
        cart_remove(product_id)
        return
    cart = cart_get()
    cart[str(product_id)] = quantity
    cart_save(cart)


def cart_items():
    items = []
    for pid, qty in cart_get().items():
        product = get_product_by_pk(int(pid))
        if product and product.available:
            line = dict(product)
            line["id"] = product.pk
            line["quantity"] = qty
            line["subtotal"] = round(float(product.price) * qty, 2)
            items.append(line)
    return items


def cart_total(items):
    return round(sum(float(i["subtotal"]) for i in items), 2)


def cart_count():
    return sum(cart_get().values())


@app.context_processor
def inject_globals():
    return {"cart_count": cart_count(), "current_username": session.get("username")}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_pk" not in session:
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_pk" not in session:
            return redirect(url_for("login", next=request.path))
        if not session.get("is_admin"):
            flash("Only admin users can access that page.")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_pk" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = verify_user(username, password)
        if user:
            session["user_pk"] = user.pk
            session["username"] = user.username
            session["is_admin"] = bool(user.is_admin)
            next_page = request.args.get("next", url_for("index"))
            return redirect(next_page)
        flash("Invalid username or password.")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_pk" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        password_repeat = request.form.get("password_repeat", "")
        if password != password_repeat:
            flash("Passwords do not match.")
        elif get_user_by_username(username):
            flash("Username already exists.")
        else:
            user_pk = insert_user(User({
                "username": username,
                "full_name": full_name,
                "password": password,
                "is_admin": False,
            }))
            session["user_pk"] = user_pk
            session["username"] = username
            session["is_admin"] = False
            return redirect(url_for("index"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Shop
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    teams, sizes = get_filter_options()
    if request.method == "POST":
        products = get_products_by_filters(
            team=request.form.get("team") or None,
            size=request.form.get("size") or None,
            max_price=request.form.get("max_price") or None,
            search=request.form.get("search") or None,
        )
    else:
        products = get_available_products()
    return render_template("shop.html", products=products, teams=teams, sizes=sizes)


@app.route("/product/<int:product_id>")
@login_required
def product(product_id):
    p = get_product_by_pk(product_id)
    if p is None:
        abort(404)
    return render_template("product.html", product=p)


# ---------------------------------------------------------------------------
# Cart and orders
# ---------------------------------------------------------------------------

@app.route("/cart")
@login_required
def cart():
    items = cart_items()
    total = cart_total(items)
    return render_template("cart.html", items=items, total=total)


@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def cart_add_route(product_id):
    p = get_product_by_pk(product_id)
    if p is None or not p.available:
        abort(404)
    cart_add(product_id)
    flash("Added to cart.")
    next_page = request.form.get("next") or request.referrer or url_for("index")
    return redirect(next_page)


@app.route("/cart/update/<int:product_id>", methods=["POST"])
@login_required
def cart_update_route(product_id):
    quantity = int(request.form.get("quantity", 0))
    cart_update_quantity(product_id, quantity)
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
@login_required
def cart_remove_route(product_id):
    cart_remove(product_id)
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = cart_items()
    if not items:
        flash("Your cart is empty.")
        return redirect(url_for("cart"))

    total = cart_total(items)

    if request.method == "GET":
        return render_template("checkout.html", items=items, total=total)

    customer_name = request.form.get("customer_name", "").strip()
    address = request.form.get("address", "").strip()
    city = request.form.get("city", "").strip()
    postal_code = request.form.get("postal_code", "").strip()
    confirmed = request.form.get("confirm_purchase") == "yes"

    if not customer_name or not address:
        flash("Please fill out your name and address before checkout.")
        return render_template("checkout.html", items=items, total=total), 400

    if not confirmed:
        flash("Please confirm that you want to purchase the items.")
        return render_template("checkout.html", items=items, total=total), 400

    order_pk = insert_order(
        session["user_pk"],
        items,
        total,
        customer_name,
        address,
        city or None,
        postal_code or None,
    )
    for item in items:
        update_product_availability(item["pk"], False)
    session["cart"] = {}
    return redirect(url_for("order_success", order_pk=order_pk))


@app.route("/order-success/<int:order_pk>")
@login_required
def order_success(order_pk):
    """Confirmation page shown directly after checkout."""
    return render_template("order_success.html", order_pk=order_pk)


@app.route("/orders")
@login_required
def orders():
    user_orders = get_orders_by_user_pk(session["user_pk"])
    detailed_orders = []
    for order in user_orders:
        detailed_orders.append({"order": order, "order_items": get_order_items(order.pk)})
    return render_template("orders.html", detailed_orders=detailed_orders)


# ---------------------------------------------------------------------------
# Admin/product management
# ---------------------------------------------------------------------------

@app.route("/admin/products", methods=["GET", "POST"])
@admin_required
def admin_products():
    if request.method == "POST":
        product_data = Product({
            "original_pid": None,
            "name": request.form.get("name"),
            "price": request.form.get("price"),
            "team": request.form.get("team"),
            "season": request.form.get("season"),
            "condition": request.form.get("condition"),
            "size": request.form.get("size"),
            "image": request.form.get("image") or "https://placehold.co/400x300?text=Football+Shirt",
            "available": True,
        })
        insert_product(product_data)
        flash("Product added.")
        return redirect(url_for("admin_products"))
    products = get_all_products()
    return render_template("admin_products.html", products=products)


@app.route("/admin/products/<int:product_id>/toggle", methods=["POST"])
@admin_required
def toggle_product(product_id):
    p = get_product_by_pk(product_id)
    if not p:
        abort(404)
    update_product_availability(product_id, not p.available)
    return redirect(url_for("admin_products"))


@app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def remove_product(product_id):
    delete_product(product_id)
    return redirect(url_for("admin_products"))


if __name__ == "__main__":
    app.run(debug=True)
