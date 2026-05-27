from typing import Dict


class ModelMixin(dict):
    pass


class User(ModelMixin):
    def __init__(self, user_data: Dict):
        super(User, self).__init__(user_data or {})
        self.pk = self.get("pk")
        self.username = self.get("username")
        self.full_name = self.get("full_name")
        self.password = self.get("password")
        self.is_admin = self.get("is_admin", False)


class Product(ModelMixin):
    def __init__(self, product_data: Dict):
        super(Product, self).__init__(product_data or {})
        self.pk = self.get("pk")
        self.id = self.get("pk")
        self.original_pid = self.get("original_pid")
        self.name = self.get("name")
        self.price = self.get("price")
        self.team = self.get("team")
        self.season = self.get("season")
        self.condition = self.get("condition")
        self.size = self.get("size")
        self.image = self.get("image")
        self.available = self.get("available", True)
        self.description = self.get("description")
        self.category = self.get("team")


class Order(ModelMixin):
    def __init__(self, order_data: Dict):
        super(Order, self).__init__(order_data or {})
        self.pk = self.get("pk")
        self.user_pk = self.get("user_pk")
        self.customer_name = self.get("customer_name")
        self.address = self.get("address")
        self.city = self.get("city")
        self.postal_code = self.get("postal_code")
        self.total = self.get("total")
        self.created_at = self.get("created_at")


class OrderItem(ModelMixin):
    def __init__(self, order_item_data: Dict):
        super(OrderItem, self).__init__(order_item_data or {})
        self.pk = self.get("pk")
        self.order_pk = self.get("order_pk")
        self.product_pk = self.get("product_pk")
        self.quantity = self.get("quantity")
        self.unit_price = self.get("unit_price")
