"""
defense_defenders/defense/targeting.py

Central algorithmic dispatcher coordinating the tower's targeting system:
1. QUEUE (FIFO): Targets the vanguard hostile (earliest arrival in arena).
2. PRIORITY QUEUE (Max-Heap): Targets the highest computed threat score.
3. GREEDY: Targets the nearest hostile by Euclidean distance.

Note: This module is purely algorithmic and contains zero Pygame dependencies.
"""

import math
from defense.queue_ds import Queue
from defense.priority_queue import MaxHeap, calculate_threat
from defense.greedy_targeting import find_nearest_enemy

MODE_QUEUE = "QUEUE"
MODE_PRIORITY_QUEUE = "PRIORITY_QUEUE"
MODE_GREEDY = "GREEDY"


class TargetingDispatcher:
    """
    Coordinates and switches between the three targeting strategies:
      1. FIFO Queue (Earliest arrival)
      2. Binary Max-Heap (Highest composite threat score)
      3. Greedy Algorithm (Nearest Euclidean distance)
    """

    def __init__(self, initial_mode: str = MODE_QUEUE):
        self.mode = initial_mode
        self.queue = Queue()
        self.heap = MaxHeap()
        self.last_selected_target = None
        self.last_calculated_metric = None

    def set_mode(self, new_mode: str) -> None:
        """Switch active targeting mode between QUEUE, PRIORITY_QUEUE, and GREEDY."""
        if new_mode in (MODE_QUEUE, MODE_PRIORITY_QUEUE, MODE_GREEDY):
            self.mode = new_mode

    def on_enemy_spawned(self, enemy) -> None:
        """Enqueue newly spawned hostile to preserve arrival order."""
        self.queue.enqueue(enemy)

    def on_enemy_removed(self, enemy) -> None:
        """Remove destroyed or despawned hostile from active queue."""
        self.queue.remove(enemy)

    def clear(self) -> None:
        """Reset internal data structures between waves or on game restart."""
        self.queue.clear()
        self.heap.clear()
        self.last_selected_target = None
        self.last_calculated_metric = None

    def select_target(self, tower_x: float, tower_y: float, tower_range: float, alive_enemies: list):
        """
        Select an eligible hostile target based on the active strategy.
        Returns the chosen Enemy object, or None if no valid in-range target exists.
        """
        if not alive_enemies:
            self.last_selected_target = None
            self.last_calculated_metric = None
            return None

        range_sq = tower_range * tower_range

        # -------------------------------------------------------------
        # 1. FIFO QUEUE TARGETING
        # -------------------------------------------------------------
        if self.mode == MODE_QUEUE:
            target = None
            # Scan queue elements in FIFO order (head to tail)
            active_items = self.queue.to_list()
            for enemy in active_items:
                if not getattr(enemy, "is_alive", lambda: True)():
                    self.queue.remove(enemy)
                    continue
                
                # Check if this alive enemy is within tower attack range
                dx = enemy.x - tower_x
                dy = enemy.y - tower_y
                dist_sq = dx * dx + dy * dy
                if dist_sq <= range_sq:
                    target = enemy
                    self.last_calculated_metric = f"Spawn Order #{getattr(enemy, 'spawn_index', '?')}"
                    break

            self.last_selected_target = target
            return target

        # -------------------------------------------------------------
        # 2. BINARY MAX-HEAP (PRIORITY QUEUE) TARGETING
        # -------------------------------------------------------------
        elif self.mode == MODE_PRIORITY_QUEUE:
            # Rebuild the heap in O(n) using Floyd's algorithm with fresh threat scores
            heap_entries = []
            for enemy in alive_enemies:
                if getattr(enemy, "is_alive", lambda: True)():
                    threat = calculate_threat(enemy, tower_x, tower_y)
                    heap_entries.append((threat, enemy))

            self.heap.build_heap(heap_entries)

            target = None
            skipped_entries = []

            # Extract elements from highest to lowest threat
            while not self.heap.is_empty():
                threat, enemy = self.heap.extract_max()
                if not getattr(enemy, "is_alive", lambda: True)():
                    continue

                dx = enemy.x - tower_x
                dy = enemy.y - tower_y
                dist_sq = dx * dx + dy * dy

                if dist_sq <= range_sq:
                    target = enemy
                    self.last_calculated_metric = f"Threat: {threat:.1f}"
                    break
                else:
                    skipped_entries.append((threat, enemy))

            # Re-insert skipped out-of-range entries
            for entry in skipped_entries:
                self.heap.insert(entry[0], entry[1])

            self.last_selected_target = target
            return target

        # -------------------------------------------------------------
        # 3. GREEDY NEAREST-ENEMY TARGETING
        # -------------------------------------------------------------
        elif self.mode == MODE_GREEDY:
            target, dist = find_nearest_enemy(tower_x, tower_y, tower_range, alive_enemies)
            self.last_selected_target = target
            self.last_calculated_metric = f"Dist: {dist}px" if target else "Out of Range"
            return target

        return None

    def get_inspection_stats(self, tower_x: float, tower_y: float, tower_range: float, alive_enemies: list) -> dict:
        """
        Generate detailed real-time statistics and explanations for ui/algorithm_lab.py.
        """
        range_sq = tower_range * tower_range
        stats = {
            "mode": self.mode,
            "target": self.last_selected_target,
            "metric": self.last_calculated_metric,
            "total_alive": len([e for e in alive_enemies if getattr(e, "is_alive", lambda: True)()]),
        }

        if self.mode == MODE_QUEUE:
            raw_queue = self.queue.to_list()
            queue_items = []
            for idx, enemy in enumerate(raw_queue[:8]):  # Show first 8
                if getattr(enemy, "is_alive", lambda: True)():
                    dx = enemy.x - tower_x
                    dy = enemy.y - tower_y
                    in_range = (dx * dx + dy * dy) <= range_sq
                    queue_items.append({
                        "pos": idx + 1,
                        "type": enemy.enemy_type,
                        "id": getattr(enemy, "spawn_index", idx + 1),
                        "hp": round(enemy.health, 1),
                        "in_range": in_range,
                    })
            stats["queue_items"] = queue_items
            stats["queue_size"] = self.queue.size()
            stats["complexity"] = "Enqueue: O(1) | Dequeue: O(1) amortized | Peek: O(1)"
            stats["rule"] = "First-Come, First-Served: attacks oldest spawned enemy in range."

        elif self.mode == MODE_PRIORITY_QUEUE:
            threat_list = []
            for enemy in alive_enemies:
                if getattr(enemy, "is_alive", lambda: True)():
                    dx = enemy.x - tower_x
                    dy = enemy.y - tower_y
                    dist = math.hypot(dx, dy)
                    in_range = (dist * dist) <= range_sq
                    threat = calculate_threat(enemy, tower_x, tower_y)
                    threat_list.append({
                        "threat": threat,
                        "type": enemy.enemy_type,
                        "id": getattr(enemy, "spawn_index", 0),
                        "dist": round(dist, 1),
                        "in_range": in_range,
                        "dmg": enemy.damage,
                        "spd": round(enemy.speed, 1),
                    })
            threat_list.sort(key=lambda x: x["threat"], reverse=True)
            stats["top_threats"] = threat_list[:6]
            stats["heap_size"] = len(threat_list)
            stats["complexity"] = "Insert: O(log n) | Extract-Max: O(log n) | Build-Heap: O(n)"
            stats["rule"] = "Max-Heap: attacks highest threat (damage*3 + speed*1.5 + 1000/dist)."

        elif self.mode == MODE_GREEDY:
            dist_list = []
            for enemy in alive_enemies:
                if getattr(enemy, "is_alive", lambda: True)():
                    dx = enemy.x - tower_x
                    dy = enemy.y - tower_y
                    dist = math.hypot(dx, dy)
                    in_range = (dist * dist) <= range_sq
                    dist_list.append({
                        "dist": round(dist, 1),
                        "dist_sq": int(dx * dx + dy * dy),
                        "type": enemy.enemy_type,
                        "id": getattr(enemy, "spawn_index", 0),
                        "in_range": in_range,
                    })
            dist_list.sort(key=lambda x: x["dist"])
            stats["nearest_list"] = dist_list[:6]
            stats["complexity"] = "Scan Nearest: O(n) using squared Euclidean distance"
            stats["rule"] = "Greedy Local Optimum: attacks closest in-range enemy."

        return stats

