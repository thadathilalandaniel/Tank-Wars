"""
dsa_defenders/config.py

This module contains all global configuration constants, screen parameters,
balance numbers, color palettes, and key bindings for DSA Defenders.
No game state is stored here; all values are static tunables.

Modules that use this:
- game/game_manager.py
- game/wave_manager.py
- game/combat.py
- ui/*
- entities/*
- systems/*
"""

import pygame

# ---------------------------------------------------------
# SCREEN & DISPLAY SETTINGS
# ---------------------------------------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Tank Wars - Tactical Tower Defense"

# Arena Boundary (Tower movement and enemy target area)
# Playable arena sits between HUD top (height ~70px) and Upgrade tray bottom (height ~140px)
ARENA_LEFT = 100
ARENA_RIGHT = 1180
ARENA_TOP = 80
ARENA_BOTTOM = 570
ARENA_WIDTH = ARENA_RIGHT - ARENA_LEFT
ARENA_HEIGHT = ARENA_BOTTOM - ARENA_TOP

# ---------------------------------------------------------
# COLOR PALETTE (Vibrant Cartoon / Tiny Towers Aesthetic)
# ---------------------------------------------------------
# Background colors (Geometric layered blues)
COLOR_BG_SKY = (77, 168, 235)
COLOR_BG_DEEP = (44, 122, 192)
COLOR_BG_LIGHT = (108, 187, 248)
COLOR_BG_TILE = (95, 178, 240)
COLOR_BG_TILE_ALT = (65, 150, 220)

# Arena Frame & Borders
COLOR_ARENA_BORDER = (30, 85, 145)
COLOR_ARENA_BORDER_DARK = (18, 50, 90)

# Tower
COLOR_TOWER_BASE = (216, 27, 96)        # Vibrant magenta/pink
COLOR_TOWER_BASE_SHADOW = (156, 12, 64)
COLOR_TOWER_OUTLINE = (28, 28, 40)
COLOR_TOWER_TURRET = (255, 255, 255)
COLOR_TOWER_TURRET_TRIM = (255, 64, 129)
COLOR_TOWER_BARREL = (40, 40, 55)

# Range Ring
COLOR_RANGE_FILL = (255, 255, 255, 30)
COLOR_RANGE_BORDER = (220, 245, 255, 160)

# Enemies
COLOR_ENEMY_SCOUT = (102, 187, 106)      # Cute vibrant green
COLOR_ENEMY_SCOUT_DARK = (56, 142, 60)
COLOR_ENEMY_RUNNER = (255, 214, 0)       # Energetic yellow
COLOR_ENEMY_RUNNER_DARK = (245, 127, 23)
COLOR_ENEMY_TANK = (239, 83, 80)         # Crimson heavy armor
COLOR_ENEMY_TANK_DARK = (183, 28, 28)
COLOR_ENEMY_BOSS = (171, 71, 188)        # Royal purple boss
COLOR_ENEMY_BOSS_DARK = (106, 27, 154)

# Projectiles & Effects
COLOR_PROJECTILE = (255, 235, 59)
COLOR_PROJECTILE_OUTLINE = (230, 81, 0)
COLOR_DAMAGE_TEXT = (255, 255, 255)
COLOR_DAMAGE_CRIT = (255, 82, 82)
COLOR_COIN_TEXT = (255, 223, 0)

# Shields & Powers
COLOR_SHIELD_BUBBLE = (0, 229, 255, 75)
COLOR_SHIELD_BORDER = (0, 229, 255, 200)
COLOR_BLAST_RING = (255, 171, 0)

# UI & HUD
COLOR_HUD_BG = (26, 42, 70)
COLOR_HUD_PANEL = (35, 58, 96)
COLOR_HUD_BORDER = (15, 25, 45)
COLOR_COIN_GOLD = (255, 215, 0)
COLOR_COIN_DARK = (190, 150, 0)
COLOR_HEART_RED = (244, 67, 54)
COLOR_HEART_OUTLINE = (183, 28, 28)

# Cards & Buttons
COLOR_CARD_BG = (50, 70, 102)
COLOR_CARD_BG_HOVER = (68, 94, 135)
COLOR_CARD_BG_DISABLED = (38, 48, 66)
COLOR_CARD_OUTLINE = (22, 32, 50)
COLOR_CARD_AFFORDABLE_BADGE = (76, 175, 80)
COLOR_CARD_UNAFFORDABLE_BADGE = (211, 47, 47)

# Text & Typography (Tiny Towers Rounded Bubble Style)
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_TEXT_MUTED = (180, 195, 215)
COLOR_TEXT_DARK = (25, 25, 35)

FONT_FAMILY_PREFERENCES = ["arialrounded", "sfnsrounded", "sfcompactrounded", "arialblack", "arial"]

def get_font(font_cache: dict, size: int, bold: bool = True) -> pygame.font.Font:
    """Retrieve or create a cached bold rounded cartoon font."""
    key = (size, bold)
    if key in font_cache:
        return font_cache[key]
    
    font_obj = None
    for name in FONT_FAMILY_PREFERENCES:
        try:
            font_obj = pygame.font.SysFont(name, size, bold=bold)
            if font_obj:
                break
        except Exception:
            continue
    if font_obj is None:
        font_obj = pygame.font.SysFont(None, size, bold=bold)
        
    font_cache[key] = font_obj
    return font_obj

