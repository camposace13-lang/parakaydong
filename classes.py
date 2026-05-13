import os, sys, time, random
from abc import ABC, abstractmethod


class TerminalUtils:
    @staticmethod
    def clear():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def divider(char="═", width=55):
        print(f"  {char * width}")

    @staticmethod
    def getch():
        try:
            import tty, termios
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                return sys.stdin.read(1).lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            return input("  > ").strip()[:1].lower()

    @staticmethod
    def print_choices(options):
        TerminalUtils.divider("─")
        for i, opt in enumerate(options):
            print(f"  [{i+1}]  {opt}")
        TerminalUtils.divider("─")
        print(f"\n  Press the number of the correct choice.")

    @staticmethod
    def pick_from_choices(options, correct_idx):
        start = time.time()
        while True:
            k = TerminalUtils.getch()
            if k == "q":
                return "QUIT", None
            try:
                chosen = int(k) - 1
            except ValueError:
                continue
            if 0 <= chosen < len(options):
                return time.time() - start, chosen


class GameSetup:
    @staticmethod
    def get_staff_names():
        print(f"  Enter your staff names:\n")
        names = []
        for role, default in [("Waiter", "Alex"), ("Chef", "Mario"), ("Cashier", "Birdo")]:
            print(f"  {role} name  : ", end="", flush=True)
            names.append(input().strip() or default)
        return names

    @staticmethod
    def create_branch():
        TerminalUtils.clear()
        TerminalUtils.divider()
        print(f"  🍕  PIZZA RESTAURANT SIMULATOR")
        TerminalUtils.divider()
        print()

        waiter_name, chef_name, cashier_name = GameSetup.get_staff_names()
        branch = Area1Branch("Area 1 Pizzeria")
        branch.set_pizza_menu()

        for staff in [Waiter(waiter_name), Chef(chef_name), Cashier(cashier_name)]:
            branch.add_staff(staff)
        for num, cap in [(1, 2), (2, 4), (3, 5)]:
            branch.add_table(Table(num, cap))

        branch.set_clock(RestaurantClock(start_hour=7))
        return branch


class NameTag:
    GREETINGS = {
        "Chef": "Let's cook!", "Cashier": "Welcome, what can I get you?",
        "Waiter": "Table for how many?", "Customer": "Hi, I'd like to order.",
        "VipCustomer": "Hello, I have a reservation.",
    }

    def __init__(self, name, role):
        self._name = name
        self._role = role

    @property
    def name(self): return self._name

    @property
    def role(self): return self._role

    @role.setter
    def role(self, value): self._role = value

    def display(self): return f"[{self._role}] {self._name}"

    def greet(self):
        return f"{self.display()}: {self.GREETINGS.get(self._role, 'Hello!')}"

class BasePlayer(ABC):
    def __init__(self, name, role):
        self.name_tag = NameTag(name, role)
        self._is_busy = False

    @property
    def is_busy(self): return self._is_busy

    def reset_busy(self): self._is_busy = False

    def introduce(self): return self.name_tag.greet()

    @abstractmethod
    def perform_primary_duty(self): pass

    def _calc_points(self, elapsed, base=5, max_bonus=5, limit=6):
        ratio = 1.0 if elapsed <= 1 else max(0.0, 1 - ((elapsed - 1) / (limit - 1)))
        return base + int(max_bonus * ratio)

    def __str__(self):
        return f"{self.name_tag.display()} ({'busy' if self._is_busy else 'available'})"


