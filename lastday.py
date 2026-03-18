# ═══════════════════════════════════════════════════════════
# LASTDAY.PY — Main / Logic module
# Imports all classes from classes.py
# Responsible for: setup, object creation, running the game
# ═══════════════════════════════════════════════════════════

from classes import (
    clear, divider,
    NameTag,
    BasePlayer, Chef, Waiter, Cashier,
    Customer, VipCustomer,
    Order, Group, Table,
    RestaurantClock,
    Restaurant, Area1Branch,
)


# ───────────────────────────────────────────────────────────
# SETUP — Creates all objects needed to run the game
# ───────────────────────────────────────────────────────────

def setup():
    """
    Creates and returns a fully configured Area1Branch.
    This function is the only logic that lives in lastday.py —
    object creation and wiring. All game logic lives in classes.py.
    """
    clear()
    divider()
    print(f"  🍕  PIZZA RESTAURANT SIMULATOR")
    divider()
    print(f"\n  Enter your staff names:\n")

    print(f"  Waiter name  : ", end="", flush=True)
    waiter_name  = input().strip() or "Alex"
    print(f"  Chef name    : ", end="", flush=True)
    chef_name    = input().strip() or "Mario"
    print(f"  Cashier name : ", end="", flush=True)
    cashier_name = input().strip() or "Birdo"

    # create the branch object
    branch = Area1Branch("Area 1 Pizzeria")
    branch.set_pizza_menu()

    # add staff objects to the branch
    branch.add_staff(Waiter(waiter_name))
    branch.add_staff(Chef(chef_name))
    branch.add_staff(Cashier(cashier_name))

    # add table objects to the branch
    branch.add_table(Table(1, 2))   # Table 1: 2 seats
    branch.add_table(Table(2, 4))   # Table 2: 4 seats
    branch.add_table(Table(3, 5))   # Table 3: 5 seats

    # attach the clock
    branch.set_clock(RestaurantClock(start_hour=7))

    return branch


# ───────────────────────────────────────────────────────────
# MAIN — Entry point
# ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    branch = setup()    # build all objects
    branch.run_shift()  # run the game — method on the object
