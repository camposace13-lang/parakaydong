import random
from datetime import datetime

class Restaurant:
    def __init__(self, name):
        self.name = name
        self.menu = {}  # Main menu
        self.customers = []

    def set_pizza_menu(self):
        """Define the standard pizza menu"""
        self.menu = {
            "Margherita": 8.99,
            "Pepperoni": 10.99,
            "Hawaiian": 9.99,
            "Italian": 7.99,
            "Filipino Style": 11.99,
            "Cheese": 6.99,
            "Veggie": 8.49
        }

    def add_menu_item(self, item_name, price):
        self.menu[item_name] = price

    def add_customer(self, customer):
        self.customers.append(customer)

    def take_order(self, customer, item_name, branch, takeout=False):
        """Take order from customer - either dine-in or takeout"""
        if item_name in branch.menu:
            price = branch.menu[item_name]
            customer.order(item_name, takeout)
            customer.pay(price)
            if takeout:
                print(f" => Order is for TAKE-OUT at {branch.branch_name}")
            else:
                print(f" => Order is for DINE-IN at {branch.branch_name}")
        else:
            print(f"Sorry, {item_name} is not on the menu.")

    def display_branches(self):
        """Display all branches"""
        print(f"\n--- {self.name} Branches ---")
        for branch in self.branches:
            print(f"  - {branch.branch_name}")
        print("----------------------------")


class MorningBranch(Restaurant):
    """Branch One - Opens in the morning only (6:00 AM - 12:00 PM) - Child class of Restaurant"""
    def __init__(self, branch_name):
        super().__init__(branch_name)
        self.branch_name = branch_name
        self.set_morning_menu()
        
    def set_morning_menu(self):
        """Morning branch has its own unique menu"""
        self.menu = {
            "Breakfast Pizza": 12.99,
            "Egg Pizza": 10.99,
            "Bacon Pizza": 11.99,
            "Veggie Delight": 9.99,
            "Margherita": 8.99
        }
    
    def __str__(self):
        return f"Morning Branch: {self.branch_name}"

    def display_menu(self):
        print(f"\n--- {self.branch_name} Menu (Morning) ---")
        for item, price in self.menu.items():
            print(f"  {item}: ${price}")
        print("---------------------------")

    def display_opening_hours(self):
        print(f"{self.branch_name}: 6:00 AM - 12:00 PM")

    def is_open(self):
        """Check if branch is open (morning only: 6 AM to 12 PM)"""
        current_hour = datetime.now().hour
        return 6 <= current_hour < 12

    def get_status(self):
        if self.is_open():
            return f"{self.branch_name} is OPEN"
        else:
            return f"{self.branch_name} is CLOSED"


class EveningBranch(Restaurant):
    """Branch Two - Opens in the evening only (5:00 PM - 10:00 PM) - Child class of Restaurant"""
    def __init__(self, branch_name):
        super().__init__(branch_name)
        self.branch_name = branch_name
        self.set_evening_menu()
        
    def set_evening_menu(self):
        """Evening branch has its own unique menu"""
        self.menu = {
            "Pepperoni": 10.99,
            "Hawaiian": 9.99,
            "BBQ Chicken": 13.99,
            "Seafood Pizza": 14.99,
            "Meat Lovers": 12.99,
            "Cheese": 6.99
        }
    
    def __str__(self):
        return f"Evening Branch: {self.branch_name}"

    def display_menu(self):
        print(f"\n--- {self.branch_name} Menu (Evening) ---")
        for item, price in self.menu.items():
            print(f"  {item}: ${price}")
        print("---------------------------")

    def display_opening_hours(self):
        print(f"{self.branch_name}: 5:00 PM - 10:00 PM")

    def is_open(self):
        """Check if branch is open (evening only: 5 PM to 10 PM)"""
        current_hour = datetime.now().hour
        return 17 <= current_hour < 22

    def get_status(self):
        if self.is_open():
            return f"{self.branch_name} is OPEN"
        else:
            return f"{self.branch_name} is CLOSED"


