# ═════════════════════════════════════════════
# PIZZALOGIC.PY — Game Logic Functions
# No classes here. All classes live in lastday.py
# This module handles: branch rules, customer
# routing, and the main game loop simulation.
# ═════════════════════════════════════════════
 
import time
import sys
import random
 
 
# ─────────────────────────────────────────────
# BRANCH SCHEDULE RULES
# ─────────────────────────────────────────────
 
def is_branch_open(branch_name, hour):
    """
    Area 1  → open 24/7
    Area F  → open 10:00 - 21:00
    Area G  → open 10:00 - 21:00
    """
    if "Area 1" in branch_name:
        return True
    if "Area F" in branch_name or "Area G" in branch_name:
        return 10 <= hour < 21
    return False
 
 
def get_open_branches(branches, hour):
    """Return list of branches that are currently open."""
    return [b for b in branches if is_branch_open(b.name, hour)]
 
 
# ─────────────────────────────────────────────
# CUSTOMER ROUTING
# ─────────────────────────────────────────────
 
def route_customer(customer, open_branches):
    """
    Send customer to a random open branch.
    VIP customers prefer Area 1 if it's open.
    Returns (branch, message) tuple.
    """
    if not open_branches:
        return None, f"{customer.name_tag.display()} found no open branches and left."
 
    role = customer.name_tag.role
    if role == "VipCustomer":
        vip_pref = [b for b in open_branches if "Area 1" in b.name]
        chosen = vip_pref[0] if vip_pref else random.choice(open_branches)
    else:
        chosen = random.choice(open_branches)
 
    available_tables = [t for t in chosen.tables if t.is_available]
    if not available_tables:
        return chosen, f"{customer.name_tag.display()} ➜ {chosen.name} (full, waiting outside)"
 
    table = random.choice(available_tables)
    msg = table.seat_customer(customer)
    return chosen, msg
 
 
# ─────────────────────────────────────────────
# STAFF ACTIVITY FEED
# ─────────────────────────────────────────────
 
def print_branch_activity(branch, clock_str, hour):
    """Print a live activity line for every staff member and customer count."""
    open_flag = "🟢 OPEN  " if is_branch_open(branch.name, hour) else "🔴 CLOSED"
    seated_total = sum(len(t.seated) for t in branch.tables)
 
    print(f"\n  ┌─ {clock_str} | {branch.name} [{open_flag}]")
 
    if is_branch_open(branch.name, hour):
        for member in branch.staff:
            duty = member.perform_primary_duty()
            print(f"  │  ✔ {duty}")
        print(f"  │  👥 Customers inside: {seated_total}")
    else:
        print(f"  │  💤 All staff resting. No customers.")
 
    print(f"  └{'─'*45}")
 
 
# ─────────────────────────────────────────────
# BRANCH STATUS BANNER
# ─────────────────────────────────────────────
 
def print_branch_status(branches, hour):
    print(f"\n  {'─'*51}")
    for branch in branches:
        open_flag = "🟢 OPEN  " if is_branch_open(branch.name, hour) else "🔴 CLOSED"
        seated_total = sum(len(t.seated) for t in branch.tables)
        capacity_total = sum(t.capacity for t in branch.tables)
        print(f"  {open_flag} | {branch.name:<22} | 👥 {seated_total}/{capacity_total} seated")
    print(f"  {'─'*51}")
 
 
# ─────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────
 
def run_game(branches, customers, clock):
    """
    Main game loop. Runs until a full 24-hr game day is complete.
    - Clock starts at 07:00
    - Area F + Area G open at 10:00, close at 21:00
    - Area 1 is open 24/7
    - Every tick: prints what each branch/staff is doing
    - Customers arrive at open branches continuously
    """
 
    print(f"\n  {'═'*51}")
    print(f"  🍕  PIZZA RESTAURANT SIMULATION STARTED")
    print(f"  {'═'*51}")
    for b in branches:
        tag = "24/7" if "Area 1" in b.name else "10:00 - 21:00"
        print(f"  • {b.name:<25} Hours: {tag}")
        print(f"    Menu  : {', '.join(b.menu)}")
        staff_names = ", ".join(s.name_tag.name for s in b.staff)
        print(f"    Staff : {staff_names}")
    print(f"  {'═'*51}\n")
    time.sleep(1.5)
 
    last_open_set       = set()
    last_phase          = None
    customer_index      = 0
    tick                = 0
 
    try:
        while True:
            h, m = clock.get_game_time()
            clock_str   = f"🕐 {h:02d}:{m:02d}"
            phase       = clock.get_phase(h)
            current_open = set(b.name for b in get_open_branches(branches, h))
 
            # ── Announce phase / open / close changes ──
            if phase != last_phase:
                print(f"\n\n  {'━'*51}")
                print(f"  ⏰  {clock_str}  —  {phase}")
                print(f"  {'━'*51}")
                last_phase = phase
 
            for branch in branches:
                just_opened = branch.name in current_open and branch.name not in last_open_set
                just_closed = branch.name not in current_open and branch.name in last_open_set
                if just_opened:
                    print(f"\n  🟢 {branch.name} just OPENED! Staff on duty:")
                    for s in branch.staff:
                        print(f"     → {s.perform_primary_duty()}")
                elif just_closed:
                    print(f"\n  🔴 {branch.name} just CLOSED. Clearing customers.")
                    for table in branch.tables:
                        table.seated.clear()
 
            last_open_set = current_open
 
            # ── Every tick: print activity for ALL branches ──
            print(f"\n  {'·'*51}")
            print(f"  {clock_str}  |  {phase}")
 
            for branch in branches:
                open_flag    = "🟢 OPEN  " if is_branch_open(branch.name, h) else "🔴 CLOSED"
                seated_total = sum(len(t.seated) for t in branch.tables)
                cap_total    = sum(t.capacity    for t in branch.tables)
 
                print(f"\n  ┌─ {branch.name}  [{open_flag}]")
 
                if is_branch_open(branch.name, h):
                    # Staff activity
                    for member in branch.staff:
                        duty = member.perform_primary_duty()
                        print(f"  │  ✔ {duty}")
 
                    # Route a customer to this branch this tick
                    cust = customers[customer_index % len(customers)]
                    _, seat_msg = route_customer(cust, [branch])
                    print(f"  │  🚶 {cust.name_tag.display()} arrived  →  {seat_msg}")
                    customer_index += 1
 
                    # Show current customer count
                    seated_now = sum(len(t.seated) for t in branch.tables)
                    print(f"  │  👥 Total customers inside: {seated_now}/{cap_total}")
 
                else:
                    print(f"  │  💤 Closed — staff resting, no customers.")
 
                print(f"  └{'─'*45}")
 
            # ── End of day check ──
            elapsed_real = time.time() - clock.start_real_time
            if elapsed_real >= (24 * 3600 / clock.time_dilation):
                print(f"\n\n  {'═'*51}")
                print(f"  🌙  End of day! Final status:")
                print_branch_status(branches, h)
                print(f"  Thanks for playing. See you tomorrow!")
                print(f"  {'═'*51}\n")
                break
 
            tick += 1
            # Sleep ~2 real seconds between ticks (= ~12 game minutes per tick)
            time.sleep(2)
 
    except KeyboardInterrupt:
        print(f"\n\n  {'═'*51}")
        print(f"  🛑  Game interrupted at {clock_str}")
        print_branch_status(branches, h)
        print(f"  {'═'*51}\n")
