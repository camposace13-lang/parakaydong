import random
from abc import ABC, abstractmethod


# ═════════════════════════════════════════════
# PARENT CLASS (via composition, not inheritance)
# Used by: BasePlayer, Customer
# ═════════════════════════════════════════════
class NameTag:                                      # COMPOSITION: shared by all classes
    def __init__(self, name, role):
        self._name = name                           # ENCAPSULATION: protected attribute
        self._role = role                           # ENCAPSULATION: protected attribute

    @property                                       # ENCAPSULATION: getter for _name
    def name(self):
        return self._name

    @property                                       # ENCAPSULATION: getter for _role
    def role(self):
        return self._role

    @role.setter                                    # ENCAPSULATION: setter for _role
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
# PARENT CLASS (Abstract)
# ABSTRACTION: forces all staff subclasses to
# implement perform_primary_duty()
# CHILD CLASSES: Chef, Cashier, Waiter
# ═════════════════════════════════════════════
class BasePlayer(ABC):                              # ABSTRACTION: ABC = Abstract Base Class
    def __init__(self, name, role):
        self.name_tag = NameTag(name, role)         # COMPOSITION: HAS-A NameTag
        self._is_busy = False                       # ENCAPSULATION: protected attribute

    @property                                       # ENCAPSULATION: getter for _is_busy
    def is_busy(self):
        return self._is_busy

    @abstractmethod                                 # ABSTRACTION: must be overridden by child classes
    def perform_primary_duty(self):
        pass

    def introduce(self):
        return self.name_tag.greet()

    def __str__(self):                              # POLYMORPHISM: overridden in each child class
        status = "busy" if self._is_busy else "available"
        return f"{self.name_tag.display()} ({status})"


# ─────────────────────────────────────────────
# CHILD CLASS (inherits from BasePlayer)
# INHERITANCE: Chef IS-A BasePlayer
# ─────────────────────────────────────────────
class Chef(BasePlayer):                             # INHERITANCE: extends BasePlayer
    def __init__(self, name):
        super().__init__(name, "Chef")              # INHERITANCE: calls BasePlayer.__init__

    def perform_primary_duty(self):                 # POLYMORPHISM: overrides BasePlayer's abstract method
        self._is_busy = True
        return f"{self.name_tag.name} is cooking"

    def _str__(self):                              # POLYMORPHISM: overrides BasePlayer.__str_
        return f"{self.name_tag.display()} | Duty: Cooking in the kitchen"


# ─────────────────────────────────────────────
# CHILD CLASS (inherits from BasePlayer)
# INHERITANCE: Cashier IS-A BasePlayer
# ─────────────────────────────────────────────
class Cashier(BasePlayer):                          # INHERITANCE: extends BasePlayer
    def __init__(self, name):
        super().__init__(name, "Cashier")           # INHERITANCE: calls BasePlayer.__init__

    def perform_primary_duty(self):                 # POLYMORPHISM: overrides BasePlayer's abstract method
        self._is_busy = True
        return f"{self.name_tag.name} is at the register"

    def _str__(self):                              # POLYMORPHISM: overrides BasePlayer.__str_
        return f"{self.name_tag.display()} | Duty: Managing the register"


# ─────────────────────────────────────────────
# CHILD CLASS (inherits from BasePlayer)
# INHERITANCE: Waiter IS-A BasePlayer
# ─────────────────────────────────────────────
class Waiter(BasePlayer):                           # INHERITANCE: extends BasePlayer
    def __init__(self, name):
        super().__init__(name, "Waiter")            # INHERITANCE: calls BasePlayer.__init__

    def perform_primary_duty(self):                 # POLYMORPHISM: overrides BasePlayer's abstract method
        self._is_busy = True
        return f"{self.name_tag.name} is serving"

    def _str__(self):                              # POLYMORPHISM: overrides BasePlayer.__str_
        return f"{self.name_tag.display()} | Duty: Serving tables"


