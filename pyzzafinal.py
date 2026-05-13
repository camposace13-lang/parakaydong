import os, sys, time, random
from abc import ABC, abstractmethod


# =============================================================================
#  SOLID LEGEND
#  [S] Single Responsibility  — one class, one reason to change
#  [O] Open / Closed          — open for extension, closed for modification
#  [L] Liskov Substitution    — subclasses safely replace their parent
#  [I] Interface Segregation  — clients depend only on methods they use
#  [D] Dependency Inversion   — depend on abstractions, not concretes
#
#  DRY LEGEND
#  [DRY] Duplication eliminated by extracting shared logic to a base class,
#        template method, or helper — subclasses override only what differs.
# =============================================================================


# ─────────────────────────────────────────────────────────────────────────────
#  ABSTRACTIONS
#
#  [I] Interfaces are deliberately narrow:
#      • IBusyTrackable  — staff with a busy-flag life-cycle
#      • IStaff          — identity only (does NOT force busy-tracking)
#      • IDutyActivatable— unifies activate_duty() across cook/cashier/seater  [DRY]
#      • ISeater, ICook, IPaymentCollector — role-specific operations
#      • IDifficultyConfig, IGroupFactory, ISummaryDisplay, IChallengeBuilder,
#        IBranchRepository — infrastructure seams
# ─────────────────────────────────────────────────────────────────────────────

class IBusyTrackable(ABC):
    """Staff whose availability can be toggled."""        # [I] split from IStaff

    @property
    @abstractmethod
    def is_busy(self) -> bool: pass

    @abstractmethod
    def reset_busy(self) -> None: pass


class IStaff(ABC):
    """Identity contract only — not every staff member tracks busy state."""  # [I]

    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def role(self) -> str: pass

    @abstractmethod
    def introduce(self) -> str: pass


class IDutyActivatable(ABC):
    """Any staff role that can be 'activated' for a turn."""  # [I] [DRY]

    @abstractmethod
    def activate_duty(self) -> str: pass


class ISeater(IDutyActivatable):           # [I] seater IS duty-activatable
    @abstractmethod
    def seat_group(self, group, tables) -> tuple: pass

    @abstractmethod
    def serve_food(self, group) -> tuple: pass


class ICook(IDutyActivatable):             # [I] cook IS duty-activatable
    @abstractmethod
    def cook(self, order, all_pizzas: list, num_choices: int) -> tuple: pass


class IPaymentCollector(IDutyActivatable): # [I] cashier IS duty-activatable
    @abstractmethod
    def collect_payment(self, group) -> tuple: pass


class IDifficultyConfig(ABC):
    @abstractmethod
    def for_day(self, day: int) -> dict: pass

    @abstractmethod
    def available_days(self) -> list: pass


class IGroupFactory(ABC):
    @abstractmethod
    def create(self): pass

    @abstractmethod
    def set_tables(self, tables: list) -> None: pass


class ISummaryDisplay(ABC):
    @abstractmethod
    def show_day_end(self, day: int, served: int, score: int) -> None: pass

    @abstractmethod
    def show_shift_end(self, score: int, served: int, staff: list) -> None: pass


class IChallengeBuilder(ABC):
    @abstractmethod
    def build_pizza_options(self, correct_pizza: str, all_pizzas: list,
                            num_choices: int) -> tuple: pass

    @abstractmethod
    def build_change_options(self, correct_change: int) -> tuple: pass


class IBranchRepository(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def menu(self) -> list: pass

    @property
    @abstractmethod
    def tables(self) -> list: pass

    @property
    @abstractmethod
    def staff(self) -> list: pass

    @property
    @abstractmethod
    def clock(self): pass

    @abstractmethod
    def get_staff_by_type(self, staff_type): pass


# ─────────────────────────────────────────────────────────────────────────────
#  UI CLASS
#  [S] GameUI has one reason to change: how the game's screens look.
# ─────────────────────────────────────────────────────────────────────────────

class GameUI:
    """All screen rendering for the game."""  # [S]

    @staticmethod
    def clear():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def print_choices(options: list):
        print("─" * 55)
        for i, opt in enumerate(options):
            print(f"  [{i+1}]  {opt}")
        print("─" * 55)
        print("\n  Press the number of the correct choice.")

    @staticmethod
    def show_header(branch_name: str, time_str: str, role: str, name: str):
        print("═" * 55)
        print(f"  🍕 {branch_name} | {time_str}")
        print(f"  👤 {role} — {name}")
        print("═" * 55)

    # ── Chef screens ─────────────────────────────────────────────────────────

    @staticmethod
    def show_cooking(name: str, order, multiplier: float):
        print(f"\n  🍳  Order in! Cook: {order.pizza} x{order.quantity}")
        print(f"  👨‍🍳 {name} is cooking (x{multiplier} difficulty)\n")

    @staticmethod
    def show_cook_result(order, pts: int):
        print(f"\n  🍳 {order.pizza} x{order.quantity} cooking...")
        print(f"  ⭐ Points earned: {pts}\n")

    @staticmethod
    def show_wrong_pizza():
        print(f"\n  ❌ Wrong pizza! The group LEFT! (-15 pts)\n")

    # ── Waiter screens ───────────────────────────────────────────────────────

    @staticmethod
    def show_arrival(group, waiter_name: str):
        title = "Ma'am" if group.is_vip else "Sir"
        vip   = "⭐VIP " if group.is_vip else ""
        print(f"  🚶 Group arrived: {vip}{group.leader_name} ({group.size})")
        print(f"  [{waiter_name}] Welcome, {title} {group.leader_name}!\n")

    @staticmethod
    def show_tables(tables: list, group_size: int) -> list:
        print("  🪑 Tables:")
        valid = []
        for t in tables:
            if t.is_occupied:
                marker = "❌ occupied"
            elif t.capacity < group_size:
                marker = "❌ too small"
            else:
                marker = "✅ available"
                valid.append(str(t.table_number))
            print(f"  [{t.table_number}] Table {t.table_number} "
                  f"(cap {t.capacity}) — {marker}")
        return valid

    # ── Cashier screens ──────────────────────────────────────────────────────

    @staticmethod
    def show_payment(group):
        print(f"  💵 Table {group.table.table_number} finished eating!")
        print(f"  {group.order.pizza} x{group.order.quantity}")
        print(f"  Total: ${group.order.total_price} | Paid: ${group.order.amount_paid}\n")

    @staticmethod
    def show_wrong_change(correct_option: str):
        print(f"\n  ❌  Wrong change! Correct was {correct_option}. (-15 pts)\n")


# ─────────────────────────────────────────────────────────────────────────────
#  CHALLENGE BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

class StandardChallengeBuilder(IChallengeBuilder):
    """Standard multiple-choice distractor builder."""  # [O]

    def build_pizza_options(self, correct_pizza: str, all_pizzas: list,
                            num_choices: int) -> tuple:
        wrong = [p for p in all_pizzas if p != correct_pizza]
        random.shuffle(wrong)
        options = wrong[:num_choices - 1] + [correct_pizza]
        random.shuffle(options)
        return options, options.index(correct_pizza)

    def build_change_options(self, correct_change: int) -> tuple:
        if correct_change == 0:
            return ["No change — $0"], 0
        offsets = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 7, 10]
        wrong: set = set()
        for delta in random.sample(offsets, len(offsets)):
            fake = correct_change + delta
            if fake >= 0 and fake != correct_change:
                wrong.add(fake)
            if len(wrong) >= 2:
                break
        for fallback in [correct_change + 1, correct_change + 2, correct_change + 3]:
            if len(wrong) >= 2:
                break
            wrong.add(fallback)
        options = [f"${x}" for x in list(wrong)[:2]] + [f"${correct_change}"]
        random.shuffle(options)
        return options, options.index(f"${correct_change}")


