# ═════════════════════════════════════════════
# PIZZALOGIC.PY — Single terminal, 3-role game
# Waiter → Chef → Cashier per customer group
# ═════════════════════════════════════════════

import os, sys, time, random

# ─────────────────────────────────────────────
# DIFFICULTY
# ─────────────────────────────────────────────
DIFFICULTY = {
    1: {"label": "⭐  EASY",      "num_choices": 3, "arrival_gap": 5},
    2: {"label": "⭐⭐  MEDIUM",   "num_choices": 4, "arrival_gap": 4},
    3: {"label": "⭐⭐⭐  HARD",   "num_choices": 5, "arrival_gap": 3},
}
PIZZA_PRICES = {
    "Margherita": 8,  "Pepperoni": 10, "Hawaiian": 9,
    "Veggie": 7,      "BBQ Chicken": 11, "Supreme": 12,
}
CUSTOMER_NAMES = ["Luigi","Yoshi","Koopa","Shy Guy","Toad Jr.",
                  "Boo","Birdo","Lakitu","Bullet Bill","Bob-omb"]
VIP_NAMES      = ["Peach","Daisy","Rosalina","Pauline"]
ALL_PIZZAS     = list(PIZZA_PRICES.keys())

# Table definitions: table_number → capacity
TABLES = {1: 2, 2: 4, 3: 5}

def get_diff(day):
    return DIFFICULTY[min(day, 3)]


# ─────────────────────────────────────────────
# TERMINAL HELPERS
# ─────────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")

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

def divider(char="═", width=55):
    print(f"  {char*width}")

def header(role_label, day, diff, score, served, clock_str, phase):
    clear()
    divider()
    print(f"  🍕  PIZZA RESTAURANT  |  {clock_str}  {phase}")
    print(f"  📅  Day {day}  {diff['label']}  |  ⭐ Score: {score}  |  👥 Served: {served}")
    divider()
    print(f"\n  👤  Current Role: {role_label}\n")

def show_tables(occupied):
    """
    occupied = dict {table_number: group_size or 0 if empty}
    """
    print(f"  🪑  Tables:")
    for tnum, cap in TABLES.items():
        seats_taken = occupied.get(tnum, 0)
        status = f"occupied ({seats_taken}/{cap})" if seats_taken > 0 else "empty"
        avail  = "❌" if seats_taken > 0 else "✅"
        print(f"     [{tnum}] Table {tnum}  —  cap {cap}  {avail}  {status}")
    print()

def show_group(cust):
    icon  = "👑" if cust["role"] == "VipCustomer" else "🧑"
    group = cust["group_size"]
    print(f"  {icon}  Group leader : {cust['name']}  [{cust['role']}]")
    print(f"     Group size  : {group} person{'s' if group > 1 else ''}")
    print(f"     Order       : {cust['pizza']}  x{group}")
    print(f"     Price each  : ${cust['unit_price']}")
    print(f"     Total bill  : ${cust['total_price']}")
    print()

def score_for_speed(elapsed, base=5, max_bonus=5, time_limit=6):
    """Under 1s = full bonus, ~3s = half, 6s+ = none."""
    ratio = 1.0 if elapsed <= 1 else max(0.0, 1 - ((elapsed - 1) / (time_limit - 1)))
    bonus = int(max_bonus * ratio)
    return base + bonus, bonus

def make_choices(correct, all_options, num):
    wrong   = [x for x in all_options if x != correct]
    random.shuffle(wrong)
    options = wrong[:num - 1] + [correct]
    random.shuffle(options)
    return options

def print_choices(options):
    divider("─")
    for i, opt in enumerate(options):
        print(f"  [{i+1}]  {opt}")
    divider("─")
    print()


# ─────────────────────────────────────────────
# CUSTOMER GROUP GENERATOR
# ─────────────────────────────────────────────
def make_customer(menu):
    is_vip     = random.random() < 0.2
    name       = random.choice(VIP_NAMES if is_vip else CUSTOMER_NAMES)
    pizza      = random.choice(menu)
    unit_price = PIZZA_PRICES.get(pizza, 10)
    # group size: 1 up to max table capacity
    max_cap    = max(TABLES.values())
    group_size = random.randint(1, max_cap)
    total      = unit_price * group_size
    paid       = total + random.choice([0, 1, 2, 5, 10])
    return {
        "name":        name,
        "role":        "VipCustomer" if is_vip else "Customer",
        "pizza":       pizza,
        "group_size":  group_size,
        "unit_price":  unit_price,
        "total_price": total,
        "paid":        paid,
        "change":      paid - total,
        "table":       None,   # assigned by waiter
    }


