"""
tests/test_defense.py

Automated headless test suite for Data Structures and Algorithms in Defense Defenders.
Verifies:
1. FIFO Queue correctness (enqueue, dequeue order, peek, size, remove).
2. Binary Max-Heap ordering on random inputs compared against sorted(reverse=True).
3. Floyd's O(n) build_heap algorithm verification.
4. Greedy Nearest Neighbor selection using squared Euclidean distance.
5. Strict verification that standard library `heapq` is NOT imported anywhere in the project.
6. TargetingDispatcher mode switching behavior.
"""

import os
import sys
import random
import unittest

# Ensure defense_defenders is in sys.path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "defense_defenders"))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from defense.queue_ds import Queue
from defense.priority_queue import MaxHeap, calculate_threat
from defense.greedy_targeting import find_nearest_enemy
from defense.targeting import TargetingDispatcher, MODE_QUEUE, MODE_PRIORITY_QUEUE, MODE_GREEDY


class MockEnemy:
    """Mock enemy representation for headless Defense verification."""
    def __init__(self, eid: int, x: float, y: float, damage: int = 1, speed: float = 80.0,
                 hp: float = 50.0, enemy_type: str = "scout", type_bonus: float = 10.0):
        self.id = eid
        self.spawn_index = eid
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.speed = speed
        self.health = hp
        self.enemy_type = enemy_type
        self.type_bonus = type_bonus
        self.alive = True

    def is_alive(self) -> bool:
        return self.alive