class Chef(BasePlayer):
    def __init__(self, name):
        super().__init__(name, "Chef")
        self._correct_cooks = self._incorrect_cooks = 0
        self._cook_multiplier = 1.0

    @property
    def correct_cooks(self): return self._correct_cooks

    @property
    def incorrect_cooks(self): return self._incorrect_cooks

    def perform_primary_duty(self):
        self._is_busy = True
        self._cook_multiplier = 1.5
        return f"{self.name_tag.name} is cooking 🍳  [Duty Active: reaction window x{self._cook_multiplier}]"

    def cook(self, order, all_pizzas, num_choices):
        wrong = [p for p in all_pizzas if p != order.pizza]
        random.shuffle(wrong)
        options = wrong[:num_choices - 1] + [order.pizza] 
        random.shuffle(options)
        correct_idx = options.index(order.pizza)

        print(f"\n  🍳  Order in! Cook: {order.pizza} x{order.quantity}\n")
        TerminalUtils.print_choices(options)
        print(f"\n  Press the correct number.")

        result = TerminalUtils.pick_from_choices(options, correct_idx)
        if result[0] == "QUIT":
            return "QUIT", 0

        elapsed, chosen = result
        if chosen == correct_idx:
            self._correct_cooks += 1
            pts = self._calc_points(elapsed * self._cook_multiplier)
            print(f"\n  ✅  Correct! {order.pizza} x{order.quantity} is cooking! (+{pts} pts)\n")
            time.sleep(1.5)
            return "OK", pts
        else:
            self._incorrect_cooks += 1
            print(f"\n  ❌  Wrong pizza! The group LEFT! (-15 pts)\n")
            time.sleep(2)
            return "WRONG", -15

    def __str__(self):
        return (f"{self.name_tag.display()} | Duty: Cooking | "
                f"Correct: {self._correct_cooks} | Mistakes: {self._incorrect_cooks}")


class Waiter(BasePlayer):
    def __init__(self, name):
        super().__init__(name, "Waiter")
        self._groups_seated = self._groups_served = 0
        self._seat_bonus = 0

    @property
    def groups_seated(self): return self._groups_seated

    @property
    def groups_served(self): return self._groups_served

    def perform_primary_duty(self):
        self._is_busy = True
        self._seat_bonus = 3
        return f"{self.name_tag.name} is serving tables 🍽️  [Duty Active: +{self._seat_bonus} pts per action]"

    def seat_group(self, group, tables):
        title = "Ma'am" if group.is_vip else "Sir"
        vip_badge = "⭐VIP " if group.is_vip else ""
        print(f"  🚶 Group arrived! Leader: {vip_badge}{group.leader_name} ({group.size} person{'s' if group.size > 1 else ''})")
        print(f"\n  [{self.name_tag.name}]: Welcome to Area 1 Pizzeria, {title} {group.leader_name}!\n")

        print(f"  🪑  Tables:")
        valid_keys = []
        for t in tables:
            if t.is_occupied:            marker = "❌ occupied"
            elif t.capacity < group.size: marker = "❌ too small"
            else:
                marker = "✅ available"
                valid_keys.append(str(t.table_number))
            print(f"     [{t.table_number}] Table {t.table_number} (cap {t.capacity}) — {marker}")
        print()

        if not valid_keys:
            print(f"  ⚠️  No table fits this group of {group.size}! Waiting...\n")
            print(f"  Press any key to retry or [Q] to quit.")
            k = TerminalUtils.getch()
            return ("QUIT", None, 0) if k == "q" else ("WAIT", None, 0)

        print(f"  Press [{'/'.join(valid_keys)}] to seat them.")
        start = time.time()

        while True:
            k = TerminalUtils.getch()
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
            pts = self._calc_points(time.time() - start) + self._seat_bonus
            print(f"\n  ✅  Group seated at Table {chosen_table.table_number}! (+{pts} pts)\n")
            time.sleep(1)
            return "OK", chosen_table, pts

    def serve_food(self, group):
        print(f"  🍕  {group.order.pizza} x{group.order.quantity} is ready!")
        print(f"  Press [S] to serve Table {group.table.table_number}.")
        start = time.time()
        while True:
            k = TerminalUtils.getch()
            if k == "s":
                self._groups_served += 1
                pts = self._calc_points(time.time() - start) + self._seat_bonus
                print(f"\n  ✅  Served to Table {group.table.table_number}! (+{pts} pts)\n")
                time.sleep(1.5)
                return "OK", pts
            elif k == "q":
                return "QUIT", 0

    def __str__(self):
        return (f"{self.name_tag.display()} | Duty: Serving | "
                f"Seated: {self._groups_seated} | Served: {self._groups_served}")


