import random
import time
import sys
from abc import ABC, abstractmethod

from pizzaclock import RestaurantClock
from pizzalogic import run_game


# ═════════════════════════════════════════════
# NAMETAG — COMPOSITION class
# Used by BasePlayer and Customer
# ═════════════════════════════════════════════
class NameTag:
    def __init__(self, name, role):
        self._name = name                           # ENCAPSULATION: protected
        self._role = role                           # ENCAPSULATION: protected

    @property
    def name(self):
        return self._name

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value):
        self._role = value

    def display(self):
        return f"[{self._role}] {self._name}"

    def greet(self):
        greetings = {
            "Chef":        "Let's cook!",
            "Cashier":     "Welcome, what can I get you?",
            "Waiter":      "Table for how many?",
            "Customer":    "Hi, I'd like to order",
            "VipCustomer": "Hello, I have a reservation"
        }
        return f"{self.display()}: {greetings.get(self._role, 'Hello')}"


# ═════════════════════════════════════════════
# BASEPLAYER — Abstract parent for all staff
# CHILD CLASSES: Chef, Cashier, Waiter
# ═════════════════════════════════════════════
class BasePlayer(ABC):                              # ABSTRACTION
    def __init__(self, name, role):
        self.name_tag = NameTag(name, role)         # COMPOSITION: HAS-A NameTag
        self._is_busy = False                       # ENCAPSULATION

    @property
    def is_busy(self):
        return self._is_busy

    @abstractmethod                                 # ABSTRACTION: subclasses must implement
    def perform_primary_duty(self):
        pass

    def introduce(self):
        return self.name_tag.greet()

    def __str__(self):
        status = "busy" if self._is_busy else "available"
        return f"{self.name_tag.display()} ({status})"


# ─────────────────────────────────────────────
class Chef(BasePlayer):                             # INHERITANCE
    def __init__(self, name):
        super().__init__(name, "Chef")

    def perform_primary_duty(self):                 # POLYMORPHISM
        self._is_busy = True
        return f"{self.name_tag.name} is cooking 🍳"

    def __str__(self):
        return f"{self.name_tag.display()} | Duty: Cooking in the kitchen"


# ─────────────────────────────────────────────
class Cashier(BasePlayer):                          # INHERITANCE
    def __init__(self, name):
        super().__init__(name, "Cashier")

    def perform_primary_duty(self):                 # POLYMORPHISM
        self._is_busy = True
        return f"{self.name_tag.name} is at the register 💰"

    def __str__(self):
        return f"{self.name_tag.display()} | Duty: Managing the register"


# ─────────────────────────────────────────────
class Waiter(BasePlayer):                           # INHERITANCE
    def __init__(self, name):
        super().__init__(name, "Waiter")

    def perform_primary_duty(self):                 # POLYMORPHISM
        self._is_busy = True
        return f"{self.name_tag.name} is serving tables 🍽️"

    def __str__(self):
        return f"{self.name_tag.display()} | Duty: Serving tables"


# ═════════════════════════════════════════════
# CUSTOMER — Parent class
# CHILD CLASS: VipCustomer
# ═════════════════════════════════════════════
class Customer:
    def __init__(self, name, money):
        self.name_tag = NameTag(name, "Customer")   # COMPOSITION
        self._money = money                         # ENCAPSULATION

    @property
    def money(self):
        return self._money

    @money.setter
    def money(self, amount):
        if amount < 0:
            raise ValueError("Money cannot be negative.")
        self._money = amount

    def introduce(self):
        return self.name_tag.greet()

    def __str__(self):
        return f"{self.name_tag.display()} | Budget: ${self._money}"


# ─────────────────────────────────────────────
class VipCustomer(Customer):                        # INHERITANCE
    def __init__(self, name, money):
        super().__init__(name, money)
        self.name_tag.role = "VipCustomer"

    def __str__(self):
        return f"{self.name_tag.display()} | Budget: ${self.money} | VIP Perks: Yes"


# ═════════════════════════════════════════════
# TABLE — Standalone composition class
# ═════════════════════════════════════════════
class Table:
    def __init__(self, table_number, capacity):
        self._table_number = table_number           # ENCAPSULATION
        self._capacity = capacity                   # ENCAPSULATION
        self.seated = []                            # COMPOSITION: list of Customers
        self.assigned_waiter = None                 # COMPOSITION: HAS-A Waiter

    @property
    def table_number(self):
        return self._table_number

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        if value < 1:
            raise ValueError("Capacity must be at least 1.")
        self._capacity = value

    @property
    def is_available(self):
        return len(self.seated) < self._capacity

    @property
    def is_empty(self):
        return len(self.seated) == 0

    def seat_customer(self, customer):
        if len(self.seated) >= self._capacity:
            return f"Table {self._table_number} is full."
        self.seated.append(customer)
        return (f"Table {self._table_number} "
                f"({len(self.seated)}/{self._capacity} seats taken)")

    def remove_customer(self, customer):
        if customer in self.seated:
            self.seated.remove(customer)
            return f"{customer.name_tag.display()} left Table {self._table_number}."
        return f"{customer.name_tag.display()} was not at this table."

    def assign_waiter(self, waiter):
        self.assigned_waiter = waiter
        waiter._is_busy = True
        return f"{waiter.name_tag.display()} assigned to Table {self._table_number}."

    def status(self):
        waiter_info = self.assigned_waiter.name_tag.name if self.assigned_waiter else "None"
        guests = ", ".join(c.name_tag.name for c in self.seated) if self.seated else "empty"
        return (f"Table {self._table_number} | Capacity: {self._capacity} | "
                f"Seated: {len(self.seated)} | Guests: {guests} | Waiter: {waiter_info}")

    def __str__(self):
        return self.status()


