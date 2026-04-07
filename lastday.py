# ═══════════════════════════════════════════════════════════
# LASTDAY.PY — Game Runner (Entry Point)
# Imports all classes from classes.py
# All setup logic handled by GameSetup class
# ═══════════════════════════════════════════════════════════

from classes import *

if __name__ == "__main__":
    branch = GameSetup.create_branch()
    branch.run_shift()