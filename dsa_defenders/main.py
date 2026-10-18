"""
dsa_defenders/main.py

Entry point for DSA Defenders.
Initializes pygame, creates the master GameManager instance, and starts the main loop.
"""

import os
import sys

# Ensure dsa_defenders folder is on sys.path so modules resolve cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import pygame
from game.game_manager import GameManager


def main():
    """Initialize pygame and launch DSA Defenders."""
    pygame.init()
    pygame.font.init()
    game = GameManager()
    game.run()


if __name__ == "__main__":
    main()