# ---------------------------------------------------------
# TOWER BALANCE & STATS
# ---------------------------------------------------------
TOWER_INITIAL_X = SCREEN_WIDTH // 2
TOWER_INITIAL_Y = 325
TOWER_RADIUS = 26
TOWER_MOVE_SPEED = 280.0       # Pixels per second
TOWER_INITIAL_RANGE = 230.0    # Attack radius in pixels
TOWER_BASE_DAMAGE = 15.0
TOWER_BASE_FIRE_COOLDOWN = 0.55  # Seconds per shot (approx 1.82 shots/s)
TOWER_MIN_FIRE_COOLDOWN = 0.12   # Maximum attack speed cap
TOWER_INITIAL_HEARTS = 5
TOWER_MAX_HEARTS = 10

# ---------------------------------------------------------
# ECONOMY & INITIAL RESOURCES
# ---------------------------------------------------------
INITIAL_COINS = 25

# Upgrade Base Costs and Multipliers
UPGRADE_ATTACK_BASE_COST = 15
UPGRADE_ATTACK_COST_MULT = 1.55
UPGRADE_ATTACK_DMG_INC = 7.0

UPGRADE_SPEED_BASE_COST = 12
UPGRADE_SPEED_COST_MULT = 1.50
UPGRADE_SPEED_CD_DEC = 0.045

UPGRADE_SHIELD_BASE_COST = 20
UPGRADE_SHIELD_COST_MULT = 1.50
SHIELD_CAPACITY_MAX = 100
SHIELD_RECHARGE_AMOUNT = 35

UPGRADE_HEART_BASE_COST = 25
UPGRADE_HEART_COST_MULT = 1.70

# Emergency Blast Power
BLAST_BASE_COST = 30
BLAST_COST_MULT = 1.75
BLAST_BASE_DAMAGE = 120.0
BLAST_COOLDOWN = 12.0  # Seconds between charges

# ---------------------------------------------------------
# WAVE SYSTEM & DIFFICULTY
# ---------------------------------------------------------
TOTAL_WAVES = 40
SPAWN_INTERVAL_INITIAL = 1.45  # Seconds between spawns at wave 1
SPAWN_INTERVAL_MIN = 0.38      # Minimum spawn interval at wave 40
WAVE_INTERMISSION_TIME = 2.5   # Seconds before auto wave start or result

# Enemy Types:
ENEMY_TYPE_SCOUT = "scout"
ENEMY_TYPE_RUNNER = "runner"
ENEMY_TYPE_TANK = "tank"
ENEMY_TYPE_BOSS = "boss"

# Base Enemy Stats (scaled by wave number)
ENEMY_STATS = {
    ENEMY_TYPE_SCOUT: {
        "name": "Scout Drone",
        "radius": 18,
        "base_hp": 25.0,
        "base_speed": 75.0,
        "damage": 1,
        "coin_reward": 5,
        "type_bonus": 10.0,
        "color": COLOR_ENEMY_SCOUT,
        "outline": COLOR_ENEMY_SCOUT_DARK,
    },
    ENEMY_TYPE_RUNNER: {
        "name": "Spark Runner",
        "radius": 15,
        "base_hp": 16.0,
        "base_speed": 135.0,
        "damage": 1,
        "coin_reward": 7,
        "type_bonus": 20.0,
        "color": COLOR_ENEMY_RUNNER,
        "outline": COLOR_ENEMY_RUNNER_DARK,
    },
    ENEMY_TYPE_TANK: {
        "name": "Goliath Tank",
        "radius": 26,
        "base_hp": 90.0,
        "base_speed": 45.0,
        "damage": 2,
        "coin_reward": 15,
        "type_bonus": 35.0,
        "color": COLOR_ENEMY_TANK,
        "outline": COLOR_ENEMY_TANK_DARK,
    },
    ENEMY_TYPE_BOSS: {
        "name": "Apex Overseer",
        "radius": 36,
        "base_hp": 380.0,
        "base_speed": 35.0,
        "damage": 3,
        "coin_reward": 60,
        "type_bonus": 120.0,
        "color": COLOR_ENEMY_BOSS,
        "outline": COLOR_ENEMY_BOSS_DARK,
    },
}

# ---------------------------------------------------------
# TARGETING MODES
# ---------------------------------------------------------
TARGET_MODE_QUEUE = "QUEUE"
TARGET_MODE_HEAP = "PRIORITY_QUEUE"
TARGET_MODE_GREEDY = "GREEDY"

# ---------------------------------------------------------
# GAME SPEEDS
# ---------------------------------------------------------
SPEED_1X = 1.0
SPEED_2X = 2.0
SPEED_3X = 3.0

# ---------------------------------------------------------
# DEBUG & TESTING FLAGS
# ---------------------------------------------------------
# Set to True to unlock all 40 waves immediately in the wave select screen
UNLOCK_ALL_WAVES = False
# Start wave override (1 to 40)
START_WAVE_OVERRIDE = 1
