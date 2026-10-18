"""
dsa_defenders/dsa/priority_queue.py

# DSA CONCEPT: BINARY MAX-HEAP
# ==============================================================================
# This module implements a manual Binary Max-Heap and Priority Queue from scratch.
# The standard library `heapq` module is STRICTLY FORBIDDEN and NOT imported.
#
# Role in Game:
# In Priority Queue targeting mode, the tower targets enemies not by arrival time,
# but by calculated THREAT SCORE. Fast runners, heavy tanks, bosses, and enemies
# dangerously close to the base receive higher threat scores. The Binary Max-Heap
# maintains the maximum threat element at its root in O(log n) time per insertion/
# extraction, and supports O(n) heap construction via Floyd's build_heap algorithm.
#
# Modules that interact with this:
# - dsa/targeting.py (the targeting dispatcher)
# - ui/algorithm_lab.py (reads heap structure for live tree/array visualization)
# ==============================================================================
"""

import math

# ==============================================================================
# VIVA NOTES: BINARY MAX-HEAP
# ==============================================================================
"""
WHAT IS A BINARY MAX-HEAP?
A Binary Max-Heap is a complete binary tree stored compactly as an array/list,
where every parent node satisfies the Max-Heap Property:
    Parent Value >= Child Values
The maximum element is therefore always at index 0 (the root).

WHY AN ARRAY REPRESENTS A COMPLETE BINARY TREE:
Because a complete binary tree has no missing leaves except possibly at the bottom
level filled left-to-right, we don't need child/parent pointers. We use arithmetic:
    parent(i) = (i - 1) // 2
    left_child(i) = 2 * i + 1
    right_child(i) = 2 * i + 2

WHY WAS A MAX-HEAP CHOSEN INSTEAD OF A SORTED LIST?
- In an unsorted list: finding the maximum takes O(n).
- In a sorted list: finding maximum is O(1), but inserting a new enemy requires O(n)
  shifting to maintain sorted order.
- In a Binary Heap: both insertion and extraction of the maximum take O(log n).
  Furthermore, rebuilding the entire heap with updated threats runs in O(n) using
  Floyd's bottom-up heap construction, making it ideal for real-time video games!

OPERATIONS & COMPLEXITIES:
--------------------------------------------------------------------------------
Operation           Time Complexity     Space Complexity    Description
--------------------------------------------------------------------------------
insert(p, item)     O(log n)            O(1)                Appends & sifts up
extract_max()       O(log n)            O(1)                Swaps with tail & sifts down
peek_max()          O(1)                O(1)                Returns root element
build_heap(items)   O(n)                O(n)                Floyd's bottom-up build
is_empty()          O(1)                O(1)                Checks if size == 0
size()              O(1)                O(1)                Returns length
--------------------------------------------------------------------------------

DRY RUN TRACE:
Insert entries with threats (10, A), (40, B), (25, C), (50, D):
1. Insert (10, A): heap = [(10, A)]
2. Insert (40, B): placed at index 1 -> parent is index 0 (10). 40 > 10, so swap!
   heap = [(40, B), (10, A)]
3. Insert (25, C): placed at index 2 -> parent is index 0 (40). 25 <= 40, stop.
   heap = [(40, B), (10, A), (25, C)]
4. Insert (50, D): placed at index 3 -> parent is index 1 (10). 50 > 10, swap!
   heap = [(40, B), (50, D), (25, C), (10, A)]
   Next parent is index 0 (40). 50 > 40, swap!
   heap = [(50, D), (40, B), (25, C), (10, A)]
5. extract_max(): root (50, D) popped. Last element (10, A) moved to root.
   Sift down 10 with larger child (40). New root is (40, B).

LIKELY VIVA QUESTIONS & SHORT ANSWERS:
Q1: Why is build_heap O(n) instead of O(n log n)?
A1: Sifting down from internal nodes towards leaves costs less work because the majority
    of nodes are at the lower levels where tree height is small. Summing h/2^h over all
    levels converges to a constant, proving Floyd's algorithm is O(n).

Q2: Why not use a Binary Search Tree (BST) instead of a Heap?
A2: A simple BST can degenerate into a linked list of height O(n) on ordered inputs.
    An array-based heap is always complete (balanced height = floor(log2(n))), requires
    zero pointer overhead, and exhibits superior CPU cache locality.

Q3: How does the game handle dynamic threat scores that change every frame?
A3: Enemies move constantly, so their distance to the tower changes. We recompute threats
    and execute `build_heap` in O(n) time during target acquisition, keeping priorities fresh.
"""


