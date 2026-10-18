"""
dsa_defenders/systems/blast.py

This module manages the player's Emergency Blast ability.
When activated, it detonates an energy shockwave that sweeps across the entire
arena, damaging all visible enemies, triggering visual screen flashes and
expanding shockwave rings.

Modules that interact with this:
- game/game_manager.py (triggers via Spacebar or upgrade card click)
- systems/economy.py (verifies upgrade affordability)
- entities/effects.py (spawns fullscreen shockwaves and flashes)
- systems/sound.py (plays deep explosion blast sound)
"""

from config import (
    BLAST_BASE_COST,
    BLAST_COST_MULT,
    BLAST_BASE_DAMAGE,
    BLAST_COOLDOWN,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)


class BlastSystem:
    """Controls the Emergency Blast power, cooldown, and area-of-effect damage."""

    def __init__(self):
        self.level = 1
        self.base_damage = BLAST_BASE_DAMAGE
        self.cooldown_max = BLAST_COOLDOWN
        self.cooldown_timer = 0.0  # Ready at start of match!

    def is_ready(self) -> bool:
        """Check if the ability is off cooldown."""
        return self.cooldown_timer <= 0.0

    def ready_fraction(self) -> float:
        """Return 0.0 (just used) to 1.0 (fully charged)."""
        if self.cooldown_max <= 0:
            return 1.0
        return max(0.0, min(1.0, 1.0 - (self.cooldown_timer / self.cooldown_max)))

    def get_damage(self) -> float:
        """Return current blast damage scaled by upgrade level."""
        return self.base_damage + (self.level - 1) * 45.0

    def get_upgrade_cost(self) -> int:
        """Calculate the cost to upgrade blast potency."""
        return int(BLAST_BASE_COST * (BLAST_COST_MULT ** (self.level - 1)))

    def upgrade(self, economy, sound_manager=None) -> bool:
        """Upgrade the blast ability damage and recharge rate."""
        cost = self.get_upgrade_cost()
        if not economy.spend(cost):
            if sound_manager:
                sound_manager.play("denied")
            return False

        self.level += 1
        self.cooldown_max = max(6.0, self.cooldown_max - 0.75)
        if sound_manager:
            sound_manager.play("upgrade")
        return True

    def activate(self, tower, enemies: list, effects, sound_manager=None,
                 targeting_dispatcher=None, economy=None) -> bool:
        """
        Detonate emergency blast damaging all living enemies currently on screen.
        """
        if not self.is_ready():
            if sound_manager:
                sound_manager.play("denied")
            return False

        # Put on cooldown
        self.cooldown_timer = self.cooldown_max

        # Play sound
        if sound_manager:
            sound_manager.play("blast")

        # Spawn dramatic visual shockwaves and screen flash
        cx = tower.x if tower else SCREEN_WIDTH // 2
        cy = tower.y if tower else SCREEN_HEIGHT // 2
        if effects:
            effects.add_shockwave(cx, cy, max_radius=850.0, color=(255, 171, 0), line_width=8)
            effects.add_screen_flash(color=(255, 240, 200), max_alpha=140, duration=0.3)

        # Apply damage to all alive enemies
        dmg = self.get_damage()
        for enemy in list(enemies):
            if getattr(enemy, "is_alive", lambda: False)():
                actual_dmg, killed = enemy.take_damage(dmg)
                if effects:
                    effects.add_floating_damage(f"{int(actual_dmg)}", enemy.x, enemy.y, crit=True)
                    if killed:
                        effects.add_explosion(enemy.x, enemy.y, enemy.color, count=16)
                        if economy:
                            economy.add_coins(enemy.coin_reward)
                            effects.add_floating_coin(enemy.coin_reward, enemy.x, enemy.y)
                        if targeting_dispatcher:
                            targeting_dispatcher.on_enemy_removed(enemy)

        # Prune killed enemies
        enemies[:] = [e for e in enemies if e.is_alive()]
        return True

    def update(self, dt: float) -> None:
        """Tick down the cooldown timer."""
        if self.cooldown_timer > 0.0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

    def reset(self) -> None:
        """Reset blast state on new game."""
        self.level = 1
        self.cooldown_max = BLAST_COOLDOWN
        self.cooldown_timer = 0.0
