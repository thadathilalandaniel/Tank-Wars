"""
defense_defenders/entities/projectile.py

This module defines the Projectile entity fired by the tower.
Projectiles home in on their target while alive, and gracefully handle
the edge case where a target is destroyed mid-flight by continuing towards
the last known location or impacting another enemy along their path.

Modules that interact with this:
- game/combat.py (spawns and updates projectiles, checks collisions)
- ui/game_screen.py (renders projectile circles and energy glow)
"""

import math
from config import COLOR_PROJECTILE


class Projectile:
    """Represents a high-velocity energy bolt fired from the central tower."""

    def __init__(self, start_x: float, start_y: float, target, damage: float,
                 speed: float = 620.0, radius: float = 6.0):
        self.x = float(start_x)
        self.y = float(start_y)
        self.target = target
        self.target_last_x = float(target.x if target else start_x)
        self.target_last_y = float(target.y if target else start_y - 100)
        self.damage = float(damage)
        self.speed = float(speed)
        self.radius = float(radius)
        self.color = COLOR_PROJECTILE

        self.alive = True
        self.distance_traveled = 0.0
        self.max_distance = 1200.0  # Max travel before despawning

        # Direction vector cache
        dx = self.target_last_x - self.x
        dy = self.target_last_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else:
            self.vx = 0.0
            self.vy = -self.speed

    def update(self, dt: float) -> None:
        """
        Advance projectile position. If original target is alive, update homing
        trajectory; otherwise continue moving in the last locked trajectory.
        """
        if not self.alive:
            return

        # If target still exists and is alive, track its current location
        if self.target is not None and getattr(self.target, "is_alive", lambda: False)():
            self.target_last_x = self.target.x
            self.target_last_y = self.target.y
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0.001:
                self.vx = (dx / dist) * self.speed
                self.vy = (dy / dist) * self.speed

        step_x = self.vx * dt
        step_y = self.vy * dt
        self.x += step_x
        self.y += step_y

        self.distance_traveled += math.hypot(step_x, step_y)
        if self.distance_traveled >= self.max_distance:
            self.alive = False

    def is_alive(self) -> bool:
        """Return True if projectile is active in flight."""
        return self.alive

    def destroy(self) -> None:
        """Mark projectile as spent."""
        self.alive = False