# ─────────────────────────────────────────────
# STAGE 1 — WAITER: choose table & seat group
# ─────────────────────────────────────────────
def stage_waiter_seat(cust, waiter, day, diff, score, served,
                      clock_str, phase, occupied):
    while True:
        header(f"🍽️  WAITER  —  {waiter}", day, diff, score, served, clock_str, phase)
        title = "Ma'am" if cust["role"] == "VipCustomer" else "Sir"
        group = cust["group_size"]

        print(f"  🚶 Group arrived! Leader: {cust['name']}  "
              f"({group} person{'s' if group > 1 else ''})")
        print(f"  [{waiter}]: Welcome to Area 1 Pizzeria, "
              f"{title} {cust['name']}!\n")
        print(f"  They want: {cust['pizza']} x{group}\n")
        show_tables(occupied)

        # find tables that can fit the group
        available = {n: c for n, c in TABLES.items()
                     if occupied.get(n, 0) == 0 and c >= group}

        if not available:
            print(f"  ⚠️  No table available for a group of {group}! "
                  f"They are waiting...\n")
            print(f"  Press any key to check again, or [Q] to quit.")
            k = getch()
            if k == "q":
                return "QUIT", score, occupied
            continue

        print(f"  Group of {group} — pick an available table "
              f"(must fit {group}+):\n")
        # show only valid choices
        valid_keys = []
        for tnum, cap in TABLES.items():
            fits   = cap >= group
            empty  = occupied.get(tnum, 0) == 0
            marker = "✅ pick" if (fits and empty) else \
                     ("❌ full" if not empty else "❌ too small")
            print(f"  [{tnum}]  Table {tnum}  (cap {cap})  —  {marker}")
            if fits and empty:
                valid_keys.append(str(tnum))
        print()
        print(f"  Press [{'/'.join(valid_keys)}] to seat them.")

        t_start = time.time()
        k = getch()
        if k == "q":
            return "QUIT", score, occupied
        if k not in valid_keys:
            # check if it's a real table number (just wrong size/full)
            if k in [str(n) for n in TABLES.keys()]:
                score = max(0, score - 15)
                print(f"\n  ❌  Wrong table! That table can't fit this group. (-15 pts)\n")
            else:
                print(f"\n  ⚠️  Invalid key. Press a table number.\n")
            time.sleep(1.5)
            continue

        # seat them
        chosen_table = int(k)
        occupied[chosen_table] = group
        cust["table"] = chosen_table

        elapsed = time.time() - t_start
        pts, bonus = score_for_speed(elapsed)
        score += pts
        bonus_str = f" +{bonus} speed bonus!" if bonus > 0 else ""
        print(f"\n  ✅  Group of {group} seated at Table {chosen_table}! "
              f"(+{pts} pts{bonus_str})\n")
        time.sleep(1)
        return "OK", score, occupied


# ─────────────────────────────────────────────
# STAGE 2 — CHEF: cook the correct pizza
# ─────────────────────────────────────────────
def stage_chef_cook(cust, chef, day, diff, score, served, clock_str, phase):
    num     = diff["num_choices"]
    group   = cust["group_size"]
    options = make_choices(cust["pizza"], ALL_PIZZAS, num)
    correct_idx = options.index(cust["pizza"])
    t_start = time.time()

    while True:
        header(f"👨‍🍳  CHEF  —  {chef}", day, diff, score, served, clock_str, phase)
        show_group(cust)
        print(f"  🍳  Order in!  Cook: {cust['pizza']} x{group}\n")
        print_choices(options)
        print(f"  Press the number of the correct pizza.")

        k = getch()
        if k == "q":
            return "QUIT", score
        try:
            chosen = int(k) - 1
        except ValueError:
            continue
        if chosen < 0 or chosen >= len(options):
            continue

        if chosen == correct_idx:
            elapsed = time.time() - t_start
            pts, bonus = score_for_speed(elapsed)
            score += pts
            bonus_str = f" +{bonus} speed bonus!" if bonus > 0 else ""
            print(f"\n  ✅  Correct! {cust['pizza']} x{group} is cooking! "
                  f"(+{pts} pts{bonus_str})\n")
            time.sleep(1.5)
            return "OK", score
        else:
            score = max(0, score - 15)
            print(f"\n  ❌  Wrong pizza! {cust['name']}'s group got the "
                  f"wrong order and LEFT! (-15 pts)\n")
            time.sleep(2)
            return "LEFT", score


