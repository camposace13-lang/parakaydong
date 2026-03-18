# ═══════════════════════════════════════════════════════════
# CLASSES.PY — All OOP classes for the Pizza Restaurant Simulator
# Imported by lastday.py (main/logic module)
# Principles: Encapsulation, Inheritance, Polymorphism, Abstraction
# ═══════════════════════════════════════════════════════════

import os, sys, time, random
from abc import ABC, abstractmethod


# ───────────────────────────────────────────────────────────
# TERMINAL UTILITIES
# Used by class methods — kept here to avoid circular imports
# ───────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def divider(char="═", width=55):
    print(f"  {char * width}")

def getch():
    """Single keypress — no Enter needed."""
    try:
        import tty, termios
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        return input("  > ").strip()[:1].lower()


# ═══════════════════════════════════════════════════════════
# NAMETAG — Composition class
# Embedded inside BasePlayer and Customer (HAS-A relationship)
# ═══════════════════════════════════════════════════════════

class NameTag:
    def __init__(self, name, role):
        self._name = name                           # ENCAPSULATION: protected attribute
        self._role = role                           # ENCAPSULATION: protected attribute

    @property
    def name(self):                                 # ENCAPSULATION: getter
        return self._name

    @property
    def role(self):                                 # ENCAPSULATION: getter
        return self._role

    @role.setter
    def role(self, value):                          # ENCAPSULATION: controlled setter
        self._role = value

    def display(self):
        return f"[{self._role}] {self._name}"

    def greet(self):
        # POLYMORPHISM: same method, different output depending on role
        greetings = {
            "Chef":        "Let's cook!",
            "Cashier":     "Welcome, what can I get you?",
            "Waiter":      "Table for how many?",
            "Customer":    "Hi, I'd like to order.",
            "VipCustomer": "Hello, I have a reservation.",
        }
        return f"{self.display()}: {greetings.get(self._role, 'Hello!')}"


# ═══════════════════════════════════════════════════════════
# BASEPLAYER — Abstract parent for all staff
# ABSTRACTION: cannot be instantiated directly
# INHERITANCE: Chef, Cashier, Waiter all extend this
# _calc_points defined ONCE here — inherited by all (no duplication)
# ═══════════════════════════════════════════════════════════

class BasePlayer(ABC):
    def __init__(self, name, role):
        self.name_tag = NameTag(name, role)         # COMPOSITION: HAS-A NameTag
        self._is_busy = False                       # ENCAPSULATION: protected attribute

    @property
    def is_busy(self):                              # ENCAPSULATION: getter
        return self._is_busy

    @abstractmethod                                 # ABSTRACTION: subclass MUST implement
    def perform_primary_duty(self):
        pass

    def introduce(self):
        return self.name_tag.greet()

    def _calc_points(self, elapsed, base=5, max_bonus=5, limit=6):
        """
        INHERITANCE: defined once in BasePlayer, inherited by Chef, Waiter, Cashier.
        Speed-based scoring: under 1s = full bonus, ~3s = half, 6s+ = no bonus.
        No duplication — all staff reuse this single method.
        """
        ratio = 1.0 if elapsed <= 1 else max(0.0, 1 - ((elapsed - 1) / (limit - 1)))
        return base + int(max_bonus * ratio)

    def __str__(self):                              # POLYMORPHISM: overridden in every subclass
        status = "busy" if self._is_busy else "available"
        return f"{self.name_tag.display()} ({status})"


# ═══════════════════════════════════════════════════════════
# CHEF — Child class of BasePlayer
# Cooks orders by selecting the correct pizza
# Inherits: name_tag, _is_busy, introduce(), _calc_points()
# ═══════════════════════════════════════════════════════════