class TwentyFourHourBranch(Restaurant):
    """Branch Three - Opens 24 hours - Child class of Restaurant"""
    def __init__(self, branch_name):
        super().__init__(branch_name)
        self.branch_name = branch_name
        self.set_24hour_menu()
        
    def set_24hour_menu(self):
        """24-hour branch has its own unique menu"""
        self.menu = {
            "Margherita": 8.99,
            "Pepperoni": 10.99,
            "Hawaiian": 9.99,
            "Italian": 7.99,
            "Filipino Style": 11.99,
            "Cheese": 6.99,
            "Veggie": 8.49,
            "Extra Cheese": 9.49,
            "Supreme": 15.99,
            "Special Combo": 18.99
        }
    
    def __str__(self):
        return f"24-Hour Branch: {self.branch_name}"

    def display_menu(self):
        print(f"\n--- {self.branch_name} Menu (24 Hours) ---")
        for item, price in self.menu.items():
            print(f"  {item}: ${price}")
        print("---------------------------")

    def display_opening_hours(self):
        print(f"{self.branch_name}: OPEN 24 HOURS")

    def is_open(self):
        """Check if branch is open (24 hours)"""
        return True

    def get_status(self):
        return f"{self.branch_name} is OPEN"


class Customer:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.orders = []

    def __str__(self):
        return f"Customer: {self.name}, Age: {self.age}"
    
    def pay(self, amount):
        print(f"{self.name} paid ${amount:.2f}")
    
    def order(self, item, takeout=False):
        self.orders.append(item)
        if takeout:
            print(f"{self.name} ordered {item} (TAKEOUT)")
        else:
            print(f"{self.name} ordered {item} (DINE-IN)")

    def view_orders(self):
        print(f"\n{self.name}'s Orders:")
        for item in self.orders:
            print(f"  - {item}")


# Demo usage
if __name__ == "__main__":
    # Create main restaurant
    pizza_place = Restaurant("Pizza Palace")
    
    # Set the main restaurant menu
    pizza_place.set_pizza_menu()
    
    # Create 3 different branch classes (each is a direct child of Restaurant)
    # Each branch has its own unique menu
    branch1 = MorningBranch("Branch One - Downtown")
    branch2 = EveningBranch("Branch Two - Uptown")
    branch3 = TwentyFourHourBranch("Branch Three - Mall")
    
    # Add branches to restaurant list
    pizza_place.branches = [branch1, branch2, branch3]
    
    # Display all branches
    print("=== PIZZA PALACE BRANCHES ===")
    pizza_place.display_branches()
    
    # Display opening hours for each branch
    print("\n=== BRANCH OPENING HOURS ===")
    for branch in pizza_place.branches:
        branch.display_opening_hours()
    
    # Check current status of each branch
    print("\n=== CURRENT BRANCH STATUS ===")
    for branch in pizza_place.branches:
        print(branch.get_status())
    
    # Display different menus for each branch
    print("\n=== DIFFERENT BRANCH MENUS ===")
    for branch in pizza_place.branches:
        branch.display_menu()
    
    # Create customers
    customer1 = Customer("John", 25)
    customer2 = Customer("Maria", 30)
    
    # Take orders (dine-in)
    print("\n--- DINE-IN ORDERS ---")
    pizza_place.take_order(customer1, "Breakfast Pizza", branch1, takeout=False)
    pizza_place.take_order(customer2, "Egg Pizza", branch1, takeout=False)
    
    # Take orders (takeout)
    print("\n--- TAKEOUT ORDERS ---")
    pizza_place.take_order(customer1, "BBQ Chicken", branch2, takeout=True)
    pizza_place.take_order(customer2, "Supreme", branch3, takeout=True)
    
    # View customer orders
    customer1.view_orders()
    customer2.view_orders()
    
    # Demonstrate inheritance hierarchy
    print("\n=== CLASS HIERARCHY ===")
    print(f"MorningBranch is a subclass of Restaurant: {issubclass(MorningBranch, Restaurant)}")
    print(f"EveningBranch is a subclass of Restaurant: {issubclass(EveningBranch, Restaurant)}")
    print(f"TwentyFourHourBranch is a subclass of Restaurant: {issubclass(TwentyFourHourBranch, Restaurant)}")

