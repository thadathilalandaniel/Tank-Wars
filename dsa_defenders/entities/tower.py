"""
dsa_defenders/entities/tower.py

This module defines the central player defense Tower entity.
It manages tower coordinates, movement clamping within the arena,
stat progression (attack power, fire rate, range, hearts, shield),
turret rotation angle, and cooldown timers.

Modules that interact with this:
- game/game_manager.py (updates movement and timers)
- game/combat.py (checks fire cooldown and target alignment)
- systems/upgrades.py (modifies tower stats)
- systems/shield.py (modifies tower shield)
- ui/game_screen.py (renders the tower primitives and turret)
"""

import math
from config import (
    TOWER_INITIAL_X,
    TOWER_INITIAL_Y,
    TOWER_RADIUS,
    TOWER_MOVE_SPEED,
    TOWER_INITIAL_RANGE,
    TOWER_BASE_DAMAGE,
    TOWER_BASE_FIRE_COOLDOWN,
    TOWER_MIN_FIRE_COOLDOWN,
    TOWER_INITIAL_HEARTS,
    TOWER_MAX_HEARTS,
    SHIELD_CAPACITY_MAX,
    ARENA_LEFT,
    ARENA_RIGHT,
    ARENA_TOP,
    ARENA_BOTTOM,
)


class Tower:
    """Represents the player's central defensive tower."""

    def __init__(self, x: float = TOWER_INITIAL_X, y: float = TOWER_INITIAL_Y):
        self.x = float(x)
        self.y = float(y)
        self.radius = TOWER_RADIUS
        self.move_speed = TOWER_MOVE_SPEED
        self.range = TOWER_INITIAL_RANGE

        # Combat attributes
        self.damage = TOWER_BASE_DAMAGE
        self.fire_cooldown = TOWER_BASE_FIRE_COOLDOWN
        self.fire_timer = 0.0

        # Health & Defense
        self.hearts = TOWER_INITIAL_HEARTS
        self.max_hearts = TOWER_MAX_HEARTS
        self.shield = 0.0
        self.max_shield = SHIELD_CAPACITY_MAX

        # Turret visual angle (radians, default pointing up = -pi/2)
        self.turret_angle = -math.pi / 2
        self.target_angle = -math.pi / 2

        # Visual feedback timers
        self.damage_flash_timer = 0.0
        self.upgrade_flash_timer = 0.0
        self.is_dragging = False

    def move(self, dx: float, dy: float, dt: float) -> None:
        """Move the tower via keyboard direction inputs, clamping within the arena."""
        length = math.hypot(dx, dy)
        if length > 0.001:
            dx /= length
            dy /= length
            self.x += dx * self.move_speed * dt
            self.y += dy * self.move_speed * dt
            self.clamp_position()

    def drag_to(self, target_x: float, target_y: float) -> None:
        """Move tower directly via mouse dragging, clamped within the arena."""
        self.x = float(target_x)
        self.y = float(target_y)
        self.clamp_position()

    def clamp_position(self) -> None:
        """Keep tower fully inside the defined arena boundaries."""
        min_x = ARENA_LEFT + self.radius + 10
        max_x = ARENA_RIGHT - self.radius - 10
        min_y = ARENA_TOP + self.radius + 10
        max_y = ARENA_BOTTOM - self.radius - 10

        self.x = max(min_x, min(max_x, self.x))
        self.y = max(min_y, min(max_y, self.y))

    def update(self, dt: float, target=None) -> None:
        """Update cooldown timers and smoothly orient turret toward target."""
        if self.fire_timer > 0:
            self.fire_timer = max(0.0, self.fire_timer - dt)

        if self.damage_flash_timer > 0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)

        if self.upgrade_flash_timer > 0:
            self.upgrade_flash_timer = max(0.0, self.upgrade_flash_timer - dt)

        # Smoothly track target with turret head
        if target is not None:
            dx = target.x - self.x
            dy = target.y - self.y
            self.target_angle = math.atan2(dy, dx)
            # Smooth interpolation
            angle_diff = (self.target_angle - self.turret_angle + math.pi) % (2 * math.pi) - math.pi
            self.turret_angle += angle_diff * min(1.0, 14.0 * dt)

    def can_fire(self) -> bool:
        """Check if firing cooldown has elapsed."""
        return self.fire_timer <= 0.0

    def trigger_shot(self) -> None:
        """Reset the shot cooldown."""
        self.fire_timer = self.fire_cooldown

    def trigger_damage_flash(self) -> None:
        """Start damage visual feedback."""
        self.damage_flash_timer = 0.25

    def trigger_upgrade_flash(self) -> None:
        """Start upgrade visual feedback."""
        self.upgrade_flash_timer = 0.35

    def is_alive(self) -> bool:
        """Tower is alive while hearts > 0."""
        return self.hearts > 0

    def reset(self) -> None:
        """Reset tower to pristine initial state."""
        self.x = float(TOWER_INITIAL_X)
        self.y = float(TOWER_INITIAL_Y)
        self.damage = TOWER_BASE_DAMAGE
        self.fire_cooldown = TOWER_BASE_FIRE_COOLDOWN
        self.fire_timer = 0.0
        self.hearts = TOWER_INITIAL_HEARTS
        self.shield = 0.0
        self.turret_angle = -math.pi / 2
        self.target_angle = -math.pi / 2
        self.damage_flash_timer = 0.0
        self.upgrade_flash_timer = 0.0
        self.is_dragging = False
