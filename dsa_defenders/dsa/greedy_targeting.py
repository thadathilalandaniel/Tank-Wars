"""
dsa_defenders/dsa/greedy_targeting.py

# DSA CONCEPT: GREEDY ALGORITHM (LOCAL OPTIMUM = NEAREST ENEMY)
# ==============================================================================
# This module implements the Greedy Nearest-Enemy targeting heuristic.
#
# Role in Game:
# In Greedy mode, the tower evaluates all living enemies within its attack radius
# and picks the single enemy that is currently closest in Euclidean distance.
#
# Optimization Note:
# To compare Euclidean distances efficiently, we use SQUARED DISTANCE (dx*dx + dy*dy).
# Because the square root function is strictly monotonically increasing for x >= 0:
#     d1 < d2  <===>  (d1)^2 < (d2)^2
# Computing sqrt involves expensive floating-point CPU cycles. By comparing squared
# values, we achieve the exact same ordering in fewer clock cycles.
#
# Modules that interact with this:
# - dsa/targeting.py (the targeting dispatcher)
# - ui/algorithm_lab.py (reads selection and distance for visualization)
# ==============================================================================
"""

import math

# ==============================================================================
# VIVA NOTES: GREEDY ALGORITHMS
# ==============================================================================
"""
WHAT IS A GREEDY ALGORITHM?
A Greedy Algorithm builds a solution piece by piece, always making the choice
that looks best at the present moment (a locally optimal choice) in the hope
that this will lead to a globally optimal solution.

WHY WAS GREEDY TARGETING CHOSEN FOR THIS GAME?
Targeting the closest enemy is an intuitive human heuristic: "eliminate what's right
in front of you first." It reacts immediately when the player moves the tower around
the arena using WASD or mouse dragging.

COMPLEXITY:
--------------------------------------------------------------------------------
Operation           Time Complexity     Space Complexity    Description
--------------------------------------------------------------------------------
find_nearest()      O(n)                O(1)                Linear scan over enemies
--------------------------------------------------------------------------------
Where n is the number of active enemies.

WHY IS GREEDY NOT ALWAYS GLOBALLY OPTIMAL?
Greedy heuristics look only at immediate local metrics (distance). For example:
- A harmless low-damage Scout might be 50 pixels away, while an apex Boss with 5x
  damage is 55 pixels away.
- Greedy will spend precious firing seconds chipping away at the Scout, allowing the
  Boss to advance and demolish the tower.
- This demonstrates a classic DSA concept: local optimality does not guarantee
  global system survival!

DRY RUN TRACE:
Tower at (640, 360), Range = 200 (Range squared = 40,000)
Enemy 1 at (640, 300): dx = 0, dy = -60 -> dist_sq = 3600 (within range)
Enemy 2 at (640, 180): dx = 0, dy = -180 -> dist_sq = 32,400 (within range)
Enemy 3 at (640, 100): dx = 0, dy = -260 -> dist_sq = 67,600 (out of range, ignored)
Compare: min(3600, 32,400) = 3600.
Greedy selects Enemy 1.

LIKELY VIVA QUESTIONS & SHORT ANSWERS:
Q1: Why do we use squared distance instead of math.sqrt()?
A1: Square root is computationally expensive. Because f(x) = x^2 is strictly increasing
    for non-negative distances, d1^2 < d2^2 strictly implies d1 < d2. We avoid sqrt
    without altering any comparison outcomes.

Q2: What is the Greedy Choice Property?
A2: A problem has the greedy choice property if a global optimum can be reached by
    consistently making locally optimal choices without backtracking.

Q3: Can moving the tower change the Greedy choice immediately?
A3: Yes! As the tower moves, distances to all enemies change dynamically. Greedy mode
    instantly updates its target each frame.
"""


def find_nearest_enemy(tower_x: float, tower_y: float, tower_range: float, enemies: list):
    """
    Find the closest living enemy within the tower's firing radius using squared Euclidean distance.
    
    # DSA CONCEPT: GREEDY ALGORITHM (LOCAL OPTIMUM = NEAREST ENEMY)
    Time Complexity: O(n)
    Space Complexity: O(1)
    
    Returns:
        tuple: (nearest_enemy, actual_distance) or (None, float('inf'))
    """
    range_sq = tower_range * tower_range
    best_enemy = None
    min_dist_sq = float('inf')

    for enemy in enemies:
        # Skip dead or inactive enemies
        if not getattr(enemy, "is_alive", lambda: True)():
            continue

        dx = enemy.x - tower_x
        dy = enemy.y - tower_y
        dist_sq = dx * dx + dy * dy

        # Must be inside attack range and strictly closer than current best
        if dist_sq <= range_sq and dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_enemy = enemy

    actual_dist = math.sqrt(min_dist_sq) if best_enemy is not None else float('inf')
    return best_enemy, round(actual_dist, 1)
