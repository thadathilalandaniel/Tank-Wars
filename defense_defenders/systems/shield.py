"""
defense_defenders/systems/shield.py

This module manages the player's energy Shield power.
The shield absorbs incoming contact damage before player hearts are lost.
When depleted to zero, it triggers a dramatic break effect.
It can be charged and upgraded using coins from the economy system.

Modules that interact with this:
- game/combat.py (routes enemy collision damage to shield absorb logic)
- systems/economy.py (verifies affordability when recharging)
- entities/effects.py (spawns shield break shards and pulse rings)
- ui/hud.py & ui/game_screen.py (renders shield bar and glowing bubble)
"""

from config import (
    SHIELD_CAPACITY_MAX,
    SHIELD_RECHARGE_AMOUNT,
    UPGRADE_SHIELD_BASE_COST,
    UPGRADE_SHIELD_COST_MULT,
)


class ShieldSystem:
    """Controls the defensive energy bubble surrounding the tower."""

    def __init__(self):
        self.capacity = 0.0
        self.max_capacity = float(SHIELD_CAPACITY_MAX)
        self.level = 0
        self.pulse_timer = 0.0
        self.hit_ripple_timer = 0.0

    def get_recharge_cost(self) -> int:
        """Calculate the coin cost to recharge the shield."""
        return int(UPGRADE_SHIELD_BASE_COST * (UPGRADE_SHIELD_COST_MULT ** self.level))

    def can_recharge(self) -> bool:
        """Check if shield has missing capacity to recharge."""
        return self.capacity < self.max_capacity

    def recharge(self, economy, effects=None, sound_manager=None, tower=None) -> bool:
        """
        Purchase shield recharge and capacity boost using coins.
        """
        if not self.can_recharge():
            return False

        cost = self.get_recharge_cost()
        if not economy.spend(cost):
            if sound_manager:
                sound_manager.play("denied")
            return False

        self.level += 1
        self.capacity = min(self.max_capacity, self.capacity + SHIELD_RECHARGE_AMOUNT)
        if tower:
            tower.shield = self.capacity

        if sound_manager:
            sound_manager.play("upgrade")

        if effects and tower:
            effects.add_sparkle(tower.x, tower.y, count=12, color=(0, 229, 255))
            effects.add_shockwave(tower.x, tower.y, max_radius=80.0, color=(0, 229, 255), line_width=3)

        return True

    def absorb_damage(self, damage: float, tower=None, effects=None, sound_manager=None) -> float:
        """
        Absorb damage up to current capacity.
        Returns remaining penetrating damage that was NOT absorbed by shield.
        """
        if self.capacity <= 0.0:
            return damage

        self.hit_ripple_timer = 0.20

        if self.capacity >= damage:
            self.capacity -= damage
            if tower:
                tower.shield = self.capacity
            if sound_manager:
                sound_manager.play("shield_hit")
            return 0.0
        else:
            # Shield shattered!
            penetrating = damage - self.capacity
            self.capacity = 0.0
            if tower:
                tower.shield = 0.0

            if sound_manager:
                sound_manager.play("shield_break")

            if effects and tower:
                effects.add_explosion(tower.x, tower.y, base_color=(0, 229, 255), count=18)
                effects.add_shockwave(tower.x, tower.y, max_radius=110.0, color=(0, 229, 255), line_width=4)

            return penetrating

    def is_active(self) -> bool:
        """Check if energy shield is currently protecting the tower."""
        return self.capacity > 0.0

    def update(self, dt: float) -> None:
        """Advance shield pulsation animation timer."""
        self.pulse_timer += dt * 3.0
        if self.hit_ripple_timer > 0:
            self.hit_ripple_timer = max(0.0, self.hit_ripple_timer - dt)

    def reset(self) -> None:
        """Reset shield status on game restart."""
        self.capacity = 0.0
        self.level = 0
        self.pulse_timer = 0.0
        self.hit_ripple_timer = 0.0