class EasyChallengeBuilder(IChallengeBuilder):
    """Beginner-friendly builder: only 1 wrong option, predictable layout."""  # [O]

    def build_pizza_options(self, correct_pizza: str, all_pizzas: list,
                            num_choices: int) -> tuple:
        wrong = [p for p in all_pizzas if p != correct_pizza]
        random.shuffle(wrong)
        options = wrong[:1] + [correct_pizza]
        return options, options.index(correct_pizza)

    def build_change_options(self, correct_change: int) -> tuple:
        if correct_change == 0:
            return ["No change — $0"], 0
        options = [f"${correct_change + 5}", f"${correct_change}"]
        return options, 1


# ─────────────────────────────────────────────────────────────────────────────
#  INPUT / SCORE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

class InputHandler:
    """Keyboard input handler. Changes only when input mechanics change."""  # [S]

    @staticmethod
    def get_choice(count: int) -> tuple:
        start = time.time()
        while True:
            k = input("  > ").strip().lower()
            if k == "q":
                return "QUIT", None
            try:
                chosen = int(k) - 1
            except ValueError:
                print("  ⚠️ Enter a number.")
                continue
            if 0 <= chosen < count:
                return time.time() - start, chosen
            print("  ⚠️ Invalid choice.")


class ScoreSystem:
    """Scoring calculations only. Changes only when the scoring formula changes."""  # [S]

    @staticmethod
    def time_bonus(elapsed: float, base: int = 5, max_bonus: int = 5,
                   limit: int = 6) -> int:
        ratio = 1.0 if elapsed <= 1 else max(0.0, 1 - ((elapsed - 1) / (limit - 1)))
        return base + int(max_bonus * ratio)

    @staticmethod
    def wrong_penalty() -> int:
        return -15

    @staticmethod
    def apply(base_score: int, change: int) -> int:
        return max(0, base_score + change)


# ─────────────────────────────────────────────────────────────────────────────
#  NAME TAG
# ─────────────────────────────────────────────────────────────────────────────

class NameTag:
    """Staff identity and greeting text. Changes only when identity display changes."""  # [S]

    GREETINGS = {
        "Chef":        "Let's cook!",
        "Cashier":     "Welcome, what can I get you?",
        "Waiter":      "Table for how many?",
        "Customer":    "Hi, I'd like to order.",
        "VipCustomer": "Hello, I have a reservation.",
    }

    def __init__(self, name: str, role: str):
        self._name = name
        self._role = role

    @property
    def name(self) -> str: return self._name

    @property
    def role(self) -> str: return self._role

    @role.setter
    def role(self, value: str): self._role = value

    def display(self) -> str: return f"[{self._role}] {self._name}"

    def greet(self) -> str:
        return f"{self.display()}: {self.GREETINGS.get(self._role, 'Hello!')}"


# ─────────────────────────────────────────────────────────────────────────────
#  BASE STAFF
# ─────────────────────────────────────────────────────────────────────────────

class BaseStaff(IStaff, IBusyTrackable):
    """
    Identity + busy-state management only.
    [S]  One reason to change: shared staff lifecycle.
    [I]  Implements both IStaff and IBusyTrackable explicitly — nothing extra forced.
    """

    def __init__(self, name: str, role: str):
        self._name_tag = NameTag(name, role)
        self._is_busy  = False

    # ── IStaff ────────────────────────────────────────────────────────────────
    @property
    def name(self) -> str:         return self._name_tag.name

    @property
    def role(self) -> str:         return self._name_tag.role

    @property
    def name_tag(self) -> NameTag: return self._name_tag

    def introduce(self) -> str:    return self._name_tag.greet()

    # ── IBusyTrackable ────────────────────────────────────────────────────────
    @property
    def is_busy(self) -> bool:     return self._is_busy

    def reset_busy(self) -> None:  self._is_busy = False

    def __str__(self) -> str:
        state = "busy" if self._is_busy else "available"
        return f"{self._name_tag.display()} ({state})"


class GuestStaff(IStaff):
    """
    Lightweight temporary staff — implements IStaff only.
    [I]  Does NOT implement IBusyTrackable because guests have no busy-state lifecycle.
         The old no-op reset_busy() stub is gone — ISP respected.
    [L]  name, role, introduce() honour the IStaff contract everywhere IStaff is expected.
    [S]  One purpose: represent a transient / covering worker.
    """

    def __init__(self, name: str, role: str):
        self._name = name
        self._role = role

    @property
    def name(self) -> str: return self._name

    @property
    def role(self) -> str: return self._role

    def introduce(self) -> str:
        return f"[{self._role}] {self._name}: Hi, I'm covering today!"

    def __str__(self) -> str:
        return f"[{self._role}] {self._name} (guest)"