class Cashier(BasePlayer):
    def __init__(self, name):
        super().__init__(name, "Cashier")
        self._total_collected = self._correct_change = self._wrong_change = 0
        self._change_bonus = 0

    @property
    def total_collected(self): return self._total_collected

    @property
    def correct_change(self): return self._correct_change

    @property
    def wrong_change(self): return self._wrong_change

    def perform_primary_duty(self):
        self._is_busy = True
        self._change_bonus = 2
        return f"{self.name_tag.name} is at the register 💰  [Duty Active: +{self._change_bonus} pts per correct change]"

    def collect_payment(self, group):
        bill, paid, change = group.order.total_price, group.order.amount_paid, group.order.change

        print(f"  💵  Table {group.table.table_number} finished eating!")
        print(f"     {group.order.pizza} x{group.order.quantity} @ ${group.order.unit_price} each")
        print(f"     Total bill : ${bill}\n     Paid       : ${paid}")
        print(f"\n  Press [G] to collect payment.")

        while True:
            k = TerminalUtils.getch()
            if k == "g":
                self._total_collected += paid
                print(f"\n  ✅  ${paid} collected!\n  🧾  Bill was: ${bill}\n")
                time.sleep(1.5)
                break
            elif k == "q":
                return "QUIT", 0

        print(f"  💵  Bill: ${bill}  |  Paid: ${paid}\n")
        print(f"  Pick the correct change to give back:\n")

        if change == 0:
            options, correct_idx = ["No change — $0"], 0
        else:
            offsets = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 7, 10]
            wrong = set()
            for delta in random.sample(offsets, len(offsets)):
                fake = change + delta
                if fake >= 0 and fake != change:
                    wrong.add(fake)
                if len(wrong) >= 2:
                    break
            # Fallback: if we still couldn't find 2 distinct wrong answers, use safe values
            if len(wrong) < 2:
                for fallback in [change + 1, change + 2, change + 3]:
                    wrong.add(fallback)
                    if len(wrong) >= 2:
                        break
            options = [f"${x}" for x in list(wrong)[:2]] + [f"${change}"]
            random.shuffle(options)
            correct_idx = options.index(f"${change}")

        TerminalUtils.print_choices(options)
        result = TerminalUtils.pick_from_choices(options, correct_idx)
        if result[0] == "QUIT":
            return "QUIT", 0

        elapsed, chosen = result
        if chosen == correct_idx:
            self._correct_change += 1
            pts = self._calc_points(elapsed) + self._change_bonus
            tip = group.tip(elapsed)
            print(f"\n  ✅  Correct change! (+{pts} pts)\n  💰  {group.leader_name} left a tip: +{tip} pts\n")
            time.sleep(1.5)
            return "OK", pts + tip
        else:
            self._wrong_change += 1
            print(f"\n  ❌  Wrong change! Correct was {options[correct_idx]}. (-15 pts)\n")
            time.sleep(1.5)
            return "WRONG", -15

    def __str__(self):
        return (f"{self.name_tag.display()} | Duty: Register | "
                f"Collected: ${self._total_collected} | "
                f"Correct: {self._correct_change} | Wrong: {self._wrong_change}")


class Order:
    PIZZA_PRICES = {
        "Margherita": 8, "Pepperoni": 10, "Hawaiian": 9,
        "Veggie": 7, "BBQ Chicken": 11, "Supreme": 12,
    }

    def __init__(self, pizza, quantity):
        self._pizza = pizza
        self._quantity = quantity
        self._unit_price = self.PIZZA_PRICES.get(pizza, 10)
        self._total = self._unit_price * quantity
        self._paid = self._total + random.choice([0, 1, 2, 5, 10])

    @property
    def pizza(self): return self._pizza

    @property
    def quantity(self): return self._quantity

    @property
    def unit_price(self): return self._unit_price

    @property
    def total_price(self): return self._total

    @property
    def amount_paid(self): return self._paid

    @property
    def change(self): return self._paid - self._total

    def __str__(self):
        return f"{self._pizza} x{self._quantity} | ${self._unit_price} each | Total: ${self._total} | Paid: ${self._paid}"