# ─────────────────────────────────────────────
# STAGE 3 — WAITER: serve the food
# ─────────────────────────────────────────────
def stage_waiter_serve(cust, waiter, day, diff, score, served, clock_str, phase):
    header(f"🍽️  WAITER  —  {waiter}", day, diff, score, served, clock_str, phase)
    show_group(cust)
    print(f"  🍕  {cust['pizza']} x{cust['group_size']} is ready!")
    print(f"  Press [S] to serve Table {cust['table']}.")
    t_start = time.time()
    while True:
        k = getch()
        if k == "s":
            elapsed = time.time() - t_start
            pts, bonus = score_for_speed(elapsed)
            score += pts
            bonus_str = f" +{bonus} speed bonus!" if bonus > 0 else ""
            print(f"\n  ✅  Served to Table {cust['table']}! "
                  f"(+{pts} pts{bonus_str})\n")
            time.sleep(1.5)
            return "OK", score
        elif k == "q":
            return "QUIT", score


# ─────────────────────────────────────────────
# STAGE 4 — CASHIER: collect & give change
# ─────────────────────────────────────────────
def stage_cashier_pay(cust, cashier, day, diff, score, served, clock_str, phase):
    total  = cust["total_price"]
    paid   = cust["paid"]
    change = cust["change"]
    group  = cust["group_size"]

    # Step A — press G to collect
    header(f"💰  CASHIER  —  {cashier}", day, diff, score, served, clock_str, phase)
    show_group(cust)
    print(f"  💵  Table {cust['table']} finished eating!")
    print(f"     {cust['pizza']} x{group} @ ${cust['unit_price']} each")
    print(f"     Total bill : ${total}")
    print(f"     Paid       : ${paid}")
    print(f"\n  Press [G] to collect payment.")
    while True:
        k = getch()
        if k == "g":
            print(f"\n  ✅  Payment collected!")
            print(f"  💵  Received : ${paid}")
            print(f"  🧾  Bill was : ${total}\n")
            time.sleep(1.5)
            break
        elif k == "q":
            return "QUIT", score

    # Step B — give correct change (1 correct, 2 wrong)
    header(f"💰  CASHIER  —  {cashier}", day, diff, score, served, clock_str, phase)
    show_group(cust)
    print(f"  💵  Total bill: ${total}  |  Paid: ${paid}\n")

    t_start = time.time()
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

    print(f"  Pick the correct change to give back:\n")
    print_choices(options)
    print(f"  Press the number of the correct change.")

    while True:
        k = getch()
        if k == "q":
            return "QUIT", score
        try:
            chosen = int(k) - 1
        except ValueError:
            continue
        if chosen < 0 or chosen >= len(options):
            continue

        if chosen == correct_idx:
            elapsed   = time.time() - t_start
            pts, bonus = score_for_speed(elapsed)
            score    += pts
            bonus_str = f" +{bonus} speed bonus!" if bonus > 0 else ""
            tip       = random.randint(1, 10) if cust["role"] == "VipCustomer" \
                        else random.randint(1, 5)
            tip_label = "VIP tip" if cust["role"] == "VipCustomer" else "tip"
            score    += tip
            print(f"\n  ✅  Correct change! (+{pts} pts{bonus_str})")
            print(f"  💰  {cust['name']} left a {tip_label}: +{tip} pts\n")
        else:
            score = max(0, score - 15)
            print(f"\n  ❌  Wrong change! Correct was "
                  f"{options[correct_idx]}. (-15 pts)\n")
        time.sleep(1.5)
        return "OK", score


# ─────────────────────────────────────────────
# DAY SUMMARY
# ─────────────────────────────────────────────
def day_summary(day, diff, score, served, total_collected):
    clear()
    divider()
    print(f"  🌙  END OF DAY {day} SHIFT  —  {diff['label']}")
    divider("─")
    print(f"  Groups served    : {served}")
    print(f"  Money collected  : ${total_collected}")
    print(f"  Total score      : {score} pts")
    if day < 3:
        nd = DIFFICULTY[day + 1]
        print(f"\n  ⚠️  Tomorrow: {nd['label']}")
        print(f"  Choices: {nd['num_choices']}  |  "
              f"Arrival gap: {nd['arrival_gap']}s")
    divider()
    print(f"\n  Rest up! Press ENTER to start Day {day + 1} shift...")
    input()