def calculate_threat(enemy, tower_x: float, tower_y: float) -> float:
    """
    Compute a composite threat score for an enemy relative to the tower.
    
    Formula:
      threat = (damage * 3.0) + (speed * 1.5) + (1000.0 / (dist + 1.0))
               + type_bonus - (health * 0.05)
               
    Explanation of Terms:
      1. damage * 3.0:
         High-damage units (Tanks, Bosses) directly endanger player hearts.
      2. speed * 1.5:
         Fast units (Runners) close the gap rapidly and require prompt interception.
      3. 1000.0 / (dist + 1.0):
         Proximity urgency. As distance approaches 0, threat spikes hyperbolically.
      4. type_bonus:
         Specific priority bonuses for Bosses (+120), Tanks (+35), Runners (+20).
      5. - (health * 0.05):
         Small tie-breaker favoring nearly defeated units to eliminate damage sources faster.
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
    A manual Binary Max-Heap storing entries of form (priority: float, item: Any).
    
    # DSA CONCEPT: BINARY MAX-HEAP
    """

    def __init__(self):
        """Initialize an empty Max-Heap array."""
        self._heap = []

    # --- Array Index Helper Functions ---
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
        """Return the number of entries currently in the heap."""
        return len(self._heap)

    def is_empty(self) -> bool:
        """Check if the heap has no entries."""
        return len(self._heap) == 0

    def peek_max(self):
        """
        Return the element with highest priority (priority, item) without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self._heap[0]

    def insert(self, priority: float, item) -> None:
        """
        Insert an item with a given priority into the heap and sift-up.
        Time Complexity: O(log n)
        """
        entry = (priority, item)
        self._heap.append(entry)
        self._sift_up(len(self._heap) - 1)

    def extract_max(self):
        """
        Remove and return the entry (priority, item) with highest priority.
        Time Complexity: O(log n)
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
        Move element at index upward until the Max-Heap property is satisfied.
        Time Complexity: O(log n)
        """
        while index > 0:
            parent_idx = self._parent(index)
            # If current priority is strictly greater than parent's priority, swap!
            if self._heap[index][0] > self._heap[parent_idx][0]:
                self._heap[index], self._heap[parent_idx] = self._heap[parent_idx], self._heap[index]
                index = parent_idx
            else:
                break

    def _sift_down(self, index: int) -> None:
        """
        Move element at index downward until the Max-Heap property is satisfied.
        Time Complexity: O(log n)
        """
        size = len(self._heap)
        while True:
            largest = index
            left_idx = self._left(index)
            right_idx = self._right(index)

            # Check if left child has higher priority
            if left_idx < size and self._heap[left_idx][0] > self._heap[largest][0]:
                largest = left_idx

            # Check if right child has even higher priority
            if right_idx < size and self._heap[right_idx][0] > self._heap[largest][0]:
                largest = right_idx

            if largest != index:
                self._heap[index], self._heap[largest] = self._heap[largest], self._heap[index]
                index = largest
            else:
                break

    def build_heap(self, entries: list) -> None:
        """
        Build a max-heap from an unsorted list of (priority, item) tuples
        using Floyd's bottom-up construction algorithm.
        Time Complexity: O(n)
        """
        self._heap = list(entries)
        # Sift down all non-leaf nodes starting from (n // 2 - 1) down to 0
        for i in range(len(self._heap) // 2 - 1, -1, -1):
            self._sift_down(i)

    def get_all_entries(self) -> list:
        """
        Return the raw underlying heap array.
        Useful for live visualization in the Algorithm Lab.
        """
        return list(self._heap)

    def clear(self) -> None:
        """Reset the heap to an empty state."""
        self._heap.clear()

    def __len__(self) -> int:
        return len(self._heap)

    def __repr__(self) -> str:
        return f"MaxHeap(size={len(self._heap)})"
