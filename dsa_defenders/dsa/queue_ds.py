"""
dsa_defenders/dsa/queue_ds.py

# DSA CONCEPT: FIFO QUEUE
# ==============================================================================
# This module implements a manual First-In-First-Out (FIFO) Queue from scratch.
# No collections.deque or external queue modules are used.
#
# Role in Game:
# When enemies spawn into the arena, they are enqueued in order of arrival.
# Under Queue targeting mode, the tower prioritizes the enemy that has been in
# the arena the longest (earliest spawn order) that is alive and within firing range.
#
# Modules that interact with this:
# - dsa/targeting.py (the targeting dispatcher)
# - ui/algorithm_lab.py (reads queue state for live visualization)
# ==============================================================================
"""

# ==============================================================================
# VIVA NOTES: FIFO QUEUE
# ==============================================================================
"""
WHAT IS A QUEUE?
A Queue is a linear data structure following the First-In, First-Out (FIFO) principle.
The element added first is the one removed first, exactly like people waiting in line
at a ticket counter.

WHY WAS A QUEUE CHOSEN FOR THIS GAME?
In tower defense games, early-spawned enemies have traveled the furthest toward the base.
A FIFO Queue models "First Come, First Served" dispatching: it ensures the tower shoots
the vanguard (oldest) enemy rather than getting distracted by newly arriving spawns.

HOW IS THIS IMPLEMENTATION STRUCTURED?
Rather than using `list.pop(0)` which takes O(n) time because every subsequent element
must shift left, this implementation uses a Python list with an integer `_head` pointer.
- Enqueue appends to the end in O(1).
- Dequeue increments `_head` in O(1).
- When dead space (`_head`) exceeds half the allocated list, a compaction step runs,
  achieving O(1) amortized dequeue time with O(n) space efficiency.

OPERATIONS & COMPLEXITY:
--------------------------------------------------------------------------------
Operation           Time Complexity     Space Complexity    Description
--------------------------------------------------------------------------------
enqueue(item)       O(1)                O(1)                Appends item at tail
dequeue()           O(1) amortized      O(1)                Removes item from head
peek()              O(1)                O(1)                Views item at head
is_empty()          O(1)                O(1)                Checks if head >= len
size()              O(1)                O(1)                Returns active count
remove(item)        O(n)                O(1)                Finds & removes element
to_list()           O(n)                O(n)                Returns active items
--------------------------------------------------------------------------------

DRY RUN TRACE:
1. Enqueue Enemy A (Spawn #1): queue = [A], head = 0 -> size = 1
2. Enqueue Enemy B (Spawn #2): queue = [A, B], head = 0 -> size = 2
3. Enqueue Enemy C (Spawn #3): queue = [A, B, C], head = 0 -> size = 3
4. Peek(): returns Enemy A (oldest)
5. Dequeue(): returns Enemy A, head becomes 1 -> remaining: [B, C], size = 2
6. If Enemy C dies mid-fight: remove(C) searches and deletes C -> [B]

LIKELY VIVA QUESTIONS & SHORT ANSWERS:
Q1: Why not just use Python's built-in `list.pop(0)` for dequeue?
A1: `list.pop(0)` has O(n) time complexity because every element in the array must
    shift one slot to the left in memory. With a head pointer, dequeue is O(1).

Q2: Why not use collections.deque?
A2: In educational DSA projects, manual implementations prove understanding of internal
    mechanics, memory management, pointers, and algorithmic trade-offs.

Q3: When would a FIFO Queue fail to defend the tower optimally?
A3: If a high-damage boss or high-speed runner spawns later, the Queue will ignore them
    and continue firing at an older, low-threat enemy until it leaves or dies.
"""


class Queue:
    """
    A manual First-In-First-Out (FIFO) Queue implemented using a list with a head pointer.
    
    # DSA CONCEPT: FIFO QUEUE
    Complexities:
      - enqueue: O(1)
      - dequeue: O(1) amortized
      - peek:    O(1)
      - remove:  O(n)
      - size:    O(1)
    """

    def __init__(self):
        """Initialize an empty FIFO queue."""
        self._items = []
        self._head = 0

    def enqueue(self, item) -> None:
        """
        Add an item to the rear (tail) of the queue.
        Time Complexity: O(1)
        """
        self._items.append(item)

    def dequeue(self):
        """
        Remove and return the front (head) item from the queue.
        Time Complexity: O(1) amortized
        Raises IndexError if the queue is empty.
        """
        if self.is_empty():
            raise IndexError("dequeue from an empty Queue")
        
        item = self._items[self._head]
        self._items[self._head] = None  # Allow garbage collection
        self._head += 1

        # Periodic memory compaction to prevent unbounded list growth
        if self._head > 32 and self._head > len(self._items) // 2:
            self._items = self._items[self._head:]
            self._head = 0

        return item

    def peek(self):
        """
        Return the front item without removing it.
        Time Complexity: O(1)
        Returns None if the queue is empty.
        """
        if self.is_empty():
            return None
        return self._items[self._head]

    def is_empty(self) -> bool:
        """
        Return True if there are no active elements in the queue, else False.
        Time Complexity: O(1)
        """
        return self._head >= len(self._items)

    def size(self) -> int:
        """
        Return the number of active elements in the queue.
        Time Complexity: O(1)
        """
        return len(self._items) - self._head

    def remove(self, item) -> bool:
        """
        Remove the first occurrence of an item (e.g. when an enemy is destroyed).
        Time Complexity: O(n)
        Returns True if item was found and removed, False otherwise.
        """
        for i in range(self._head, len(self._items)):
            if self._items[i] == item:
                # Remove element and shift
                del self._items[i]
                return True
        return False

    def to_list(self) -> list:
        """
        Return a Python list containing active elements in FIFO order.
        Useful for UI rendering in the Algorithm Lab.
        Time Complexity: O(n)
        """
        return [item for item in self._items[self._head:] if item is not None]

    def clear(self) -> None:
        """Reset the queue to an empty state."""
        self._items = []
        self._head = 0

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"Queue({self.to_list()})"
