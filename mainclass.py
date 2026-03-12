import random

class Restaurant:
    def __init__(self, name):
        self.name = name
        self.menu = {}
        self.customers = []

    def add_menu_item(self, item_name, price):
        self.menu[item_name] = price

    def add_customer(self, customer):
        self.customers.append(customer)

    def take_order(self, customer, item_name):
        if item_name in self.menu:
            price = self.menu[item_name]
            customer.order(item_name)
            customer.pay(price)
        else:
            print(f"Sorry, {item_name} is not on the menu.")
    
    def branch_one(self):
        print(f"Welcome to {self.name} - Branch One!")
        self.add_menu_item("Italian", 5)
        self.add_menu_item("Hawaian", 2)
        self.add_menu_item("Filipino style", 1)
class Costumer:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"Costumer: {self.name}, Age: {self.age}"
    
    def pay(self, amount):
        print(f"{self.name} paid {amount} dollars.")
    
    def order(self, item):
        print(f"{self.name} ordered {item}.")