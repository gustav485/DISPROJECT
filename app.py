from flask import Flask, render_template, abort

app = Flask(__name__)

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


@app.route("/")
def index():
    return render_template("shop.html", products=products)


@app.route("/product/<int:product_id>")
def product(product_id):
    p = next((p for p in products if p["id"] == product_id), None)
    if p is None:
        abort(404)
    return render_template("product.html", product=p)


if __name__ == "__main__":
    app.run(debug=True)
