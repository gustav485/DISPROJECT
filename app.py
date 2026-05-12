from flask import Flask, render_template, abort, redirect, url_for, request, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = "dev-secret-key"

USERS = {
    "admin": "password123",
}

products = [
    {"id": 1, "name": "Wireless Headphones", "price": 79.99, "category": "Electronics", "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life.", "image": "https://placehold.co/400x300?text=Headphones"},
    {"id": 2, "name": "Running Shoes", "price": 119.99, "category": "Footwear", "description": "Lightweight running shoes with responsive cushioning, perfect for long-distance runs.", "image": "https://placehold.co/400x300?text=Running+Shoes"},
    {"id": 3, "name": "Coffee Maker", "price": 49.99, "category": "Kitchen", "description": "12-cup programmable coffee maker with built-in grinder and thermal carafe.", "image": "https://placehold.co/400x300?text=Coffee+Maker"},
    {"id": 4, "name": "Yoga Mat", "price": 34.99, "category": "Sports", "description": "Non-slip eco-friendly yoga mat, 6mm thick with alignment lines.", "image": "https://placehold.co/400x300?text=Yoga+Mat"},
    {"id": 5, "name": "Mechanical Keyboard", "price": 149.99, "category": "Electronics", "description": "Compact TKL mechanical keyboard with RGB lighting and tactile switches.", "image": "https://placehold.co/400x300?text=Keyboard"},
    {"id": 6, "name": "Sunglasses", "price": 59.99, "category": "Accessories", "description": "UV400 polarized sunglasses with lightweight titanium frame.", "image": "https://placehold.co/400x300?text=Sunglasses"},
    {"id": 7, "name": "Backpack", "price": 89.99, "category": "Accessories", "description": "30L waterproof hiking backpack with laptop compartment and ergonomic straps.", "image": "https://placehold.co/400x300?text=Backpack"},
    {"id": 8, "name": "Desk Lamp", "price": 39.99, "category": "Home", "description": "LED desk lamp with adjustable brightness, color temperature, and USB charging port.", "image": "https://placehold.co/400x300?text=Desk+Lamp"},
    {"id": 9, "name": "Water Bottle", "price": 24.99, "category": "Sports", "description": "Insulated stainless steel water bottle, keeps drinks cold 24h or hot 12h.", "image": "https://placehold.co/400x300?text=Water+Bottle"},
    {"id": 10, "name": "Notebook Set", "price": 18.99, "category": "Stationery", "description": "Set of 3 hardcover dot-grid notebooks, 192 pages each, lay-flat binding.", "image": "https://placehold.co/400x300?text=Notebooks"},
]


# ---------------------------------------------------------------------------
# Cart helpers — swap these out when adding a database
# ---------------------------------------------------------------------------

def get_product(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def cart_get():
    """Return the raw cart dict {str(product_id): quantity} from session."""
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
    """Return enriched cart lines: product fields + quantity + subtotal."""
    items = []
    for pid, qty in cart_get().items():
        product = get_product(int(pid))
        if product:
            items.append({**product, "quantity": qty, "subtotal": round(product["price"] * qty, 2)})
    return items


def cart_total(items):
    return round(sum(i["subtotal"] for i in items), 2)


def cart_count():
    return sum(cart_get().values())


# Make cart_count available in all templates
@app.context_processor
def inject_cart_count():
    return {"cart_count": cart_count()}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if USERS.get(username) == password:
            session["username"] = username
            next_page = request.args.get("next", url_for("index"))
            return redirect(next_page)
        flash("Invalid username or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Shop
# ---------------------------------------------------------------------------

@app.route("/")
@login_required
def index():
    return render_template("shop.html", products=products)


@app.route("/product/<int:product_id>")
@login_required
def product(product_id):
    p = get_product(product_id)
    if p is None:
        abort(404)
    return render_template("product.html", product=p)


# ---------------------------------------------------------------------------
# Cart
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
    if get_product(product_id) is None:
        abort(404)
    cart_add(product_id)
    flash(f"Added to cart.")
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


if __name__ == "__main__":
    app.run(debug=True)