class Customer:
    NAMES = ["Luigi", "Yoshi", "Koopa", "Shy Guy", "Toad Jr.",
             "Boo", "Birdo", "Lakitu", "Bullet Bill", "Bob-omb"]

    def __init__(self, name, money):
        self.name_tag = NameTag(name, "Customer")
        self._money = money

    @property
    def money(self): return self._money

    @money.setter
    def money(self, amount):
        if amount < 0: raise ValueError("Money cannot be negative.")
        self._money = amount

    def introduce(self): return self.name_tag.greet()

    def tip_amount(self, elapsed_time=0):
        base = random.randint(1, 5)
        bonus = self._calc_time_bonus(elapsed_time)
        return base + bonus

    def _calc_time_bonus(self, elapsed):
        if elapsed <= 1: return 3
        elif elapsed <= 3: return 2
        else: return 0

    def __str__(self): return f"{self.name_tag.display()} | Budget: ${self._money}"


class VipCustomer(Customer):
    NAMES = ["Peach", "Daisy", "Rosalina", "Pauline"]

    def __init__(self, name, money):
        super().__init__(name, money)
        self.name_tag.role = "VipCustomer"

    def tip_amount(self, elapsed_time=0):
        base = 7
        bonus = self._calc_time_bonus(elapsed_time)
        return base + bonus

    def __str__(self):
        return f"{self.name_tag.display()} | Budget: ${self.money} | VIP Perks: Yes"


class Group:
    def __init__(self, leader, size, order):
        self._leader = leader
        self._size = size
        self._order = order
        self._table = None

    @property
    def leader_name(self): return self._leader.name_tag.name

    @property
    def is_vip(self): return isinstance(self._leader, VipCustomer)

    @property
    def size(self): return self._size

    @property
    def order(self): return self._order

    @property
    def table(self): return self._table

    # FIX #1: table setter now also updates Table._current_group for consistency
    @table.setter
    def table(self, t):
        self._table = t

    def tip(self, elapsed_time=0):
        return self._leader.tip_amount(elapsed_time)

    def __str__(self):
        return f"Group of {self._size} | Leader: {self.leader_name} | Order: {self._order}"


class Table:
    def __init__(self, table_number, capacity):
        self._table_number = table_number
        self._capacity = capacity
        self._current_group = None

    @property
    def table_number(self): return self._table_number

    @property
    def capacity(self): return self._capacity

    @capacity.setter
    def capacity(self, value):
        if value < 1: raise ValueError("Capacity must be at least 1.")
        self._capacity = value

    @property
    def is_occupied(self): return self._current_group is not None

    @property
    def is_available(self): return self._current_group is None

    def seat(self, group):
        self._current_group = group
        group.table = self  # group.table setter handles its own side

    def clear(self): self._current_group = None

    def __str__(self):
        status = f"occupied — group of {self._current_group.size}" if self.is_occupied else "empty"
        return f"Table {self._table_number} | Cap: {self._capacity} | {status}"