class Chef(BasePlayer):                             # INHERITANCE: Chef IS-A BasePlayer
    def __init__(self, name):
        super().__init__(name, "Chef")              # reuses BasePlayer.__init__
        self._correct_cooks   = 0                  # ENCAPSULATION: protected
        self._incorrect_cooks = 0                  # ENCAPSULATION: protected

    @property
    def correct_cooks(self):
        return self._correct_cooks

    @property
    def incorrect_cooks(self):
        return self._incorrect_cooks

    def perform_primary_duty(self):                 # POLYMORPHISM: overrides abstract method
        self._is_busy = True
        return f"{self.name_tag.name} is cooking 🍳"

    def cook(self, order, all_pizzas, num_choices):
        """Chef picks the correct pizza from choices."""
        wrong   = [p for p in all_pizzas if p != order.pizza]
        random.shuffle(wrong)
        options = wrong[:num_choices - 1] + [order.pizza]
        random.shuffle(options)
        correct_idx = options.index(order.pizza)

        print(f"\n  🍳  Order in! Cook: {order.pizza} x{order.quantity}\n")
        divider("─")
        for i, opt in enumerate(options):
            print(f"  [{i+1}]  {opt}")
        divider("─")
        print(f"\n  Press the correct number.")

        start = time.time()
        while True:
            k = getch()
            if k == "q":
                return "QUIT", 0
            try:
                chosen = int(k) - 1
            except ValueError:
                continue
            if chosen < 0 or chosen >= len(options):
                continue

            elapsed = time.time() - start
            if chosen == correct_idx:
                self._correct_cooks += 1
                pts = self._calc_points(elapsed)    # INHERITANCE: from BasePlayer
                print(f"\n  ✅  Correct! {order.pizza} x{order.quantity} "
                      f"is cooking! (+{pts} pts)\n")
                time.sleep(1.5)
                return "OK", pts
            else:
                self._incorrect_cooks += 1
                print(f"\n  ❌  Wrong pizza! The group LEFT! (-15 pts)\n")
                time.sleep(2)
                return "WRONG", -15

    def __str__(self):                              # POLYMORPHISM: overrides BasePlayer.__str__
        return (f"{self.name_tag.display()} | Duty: Cooking | "
                f"Correct: {self._correct_cooks} | "
                f"Mistakes: {self._incorrect_cooks}")


# ═══════════════════════════════════════════════════════════
# WAITER — Child class of BasePlayer
# Seats groups and serves food
# Inherits: name_tag, _is_busy, introduce(), _calc_points()
# ═══════════════════════════════════════════════════════════

class Waiter(BasePlayer):                           # INHERITANCE: Waiter IS-A BasePlayer
    def __init__(self, name):
        super().__init__(name, "Waiter")            # reuses BasePlayer.__init__
        self._groups_seated = 0                     # ENCAPSULATION: protected
        self._groups_served = 0                     # ENCAPSULATION: protected

    @property
    def groups_seated(self):
        return self._groups_seated

    @property
    def groups_served(self):
        return self._groups_served

    def perform_primary_duty(self):                 # POLYMORPHISM: overrides abstract method
        self._is_busy = True
        return f"{self.name_tag.name} is serving tables 🍽️"

    def seat_group(self, group, tables):
        """Waiter picks a table and seats the group."""
        title = "Ma'am" if group.is_vip else "Sir"
        print(f"  🚶 Group arrived! Leader: {group.leader_name} "
              f"({group.size} person{'s' if group.size > 1 else ''})")
        print(f"\n  [{self.name_tag.name}]: Welcome to Area 1 Pizzeria, "
              f"{title} {group.leader_name}!\n")
        print(f"  They want: {group.order.pizza} x{group.order.quantity}\n")

        print(f"  🪑  Tables:")
        valid_keys = []
        for t in tables:
            if t.is_occupied:
                marker = "❌ occupied"
            elif t.capacity < group.size:
                marker = "❌ too small"
            else:
                marker = "✅ available"
                valid_keys.append(str(t.table_number))
            print(f"     [{t.table_number}] Table {t.table_number} "
                  f"(cap {t.capacity}) — {marker}")
        print()

        if not valid_keys:
            print(f"  ⚠️  No table fits this group of {group.size}! Waiting...\n")
            print(f"  Press any key to retry or [Q] to quit.")
            k = getch()
            return ("QUIT", None, 0) if k == "q" else ("WAIT", None, 0)

        print(f"  Press [{'/'.join(valid_keys)}] to seat them.")
        start = time.time()

        while True:
            k = getch()
            if k == "q":
                return "QUIT", None, 0
            if k in [str(t.table_number) for t in tables] and k not in valid_keys:
                print(f"\n  ❌  Wrong table! Can't fit or occupied. (-15 pts)\n")
                time.sleep(1.5)
                return "WRONG_TABLE", None, -15
            if k not in valid_keys:
                print(f"\n  ⚠️  Invalid key. Try again.\n")
                time.sleep(1)
                continue

            chosen_table = next(t for t in tables if str(t.table_number) == k)
            chosen_table.seat(group)
            self._groups_seated += 1
            elapsed = time.time() - start
            pts = self._calc_points(elapsed)        # INHERITANCE: from BasePlayer
            print(f"\n  ✅  Group seated at Table {chosen_table.table_number}! "
                  f"(+{pts} pts)\n")
            time.sleep(1)
            return "OK", chosen_table, pts

    def serve_food(self, group):
        """Waiter delivers cooked food to the table."""
        print(f"  🍕  {group.order.pizza} x{group.order.quantity} is ready!")
        print(f"  Press [S] to serve Table {group.table.table_number}.")
        start = time.time()
        while True:
            k = getch()
            if k == "s":
                self._groups_served += 1
                elapsed = time.time() - start
                pts = self._calc_points(elapsed)    # INHERITANCE: from BasePlayer
                print(f"\n  ✅  Served to Table {group.table.table_number}! "
                      f"(+{pts} pts)\n")
                time.sleep(1.5)
                return "OK", pts
            elif k == "q":
                return "QUIT", 0

    def __str__(self):                              # POLYMORPHISM: overrides BasePlayer.__str__
        return (f"{self.name_tag.display()} | Duty: Serving | "
                f"Seated: {self._groups_seated} | "
                f"Served: {self._groups_served}")


