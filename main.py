"""
main.py (Root Launcher)

Entry point launcher for DSA Defenders. Sets up sys.path and delegates directly
to dsa_defenders/main.py when executed from the project root.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(BASE_DIR, "dsa_defenders")

# Add 'dsa_defenders' to sys.path so package modules resolve cleanly
if PACKAGE_DIR not in sys.path:
    sys.path.insert(0, PACKAGE_DIR)

from dsa_defenders.main import main

if __name__ == "__main__":
    main()

