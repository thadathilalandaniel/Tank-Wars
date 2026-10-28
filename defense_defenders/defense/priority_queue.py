import math


def calculate_threat(enemy, tower_x: float, tower_y: float) -> float:
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
        if self.is_empty():
            return None
        return self._heap[0]

    def insert(self, priority: float, item) -> None:
        entry = (priority, item)
        self._heap.append(entry)
        self._sift_up(len(self._heap) - 1)

    def extract_max(self):
        if self.is_empty():
            raise IndexError("extract_max from empty MaxHeap")

        root = self._heap[0]
        last = self._heap.pop()

        if len(self._heap) > 0:
            self._heap[0] = last
            self._sift_down(0)

        return root

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent_idx = self._parent(index)
            if self._heap[index][0] > self._heap[parent_idx][0]:
                self._heap[index], self._heap[parent_idx] = self._heap[parent_idx], self._heap[index]
                index = parent_idx
            else:
                break

    def _sift_down(self, index: int) -> None:
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
        self._heap = list(entries)
        for i in range(len(self._heap) // 2 - 1, -1, -1):
            self._sift_down(i)

    def get_all_entries(self) -> list:
        return list(self._heap)

    def clear(self) -> None:
        self._heap.clear()

    def __len__(self) -> int:
        return len(self._heap)

    def __repr__(self) -> str:
        return f"MaxHeap(size={len(self._heap)})"

