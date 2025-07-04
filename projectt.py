from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class IShippable(ABC):
    @abstractmethod
    def get_name(self): pass

    @abstractmethod
    def get_weight(self): pass

class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def is_expired(self):
        return False

    def requires_shipping(self):
        return False

class ExpirableProduct(Product):
    def __init__(self, name, price, quantity, expiry_date):
        super().__init__(name, price, quantity)
        self.expiry_date = expiry_date

    def is_expired(self):
        return datetime.now() > self.expiry_date

class ShippableProduct(Product, IShippable):
    def __init__(self, name, price, quantity, weight):
        super().__init__(name, price, quantity)
        self.weight = weight

    def requires_shipping(self):
        return True

    def get_name(self):
        return self.name

    def get_weight(self):
        return self.weight

class ShippableExpirableProduct(ExpirableProduct, IShippable):
    def __init__(self, name, price, quantity, expiry_date, weight):
        super().__init__(name, price, quantity, expiry_date)
        self.weight = weight

    def requires_shipping(self):
        return True

    def get_name(self):
        return self.name

    def get_weight(self):
        return self.weight

class Customer:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

class CartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

    def total_price(self):
        return self.quantity * self.product.price

class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, product, quantity):
        if quantity > product.quantity:
            raise Exception(f"Not enough quantity for {product.name}")
        self.items.append(CartItem(product, quantity))

    def checkout(self, customer):
        if not self.items:
            raise Exception("Cart is empty")

        subtotal = 0
        shipping_fees = 0
        shippable_items = []

        for item in self.items:
            if item.product.is_expired():
                raise Exception(f"Product {item.product.name} is expired")
            if item.quantity > item.product.quantity:
                raise Exception(f"Insufficient stock for {item.product.name}")

            subtotal += item.total_price()
            if isinstance(item.product, IShippable):
                shipping_fees += item.product.get_weight() * 10
                shippable_items.append(item.product)

        total = subtotal + shipping_fees
        if customer.balance < total:
            raise Exception("Insufficient balance")

        customer.balance -= total
        for item in self.items:
            item.product.quantity -= item.quantity

        print("Checkout Summary:")
        print(f"Subtotal: {subtotal} EGP")
        print(f"Shipping Fees: {shipping_fees} EGP")
        print(f"Total Paid: {total} EGP")
        print(f"Customer Balance: {customer.balance} EGP")

        if shippable_items:
            ShippingService.send(shippable_items)

class ShippingService:
    @staticmethod
    def send(items):
        print("\nShipping the following items:")
        for item in items:
            print(f"- {item.get_name()} ({item.get_weight()} kg)")

# Test case
if __name__ == "__main__":
    cheese = ShippableExpirableProduct("Cheese", 50, 10, datetime.now() + timedelta(days=5), 1.5)
    tv = ShippableProduct("TV", 5000, 2, 8)
    card = Product("Scratch Card", 10, 20)
    products = [cheese, tv, card]

    customer = Customer(input("Enter your name: "), 6000)
    cart = Cart()

    def show_products():
        print("\nAvailable Products:")
        for idx, p in enumerate(products, 1):
            status = " (Expired)" if hasattr(p, 'is_expired') and p.is_expired() else ""
            print(f"{idx}. {p.name} - {p.price} EGP - {p.quantity} in stock{status}")

    def show_cart():
        print("\nYour Cart:")
        if not cart.items:
            print("Cart is empty.")
            return
        for idx, item in enumerate(cart.items, 1):
            print(f"{idx}. {item.product.name} x {item.quantity} = {item.total_price()} EGP")

    while True:
        print("\n--- Main Menu ---")
        print("1. View Products")
        print("2. Add Product to Cart")
        print("3. View Cart")
        print("4. Checkout")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            show_products()
        elif choice == "2":
            show_products()
            try:
                idx = int(input("Enter product number to add: ")) - 1
                if idx < 0 or idx >= len(products):
                    print("Invalid product number.")
                    continue
                qty = int(input(f"Enter quantity for {products[idx].name}: "))
                cart.add_item(products[idx], qty)
                print(f"Added {qty} x {products[idx].name} to cart.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "3":
            show_cart()
        elif choice == "4":
            try:
                cart.checkout(customer)
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
