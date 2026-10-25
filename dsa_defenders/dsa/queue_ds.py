"""
dsa_defenders/dsa/queue_ds.py

Manual First-In-First-Out (FIFO) Queue implemented from foundational principles.
No collections.deque or external queue libraries are used.

Role in Game:
Under Queue targeting mode, incoming enemies are enqueued in sequential arrival order.
The defense tower prioritizes the vanguard (oldest alive enemy in attack range) to
intercept hostiles that have traveled furthest toward the base.
"""


class Queue:
    """
    A manual FIFO Queue implemented using a list with an integer head pointer.

    Algorithmic Decisions & Complexities:
      - enqueue(item): O(1) appending to tail.
      - dequeue(): O(1) amortized. Instead of list.pop(0) which takes O(n) due to shifting
        every subsequent element left, an integer `_head` pointer is incremented in O(1).
      - Memory Compaction: When dead space (`_head`) exceeds 32 slots and more than half
        the allocated list, the list is sliced to reclaim memory while keeping amortized O(1).
      - peek(): O(1) access to front element.
      - remove(item): O(n) search to delete an enemy destroyed mid-game.
      - size(): O(1) calculated as len(_items) - _head.
    """

    def __init__(self):
        self._items = []
        self._head = 0

    def enqueue(self, item) -> None:
        """Add an item to the rear (tail) of the queue in O(1) time."""
        self._items.append(item)

    def dequeue(self):
        """
        Remove and return the front item in O(1) amortized time.
        Raises IndexError if the queue is empty.
        """
        if self.is_empty():
            raise IndexError("dequeue from an empty Queue")

        item = self._items[self._head]
        self._items[self._head] = None  # Clear reference to allow garbage collection
        self._head += 1

        # Periodic memory compaction to prevent unbounded list growth
        if self._head > 32 and self._head > len(self._items) // 2:
            self._items = self._items[self._head:]
            self._head = 0

        return item

    def peek(self):
        """Return the front item without removing it in O(1) time, or None if empty."""
        if self.is_empty():
            return None
        return self._items[self._head]

    def is_empty(self) -> bool:
        """Return True if there are no active elements in the queue (O(1))."""
        return self._head >= len(self._items)

    def size(self) -> int:
        """Return the number of active elements in O(1) time."""
        return len(self._items) - self._head

    def remove(self, item) -> bool:
        """
        Remove the first occurrence of an item in O(n) time (e.g., when an enemy is defeated).
        Returns True if found and removed, False otherwise.
        """
        for i in range(self._head, len(self._items)):
            if self._items[i] == item:
                del self._items[i]
                return True
        return False

    def to_list(self) -> list:
        """Return active elements in FIFO order for iteration and live UI inspection."""
        return [item for item in self._items[self._head:] if item is not None]

    def clear(self) -> None:
        """Reset the queue to an empty state."""
        self._items = []
        self._head = 0

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"Queue({self.to_list()})"

