"""
defense_defenders/defense/priority_queue.py

Manual Binary Max-Heap and Priority Queue implemented from foundational principles.
Standard library heapq is strictly not used.

Role in Game:
Under Priority Queue targeting mode, the defense tower prioritizes enemies by dynamic
threat score (damage, speed, proximity to tower, archetype bonus, and low health).
The Binary Max-Heap keeps the highest threat hostile at the root (index 0) in O(log n)
insertion/extraction time, and supports O(n) construction via Floyd's build_heap algorithm.
"""

import math


def calculate_threat(enemy, tower_x: float, tower_y: float) -> float:
    """
    Compute a composite threat score for an enemy relative to the tower.

    Formula:
      threat = (damage * 3.0) + (speed * 1.5) + (1000.0 / (dist + 1.0))
               + type_bonus - (health * 0.05)

    Algorithmic Rationale:
      - damage * 3.0: High-damage hostiles (Tanks, Bosses) directly endanger player hearts.
      - speed * 1.5: Fast units (Runners) close distance quickly and must be intercepted.
      - 1000.0 / (dist + 1.0): Hyperbolic proximity scaling prioritizes enemies near the tower.
      - type_bonus: Static priority bonuses for Bosses (+120), Tanks (+35), Runners (+20).
      - -(health * 0.05): Tie-breaker favoring weakened enemies to eliminate damage sources faster.
    """
    dx = enemy.x - tower_x
    dy = enemy.y - tower_y
    dist = math.hypot(dx, dy)

    threat = (
        (enemy.damage * 3.0)
        + (enemy.speed * 1.5)
        + (1000.0 / (dist + 1.0))
        + getattr(enemy, "type_bonus", 10.0)
        - (enemy.health * 0.05)
    )
    return round(threat, 2)


class MaxHeap:
    """
    A manual Binary Max-Heap storing (priority: float, item: Any) entries.

    Parent and child indices in a complete binary tree represented as an array:
      - parent(i) = (i - 1) // 2
      - left_child(i) = 2 * i + 1
      - right_child(i) = 2 * i + 2
    """

    def __init__(self):
        self._heap = []

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right(i: int) -> int:
        return 2 * i + 2

    def size(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def peek_max(self):
        """Return the maximum element (index 0) without removing it in O(1) time."""
        if self.is_empty():
            return None
        return self._heap[0]

    def insert(self, priority: float, item) -> None:
        """
        Insert an element in O(log n) time.
        Appends to the tail to preserve tree completeness, then sifts up to restore the max-heap property.
        """
        entry = (priority, item)
        self._heap.append(entry)
        self._sift_up(len(self._heap) - 1)

    def extract_max(self):
        """
        Remove and return the highest priority entry in O(log n) time.
        Replaces root with the last array element, then sifts down to restore the max-heap property.
        """
        if self.is_empty():
            raise IndexError("extract_max from empty MaxHeap")

        root = self._heap[0]
        last = self._heap.pop()

        if len(self._heap) > 0:
            self._heap[0] = last
            self._sift_down(0)

        return root

    def _sift_up(self, index: int) -> None:
        """
        Bubble element at `index` upward while its priority exceeds its parent's priority.
        Time Complexity: O(log n) bounded by tree height.
        """
        while index > 0:
            parent_idx = self._parent(index)
            if self._heap[index][0] > self._heap[parent_idx][0]:
                self._heap[index], self._heap[parent_idx] = self._heap[parent_idx], self._heap[index]
                index = parent_idx
            else:
                break

    def _sift_down(self, index: int) -> None:
        """
        Trickle element at `index` downward by swapping with its largest child until heap invariant holds.
        Time Complexity: O(log n) bounded by tree height.
        """
        size = len(self._heap)
        while True:
            largest = index
            left_idx = self._left(index)
            right_idx = self._right(index)

            if left_idx < size and self._heap[left_idx][0] > self._heap[largest][0]:
                largest = left_idx

            if right_idx < size and self._heap[right_idx][0] > self._heap[largest][0]:
                largest = right_idx

            if largest != index:
                self._heap[index], self._heap[largest] = self._heap[largest], self._heap[index]
                index = largest
            else:
                break

    def build_heap(self, entries: list) -> None:
        """
        Build a max-heap in O(n) time using Floyd's bottom-up algorithm.
        Starts at the last non-leaf node (n // 2 - 1) and sifts down to root.
        """
        self._heap = list(entries)
        for i in range(len(self._heap) // 2 - 1, -1, -1):
            self._sift_down(i)

    def get_all_entries(self) -> list:
        """Return a copy of the raw heap array for UI inspection in Algorithm Lab."""
        return list(self._heap)

    def clear(self) -> None:
        """Reset the heap to an empty state."""
        self._heap.clear()

    def __len__(self) -> int:
        return len(self._heap)

    def __repr__(self) -> str:
        return f"MaxHeap(size={len(self._heap)})"

