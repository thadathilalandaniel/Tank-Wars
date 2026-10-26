"""
defense_defenders/game/collision.py

This module contains collision detection and geometric spatial checks.
Uses squared distance comparisons wherever possible to avoid unnecessary
and expensive square root calculations during real-time game ticks.

Modules that interact with this:
- game/combat.py (projectile vs enemy, enemy vs tower)
- defense/* (range checks for targeting)
- game/game_manager.py (mouse click checks)
"""

import math


def distance_sq(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate squared Euclidean distance between two points."""
    dx = x2 - x1
    dy = y2 - y1
    return dx * dx + dy * dy


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate exact Euclidean distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)


def circle_circle_collision(x1: float, y1: float, r1: float,
                            x2: float, y2: float, r2: float) -> bool:
    """
    Check if two 2D circles intersect using squared radius comparison.
    Time Complexity: O(1)
    """
    radius_sum = r1 + r2
    return distance_sq(x1, y1, x2, y2) <= (radius_sum * radius_sum)


def point_in_circle(px: float, py: float, cx: float, cy: float, radius: float) -> bool:
    """Check if a point (px, py) lies inside or on the boundary of circle (cx, cy, radius)."""
    return distance_sq(px, py, cx, cy) <= (radius * radius)


def is_in_range(source_x: float, source_y: float, target_x: float, target_y: float,
                attack_range: float) -> bool:
    """Check if target point is within the source circle's attack range."""
    return distance_sq(source_x, source_y, target_x, target_y) <= (attack_range * attack_range)