# ═════════════════════════════════════════════
# PARENT CLASS
# CHILD CLASS: VipCustomer
# ═════════════════════════════════════════════
class Customer:                                     # PARENT CLASS for VipCustomer
    def __init__(self, name, money):
        self.name_tag = NameTag(name, "Customer")   # COMPOSITION: HAS-A NameTag
        self._money = money                         # ENCAPSULATION: protected attribute

    @property                                       # ENCAPSULATION: getter for _money
    def money(self):
        return self._money

    @money.setter                                   # ENCAPSULATION: setter with validation
    def money(self, amount):
        if amount < 0:
            raise ValueError("Money cannot be negative.")
        self._money = amount

    def introduce(self):
        return self.name_tag.greet()

    def __str__(self):                              # POLYMORPHISM: overridden in VipCustomer
        return f"{self.name_tag.display()} | Budget: ${self._money}"


# ─────────────────────────────────────────────
# CHILD CLASS (inherits from Customer)
# INHERITANCE: VipCustomer IS-A Customer
# ─────────────────────────────────────────────
class VipCustomer(Customer):                        # INHERITANCE: extends Customer
    def __init__(self, name, money):
        super().__init__(name, money)               # INHERITANCE: calls Customer.__init__
        self.name_tag.role = "VipCustomer"          # overrides role from parent

    def _str__(self):                              # POLYMORPHISM: overrides Customer.__str_
        return f"{self.name_tag.display()} | Budget: ${self.money} | VIP Perks: Yes"


# ═════════════════════════════════════════════
# STANDALONE CLASS
# COMPOSITION: HAS-A Waiter, HAS-A list of Customers
# ═════════════════════════════════════════════
class Table:                                        # COMPOSITION: holds Waiter + Customer objects
    def __init__(self, table_number, capacity):
        self._table_number = table_number           # ENCAPSULATION: protected attribute
        self._capacity = capacity                   # ENCAPSULATION: protected attribute
        self.seated = []                            # COMPOSITION: HAS-A list of Customers
        self.assigned_waiter = None                 # COMPOSITION: HAS-A Waiter

    @property                                       # ENCAPSULATION: getter for _table_number
    def table_number(self):
        return self._table_number

    @property                                       # ENCAPSULATION: getter for _capacity
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

    @property                                       # ENCAPSULATION: computed read-only property
    def is_empty(self):
        return len(self.seated) == 0

    def seat_customer(self, customer):
        if len(self.seated) >= self._capacity:
            return f"Table {self._table_number} is full ({self._capacity}/{self._capacity} seats taken)."
        self.seated.append(customer)
        return (f"{customer.name_tag.display()} seated at Table {self._table_number} "
                f"({len(self.seated)}/{self._capacity} seats taken).")

    def remove_customer(self, customer):
        if customer in self.seated:
            self.seated.remove(customer)
            return f"{customer.name_tag.display()} left Table {self._table_number}."
        return f"{customer.name_tag.display()} was not at this table."

    def assign_waiter(self, waiter):
        self.assigned_waiter = waiter               # COMPOSITION: Table HAS-A Waiter
        waiter._is_busy = True
        return f"{waiter.name_tag.display()} is now serving Table {self._table_number}."

    def status(self):
        waiter_info = self.assigned_waiter.name_tag.name if self.assigned_waiter else "None"
        guests = ", ".join(c.name_tag.name for c in self.seated) if self.seated else "empty"
        return (f"Table {self._table_number} | Capacity: {self._capacity} | "
                f"Seated: {len(self.seated)} | Guests: {guests} | Waiter: {waiter_info}")

    def __str__(self):                              # POLYMORPHISM: custom string output
        return self.status()


# ═════════════════════════════════════════════
# PARENT CLASS (Abstract)
# ABSTRACTION: forces all branch subclasses to
# implement set_pizza_menu()
# CHILD CLASSES: Area1Branch, AreaFBranch, AreaGBranch
# ═════════════════════════════════════════════
class Restaurant(ABC):                              # ABSTRACTION: ABC = Abstract Base Class
    def __init__(self, name):
        self._name = name                           # ENCAPSULATION: protected attribute
        self.menu = []                              # COMPOSITION: HAS-A list of menu items
        self.tables = []                            # COMPOSITION: HAS-A list of Tables
        self.staff = []                             # COMPOSITION: HAS-A list of staff

    @property                                       # ENCAPSULATION: getter for _name
    def name(self):
        return self._name

    @abstractmethod                                 # ABSTRACTION: must be overridden by branch subclasses
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
        items = ", ".join(self.menu)
        return f"{self._name} Menu: {items}"

    def show_tables(self):
        if not self.tables:
            return f"{self._name} has no tables."
        return "\n".join(str(t) for t in self.tables)

    def show_staff(self):
        if not self.staff:
            return f"{self._name} has no staff."
        return "\n".join(str(s) for s in self.staff)

    def __str__(self):                              # POLYMORPHISM: overridden in each branch
        return (f"=== {self._name} ===\n"
                f"Menu items : {len(self.menu)}\n"
                f"Tables     : {len(self.tables)}\n"
                f"Staff      : {len(self.staff)}")


