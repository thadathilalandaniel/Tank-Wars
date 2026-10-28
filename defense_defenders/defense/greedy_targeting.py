import math

def find_nearest_enemy(tower_x: float, tower_y: float, tower_range: float, enemies: list):
    range_sq = tower_range * tower_range
    best_enemy = None
    min_dist_sq = float('inf')

    for enemy in enemies:
        if not getattr(enemy, "is_alive", lambda: True)():
            continue

        dx = enemy.x - tower_x
        dy = enemy.y - tower_y
        dist_sq = dx * dx + dy * dy

        if dist_sq <= range_sq and dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_enemy = enemy

    actual_dist = math.sqrt(min_dist_sq) if best_enemy is not None else float('inf')
    return best_enemy, round(actual_dist, 1)
