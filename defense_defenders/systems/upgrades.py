"""
defense_defenders/systems/upgrades.py

This module manages the player's stat upgrades:
1. Attack Power: Increases damage per shot.
2. Shooting Speed: Decreases fire cooldown timer (capped at a minimum).
3. Extra Hearts: Grants an extra life, capped at MAX_HEARTS.

Each upgrade computes dynamic costs, interacts with EconomySystem,
and updates the player's Tower entity.

Modules that interact with this:
- entities/tower.py (receives stat boosts)
- systems/economy.py (processes coin deductions)
- entities/effects.py (spawns purchase sparkles)
- ui/buttons.py & ui/hud.py (displays upgrade levels and costs)
"""

from config import (
    UPGRADE_ATTACK_BASE_COST,
    UPGRADE_ATTACK_COST_MULT,
    UPGRADE_ATTACK_DMG_INC,
    UPGRADE_SPEED_BASE_COST,
    UPGRADE_SPEED_COST_MULT,
    UPGRADE_SPEED_CD_DEC,
    TOWER_MIN_FIRE_COOLDOWN,
    UPGRADE_HEART_BASE_COST,
    UPGRADE_HEART_COST_MULT,
    TOWER_MAX_HEARTS,
)


class UpgradeSystem:
    """Manages progression levels, cost curves, and stat modifications."""

    def __init__(self):
        self.attack_level = 1
        self.speed_level = 1
        self.heart_level = 1

    # --- Attack Power ---
    def get_attack_cost(self) -> int:
        return int(UPGRADE_ATTACK_BASE_COST * (UPGRADE_ATTACK_COST_MULT ** (self.attack_level - 1)))

    def upgrade_attack(self, tower, economy, effects=None, sound_manager=None) -> bool:
        cost = self.get_attack_cost()
        if not economy.spend(cost):
            if sound_manager:
                sound_manager.play("denied")
            return False

        self.attack_level += 1
        tower.damage += UPGRADE_ATTACK_DMG_INC
        tower.trigger_upgrade_flash()

        if sound_manager:
            sound_manager.play("upgrade")
        if effects:
            effects.add_sparkle(tower.x, tower.y, count=10, color=(255, 171, 0))
        return True

    # --- Shooting Speed ---
    def get_speed_cost(self) -> int:
        return int(UPGRADE_SPEED_BASE_COST * (UPGRADE_SPEED_COST_MULT ** (self.speed_level - 1)))

    def is_speed_maxed(self, tower) -> bool:
        return tower.fire_cooldown <= TOWER_MIN_FIRE_COOLDOWN

    def upgrade_speed(self, tower, economy, effects=None, sound_manager=None) -> bool:
        if self.is_speed_maxed(tower):
            return False

        cost = self.get_speed_cost()
        if not economy.spend(cost):
            if sound_manager:
                sound_manager.play("denied")
            return False

        self.speed_level += 1
        tower.fire_cooldown = max(TOWER_MIN_FIRE_COOLDOWN, tower.fire_cooldown - UPGRADE_SPEED_CD_DEC)
        tower.trigger_upgrade_flash()

        if sound_manager:
            sound_manager.play("upgrade")
        if effects:
            effects.add_sparkle(tower.x, tower.y, count=10, color=(0, 229, 255))
        return True

    # --- Extra Hearts ---
    def get_heart_cost(self) -> int:
        return int(UPGRADE_HEART_BASE_COST * (UPGRADE_HEART_COST_MULT ** (self.heart_level - 1)))

    def is_heart_maxed(self, tower) -> bool:
        return tower.hearts >= TOWER_MAX_HEARTS

    def upgrade_heart(self, tower, economy, effects=None, sound_manager=None) -> bool:
        if self.is_heart_maxed(tower):
            return False

        cost = self.get_heart_cost()
        if not economy.spend(cost):
            if sound_manager:
                sound_manager.play("denied")
            return False

        self.heart_level += 1
        tower.hearts = min(TOWER_MAX_HEARTS, tower.hearts + 1)
        tower.trigger_upgrade_flash()

        if sound_manager:
            sound_manager.play("upgrade")
        if effects:
            effects.add_sparkle(tower.x, tower.y, count=12, color=(244, 67, 54))
        return True

    def reset(self) -> None:
        """Reset all upgrade levels for a fresh game."""
        self.attack_level = 1
        self.speed_level = 1
        self.heart_level = 1
