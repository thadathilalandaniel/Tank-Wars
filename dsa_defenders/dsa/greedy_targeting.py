"""
dsa_defenders/dsa/greedy_targeting.py

Greedy Nearest-Enemy targeting heuristic implemented from foundational principles.

Role in Game:
In Greedy mode, the defense tower scans all alive enemies within its attack radius and
picks the single hostile that is physically closest (minimum Euclidean distance).

Algorithmic Trade-off:
- Greedy heuristics make locally optimal choices at each decision instant without evaluating
  global threat. While highly responsive to player positioning, it may target a low-damage
  scout nearby while a high-damage boss advances just behind it.
- Performance: To compare distances efficiently, the algorithm evaluates SQUARED distance
  (dx*dx + dy*dy) against range_squared, avoiding expensive floating-point math.sqrt() calls
  during the linear scan.
"""

import math


def find_nearest_enemy(tower_x: float, tower_y: float, tower_range: float, enemies: list):
    """
    Find the closest living enemy within the tower's firing radius using squared Euclidean distance.

    Time Complexity: O(n) where n is the number of active enemies.
    Space Complexity: O(1) auxiliary space.

    Returns:
        tuple: (nearest_enemy, actual_distance) or (None, float('inf'))
    """
    range_sq = tower_range * tower_range
    best_enemy = None
    min_dist_sq = float('inf')

    for enemy in enemies:
        if not getattr(enemy, "is_alive", lambda: True)():
            continue

        dx = enemy.x - tower_x
        dy = enemy.y - tower_y
        dist_sq = dx * dx + dy * dy

        # Must be within attack radius and strictly closer than current best candidate
        if dist_sq <= range_sq and dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_enemy = enemy

    # Compute actual square root only once for display purposes
    actual_dist = math.sqrt(min_dist_sq) if best_enemy is not None else float('inf')
    return best_enemy, round(actual_dist, 1)

