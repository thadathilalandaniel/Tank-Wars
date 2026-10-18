"""
dsa_defenders/entities/enemy.py

This module defines the Enemy entity class.
Enemies possess distinct archetypes (Scout, Runner, Tank, Boss) with different
health pools, movement speeds, damage values, and threat bonuses.
They navigate towards the player's tower and carry state for health bars and
cute walking animations.

Modules that interact with this:
- game/wave_manager.py (spawns and scales enemies)
- game/combat.py (applies projectile damage)
- dsa/* (evaluates threat, queue order, distance)
- ui/game_screen.py (renders the cute robot graphics)
"""

import math
from config import ENEMY_STATS, ENEMY_TYPE_SCOUT


class Enemy:
    """Represents a robotic enemy approaching the central tower."""

    _next_id = 1

    def __init__(self, x: float, y: float, enemy_type: str = ENEMY_TYPE_SCOUT,
                 hp_mult: float = 1.0, spd_mult: float = 1.0):
        self.id = Enemy._next_id
        Enemy._next_id += 1
        self.spawn_index = self.id  # For FIFO queue arrival tracking

        self.x = float(x)
        self.y = float(y)
        self.enemy_type = enemy_type

        # Retrieve base archetype stats
        base = ENEMY_STATS.get(enemy_type, ENEMY_STATS[ENEMY_TYPE_SCOUT])
        self.radius = base["radius"]
        self.max_health = float(base["base_hp"]) * hp_mult
        self.health = self.max_health
        self.speed = float(base["base_speed"]) * spd_mult
        self.damage = int(base["damage"])
        self.coin_reward = int(base["coin_reward"])
        self.type_bonus = float(base["type_bonus"])

        self.color = base["color"]
        self.outline_color = base["outline"]

        # Animation states
        self.anim_phase = float(self.id % 10)
        self.hit_flash_timer = 0.0

    def move_towards(self, target_x: float, target_y: float, dt: float) -> None:
        """Advance directly toward target coordinates using delta time."""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 0.001:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        # Advance walk cycle animation
        self.anim_phase += dt * (self.speed / 15.0)

        if self.hit_flash_timer > 0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)

    def take_damage(self, amount: float) -> tuple[float, bool]:
        """
        Apply damage to the enemy.
        Returns:
            (actual_damage_dealt, is_killed)
        """
        damage_dealt = min(self.health, amount)
        self.health -= damage_dealt
        self.hit_flash_timer = 0.12
        return damage_dealt, self.health <= 0.0

    def is_alive(self) -> bool:
        """Check if enemy still has health remaining."""
        return self.health > 0.0

    def health_fraction(self) -> float:
        """Return current health ratio between 0.0 and 1.0."""
        if self.max_health <= 0:
            return 0.0
        return max(0.0, min(1.0, self.health / self.max_health))

    def __repr__(self) -> str:
        return f"Enemy(id={self.id}, type={self.enemy_type}, hp={self.health:.0f}/{self.max_health:.0f})"