# ─────────────────────────────────────────────────────────────────────────────
#  ABSTRACT COOK  [DRY]  [S]  [O]
#
#  cook() logic was duplicated verbatim in Chef and TraineeCook.
#  The only behavioural difference is _cook_multiplier and the activate_duty label.
#  Template-method pattern: cook() calls _multiplier (hook) so subclasses
#  override a single property instead of a 30-line method.
# ─────────────────────────────────────────────────────────────────────────────

class AbstractCook(BaseStaff, ICook):
    """
    Shared cook() implementation via Template Method pattern.
    [DRY] Eliminates the duplicated cook() body from Chef and TraineeCook.
    [S]   One reason to change: how the cooking mini-game works.
    [O]   Subclasses extend by overriding _multiplier and activate_duty only.
    """

    def __init__(self, name: str, challenge_builder: IChallengeBuilder):  # [D]
        super().__init__(name, "Chef")
        self._builder          = challenge_builder
        self._correct_cooks    = 0
        self._incorrect_cooks  = 0

    @property
    def correct_cooks(self) -> int:   return self._correct_cooks

    @property
    def incorrect_cooks(self) -> int: return self._incorrect_cooks

    @property
    @abstractmethod
    def _multiplier(self) -> float:
        """Hook: subclass returns its difficulty multiplier."""  # [O] [DRY]

    # ── Template method — shared by all cooks  [DRY] ──────────────────────────
    def cook(self, order, all_pizzas: list, num_choices: int) -> tuple:
        options, correct_idx = self._builder.build_pizza_options(
            order.pizza, all_pizzas, num_choices
        )
        GameUI.show_cooking(self.name, order, self._multiplier)
        GameUI.print_choices(options)
        print("\n  Press the correct number.")

        result = InputHandler.get_choice(len(options))
        if result[0] == "QUIT":
            return "QUIT", 0

        elapsed, chosen = result
        if chosen == correct_idx:
            self._correct_cooks += 1
            pts = ScoreSystem.time_bonus(elapsed * self._multiplier)
            GameUI.show_cook_result(order, pts)
            time.sleep(1.5)
            return "OK", pts
        else:
            self._incorrect_cooks += 1
            GameUI.show_wrong_pizza()
            time.sleep(2)
            return "WRONG", ScoreSystem.wrong_penalty()

    def __str__(self) -> str:
        return (f"{self._name_tag.display()} | Duty: Cooking | "
                f"Correct: {self._correct_cooks} | Mistakes: {self._incorrect_cooks}")


class Chef(AbstractCook):
    """Full-difficulty chef: x1.5 time multiplier when on duty."""  # [O] [L]

    def __init__(self, name: str, challenge_builder: IChallengeBuilder):  # [D]
        super().__init__(name, challenge_builder)
        self._active_multiplier = 1.0

    @property
    def _multiplier(self) -> float: return self._active_multiplier  # [O] hook

    def activate_duty(self) -> str:
        self._is_busy             = True
        self._active_multiplier   = 1.5
        return (f"{self.name} is cooking 🍳  "
                f"[Duty Active: reaction window x{self._active_multiplier}]")


class TraineeCook(AbstractCook):
    """Trainee chef: no time pressure (multiplier stays 1.0)."""  # [O] [L]

    @property
    def _multiplier(self) -> float: return 1.0  # [O] hook — no penalty

    def activate_duty(self) -> str:
        self._is_busy = True
        return f"{self.name} is cooking 🍳  [Trainee Mode: no time multiplier]"

    def __str__(self) -> str:
        return (f"{self._name_tag.display()} | Duty: Trainee Cooking | "
                f"Correct: {self._correct_cooks} | Mistakes: {self._incorrect_cooks}")


# ─────────────────────────────────────────────────────────────────────────────
#  ABSTRACT WAITER  [DRY]  [S]  [O]
#
#  seat_group() and serve_food() were duplicated verbatim in Waiter and HeadWaiter.
#  The only difference is _base_seat_bonus and the activate_duty label.
#  Extract to AbstractWaiter; subclasses override _base_seat_bonus and activate_duty.
# ─────────────────────────────────────────────────────────────────────────────

class AbstractWaiter(BaseStaff, ISeater):
    """
    Shared seat_group() / serve_food() via Template Method pattern.
    [DRY] Eliminates 60+ duplicated lines between Waiter and HeadWaiter.
    [S]   One reason to change: how seating / serving interactions work.
    [O]   Subclasses extend by overriding _base_seat_bonus and activate_duty only.
    """

    def __init__(self, name: str):
        super().__init__(name, "Waiter")
        self._groups_seated = 0
        self._groups_served = 0
        self._seat_bonus    = 0

    @property
    def groups_seated(self) -> int: return self._groups_seated

    @property
    def groups_served(self) -> int: return self._groups_served

    @property
    @abstractmethod
    def _base_seat_bonus(self) -> int:
        """Hook: subclass returns its per-action bonus."""  # [O] [DRY]

    # ── Template methods — shared by all waiters  [DRY] ──────────────────────
    def seat_group(self, group, tables: list) -> tuple:
        GameUI.show_arrival(group, self.name)
        valid_keys = GameUI.show_tables(tables, group.size)

        if not valid_keys:
            print("  ❌ No available tables!\n")
            time.sleep(1.5)
            return "WAIT", None, 0

        result = InputHandler.get_choice(len(tables))
        if result[0] == "QUIT":
            return "QUIT", None, 0

        elapsed, chosen = result
        chosen_table = tables[chosen]

        if str(chosen_table.table_number) not in valid_keys:
            print(f"\n  ❌ Wrong table! (-15 pts)\n")
            time.sleep(1.5)
            return "WRONG_TABLE", None, ScoreSystem.wrong_penalty()

        chosen_table.seat(group)
        self._groups_seated += 1
        pts = ScoreSystem.time_bonus(elapsed) + self._seat_bonus
        print(f"\n  ✅ Seated at Table {chosen_table.table_number}! (+{pts} pts)\n")
        time.sleep(1.5)
        return "OK", chosen_table, pts

    def serve_food(self, group) -> tuple:
        print(f"  🍕  {group.order.pizza} x{group.order.quantity} is ready!")
        print(f"  Press [S] to serve Table {group.table.table_number}.")
        start = time.time()
        while True:
            k = input("  > ").strip().lower()
            if k == "s":
                self._groups_served += 1
                pts = ScoreSystem.time_bonus(time.time() - start) + self._seat_bonus
                print(f"\n  ✅  Served to Table {group.table.table_number}! (+{pts} pts)\n")
                time.sleep(1.5)
                return "OK", pts
            elif k == "q":
                return "QUIT", 0

    def __str__(self) -> str:
        return (f"{self._name_tag.display()} | Duty: Serving | "
                f"Seated: {self._groups_seated} | Served: {self._groups_served}")


