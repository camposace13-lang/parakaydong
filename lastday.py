from abc import ABC, abstractmethod

from pizzaclock import RestaurantClock
from pizzalogic import run_game


# ═════════════════════════════════════════════
# NAMETAG — COMPOSITION class
# Used by BasePlayer and Customer
# ═════════════════════════════════════════════
class NameTag:
    def __init__(self, name, role):
        self._name = name                           # ENCAPSULATION: protected attribute
        self._role = role                           # ENCAPSULATION: protected attribute

    @property                                       # ENCAPSULATION: getter
    def name(self):
        return self._name

    @property                                       # ENCAPSULATION: getter
    def role(self):
        return self._role

    @role.setter                                    # ENCAPSULATION: setter
    def role(self, value):
        self._role = value

    def display(self):
        return f"[{self._role}] {self._name}"

    def greet(self):                                # POLYMORPHISM: different greeting per role
        greetings = {
            "Chef":        "Let's cook!",
            "Cashier":     "Welcome, what can I get you?",
            "Waiter":      "Table for how many?",
            "Customer":    "Hi, I'd like to order",
            "VipCustomer": "Hello, I have a reservation",
        }
        return f"{self.display()}: {greetings.get(self._role, 'Hello')}"


# ═════════════════════════════════════════════
# BASEPLAYER — Abstract parent for all staff
# CHILD CLASSES: Chef, Cashier, Waiter
# ═════════════════════════════════════════════
class BasePlayer(ABC):                              # ABSTRACTION: abstract base class
    def __init__(self, name, role):
        self.name_tag = NameTag(name, role)         # COMPOSITION: HAS-A NameTag
        self._is_busy = False                       # ENCAPSULATION: protected attribute

    @property                                       # ENCAPSULATION: getter
    def is_busy(self):
        return self._is_busy

    @abstractmethod                                 # ABSTRACTION: must be overridden
    def perform_primary_duty(self):
        pass

    def introduce(self):                            # uses NameTag.greet()
        return self.name_tag.greet()

    def __str__(self):                              # POLYMORPHISM: overridden in subclasses
        status = "busy" if self._is_busy else "available"
        return f"{self.name_tag.display()} ({status})"


# ─────────────────────────────────────────────
class Chef(BasePlayer):                             # INHERITANCE: Chef IS-A BasePlayer
    def __init__(self, name):
        super().__init__(name, "Chef")

    def perform_primary_duty(self):                 # POLYMORPHISM: overrides abstract method
        self._is_busy = True
        return f"{self.name_tag.name} is cooking 🍳"

    def __str__(self):                              # POLYMORPHISM: overrides BasePlayer.__str__
        return f"{self.name_tag.display()} | Duty: Cooking in the kitchen"


# ─────────────────────────────────────────────
class Cashier(BasePlayer):                          # INHERITANCE: Cashier IS-A BasePlayer
    def __init__(self, name):
        super().__init__(name, "Cashier")

    def perform_primary_duty(self):                 # POLYMORPHISM: overrides abstract method
        self._is_busy = True
        return f"{self.name_tag.name} is at the register 💰"

    def __str__(self):                              # POLYMORPHISM: overrides BasePlayer.__str__
        return f"{self.name_tag.display()} | Duty: Managing the register"


# ─────────────────────────────────────────────
class Waiter(BasePlayer):                           # INHERITANCE: Waiter IS-A BasePlayer
    def __init__(self, name):
        super().__init__(name, "Waiter")

    def perform_primary_duty(self):                 # POLYMORPHISM: overrides abstract method
        self._is_busy = True
        return f"{self.name_tag.name} is serving tables 🍽️"

    def __str__(self):                              # POLYMORPHISM: overrides BasePlayer.__str__
        return f"{self.name_tag.display()} | Duty: Serving tables"


# ═════════════════════════════════════════════
# CUSTOMER — Parent class
# CHILD CLASS: VipCustomer
# ═════════════════════════════════════════════
class Customer:
    def __init__(self, name, money):
        self.name_tag = NameTag(name, "Customer")   # COMPOSITION: HAS-A NameTag
        self._money   = money                       # ENCAPSULATION: protected attribute

    @property                                       # ENCAPSULATION: getter
    def money(self):
        return self._money

    @money.setter                                   # ENCAPSULATION: setter with validation
    def money(self, amount):
        if amount < 0:
            raise ValueError("Money cannot be negative.")
        self._money = amount

    def introduce(self):                            # uses NameTag.greet()
        return self.name_tag.greet()

    def __str__(self):                              # POLYMORPHISM: overridden in VipCustomer
        return f"{self.name_tag.display()} | Budget: ${self._money}"