# ─────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────
def run_game(branches, clock):
    menu = next(b.menu for b in branches if "Area 1" in b.name)

    clear()
    divider()
    print(f"  🍕  PIZZA RESTAURANT SIMULATOR")
    divider()
    print(f"  Tables:  Table 1 (2 seats)  |  "
          f"Table 2 (4 seats)  |  Table 3 (5 seats)")
    print(f"\n  You play all 3 roles per group:")
    print(f"  🍽️  Waiter  → [1/2/3] pick table, [T] seat group")
    print(f"  👨‍🍳  Chef    → [1/2/3] correct pizza (wrong = group leaves)")
    print(f"  💰  Cashier → [G] collect, [1/2/3] correct change")
    print(f"\n  Speed bonus: <1s = full  |  ~3s = half  |  6s+ = none")
    print(f"  Wrong key  : -15 pts")
    print(f"  Tip: Regular 1–5 pts  |  VIP 1–10 pts")
    print(f"  Day advances every 5 groups served.")
    divider()

    print(f"\n  Waiter name  : ", end="", flush=True)
    waiter  = input().strip() or "Alex"
    print(f"  Chef name    : ", end="", flush=True)
    chef    = input().strip() or "Mario"
    print(f"  Cashier name : ", end="", flush=True)
    cashier = input().strip() or "Birdo"

    print(f"\n  Press ENTER to start!\n")
    input()

    score           = 0
    served          = 0
    day             = 1
    total_collected = 0              # total money received from customers
    occupied        = {1: 0, 2: 0, 3: 0}   # table_number → group_size seated (0 = empty)

    while True:
        diff      = get_diff(day)
        clock_str = clock.time_str()
        h, _      = clock.get_game_time()
        phase     = clock.get_phase(h)

        # arrival gap screen
        clear()
        divider()
        print(f"  🍕  PIZZA RESTAURANT  |  {clock_str}  {phase}")
        print(f"  📅  Day {day}  {diff['label']}  |  "
              f"⭐ Score: {score}  |  👥 Served: {served}")
        divider()
        show_tables(occupied)
        print(f"  ⏳  Next group arriving in {diff['arrival_gap']} seconds...")
        print(f"  (Press Q anytime during an action to quit)\n")
        time.sleep(diff["arrival_gap"])

        cust = make_customer(menu)

        # Stage 1: Waiter picks table & seats group
        status, score, occupied = stage_waiter_seat(
            cust, waiter, day, diff, score, served, clock_str, phase, occupied)
        if status == "QUIT": break

        # Stage 2: Chef cooks
        status, score = stage_chef_cook(
            cust, chef, day, diff, score, served, clock_str, phase)
        if status == "QUIT": break
        if status == "LEFT":
            occupied[cust["table"]] = 0   # free the table
            continue

        # Stage 3: Waiter serves
        status, score = stage_waiter_serve(
            cust, waiter, day, diff, score, served, clock_str, phase)
        if status == "QUIT": break

        # Stage 4: Cashier collects & gives change
        status, score = stage_cashier_pay(
            cust, cashier, day, diff, score, served, clock_str, phase)
        if status == "QUIT": break

        # track money collected
        total_collected += cust["paid"]

        # free the table after group leaves
        occupied[cust["table"]] = 0
        served += 1

        # day progression every 5 served
        if served % 5 == 0:
            day_summary(day, diff, score, served, total_collected)
            day += 1

    # final screen
    clear()
    divider("▓")
    print(f"  🌙  SHIFT ENDED — Time to clock out!")
    divider("─")
    print(f"  Days worked      : {day}")
    print(f"  Groups served    : {served}")
    print(f"  Total collected  : ${total_collected}")
    print(f"  Final Score      : {score} pts")
    divider("─")
    if   score >= 500: print(f"  🥇  LEGENDARY STAFF — Unstoppable!")
    elif score >= 300: print(f"  🥈  STAR CREW — Incredible work!")
    elif score >= 180: print(f"  🥉  SOLID SHIFT — Well done!")
    elif score >= 80:  print(f"  🎖️   DECENT SHIFT — Keep it up!")
    else:              print(f"  😅  ROUGH SHIFT — Better luck next time!")
    divider("▓")
    print(f"  See you next shift! 👋\n")