class Waiter(AbstractWaiter):
    """Standard waiter: +3 pts per action on duty."""  # [O] [L]

    @property
    def _base_seat_bonus(self) -> int: return 3  # [O] hook

    def activate_duty(self) -> str:
        self._is_busy    = True
        self._seat_bonus = self._base_seat_bonus
        return (f"{self.name} is serving tables 🍽️  "
                f"[Duty Active: +{self._seat_bonus} pts per action]")


class HeadWaiter(AbstractWaiter):
    """Senior waiter: +6 pts per action on duty (double bonus)."""  # [O] [L]

    @property
    def _base_seat_bonus(self) -> int: return 6  # [O] hook — higher tier

    def activate_duty(self) -> str:
        self._is_busy    = True
        self._seat_bonus = self._base_seat_bonus
        return (f"{self.name} is heading the floor 🍽️⭐  "
                f"[Head Waiter: +{self._seat_bonus} pts per action]")

    def __str__(self) -> str:
        return (f"{self._name_tag.display()} | Duty: Head Waiter | "
                f"Seated: {self._groups_seated} | Served: {self._groups_served}")


# ─────────────────────────────────────────────────────────────────────────────
#  CASHIER / SELF-CHECKOUT
# ─────────────────────────────────────────────────────────────────────────────

class Cashier(BaseStaff, IPaymentCollector):
    """Payment collection interaction only."""  # [S]

    def __init__(self, name: str, challenge_builder: IChallengeBuilder):  # [D]
        super().__init__(name, "Cashier")
        self._builder         = challenge_builder
        self._total_collected = 0
        self._correct_change  = 0
        self._wrong_change    = 0
        self._change_bonus    = 0

    @property
    def total_collected(self) -> int: return self._total_collected

    @property
    def correct_change(self) -> int:  return self._correct_change

    @property
    def wrong_change(self) -> int:    return self._wrong_change

    def activate_duty(self) -> str:
        self._is_busy      = True
        self._change_bonus = 2
        return (f"{self.name} is at the register 💰  "
                f"[Duty Active: +{self._change_bonus} pts per correct change]")

    def collect_payment(self, group) -> tuple:
        bill = group.order.total_price
        paid = group.order.amount_paid
        GameUI.show_payment(group)

        while True:
            k = input("  > ").strip().lower()
            if k == "g":
                self._total_collected += paid
                print(f"\n  ✅  ${paid} collected!\n  🧾  Bill was: ${bill}\n")
                time.sleep(1.5)
                break
            elif k == "q":
                return "QUIT", 0

        print(f"  💵  Bill: ${bill}  |  Paid: ${paid}\n")
        print(f"  Pick the correct change to give back:\n")

        options, correct_idx = self._builder.build_change_options(group.order.change)
        GameUI.print_choices(options)

        result = InputHandler.get_choice(len(options))
        if result[0] == "QUIT":
            return "QUIT", 0

        elapsed, chosen = result
        if chosen == correct_idx:
            self._correct_change += 1
            pts = ScoreSystem.time_bonus(elapsed) + self._change_bonus
            tip = group.tip(elapsed)
            print(f"\n  ✅  Correct change! (+{pts} pts)\n"
                  f"  💰  {group.leader_name} left a tip: +{tip} pts\n")
            time.sleep(1.5)
            return "OK", pts + tip
        else:
            self._wrong_change += 1
            GameUI.show_wrong_change(options[correct_idx])
            time.sleep(1.5)
            return "WRONG", ScoreSystem.wrong_penalty()

    def __str__(self) -> str:
        return (f"{self._name_tag.display()} | Duty: Register | "
                f"Collected: ${self._total_collected} | "
                f"Correct: {self._correct_change} | Wrong: {self._wrong_change}")


class SelfCheckout(BaseStaff, IPaymentCollector):
    """Automated payment: auto-collects, no change quiz, awards flat points."""  # [O] [L] [S]

    _FLAT_REWARD = 3  # [S] [DRY] single source of truth for the flat reward

    def __init__(self, name: str):
        super().__init__(name, "Cashier")
        self._total_collected = 0
        self._transactions    = 0

    @property
    def total_collected(self) -> int: return self._total_collected

    @property
    def transactions(self) -> int:    return self._transactions

    def activate_duty(self) -> str:
        self._is_busy = True
        return (f"{self.name} is ready 🤖  "
                f"[Self-Checkout: auto-collect, flat +{self._FLAT_REWARD} pts]")

    # [L] Returns ("OK"|"QUIT", int) — same contract as Cashier.collect_payment()
    def collect_payment(self, group) -> tuple:
        GameUI.show_payment(group)
        print("  🤖  Self-checkout: processing payment automatically...\n")
        time.sleep(1.0)
        k = input("  Press [G] to confirm or [Q] to quit.\n  > ").strip().lower()
        if k == "q":
            return "QUIT", 0
        self._total_collected += group.order.amount_paid
        self._transactions    += 1
        print(f"\n  ✅  Payment processed! (+{self._FLAT_REWARD} pts)"
              f" — No change quiz for self-checkout.\n")
        time.sleep(1.5)
        return "OK", self._FLAT_REWARD

    def __str__(self) -> str:
        return (f"{self._name_tag.display()} | Duty: Self-Checkout | "
                f"Collected: ${self._total_collected} | "
                f"Transactions: {self._transactions}")


# ─────────────────────────────────────────────────────────────────────────────
#  DOMAIN MODELS
# ─────────────────────────────────────────────────────────────────────────────

