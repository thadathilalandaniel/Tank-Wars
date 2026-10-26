"""
defense_defenders/main.py

Primary entry point for Defense Defenders. Initializes Pygame subsystems, constructs
the master GameManager instance, and enters the 60 FPS main game loop.
"""

import os
import sys

# Ensure defense_defenders directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import pygame
from game.game_manager import GameManager


def main():
    """Initialize Pygame subsystems and start the game loop."""
    pygame.init()
    pygame.font.init()
    game = GameManager()
    game.run()


if __name__ == "__main__":
    main()