# ─────────────────────────────────────────────
class VipCustomer(Customer):                        # INHERITANCE: VipCustomer IS-A Customer
    def __init__(self, name, money):
        super().__init__(name, money)
        self.name_tag.role = "VipCustomer"

    def __str__(self):                              # POLYMORPHISM: overrides Customer.__str__
        return f"{self.name_tag.display()} | Budget: ${self.money} | VIP Perks: Yes"


# ═════════════════════════════════════════════
# TABLE — Standalone class
# Represents a physical table in the restaurant
# ═════════════════════════════════════════════
class Table:
    def __init__(self, table_number, capacity):
        self._table_number = table_number           # ENCAPSULATION: protected attribute
        self._capacity     = capacity               # ENCAPSULATION: protected attribute
        self.seated        = []                     # COMPOSITION: holds Customer objects

    @property                                       # ENCAPSULATION: getter
    def table_number(self):
        return self._table_number

    @property                                       # ENCAPSULATION: getter
    def capacity(self):
        return self._capacity

    @capacity.setter                                # ENCAPSULATION: setter with validation
    def capacity(self, value):
        if value < 1:
            raise ValueError("Capacity must be at least 1.")
        self._capacity = value

    @property                                       # ENCAPSULATION: computed read-only property
    def is_available(self):
        return len(self.seated) < self._capacity

    def seat_customer(self, customer):
        if len(self.seated) >= self._capacity:
            return f"Table {self._table_number} is full."
        self.seated.append(customer)
        return f"Table {self._table_number} ({len(self.seated)}/{self._capacity} seats taken)"

    def remove_customer(self, customer):
        if customer in self.seated:
            self.seated.remove(customer)
            return f"{customer.name_tag.display()} left Table {self._table_number}."
        return f"{customer.name_tag.display()} was not at this table."

    def __str__(self):
        guests = ", ".join(c.name_tag.name for c in self.seated) if self.seated else "empty"
        return (f"Table {self._table_number} | Cap: {self._capacity} | "
                f"Seated: {len(self.seated)} | Guests: {guests}")


# ═════════════════════════════════════════════
# RESTAURANT — Abstract parent for all branches
# CHILD CLASS: Area1Branch
# ═════════════════════════════════════════════
class Restaurant(ABC):                              # ABSTRACTION: abstract base class
    def __init__(self, name):
        self._name  = name                          # ENCAPSULATION: protected attribute
        self.menu   = []                            # COMPOSITION: list of menu items
        self.tables = []                            # COMPOSITION: list of Table objects
        self.staff  = []                            # COMPOSITION: list of BasePlayer objects

    @property                                       # ENCAPSULATION: getter
    def name(self):
        return self._name

    @abstractmethod                                 # ABSTRACTION: must be overridden
    def set_pizza_menu(self):
        pass

    def add_table(self, table):
        self.tables.append(table)

    def add_staff(self, member):
        self.staff.append(member)

    def show_staff(self):
        return "\n".join(s.introduce() for s in self.staff)  # calls greet() via introduce()

    def __str__(self):                              # POLYMORPHISM: overridden in subclasses
        return (f"=== {self._name} ===\n"
                f"Menu  : {', '.join(self.menu)}\n"
                f"Tables: {len(self.tables)}\n"
                f"Staff : {len(self.staff)}")


# ─────────────────────────────────────────────
class Area1Branch(Restaurant):                      # INHERITANCE: Area1Branch IS-A Restaurant
    def __init__(self, name):
        super().__init__(name)

    def set_pizza_menu(self):                       # POLYMORPHISM: overrides abstract method
        self.menu = ["Margherita", "Pepperoni", "Hawaiian",
                     "Veggie", "BBQ Chicken", "Supreme"]


# ═════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════
if __name__ == "__main__":

    # ── Branch ──────────────────────────────
    branch1 = Area1Branch("Area 1 Pizzeria")
    branch1.set_pizza_menu()

    # ── Staff ────────────────────────────────
    branch1.add_staff(Chef("Mario"))
    branch1.add_staff(Cashier("Birdo"))
    branch1.add_staff(Waiter("Toad"))

    # ── Tables (match TABLES dict in pizzalogic) ──
    # Table 1 = 2 seats, Table 2 = 4 seats, Table 3 = 5 seats
    branch1.add_table(Table(1, 2))
    branch1.add_table(Table(2, 4))
    branch1.add_table(Table(3, 5))

    # ── Show staff greetings (demonstrates greet() + introduce()) ──
    print(branch1)
    print()
    print(branch1.show_staff())
    print()

    # ── Clock ────────────────────────────────
    clock = RestaurantClock(start_hour=7)

    # ── Start game ───────────────────────────
    run_game(branches=[branch1], clock=clock)