class Order:
    """Pizza order data and price calculations only."""  # [S]

    PIZZA_PRICES = {
        "Margherita": 8, "Pepperoni": 10, "Hawaiian": 9,
        "Veggie": 7,     "BBQ Chicken": 11, "Supreme": 12,
    }

    def __init__(self, pizza: str, quantity: int):
        self._pizza      = pizza
        self._quantity   = quantity
        self._unit_price = self.PIZZA_PRICES.get(pizza, 10)
        self._total      = self._unit_price * quantity
        self._paid       = self._total + random.choice([0, 1, 2, 5, 10])

    @property
    def pizza(self) -> str:       return self._pizza

    @property
    def quantity(self) -> int:    return self._quantity

    @property
    def unit_price(self) -> int:  return self._unit_price

    @property
    def total_price(self) -> int: return self._total

    @property
    def amount_paid(self) -> int: return self._paid

    @property
    def change(self) -> int:      return self._paid - self._total

    def __str__(self) -> str:
        return (f"{self._pizza} x{self._quantity} | "
                f"${self._unit_price} each | Total: ${self._total} | Paid: ${self._paid}")


class Customer:
    """Customer identity and tip logic only."""  # [S]

    NAMES = ["Luigi", "Yoshi", "Koopa", "Shy Guy", "Toad Jr.",
             "Boo", "Birdo", "Lakitu", "Bullet Bill", "Bob-omb"]

    def __init__(self, name: str, money: int):
        self.name_tag  = NameTag(name, "Customer")
        self._money    = money

    @property
    def money(self) -> int: return self._money

    @money.setter
    def money(self, amount: int):
        if amount < 0:
            raise ValueError("Money cannot be negative.")
        self._money = amount

    def introduce(self) -> str: return self.name_tag.greet()

    def tip_amount(self, elapsed_time: float = 0) -> int:
        if elapsed_time < 2:   return random.randint(3, 6)
        elif elapsed_time < 5: return random.randint(1, 3)
        else:                  return 0

    def __str__(self) -> str:
        return f"{self.name_tag.display()} | Budget: ${self._money}"


class VipCustomer(Customer):
    """VIP customer with higher tip amounts. Fully substitutable for Customer."""  # [L]

    NAMES = ["Peach", "Daisy", "Rosalina", "Pauline"]

    def __init__(self, name: str, money: int):
        super().__init__(name, money)
        self.name_tag.role = "VipCustomer"

    # [L] Overrides tip_amount — same signature and semantics, higher values
    def tip_amount(self, elapsed_time: float = 0) -> int:
        if elapsed_time < 2:   return random.randint(8, 12)
        elif elapsed_time < 5: return random.randint(5, 8)
        else:                  return random.randint(2, 5)

    def __str__(self) -> str:
        return f"{self.name_tag.display()} | Budget: ${self.money} | VIP Perks: Yes"


class Group:
    """Customer group: composition and tip delegation only."""  # [S]

    def __init__(self, leader, size: int, order: Order):
        self._leader = leader
        self._size   = size
        self._order  = order
        self._table  = None

    @property
    def leader_name(self) -> str: return self._leader.name_tag.name

    @property
    def is_vip(self) -> bool:     return isinstance(self._leader, VipCustomer)

    @property
    def size(self) -> int:        return self._size

    @property
    def order(self) -> Order:     return self._order

    @property
    def table(self):              return self._table

    @table.setter
    def table(self, t):           self._table = t

    def tip(self, elapsed_time: float = 0) -> int:
        return self._leader.tip_amount(elapsed_time)

    def __str__(self) -> str:
        return (f"Group of {self._size} | "
                f"Leader: {self.leader_name} | Order: {self._order}")


class Table:
    """Table state and capacity management only."""  # [S]

    def __init__(self, table_number: int, capacity: int):
        self._table_number  = table_number
        self._capacity      = capacity
        self._current_group = None

    @property
    def table_number(self) -> int:  return self._table_number

    @property
    def capacity(self) -> int:      return self._capacity

    @capacity.setter
    def capacity(self, value: int):
        if value < 1:
            raise ValueError("Capacity must be at least 1.")
        self._capacity = value

    @property
    def is_occupied(self) -> bool:  return self._current_group is not None

    @property
    def is_available(self) -> bool: return self._current_group is None

    def seat(self, group: Group):
        self._current_group = group
        group.table = self

    def clear(self): self._current_group = None

    def __str__(self) -> str:
        status = (f"occupied — group of {self._current_group.size}"
                  if self.is_occupied else "empty")
        return f"Table {self._table_number} | Cap: {self._capacity} | {status}"


# ─────────────────────────────────────────────────────────────────────────────
#  DIFFICULTY CONFIGS
# ─────────────────────────────────────────────────────────────────────────────

class BaseDifficultyConfig(IDifficultyConfig):
    """
    [DRY] Shared for_day() / available_days() logic using a _LEVELS dict hook.
    Subclasses only provide their own _LEVELS — no method duplication.
    [O]   Open for new curves by subclassing and overriding _LEVELS.
    """

    _LEVELS: dict = {}  # hook — subclass overrides this class attribute

    def for_day(self, day: int) -> dict:
        return self._LEVELS[min(day, max(self._LEVELS))]

    def available_days(self) -> list:
        return list(self._LEVELS.keys())


class StandardDifficultyConfig(BaseDifficultyConfig):
    """Standard 3-tier difficulty curve."""  # [O]

    _LEVELS = {
        1: {"label": "⭐  EASY",     "choices": 3, "gap": 5},
        2: {"label": "⭐⭐  MEDIUM",  "choices": 4, "gap": 4},
        3: {"label": "⭐⭐⭐  HARD",  "choices": 5, "gap": 3},
    }


class RushHourDifficultyConfig(BaseDifficultyConfig):
    """Hard-from-day-one difficulty curve for rush-hour mode."""  # [O]

    _LEVELS = {
        1: {"label": "🔥  RUSH EASY",    "choices": 4, "gap": 3},
        2: {"label": "🔥🔥  RUSH MED",   "choices": 5, "gap": 2},
        3: {"label": "🔥🔥🔥  RUSH MAX", "choices": 6, "gap": 1},
    }


# ─────────────────────────────────────────────────────────────────────────────
#  CLOCK
# ─────────────────────────────────────────────────────────────────────────────