# ═══════════════════════════════════════════════════════════
# CASHIER — Child class of BasePlayer
# Collects payment and gives correct change
# Inherits: name_tag, _is_busy, introduce(), _calc_points()
# ═══════════════════════════════════════════════════════════

class Cashier(BasePlayer):                          # INHERITANCE: Cashier IS-A BasePlayer
    def __init__(self, name):
        super().__init__(name, "Cashier")           # reuses BasePlayer.__init__
        self._total_collected = 0                   # ENCAPSULATION: protected
        self._correct_change  = 0                   # ENCAPSULATION: protected
        self._wrong_change    = 0                   # ENCAPSULATION: protected

    @property
    def total_collected(self):
        return self._total_collected

    @property
    def correct_change(self):
        return self._correct_change

    @property
    def wrong_change(self):
        return self._wrong_change

    def perform_primary_duty(self):                 # POLYMORPHISM: overrides abstract method
        self._is_busy = True
        return f"{self.name_tag.name} is at the register 💰"

    def collect_payment(self, group):
        """Collects bill and asks cashier to select correct change."""
        bill   = group.order.total_price
        paid   = group.order.amount_paid
        change = group.order.change

        # Step A: collect
        print(f"  💵  Table {group.table.table_number} finished eating!")
        print(f"     {group.order.pizza} x{group.order.quantity} "
              f"@ ${group.order.unit_price} each")
        print(f"     Total bill : ${bill}")
        print(f"     Paid       : ${paid}")
        print(f"\n  Press [G] to collect payment.")

        while True:
            k = getch()
            if k == "g":
                self._total_collected += paid
                print(f"\n  ✅  ${paid} collected!")
                print(f"  🧾  Bill was: ${bill}\n")
                time.sleep(1.5)
                break
            elif k == "q":
                return "QUIT", 0

        # Step B: give change — cashier figures it out (no hint shown)
        print(f"  💵  Bill: ${bill}  |  Paid: ${paid}\n")
        print(f"  Pick the correct change to give back:\n")

        start = time.time()
        if change == 0:
            options     = ["No change — $0"]
            correct_idx = 0
        else:
            wrong = set()
            attempts = 0
            while len(wrong) < 2 and attempts < 50:
                attempts += 1
                fake = change + random.choice([-3, -2, -1, 1, 2, 3, 5])
                if fake >= 0 and fake != change:
                    wrong.add(fake)
            options = [f"${x}" for x in list(wrong)] + [f"${change}"]
            random.shuffle(options)
            correct_idx = options.index(f"${change}")

        divider("─")
        for i, opt in enumerate(options):
            print(f"  [{i+1}]  {opt}")
        divider("─")
        print(f"\n  Press the number of the correct change.")

        while True:
            k = getch()
            if k == "q":
                return "QUIT", 0
            try:
                chosen = int(k) - 1
            except ValueError:
                continue
            if chosen < 0 or chosen >= len(options):
                continue

            elapsed = time.time() - start
            if chosen == correct_idx:
                self._correct_change += 1
                pts = self._calc_points(elapsed)    # INHERITANCE: from BasePlayer
                tip = group.tip()
                print(f"\n  ✅  Correct change! (+{pts} pts)")
                print(f"  💰  {group.leader_name} left a tip: +{tip} pts\n")
                time.sleep(1.5)
                return "OK", pts + tip
            else:
                self._wrong_change += 1
                print(f"\n  ❌  Wrong change! Correct was "
                      f"{options[correct_idx]}. (-15 pts)\n")
                time.sleep(1.5)
                return "WRONG", -15

    def __str__(self):                              # POLYMORPHISM: overrides BasePlayer.__str__
        return (f"{self.name_tag.display()} | Duty: Register | "
                f"Collected: ${self._total_collected} | "
                f"Correct: {self._correct_change} | "
                f"Wrong: {self._wrong_change}")