class TestDefenseDefenders(unittest.TestCase):

    def test_queue_fifo(self):
        """Verify FIFO Queue adheres strictly to First-In, First-Out semantics."""
        q = Queue()
        self.assertTrue(q.is_empty())
        self.assertEqual(q.size(), 0)

        # Enqueue items
        items = ["Enemy_A", "Enemy_B", "Enemy_C", "Enemy_D", "Enemy_E"]
        for itm in items:
            q.enqueue(itm)

        self.assertFalse(q.is_empty())
        self.assertEqual(q.size(), 5)
        self.assertEqual(q.peek(), "Enemy_A")

        # Dequeue elements and verify arrival order
        self.assertEqual(q.dequeue(), "Enemy_A")
        self.assertEqual(q.dequeue(), "Enemy_B")
        self.assertEqual(q.size(), 3)
        self.assertEqual(q.peek(), "Enemy_C")

        # Test middle removal (e.g. enemy killed mid-game)
        removed = q.remove("Enemy_D")
        self.assertTrue(removed)
        self.assertEqual(q.size(), 2)
        self.assertEqual(q.to_list(), ["Enemy_C", "Enemy_E"])

        # Dequeue remaining
        self.assertEqual(q.dequeue(), "Enemy_C")
        self.assertEqual(q.dequeue(), "Enemy_E")
        self.assertTrue(q.is_empty())

    def test_max_heap_random_inputs(self):
        """Verify Binary Max-Heap extracts elements in descending priority order on random inputs."""
        heap = MaxHeap()
        self.assertTrue(heap.is_empty())

        random.seed(42)
        random_values = [round(random.uniform(1.0, 1000.0), 2) for _ in range(120)]

        for val in random_values:
            heap.insert(val, f"item_{val}")

        self.assertEqual(len(heap), 120)

        # Extract all elements and compare against Python's sorted(reverse=True)
        extracted = []
        while not heap.is_empty():
            prio, item = heap.extract_max()
            extracted.append(prio)

        expected = sorted(random_values, reverse=True)
        self.assertEqual(extracted, expected, "MaxHeap extraction did not match sorted descending order!")

    def test_floyds_build_heap(self):
        """Verify Floyd's O(n) build_heap algorithm maintains the max-heap property."""
        random.seed(99)
        entries = [(round(random.uniform(1.0, 500.0), 2), f"val_{i}") for i in range(80)]

        heap = MaxHeap()
        heap.build_heap(entries)

        extracted = []
        while not heap.is_empty():
            prio, _ = heap.extract_max()
            extracted.append(prio)

        expected = sorted([e[0] for e in entries], reverse=True)
        self.assertEqual(extracted, expected, "build_heap did not produce a valid Max-Heap!")

    def test_greedy_nearest_selection(self):
        """Verify Greedy targeting picks the true minimum Euclidean distance inside range."""
        tower_x, tower_y = 640.0, 360.0
        tower_range = 200.0

        e_far_out = MockEnemy(1, 640.0, 100.0)      # dist = 260px (out of range)
        e_close = MockEnemy(2, 640.0, 300.0)        # dist = 60px (inside range)
        e_medium = MockEnemy(3, 640.0, 240.0)       # dist = 120px (inside range)
        e_closest = MockEnemy(4, 640.0, 335.0)      # dist = 25px (inside range, local minimum!)

        enemies = [e_far_out, e_close, e_medium, e_closest]
        target, dist = find_nearest_enemy(tower_x, tower_y, tower_range, enemies)

        self.assertIsNotNone(target)
        self.assertEqual(target.id, 4)
        self.assertEqual(dist, 25.0)

        # Verify dead enemy is skipped
        e_closest.alive = False
        target2, dist2 = find_nearest_enemy(tower_x, tower_y, tower_range, enemies)
        self.assertEqual(target2.id, 2)
        self.assertEqual(dist2, 60.0)

    def test_no_heapq_imported_anywhere(self):
        """Ensure standard library heapq is NOT imported anywhere in the project."""
        forbidden = "import heapq"
        forbidden_from = "from heapq"

        defense_dir = os.path.join(PROJECT_DIR)
        found_violations = []

        for root, _, files in os.walk(defense_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for idx, line in enumerate(lines, start=1):
                            clean = line.strip()
                            if clean.startswith(forbidden) or clean.startswith(forbidden_from):
                                found_violations.append(f"{file}:{idx}: {clean}")

        self.assertEqual(len(found_violations), 0,
                         f"Found forbidden heapq imports in project:\n" + "\n".join(found_violations))

    def test_targeting_dispatcher_modes_differ(self):
        """
        Verify that changing targeting mode measurably selects different targets
        when arrival order, distance, and threat differ.
        """
        tower_x, tower_y = 640.0, 360.0
        tower_range = 250.0

        # Enemy 1: Spawned first (#1), but far away and low threat
        e1 = MockEnemy(eid=1, x=640.0, y=170.0, damage=1, speed=50.0, hp=20.0, enemy_type="scout", type_bonus=5.0)
        # Enemy 2: Spawned second (#2), physically closest to tower
        e2 = MockEnemy(eid=2, x=640.0, y=320.0, damage=1, speed=70.0, hp=15.0, enemy_type="runner", type_bonus=10.0)
        # Enemy 3: Spawned third (#3), but massive threat (Boss with high damage and boss bonus)
        e3 = MockEnemy(eid=3, x=640.0, y=200.0, damage=5, speed=90.0, hp=200.0, enemy_type="boss", type_bonus=150.0)

        enemies = [e1, e2, e3]
        dispatcher = TargetingDispatcher()
        for e in enemies:
            dispatcher.on_enemy_spawned(e)

        # 1. QUEUE MODE -> selects Enemy 1 (earliest spawn #1)
        dispatcher.set_mode(MODE_QUEUE)
        target_q = dispatcher.select_target(tower_x, tower_y, tower_range, enemies)
        self.assertEqual(target_q.id, 1, "Queue mode should select earliest arrival (Enemy 1)")

        # 2. GREEDY MODE -> selects Enemy 2 (closest distance: 40px)
        dispatcher.set_mode(MODE_GREEDY)
        target_g = dispatcher.select_target(tower_x, tower_y, tower_range, enemies)
        self.assertEqual(target_g.id, 2, "Greedy mode should select closest distance (Enemy 2)")

        # 3. PRIORITY QUEUE MODE -> selects Enemy 3 (Apex Boss with highest threat score)
        dispatcher.set_mode(MODE_PRIORITY_QUEUE)
        target_h = dispatcher.select_target(tower_x, tower_y, tower_range, enemies)
        self.assertEqual(target_h.id, 3, "Priority Queue should select highest threat (Enemy 3 Boss)")


if __name__ == "__main__":
    unittest.main()