# ═════════════════════════════════════════════
# RESTAURANT — Abstract parent for all branches
# CHILD CLASSES: Area1Branch, AreaFBranch, AreaGBranch
# ═════════════════════════════════════════════
class Restaurant(ABC):                              # ABSTRACTION
    def __init__(self, name):
        self._name = name                           # ENCAPSULATION
        self.menu   = []                            # COMPOSITION: list of menu items
        self.tables = []                            # COMPOSITION: list of Tables
        self.staff  = []                            # COMPOSITION: list of staff

    @property
    def name(self):
        return self._name

    @abstractmethod                                 # ABSTRACTION: must be overridden
    def set_pizza_menu(self):
        pass

    def add_table(self, table):
        self.tables.append(table)
        return f"Table {table.table_number} added to {self._name}."

    def add_staff(self, member):
        self.staff.append(member)
        return f"{member.name_tag.display()} added to {self._name} staff."

    def show_menu(self):
        if not self.menu:
            return f"{self._name} has no menu set."
        return f"{self._name} Menu: {', '.join(self.menu)}"

    def show_tables(self):
        if not self.tables:
            return f"{self._name} has no tables."
        return "\n".join(str(t) for t in self.tables)

    def show_staff(self):
        if not self.staff:
            return f"{self._name} has no staff."
        return "\n".join(str(s) for s in self.staff)

    def __str__(self):
        return (f"=== {self._name} ===\n"
                f"Menu items : {len(self.menu)}\n"
                f"Tables     : {len(self.tables)}\n"
                f"Staff      : {len(self.staff)}")


# ─────────────────────────────────────────────
class Area1Branch(Restaurant):                      # INHERITANCE — 24/7 branch
    def __init__(self, name):
        super().__init__(name)

    def set_pizza_menu(self):                       # POLYMORPHISM
        self.menu = ["Margherita", "Pepperoni", "Hawaiian", "Veggie"]


# ─────────────────────────────────────────────
class AreaFBranch(Restaurant):                      # INHERITANCE — 10am–9pm branch
    def __init__(self, name):
        super().__init__(name)

    def set_pizza_menu(self):                       # POLYMORPHISM
        self.menu = ["Margherita", "Pepperoni", "Hawaiian", "BBQ Chicken"]


# ─────────────────────────────────────────────
class AreaGBranch(Restaurant):                      # INHERITANCE — 10am–9pm branch
    def __init__(self, name):
        super().__init__(name)

    def set_pizza_menu(self):                       # POLYMORPHISM
        self.menu = ["Margherita", "Pepperoni", "Hawaiian", "Supreme"]


# ═════════════════════════════════════════════
# MAIN — Sets up objects and starts the game
# Logic (routing, loop, scheduling) → pizzalogic.py
# Clock                             → pizzaclock.py
# ═════════════════════════════════════════════
if __name__ == "__main__":

    # ── Branches ────────────────────────────
    branch1 = Area1Branch("Area 1 Pizzeria")    # 24/7
    branchF = AreaFBranch("Area F Pizzeria")    # 10am–9pm
    branchG = AreaGBranch("Area G Pizzeria")    # 10am–9pm

    branch1.set_pizza_menu()
    branchF.set_pizza_menu()
    branchG.set_pizza_menu()

    # ── Staff — Area 1 (24/7 needs more staff) ──
    branch1.add_staff(Chef("Mario"))
    branch1.add_staff(Chef("Rosalina"))
    branch1.add_staff(Cashier("Birdo"))
    branch1.add_staff(Waiter("Toad"))
    branch1.add_staff(Waiter("Toadette"))

    # ── Staff — Area F ──────────────────────
    branchF.add_staff(Chef("Wario"))
    branchF.add_staff(Cashier("Waluigi"))
    branchF.add_staff(Waiter("Koopa"))

    # ── Staff — Area G ──────────────────────
    branchG.add_staff(Chef("Bowser"))
    branchG.add_staff(Cashier("Kamek"))
    branchG.add_staff(Waiter("Goomba"))

    # ── Tables ──────────────────────────────
    # Area 1 — 3 tables
    t1a = Table(1, 4); t1b = Table(2, 2); t1c = Table(3, 4)
    branch1.add_table(t1a); branch1.add_table(t1b); branch1.add_table(t1c)
    t1a.assign_waiter(branch1.staff[3])   # Toad
    t1b.assign_waiter(branch1.staff[4])   # Toadette

    # Area F — 2 tables
    tfa = Table(1, 4); tfb = Table(2, 3)
    branchF.add_table(tfa); branchF.add_table(tfb)
    tfa.assign_waiter(branchF.staff[2])   # Koopa

    # Area G — 2 tables
    tga = Table(1, 4); tgb = Table(2, 3)
    branchG.add_table(tga); branchG.add_table(tgb)
    tga.assign_waiter(branchG.staff[2])   # Goomba

    # ── Customers (mix of regular + VIP) ────
    customers = [
        Customer("Luigi", 30),
        Customer("Yoshi", 25),
        Customer("Toad Jr.", 20),
        Customer("Koopa Kid", 15),
        Customer("Shy Guy", 18),
        VipCustomer("Peach", 100),
        VipCustomer("Daisy", 90),
        VipCustomer("Rosalina", 120),
    ]

    # ── Clock starts at 07:00 ───────────────
    clock = RestaurantClock(start_hour=7)

    # ── Hand off to game logic ───────────────
    # All scheduling, routing, and loop logic
    # is handled inside pizzalogic.run_game()
    run_game(
        branches  = [branch1, branchF, branchG],
        customers = customers,
        clock     = clock
    )
