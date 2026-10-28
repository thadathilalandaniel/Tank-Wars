class Queue:
    def __init__(self):
        self._items = []
        self._head = 0

    def enqueue(self, item) -> None:
        self._items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from an empty Queue")

        item = self._items[self._head]
        self._items[self._head] = None
        self._head += 1

        if self._head > 32 and self._head > len(self._items) // 2:
            self._items = self._items[self._head:]
            self._head = 0

        return item

    def peek(self):
        if self.is_empty():
            return None
        return self._items[self._head]

    def is_empty(self) -> bool:
        return self._head >= len(self._items)

    def size(self) -> int:
        return len(self._items) - self._head

    def remove(self, item) -> bool:
        for i in range(self._head, len(self._items)):
            if self._items[i] == item:
                del self._items[i]
                return True
        return False

    def to_list(self) -> list:
        return [item for item in self._items[self._head:] if item is not None]

    def clear(self) -> None:
        self._items = []
        self._head = 0

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"Queue({self.to_list()})"