# ─────────────────────────────────────────────
# CHILD CLASS (inherits from Restaurant)
# INHERITANCE: Area1Branch IS-A Restaurant
# ─────────────────────────────────────────────
class Area1Branch(Restaurant):                      # INHERITANCE: extends Restaurant
    def __init__(self, name):
        super().__init__(name)                      # INHERITANCE: calls Restaurant.__init__

    def set_pizza_menu(self):                       # POLYMORPHISM: overrides Restaurant's abstract method
        self.menu = ["Margherita", "Pepperoni", "Hawaiian", "Veggie"]


# ─────────────────────────────────────────────
# CHILD CLASS (inherits from Restaurant)
# INHERITANCE: AreaFBranch IS-A Restaurant
# ─────────────────────────────────────────────
class AreaFBranch(Restaurant):                      # INHERITANCE: extends Restaurant
    def __init__(self, name):
        super().__init__(name)                      # INHERITANCE: calls Restaurant.__init__

    def set_pizza_menu(self):                       # POLYMORPHISM: overrides Restaurant's abstract method
        self.menu = ["Margherita", "Pepperoni", "Hawaiian", "BBQ Chicken"]


# ─────────────────────────────────────────────
# CHILD CLASS (inherits from Restaurant)
# INHERITANCE: AreaGBranch IS-A Restaurant
# ─────────────────────────────────────────────
class AreaGBranch(Restaurant):                      # INHERITANCE: extends Restaurant
    def __init__(self, name):
        super().__init__(name)                      # INHERITANCE: calls Restaurant.__init__

    def set_pizza_menu(self):                       # POLYMORPHISM: overrides Restaurant's abstract method
        self.menu = ["Margherita", "Pepperoni", "Hawaiian", "Supreme"]


# ─────────────────────────────────────────────
# Test
# ─────────────────────────────────────────────

# Create branch instances (CHILD CLASS objects)
branch1 = Area1Branch("Area 1 Pizzeria")
branchF = AreaFBranch("Area F Pizzeria")
branchG = AreaGBranch("Area G Pizzeria")

# Set menus (POLYMORPHISM: same call, different menu)
branch1.set_pizza_menu()
branchF.set_pizza_menu()
branchG.set_pizza_menu()

# Create staff instances (CHILD CLASS objects of BasePlayer)
chef    = Chef("Mario")
cashier = Cashier("Birdo")
waiter  = Waiter("Toad")

# Create table instances (COMPOSITION objects)
table1 = Table(1, 2)
table2 = Table(2, 4)

# Create customer instances
customer  = Customer("Luigi", 30)
vip       = VipCustomer("Peach", 100)       # CHILD CLASS object of Customer
customer2 = Customer("Yoshi", 25)

# Add staff and tables to branch1 (COMPOSITION)
branch1.add_staff(chef)
branch1.add_staff(cashier)
branch1.add_staff(waiter)
branch1.add_table(table1)
branch1.add_table(table2)

# POLYMORPHISM: same call, different menu per branch
print("=== Branch Menus (Polymorphism) ===")
branches = [branch1, branchF, branchG]
for branch in branches:
    print(branch.show_menu())

# POLYMORPHISM: _str_ behaves differently per branch
print("\n=== Branch Summaries ===")
for branch in branches:
    print(branch)

# ABSTRACTION + POLYMORPHISM: same method, different behavior per staff
print("\n=== Staff Duties ===")
for member in branch1.staff:
    print(member.perform_primary_duty())

# COMPOSITION: table seating
print("\n=== Table Seating ===")
print(table1.assign_waiter(waiter))
print(table1.seat_customer(customer))
print(table1.seat_customer(vip))
print(table1.seat_customer(customer2))
print(table2.seat_customer(customer2))

print("\n=== Table Status ===")
print(branch1.show_tables())