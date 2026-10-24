"""
Top-level entry point launcher for DSA Defenders.
Delegates directly to dsa_defenders/main.py.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(BASE_DIR, "dsa_defenders")
if PACKAGE_DIR not in sys.path:
    sys.path.insert(0, PACKAGE_DIR)

from dsa_defenders.main import main

if __name__ == "__main__":
    main()