class RestaurantClock:
    def __init__(self, start_hour=7):
        self._dilation = 360
        self._start_real = time.time()
        self._offset = start_hour * 3600

    def get_game_time(self):
        total = int(((time.time() - self._start_real) * self._dilation + self._offset) // 60)
        return (total // 60) % 24, total % 60

    def get_phase(self, hour):
        if 5  <= hour < 12: return "MORNING 🌅"
        if 12 <= hour < 17: return "AFTERNOON ☀️"
        if 17 <= hour < 20: return "EVENING 🌆"
        return "NIGHT 🌙"

    def time_str(self):
        h, m = self.get_game_time()
        return f"{h:02d}:{m:02d}"


class Restaurant(ABC):
    def __init__(self, name):
        self._name = name
        self._menu = []
        self._tables = []
        self._staff = []
        self._clock = None

    @property
    def name(self): return self._name

    @property
    def menu(self): return list(self._menu)

    def _set_menu(self, items):
        if not items or not isinstance(items, list):
            raise ValueError("Menu must be a non-empty list.")
        self._menu = items

    @abstractmethod
    def set_pizza_menu(self): pass

    def set_clock(self, clock): self._clock = clock

    def add_table(self, table): self._tables.append(table)

    def add_staff(self, member): self._staff.append(member)

    def get_staff_by_type(self, staff_type):
        return next((s for s in self._staff if isinstance(s, staff_type)), None)

    def show_staff(self):
        print(f"\n  👥  Staff at {self._name}:")
        for s in self._staff: print(f"     {s.introduce()}")
        print()

    def show_tables(self):
        print(f"  🪑  Tables:")
        for t in self._tables: print(f"     {t}")
        print()

    @abstractmethod
    def run_shift(self): pass

    def __str__(self):
        return (f"=== {self._name} ===\n"
                f"Menu  : {', '.join(self._menu)}\n"
                f"Tables: {len(self._tables)}\nStaff : {len(self._staff)}")


class Area1Branch(Restaurant):
    DIFFICULTY = {
        1: {"label": "⭐  EASY",    "choices": 3, "gap": 5},
        2: {"label": "⭐⭐  MEDIUM", "choices": 4, "gap": 4},
        3: {"label": "⭐⭐⭐  HARD", "choices": 5, "gap": 3},
    }

    def __init__(self, name):
        super().__init__(name)
        self._score = 0
        self._served = 0
        self._day = 1
        self._total_collected = 0

    @property
    def score(self): return self._score

    @property
    def served(self): return self._served

    def set_pizza_menu(self):
        self._set_menu(["Margherita", "Pepperoni", "Hawaiian", "Veggie", "BBQ Chicken", "Supreme"])

    def _get_diff(self): return self.DIFFICULTY[min(self._day, 3)]

    def _make_group(self):
        is_vip = random.random() < 0.2
        if is_vip:
            name = random.choice(VipCustomer.NAMES)
            leader = VipCustomer(name, random.randint(80, 150))
        else:
            name = random.choice(Customer.NAMES)
            leader = Customer(name, random.randint(15, 50))
        max_cap = max(t.capacity for t in self._tables)
        pizza = random.choice(self._menu)
        return Group(leader, random.randint(1, max_cap), Order(pizza, random.randint(1, max_cap)))

    def _show_header(self, role_label):
        diff = self._get_diff()
        TerminalUtils.clear()
        TerminalUtils.divider()
        print(f"  🍕  {self._name}  |  {self._clock.time_str()}  {self._clock.get_phase(self._clock.get_game_time()[0])}")
        print(f"  📅  Day {self._day}  {diff['label']}  |  ⭐ Score: {self._score}  |  👥 Served: {self._served}")
        TerminalUtils.divider()
        print(f"\n  👤  Current Role: {role_label}\n")

    def _day_summary(self):
        diff = self._get_diff()
        TerminalUtils.clear()
        TerminalUtils.divider()
        print(f"  🌙  END OF DAY {self._day} SHIFT  —  {diff['label']}")
        TerminalUtils.divider("─")
        print(f"  Groups served    : {self._served}")
        print(f"  Money collected  : ${self._total_collected}")
        print(f"  Total score      : {self._score} pts")
        if self._day < 3:
            nd = self.DIFFICULTY[self._day + 1]
            print(f"\n  ⚠️  Tomorrow: {nd['label']}")
            print(f"  Choices: {nd['choices']}  |  Arrival gap: {nd['gap']}s")
        TerminalUtils.divider()
        print(f"\n  Rest up! Press ENTER to start Day {self._day + 1} shift...")
        input()

    def run_shift(self):
        if self._clock is None:
            raise RuntimeError("Set a clock first: branch.set_clock(clock)")

        waiter  = self.get_staff_by_type(Waiter)
        chef    = self.get_staff_by_type(Chef)
        cashier = self.get_staff_by_type(Cashier)

        if not all([waiter, chef, cashier]):
            print("  ❌  Missing staff! Need a Waiter, Chef, and Cashier.")
            return

        TerminalUtils.clear()
        TerminalUtils.divider()
        print(f"  🍕  {self._name}")
        TerminalUtils.divider()
        self.show_staff()
        self.show_tables()
        print(f"Waiter  → [1/2/3] pick table  (+3 seat bonus from duty)")
        print(f"Chef    → [1/2/3] correct pizza  (1.5x reaction window from duty)")
        print(f"Cashier → [G] collect, [1/2/3] correct change  (+2 pts from duty)")
        print(f"\n  Speed bonus: <1s = full | ~3s = half | 6s+ = none")
        print(f"  Wrong key  : -15 pts | Tip: Regular 1-8 | VIP 7-10")
        print(f"  Day advances every 5 groups served.")
        TerminalUtils.divider()
        print(f"\n  Press ENTER to start the shift!\n")
        input()

        while True:
            diff = self._get_diff()
            TerminalUtils.clear()
            TerminalUtils.divider()
            print(f"  🍕  {self._name}  |  {self._clock.time_str()}")
            print(f"  📅  Day {self._day}  {diff['label']}  |  ⭐ Score: {self._score}  |  👥 Served: {self._served}")
            TerminalUtils.divider()
            self.show_tables()
            print(f"  ⏳  Next group in {diff['gap']} seconds... (Q to end shift)\n")
            time.sleep(diff["gap"])

            group = self._make_group()

            self._show_header(f"WAITER  —  {waiter.name_tag.name}")
            print(f"  {waiter.perform_primary_duty()}\n")
            status, table, pts = waiter.seat_group(group, self._tables)
            waiter.reset_busy()  # FIX #6: reset after each action
            if status == "QUIT":  break
            if status == "WAIT":  continue
            if status == "WRONG_TABLE":
                self._score = max(0, self._score + pts)
                continue
            self._score += pts

            self._show_header(f"CHEF  —  {chef.name_tag.name}")
            print(f"  {chef.perform_primary_duty()}\n")
            status, pts = chef.cook(group.order, self._menu, diff["choices"])
            chef.reset_busy()  # FIX #6: reset after each action
            if status == "QUIT":  break
            if status == "WRONG":
                self._score = max(0, self._score + pts)
                table.clear()
                continue
            self._score += pts

            self._show_header(f"WAITER  —  {waiter.name_tag.name}")
            print(f"  {waiter.perform_primary_duty()}\n")
            status, pts = waiter.serve_food(group)
            waiter.reset_busy()  # FIX #6: reset after each action
            if status == "QUIT":  break
            self._score += pts

            self._show_header(f"CASHIER  —  {cashier.name_tag.name}")
            print(f"  {cashier.perform_primary_duty()}\n")
            status, pts = cashier.collect_payment(group)
            cashier.reset_busy()  # FIX #6: reset after each action
            if status == "QUIT":  break
            self._score = max(0, self._score + pts) if pts < 0 else self._score + pts

            self._total_collected += group.order.amount_paid
            table.clear()
            self._served += 1

            if self._served % 5 == 0:
                self._day_summary()
                self._day += 1

        self._end_of_shift(waiter, chef, cashier)

    def _end_of_shift(self, waiter, chef, cashier):
        days_worked = self._day
        TerminalUtils.clear()
        TerminalUtils.divider("▓")
        print(f"  🌙  SHIFT ENDED — Time to clock out!")
        TerminalUtils.divider("─")
        print(f"  Days worked      : {days_worked}")
        print(f"  Groups served    : {self._served}")
        print(f"  Money collected  : ${self._total_collected}")
        print(f"  Final Score      : {self._score} pts")
        TerminalUtils.divider("─")
        print(f"\n  📊  Staff Performance:")
        for s in [waiter, chef, cashier]: print(f"  {s}")
        TerminalUtils.divider("─")
        sc = self._score
        if   sc >= 500: print(f"  🥇  LEGENDARY STAFF — Unstoppable!")
        elif sc >= 300: print(f"  🥈  STAR CREW — Incredible work!")
        elif sc >= 180: print(f"  🥉  SOLID SHIFT — Well done!")
        elif sc >= 80:  print(f"  🎖️   DECENT SHIFT — Keep it up!")
        else:           print(f"  😅  ROUGH SHIFT — Better luck next time!")
        TerminalUtils.divider("▓")
        print(f"\n  See you next shift! \n")