# ═══════════════════════════════════════════════════════════
# ORDER — Full details of a group's food order
# ENCAPSULATION: all price/payment data protected with getters
# ═══════════════════════════════════════════════════════════

class Order:
    PIZZA_PRICES = {
        "Margherita": 8,  "Pepperoni": 10, "Hawaiian": 9,
        "Veggie": 7,      "BBQ Chicken": 11, "Supreme": 12,
    }

    def __init__(self, pizza, quantity):
        self._pizza      = pizza                    # ENCAPSULATION: protected
        self._quantity   = quantity                 # ENCAPSULATION: protected
        self._unit_price = self.PIZZA_PRICES.get(pizza, 10)
        self._total      = self._unit_price * quantity
        self._paid       = self._total + random.choice([0, 1, 2, 5, 10])

    @property
    def pizza(self):
        return self._pizza

    @property
    def quantity(self):
        return self._quantity

    @property
    def unit_price(self):
        return self._unit_price

    @property
    def total_price(self):
        return self._total

    @property
    def amount_paid(self):
        return self._paid

    @property
    def change(self):
        return self._paid - self._total

    def __str__(self):
        return (f"{self._pizza} x{self._quantity} | "
                f"${self._unit_price} each | "
                f"Total: ${self._total} | Paid: ${self._paid}")


# ═══════════════════════════════════════════════════════════
# CUSTOMER — Parent class
# CHILD CLASS: VipCustomer
# tip_amount() is POLYMORPHIC — different per customer type
# ═══════════════════════════════════════════════════════════

class Customer:
    NAMES = ["Luigi","Yoshi","Koopa","Shy Guy","Toad Jr.",
             "Boo","Birdo","Lakitu","Bullet Bill","Bob-omb"]

    def __init__(self, name, money):
        self.name_tag = NameTag(name, "Customer")   # COMPOSITION: HAS-A NameTag
        self._money   = money                       # ENCAPSULATION: protected

    @property
    def money(self):                                # ENCAPSULATION: getter
        return self._money

    @money.setter
    def money(self, amount):                        # ENCAPSULATION: setter + validation
        if amount < 0:
            raise ValueError("Money cannot be negative.")
        self._money = amount

    def introduce(self):
        return self.name_tag.greet()

    def tip_amount(self):                           # POLYMORPHISM: overridden in VipCustomer
        return random.randint(1, 5)

    def __str__(self):                              # POLYMORPHISM: overridden in VipCustomer
        return f"{self.name_tag.display()} | Budget: ${self._money}"


# ───────────────────────────────────────────────────────────
class VipCustomer(Customer):                        # INHERITANCE: VipCustomer IS-A Customer
    NAMES = ["Peach", "Daisy", "Rosalina", "Pauline"]

    def __init__(self, name, money):
        super().__init__(name, money)               # reuses Customer.__init__
        self.name_tag.role = "VipCustomer"

    def tip_amount(self):                           # POLYMORPHISM: VIPs tip 1-10 vs 1-5
        return random.randint(1, 10)

    def __str__(self):                              # POLYMORPHISM: adds VIP Perks line
        return (f"{self.name_tag.display()} | "
                f"Budget: ${self.money} | VIP Perks: Yes")


# ═══════════════════════════════════════════════════════════
# GROUP — A group of customers dining together
# COMPOSITION: HAS-A Customer (leader), HAS-A Order, HAS-A Table
# ═══════════════════════════════════════════════════════════