class RestaurantClock:
    """Game-time calculation and phase labelling only."""  # [S]

    _PHASE_MAP = [          # [DRY] single source of truth for phase boundaries
        (5,  12, "MORNING 🌅"),
        (12, 17, "AFTERNOON ☀️"),
        (17, 20, "EVENING 🌆"),
    ]

    def __init__(self, start_hour: int = 7):
        self._dilation   = 360
        self._start_real = time.time()
        self._offset     = start_hour * 3600

    def get_game_time(self) -> tuple:
        total = int(((time.time() - self._start_real) * self._dilation
                     + self._offset) // 60)
        return (total // 60) % 24, total % 60

    def get_phase(self, hour: int) -> str:
        for start, end, label in self._PHASE_MAP:
            if start <= hour < end:
                return label
        return "NIGHT 🌙"

    def time_str(self) -> str:
        h, m = self.get_game_time()
        return f"{h:02d}:{m:02d}"


# ─────────────────────────────────────────────────────────────────────────────
#  GROUP FACTORIES
# ─────────────────────────────────────────────────────────────────────────────

class BaseGroupFactory(IGroupFactory):
    """
    [DRY] Shared table/menu storage and set_tables() for all factories.
    Subclasses only override create() and _make_leader().
    [O]   Open for new group types by subclassing.
    """

    def __init__(self, tables: list, menu: list):
        self._tables = tables
        self._menu   = menu

    def set_tables(self, tables: list) -> None:
        self._tables = tables

    @property
    def _max_cap(self) -> int:          # [DRY] computed once, used in create()
        return max(t.capacity for t in self._tables)


class GroupFactory(BaseGroupFactory):
    """Random mixed-group factory: 20 % chance of VIP leader."""  # [O]

    def create(self) -> Group:
        is_vip = random.random() < 0.2
        leader = (VipCustomer(random.choice(VipCustomer.NAMES), random.randint(80, 150))
                  if is_vip else
                  Customer(random.choice(Customer.NAMES), random.randint(15, 50)))
        pizza  = random.choice(self._menu)
        return Group(leader,
                     random.randint(1, self._max_cap),
                     Order(pizza, random.randint(1, self._max_cap)))


class VipNightFactory(BaseGroupFactory):
    """Spawns exclusively VIP groups with larger party sizes."""  # [O] [L]

    def create(self) -> Group:          # [L] same return type as GroupFactory
        leader = VipCustomer(random.choice(VipCustomer.NAMES),
                             random.randint(100, 200))
        pizza  = random.choice(self._menu)
        size   = random.randint(self._max_cap // 2, self._max_cap)
        return Group(leader, size, Order(pizza, size))


# ─────────────────────────────────────────────────────────────────────────────
#  SHIFT SUMMARIES
# ─────────────────────────────────────────────────────────────────────────────

class ShiftSummary(ISummaryDisplay):
    """End-of-day and end-of-shift display only."""  # [S]

    def show_day_end(self, day: int, served: int, score: int) -> None:
        GameUI.clear()
        print("═" * 55)
        print(f"  🌙  END OF DAY {day}")
        print("─" * 55)
        print(f"  Served : {served}")
        print(f"  Score  : {score}")
        print("═" * 55)
        input("\nPress ENTER to continue...")

    def show_shift_end(self, score: int, served: int, staff: list) -> None:
        GameUI.clear()
        print("▓" * 55)
        print("  🌙 SHIFT ENDED")
        print("─" * 55)
        print(f"  Score : {score}")
        print(f"  Served: {served}")
        print("─" * 55)
        for s in staff:
            print(f"  {s}")
        print("▓" * 55)


class QuickSummary(ISummaryDisplay):
    """Compact summary: single line per event, no pause."""  # [O]

    def show_day_end(self, day: int, served: int, score: int) -> None:
        print(f"\n  📋  Day {day} done — Served: {served} | Score: {score}\n")

    def show_shift_end(self, score: int, served: int, staff: list) -> None:
        print(f"\n  🏁  Shift over — Score: {score} | "
              f"Served: {served} | Staff: {len(staff)}\n")


# ─────────────────────────────────────────────────────────────────────────────
#  BRANCH
# ─────────────────────────────────────────────────────────────────────────────

class BranchRegistry(IBranchRepository):
    """Staff, table, and menu registration only."""  # [S]

    def __init__(self, name: str, clock: RestaurantClock):
        self._name:   str  = name
        self._clock         = clock
        self._menu:   list = []
        self._tables: list = []
        self._staff:  list = []

    @property
    def name(self) -> str:    return self._name

    @property
    def menu(self) -> list:   return list(self._menu)

    @property
    def tables(self) -> list: return self._tables

    @property
    def staff(self) -> list:  return list(self._staff)

    @property
    def clock(self):          return self._clock

    def set_menu(self, items: list):
        if not items or not isinstance(items, list):
            raise ValueError("Menu must be a non-empty list.")
        self._menu = items

    def add_table(self, table: Table):    self._tables.append(table)
    def add_staff(self, member: IStaff):  self._staff.append(member)

    def get_staff_by_type(self, staff_type):
        return next((s for s in self._staff if isinstance(s, staff_type)), None)

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


class ReadOnlyBranch(IBranchRepository):
    """
    Frozen branch snapshot — read-only, built from an existing registry.
    [O]  Useful for previews, replays, or testing without mutation risk.
    [L]  All five properties + get_staff_by_type() honour IBranchRepository's contract.
    [D]  Constructor accepts IBranchRepository — not the concrete BranchRegistry.
    """

    def __init__(self, source: IBranchRepository):  # [D]
        self._name   = source.name
        self._menu   = list(source.menu)
        self._tables = list(source.tables)
        self._staff  = list(source.staff)
        self._clock  = source.clock

    @property
    def name(self) -> str:    return self._name

    @property
    def menu(self) -> list:   return list(self._menu)

    @property
    def tables(self) -> list: return list(self._tables)

    @property
    def staff(self) -> list:  return list(self._staff)

    @property
    def clock(self):          return self._clock

    def get_staff_by_type(self, staff_type):
        return next((s for s in self._staff if isinstance(s, staff_type)), None)

    def show_staff(self):
        print(f"\n  👥  Staff at {self._name} (read-only snapshot):")
        for s in self._staff:
            print(f"     {s.introduce()}")
        print()

    def show_tables(self):
        print(f"  🪑  Tables (snapshot):")
        for t in self._tables:
            print(f"     {t}")
        print()


class BranchState:
    """
    Mutable game state (score, served, day, cash) only.
    [S]  One reason to change: what constitutes game state.
    [S]  All attributes are now private with validated properties — encapsulation.
    """

    def __init__(self):
        self._score:           int = 0
        self._served:          int = 0
        self._day:             int = 1
        self._total_collected: int = 0

    # ── Validated properties  [S] ─────────────────────────────────────────────
    @property
    def score(self) -> int: return self._score

    @property
    def served(self) -> int: return self._served

    @property
    def day(self) -> int: return self._day

    @day.setter
    def day(self, value: int):
        if value < 1:
            raise ValueError("Day must be at least 1.")
        self._day = value

    @property
    def total_collected(self) -> int: return self._total_collected

    def add_score(self, pts: int):
        self._score = max(0, self._score + pts)

    def record_served(self, amount_paid: int):
        self._served          += 1
        self._total_collected += amount_paid


# ─────────────────────────────────────────────────────────────────────────────
#  GAME ENGINE
#
#  [S]  One reason to change: how turns are sequenced.
#  [O]  All collaborators are injected — extend by swapping implementations.
#  [D]  Every dependency typed as an abstraction (I* interface).
#  [DRY] _run_duty_phase() eliminates the 4x repeated
#        (show_header → activate_duty → call → reset_busy → handle) pattern.
# ─────────────────────────────────────────────────────────────────────────────

class GameEngine:
    """Game-loop orchestration only."""  # [S]

    def __init__(
        self,
        registry:   IBranchRepository,
        state:      BranchState,
        difficulty: IDifficultyConfig,
        factory:    IGroupFactory,
        summary:    ISummaryDisplay,
    ):
        self._registry   = registry   # [D]
        self._state      = state
        self._difficulty = difficulty # [D]
        self._factory    = factory    # [D]
        self._summary    = summary    # [D]

        self._waiter:  ISeater           = None
        self._chef:    ICook             = None
        self._cashier: IPaymentCollector = None

    def run(self):
        # [D] Look up by interface — HeadWaiter, TraineeCook, SelfCheckout are found
        #     just as correctly as Waiter, Chef, Cashier.
        self._waiter  = self._registry.get_staff_by_type(ISeater)
        self._chef    = self._registry.get_staff_by_type(ICook)
        self._cashier = self._registry.get_staff_by_type(IPaymentCollector)

        if not all([self._waiter, self._chef, self._cashier]):
            print("  ❌  Missing staff! Need an ISeater, ICook, and IPaymentCollector.")
            return

        self._start_shift()

        while self._run_turn():
            pass

        self._summary.show_shift_end(
            self._state.score,
            self._state.served,
            self._registry.staff,
        )

    # ── Turn helpers ──────────────────────────────────────────────────────────

    def _start_shift(self):
        reg = self._registry
        GameUI.clear()
        print("═" * 55)
        print(f"  🍕  {reg.name}")
        print("═" * 55)
        reg.show_staff()
        reg.show_tables()
        print("Waiter  → [1/2/3] pick table")
        print("Chef    → [1/2/3] correct pizza")
        print("Cashier → [G] collect, [1/2/3] change")
        print("═" * 55)
        print("\n  Press ENTER to start the shift!\n")
        input()

    def _run_turn(self) -> bool:
        reg   = self._registry
        state = self._state
        diff  = self._difficulty.for_day(state.day)

        GameUI.clear()
        print("═" * 55)
        print(f"  🍕  {reg.name}  |  {reg.clock.time_str()}")
        print(f"  📅  Day {state.day}  {diff['label']}  |  "
              f"⭐ Score: {state.score}  |  👥 Served: {state.served}")
        print("═" * 55)
        reg.show_tables()
        print(f"  ⏳  Next group in {diff['gap']} seconds... (Q to end shift)\n")
        time.sleep(diff["gap"])

        group = self._factory.create()

        if not self._do_seating(group):  return False
        if group.table is None:          return True
        if not self._do_cooking(group):  return False
        if group.table is None:          return True
        if not self._do_serving(group):  return False
        if not self._do_payment(group):  return False

        self._finalize_turn(group)
        return True

    # ──────────────────────────────────────────────────────────────────────────
    #  _run_duty_phase: Template Method for every duty interaction  [DRY]
    #
    #  Before: _do_seating, _do_cooking, _do_serving, _do_payment each contained
    #          the same (show_header → activate → call action → reset) skeleton,
    #          duplicated four times with trivial differences.
    #
    #  After:  One method handles the skeleton; callers pass the staff member,
    #          their role label, and a lambda for the unique action call.
    # ──────────────────────────────────────────────────────────────────────────
    def _run_duty_phase(self, staff, role_label: str, action_fn) -> tuple:
        """
        Execute one duty phase.
        [DRY] Eliminates the 4x repeated show_header → activate_duty → action
              → reset_busy skeleton.
        Returns the raw tuple from action_fn, or ("QUIT", 0) if the player quits.
        """
        self._show_header(staff.name, role_label)
        print(staff.activate_duty(), "\n")
        result = action_fn()
        if isinstance(staff, IBusyTrackable):   # [I] only reset when trackable
            staff.reset_busy()
        return result

    def _do_seating(self, group) -> bool:
        status, table, pts = self._run_duty_phase(
            self._waiter, "WAITER",
            lambda: self._waiter.seat_group(group, self._registry.tables)
        )
        self._state.add_score(pts)
        return status != "QUIT"

    def _do_cooking(self, group) -> bool:
        diff = self._difficulty.for_day(self._state.day)
        status, pts = self._run_duty_phase(
            self._chef, "CHEF",
            lambda: self._chef.cook(group.order, self._registry.menu, diff["choices"])
        )
        self._state.add_score(pts)
        if status == "QUIT":
            return False
        if status == "WRONG":
            group.table.clear()
        return True

    def _do_serving(self, group) -> bool:
        status, pts = self._run_duty_phase(
            self._waiter, "WAITER",
            lambda: self._waiter.serve_food(group)
        )
        self._state.add_score(pts)
        return status != "QUIT"

    def _do_payment(self, group) -> bool:
        status, pts = self._run_duty_phase(
            self._cashier, "CASHIER",
            lambda: self._cashier.collect_payment(group)
        )
        self._state.add_score(pts)
        return status != "QUIT"

    def _finalize_turn(self, group):
        self._state.record_served(group.order.amount_paid)
        group.table.clear()
        if self._state.served % 5 == 0:
            self._summary.show_day_end(
                self._state.day, self._state.served, self._state.score
            )
            self._state.day += 1

    def _show_header(self, name: str, role: str):
        reg = self._registry
        GameUI.clear()
        GameUI.show_header(reg.name, reg.clock.time_str(), role, name)


# ─────────────────────────────────────────────────────────────────────────────
#  GAME SETUP  — Composition Root
#  [D] The ONLY place concrete types are assembled — all wiring happens here.
#  [S] _build_* methods focus on wiring; UI printing is extracted to _preview_branch.
# ─────────────────────────────────────────────────────────────────────────────

class GameSetup:

    _MENU = ["Margherita", "Pepperoni", "Hawaiian",
             "Veggie", "BBQ Chicken", "Supreme"]   # [DRY] single definition

    _TABLES = [(1, 2), (2, 4), (3, 5)]             # [DRY] single definition

    @staticmethod
    def _pick_mode() -> str:
        print("  Select game mode:\n")
        print("  [1]  Normal     — standard staff and difficulty")
        print("  [2]  Trainee    — easier challenges, no time multiplier")
        print("  [3]  Rush Hour  — VIP crowd, hard difficulty, self-checkout")
        print()
        while True:
            k = input("  > ").strip()
            if k in ("1", "2", "3"):
                return k
            print("  ⚠️  Enter 1, 2, or 3.")

    @staticmethod
    def _get_staff_names(roles: list) -> list:
        """Prompt for each role's name, falling back to the supplied default."""
        print("\n  Enter your staff names:\n")
        names = []
        for role, default in roles:
            print(f"  {role} name  : ", end="", flush=True)
            names.append(input().strip() or default)
        return names

    @staticmethod
    def _make_branch(branch_name: str, start_hour: int,
                     staff: list) -> BranchRegistry:
        """
        [DRY] Single place that builds a BranchRegistry with the shared menu
        and shared table layout — prevents repetition across _build_* methods.
        """
        registry = BranchRegistry(branch_name, RestaurantClock(start_hour))
        registry.set_menu(GameSetup._MENU)
        for num, cap in GameSetup._TABLES:
            registry.add_table(Table(num, cap))
        for member in staff:
            registry.add_staff(member)
        return registry

    @staticmethod
    def _preview_branch(registry: IBranchRepository) -> None:
        """[S] Print-only: show a read-only snapshot before the shift begins."""
        preview: IBranchRepository = ReadOnlyBranch(registry)  # [O] safe snapshot
        GameUI.clear()
        print("═" * 55)
        print(f"  📋  Branch Preview (read-only snapshot)")
        print("═" * 55)
        preview.show_staff()
        preview.show_tables()
        input("  Press ENTER to continue...\n")

    # ── Build methods — each wires a distinct set of concrete classes  [O] ─────

    @staticmethod
    def _build_normal() -> GameEngine:
        waiter_name, chef_name, cashier_name = GameSetup._get_staff_names([
            ("Waiter", "Alex"), ("Chef", "Mario"), ("Cashier", "Birdo")
        ])
        builder: IChallengeBuilder = StandardChallengeBuilder()
        registry = GameSetup._make_branch(
            "Area 1 Pizzeria", 7,
            [Waiter(waiter_name), Chef(chef_name, builder), Cashier(cashier_name, builder)]
        )
        return GameEngine(
            registry, BranchState(),
            StandardDifficultyConfig(),
            GroupFactory(registry.tables, registry.menu),
            ShiftSummary(),
        )

    @staticmethod
    def _build_trainee() -> GameEngine:
        waiter_name, cook_name, cashier_name = GameSetup._get_staff_names([
            ("Waiter", "Alex"), ("Trainee Cook", "Luigi"), ("Cashier", "Birdo")
        ])
        easy_builder: IChallengeBuilder = EasyChallengeBuilder()  # [O] easier options
        registry = GameSetup._make_branch(
            "Area 1 Pizzeria — Trainee Shift", 7,
            [Waiter(waiter_name), TraineeCook(cook_name, easy_builder),  # [O] TraineeCook
             Cashier(cashier_name, easy_builder)]
        )
        return GameEngine(
            registry, BranchState(),
            StandardDifficultyConfig(),
            GroupFactory(registry.tables, registry.menu),
            QuickSummary(),                                               # [O] fast summary
        )

    @staticmethod
    def _build_rush_hour() -> GameEngine:
        head_waiter_name, chef_name = GameSetup._get_staff_names([
            ("Head Waiter", "Rosa"), ("Chef", "Mario")
        ])
        builder: IChallengeBuilder = StandardChallengeBuilder()
        registry = GameSetup._make_branch(
            "Area 1 Pizzeria — Rush Hour", 11,
            [HeadWaiter(head_waiter_name),                 # [O] HeadWaiter
             Chef(chef_name, builder),
             SelfCheckout("Kiosk-1"),                      # [O] SelfCheckout
             GuestStaff("Marco", "Support")]               # [O] GuestStaff
        )
        GameSetup._preview_branch(registry)                # [S] preview separated
        return GameEngine(
            registry, BranchState(),
            RushHourDifficultyConfig(),                    # [O] harder curve
            VipNightFactory(registry.tables, registry.menu),  # [O] VIP-only groups
            ShiftSummary(),
        )

    # ── Composition root ──────────────────────────────────────────────────────

    @staticmethod
    def create_game() -> GameEngine:
        """Composition root — the ONLY place concrete types are assembled."""  # [D]
        GameUI.clear()
        print("═" * 55)
        print("  🍕  PIZZA RESTAURANT SIMULATOR")
        print("═" * 55)
        print()

        mode = GameSetup._pick_mode()
        GameUI.clear()
        print("═" * 55)

        _BUILDERS = {
            "1": ("  🍕  NORMAL MODE",     GameSetup._build_normal),
            "2": ("  🎓  TRAINEE MODE",    GameSetup._build_trainee),
            "3": ("  🔥  RUSH HOUR MODE",  GameSetup._build_rush_hour),
        }
        label, builder_fn = _BUILDERS[mode]   # [DRY] no if/elif chain
        print(label)
        print("═" * 55)
        return builder_fn()