class Group:
    def __init__(self, leader, size, order):
        self._leader = leader                       # COMPOSITION: HAS-A Customer
        self._size   = size                         # ENCAPSULATION: protected
        self._order  = order                        # COMPOSITION: HAS-A Order
        self._table  = None                         # COMPOSITION: HAS-A Table (set on seating)

    @property
    def leader_name(self):
        return self._leader.name_tag.name

    @property
    def is_vip(self):
        return isinstance(self._leader, VipCustomer)

    @property
    def size(self):
        return self._size

    @property
    def order(self):
        return self._order

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, t):                             # ENCAPSULATION: controlled setter
        self._table = t

    def tip(self):
        # POLYMORPHISM: returns 1-5 for Customer, 1-10 for VipCustomer
        return self._leader.tip_amount()

    def __str__(self):
        return (f"Group of {self._size} | "
                f"Leader: {self.leader_name} | "
                f"Order: {self._order}")


# ═══════════════════════════════════════════════════════════
# TABLE — A physical dining table
# ENCAPSULATION: capacity validated, group access controlled
# ═══════════════════════════════════════════════════════════

class Table:
    def __init__(self, table_number, capacity):
        self._table_number  = table_number          # ENCAPSULATION: protected
        self._capacity      = capacity              # ENCAPSULATION: protected
        self._current_group = None                  # COMPOSITION: HAS-A Group when occupied

    @property
    def table_number(self):
        return self._table_number

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value):                      # ENCAPSULATION: validates input
        if value < 1:
            raise ValueError("Capacity must be at least 1.")
        self._capacity = value

    @property
    def is_occupied(self):
        return self._current_group is not None

    @property
    def is_available(self):
        return self._current_group is None

    def seat(self, group):
        """Seat a group and link the table back to the group."""
        self._current_group = group
        group.table = self

    def clear(self):
        """Free the table when the group leaves."""
        self._current_group = None

    def __str__(self):
        status = (f"occupied — group of {self._current_group.size}"
                  if self.is_occupied else "empty")
        return f"Table {self._table_number} | Cap: {self._capacity} | {status}"


# ═══════════════════════════════════════════════════════════
# RESTAURANTCLOCK — Tracks in-game time
# ENCAPSULATION: all time data protected
# ═══════════════════════════════════════════════════════════

class RestaurantClock:
    def __init__(self, start_hour=7):
        self._dilation   = 360                      # ENCAPSULATION: protected
        self._start_real = time.time()              # ENCAPSULATION: protected
        self._offset     = start_hour * 3600        # ENCAPSULATION: protected

    def get_game_time(self):
        elapsed = time.time() - self._start_real
        total   = int((elapsed * self._dilation + self._offset) // 60)
        return (total // 60) % 24, total % 60

    def get_phase(self, hour):
        if 5  <= hour < 12: return "MORNING 🌅"
        if 12 <= hour < 17: return "AFTERNOON ☀️"
        if 17 <= hour < 20: return "EVENING 🌆"
        return "NIGHT 🌙"

    def time_str(self):
        h, m = self.get_game_time()
        return f"{h:02d}:{m:02d}"


# ═══════════════════════════════════════════════════════════
# RESTAURANT — Abstract parent for all branches
# ABSTRACTION: cannot be instantiated — forces subclasses to
#   implement set_pizza_menu() and run_shift()
# ENCAPSULATION: _set_menu() protects how menu is assigned
# ═══════════════════════════════════════════════════════════

class Restaurant(ABC):                              # ABSTRACTION
    def __init__(self, name):
        self._name   = name                         # ENCAPSULATION: protected
        self._menu   = []                           # ENCAPSULATION: protected
        self._tables = []                           # COMPOSITION: HAS-A list of Tables
        self._staff  = []                           # COMPOSITION: HAS-A list of BasePlayer
        self._clock  = None                         # COMPOSITION: HAS-A RestaurantClock

    @property
    def name(self):
        return self._name

    @property
    def menu(self):
        return list(self._menu)                     # returns copy — protects internal list

    def _set_menu(self, items):
        """
        ENCAPSULATION: protected method — only this class and subclasses
        can assign the menu. Validates that items is a non-empty list.
        """
        if not items or not isinstance(items, list):
            raise ValueError("Menu must be a non-empty list.")
        self._menu = items

    @abstractmethod                                 # ABSTRACTION: subclass MUST implement
    def set_pizza_menu(self):
        pass

    def set_clock(self, clock):
        self._clock = clock

    def add_table(self, table):
        self._tables.append(table)

    def add_staff(self, member):
        self._staff.append(member)

    def get_staff_by_type(self, staff_type):
        """Return first staff member of the given type."""
        return next((s for s in self._staff
                     if isinstance(s, staff_type)), None)

    def show_staff(self):
        print(f"\n  👥  Staff at {self._name}:")
        for s in self._staff:
            print(f"     {s.introduce()}")
        print()

    def show_tables(self):
        print(f"  🪑  Tables:")
        for t in self._tables:
            print(f"     {t}")
        print()

    @abstractmethod                                 # ABSTRACTION: subclass MUST implement
    def run_shift(self):
        """Each branch runs its own shift loop."""
        pass

    def __str__(self):                              # POLYMORPHISM: overridden in subclasses
        return (f"=== {self._name} ===\n"
                f"Menu  : {', '.join(self._menu)}\n"
                f"Tables: {len(self._tables)}\n"
                f"Staff : {len(self._staff)}")


# ═══════════════════════════════════════════════════════════
# AREA1BRANCH — Child class of Restaurant
# The playable branch — run_shift() is the full game loop
# as a METHOD on this object
# ═══════════════════════════════════════════════════════════

class Area1Branch(Restaurant):                      # INHERITANCE: Area1Branch IS-A Restaurant

    DIFFICULTY = {
        1: {"label": "⭐  EASY",     "choices": 3, "gap": 5},
        2: {"label": "⭐⭐  MEDIUM",  "choices": 4, "gap": 4},
        3: {"label": "⭐⭐⭐  HARD",  "choices": 5, "gap": 3},
    }

    def __init__(self, name):
        super().__init__(name)                      # reuses Restaurant.__init__
        self._score           = 0                  # ENCAPSULATION: protected
        self._served          = 0                  # ENCAPSULATION: protected
        self._day             = 1                  # ENCAPSULATION: protected
        self._total_collected = 0                  # ENCAPSULATION: protected

    @property
    def score(self):
        return self._score

    @property
    def served(self):
        return self._served

    def set_pizza_menu(self):                       # POLYMORPHISM: overrides abstract method
        self._set_menu(["Margherita", "Pepperoni", "Hawaiian",
                        "Veggie", "BBQ Chicken", "Supreme"])

    def _get_diff(self):
        return self.DIFFICULTY[min(self._day, 3)]

    def _make_group(self):
        """Spawn a random customer group with an order."""
        is_vip = random.random() < 0.2
        if is_vip:
            name   = random.choice(VipCustomer.NAMES)
            leader = VipCustomer(name, random.randint(80, 150))
        else:
            name   = random.choice(Customer.NAMES)
            leader = Customer(name, random.randint(15, 50))

        max_cap = max(t.capacity for t in self._tables)
        size    = random.randint(1, max_cap)
        pizza   = random.choice(self._menu)
        order   = Order(pizza, size)
        return Group(leader, size, order)

    def _show_header(self, role_label):
        diff = self._get_diff()
        clear()
        divider()
        print(f"  🍕  {self._name}  |  {self._clock.time_str()}  "
              f"{self._clock.get_phase(self._clock.get_game_time()[0])}")
        print(f"  📅  Day {self._day}  {diff['label']}  |  "
              f"⭐ Score: {self._score}  |  "
              f"👥 Served: {self._served}")
        divider()
        print(f"\n  👤  Current Role: {role_label}\n")

    def _day_summary(self):
        diff = self._get_diff()
        clear()
        divider()
        print(f"  🌙  END OF DAY {self._day} SHIFT  —  {diff['label']}")
        divider("─")
        print(f"  Groups served    : {self._served}")
        print(f"  Money collected  : ${self._total_collected}")
        print(f"  Total score      : {self._score} pts")
        if self._day < 3:
            nd = self.DIFFICULTY[self._day + 1]
            print(f"\n  ⚠️  Tomorrow: {nd['label']}")
            print(f"  Choices: {nd['choices']}  |  Arrival gap: {nd['gap']}s")
        divider()
        print(f"\n  Rest up! Press ENTER to start Day {self._day + 1} shift...")
        input()

    def run_shift(self):                            # POLYMORPHISM: overrides abstract method
        """
        Full game loop — runs as a METHOD on this restaurant object.
        Delegates every action to the staff objects (Waiter, Chef, Cashier).
        This is true OOP: objects doing work by calling each other's methods.
        """
        if self._clock is None:
            raise RuntimeError("Set a clock first: branch.set_clock(clock)")

        waiter  = self.get_staff_by_type(Waiter)
        chef    = self.get_staff_by_type(Chef)
        cashier = self.get_staff_by_type(Cashier)

        if not all([waiter, chef, cashier]):
            print("  ❌  Missing staff! Need a Waiter, Chef, and Cashier.")
            return

        # intro screen
        clear()
        divider()
        print(f"  🍕  {self._name}")
        divider()
        self.show_staff()
        self.show_tables()
        print(f"  🍽️  Waiter  → [1/2/3] pick table")
        print(f"  👨‍🍳  Chef    → [1/2/3] correct pizza (wrong = group leaves)")
        print(f"  💰  Cashier → [G] collect, [1/2/3] correct change")
        print(f"\n  Speed bonus: <1s = full | ~3s = half | 6s+ = none")
        print(f"  Wrong key  : -15 pts | Tip: Regular 1–5 | VIP 1–10")
        print(f"  Day advances every 5 groups served.")
        divider()
        print(f"\n  Press ENTER to start the shift!\n")
        input()

        # main loop
        while True:
            diff = self._get_diff()

            # arrival gap screen
            clear()
            divider()
            print(f"  🍕  {self._name}  |  {self._clock.time_str()}")
            print(f"  📅  Day {self._day}  {diff['label']}  |  "
                  f"⭐ Score: {self._score}  |  "
                  f"👥 Served: {self._served}")
            divider()
            self.show_tables()
            print(f"  ⏳  Next group in {diff['gap']} seconds... "
                  f"(Q to end shift)\n")
            time.sleep(diff["gap"])

            group = self._make_group()

            # STAGE 1: Waiter object seats the group
            self._show_header(f"🍽️  WAITER  —  {waiter.name_tag.name}")
            status, table, pts = waiter.seat_group(group, self._tables)
            if status == "QUIT":  break
            if status == "WAIT":  continue
            if status == "WRONG_TABLE":
                self._score = max(0, self._score + pts)
                continue
            self._score += pts

            # STAGE 2: Chef object cooks the order
            self._show_header(f"👨‍🍳  CHEF  —  {chef.name_tag.name}")
            status, pts = chef.cook(group.order, self._menu, diff["choices"])
            if status == "QUIT":  break
            if status == "WRONG":
                self._score = max(0, self._score + pts)
                table.clear()
                continue
            self._score += pts

            # STAGE 3: Waiter object serves the food
            self._show_header(f"🍽️  WAITER  —  {waiter.name_tag.name}")
            status, pts = waiter.serve_food(group)
            if status == "QUIT":  break
            self._score += pts

            # STAGE 4: Cashier object collects payment
            self._show_header(f"💰  CASHIER  —  {cashier.name_tag.name}")
            status, pts = cashier.collect_payment(group)
            if status == "QUIT":  break
            if pts < 0:
                self._score = max(0, self._score + pts)
            else:
                self._score += pts

            self._total_collected += group.order.amount_paid
            table.clear()
            self._served += 1

            if self._served % 5 == 0:
                self._day_summary()
                self._day += 1

        # shift ended
        self._end_of_shift(waiter, chef, cashier)

    def _end_of_shift(self, waiter, chef, cashier):
        clear()
        divider("▓")
        print(f"  🌙  SHIFT ENDED — Time to clock out!")
        divider("─")
        print(f"  Days worked      : {self._day}")
        print(f"  Groups served    : {self._served}")
        print(f"  Money collected  : ${self._total_collected}")
        print(f"  Final Score      : {self._score} pts")
        divider("─")
        print(f"\n  📊  Staff Performance:")
        print(f"  {waiter}")
        print(f"  {chef}")
        print(f"  {cashier}")
        divider("─")
        sc = self._score
        if   sc >= 500: print(f"  🥇  LEGENDARY STAFF — Unstoppable!")
        elif sc >= 300: print(f"  🥈  STAR CREW — Incredible work!")
        elif sc >= 180: print(f"  🥉  SOLID SHIFT — Well done!")
        elif sc >= 80:  print(f"  🎖️   DECENT SHIFT — Keep it up!")
        else:           print(f"  😅  ROUGH SHIFT — Better luck next time!")
        divider("▓")
        print(f"\n  See you next shift! 👋\n")
