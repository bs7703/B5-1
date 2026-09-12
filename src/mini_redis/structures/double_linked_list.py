"""
Non-circular doubly linked list.

Design:
- O(1) insertion and removal with known Node references.
- No membership search is performed.
- Internal operations assume valid nodes.
- Node ownership validation is intentionally omitted.
"""
from re import L
from typing import Generic, Iterator, Optional
from src.mini_redis.structures.node import DoubleLinkedListNode
from src.type_defs import T

class DoubleLinkedList(Generic[T]):
    """
    A non-circular doubly linked list.

    Invariants:
    - _size == 0 iff head is None and tail is None.
    - _size == 1 implies head is tail.
    - If head exists, head.prev is None.
    - If tail exists, tail.next is None.
    - For adjacent nodes A and B:
      A.next is B iff B.prev is A.
    - _size equals the number of reachable nodes.

    Preconditions:
    - _detach(node), remove_node(node), and move_to_front(node)
      assume that node belongs to this list.
    """

    __slots__ = ("head", "tail", "_size")

    def __init__(self) -> None:
        self.head: Optional[DoubleLinkedListNode[T]] = None
        self.tail: Optional[DoubleLinkedListNode[T]] = None
        self._size: int = 0

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def _detach(self, node: DoubleLinkedListNode[T]) -> None:
        """
        Detach a node from the list without changing _size.

        Precondition:
            node belongs to this list.

        Postcondition:
            node.prev is None.
            node.next is None.
        """
        prev = node.prev
        next_ = node.next

        if prev is not None:
            prev.next = next_
        else:
            self.head = next_

        if next_ is not None:
            next_.prev = prev
        else:
            self.tail = prev

        node.prev = None
        node.next = None

    def _insert_before(self, target: DoubleLinkedListNode[T], node: DoubleLinkedListNode[T]) -> None:
        prev = target.prev

        node.prev = prev
        node.next = target
        target.prev = node

        if prev is not None:
            prev.next = node
        else:
            self.head = node

    def _insert_after(self, target: DoubleLinkedListNode[T], node: DoubleLinkedListNode[T]) -> None:
        next_ = target.next

        node.prev = target
        node.next = next_
        target.next = node

        if next_ is not None:
            next_.prev = node
        else:
            self.tail = node

    def insert_front(self, data: T) -> DoubleLinkedListNode[T]:
        node = DoubleLinkedListNode(data)

        if self.head is not None:
            self._insert_before(self.head, node)
        else:
            self.head = node
            self.tail = node

        self._size += 1
        return node

    def insert_back(self, data: T) -> DoubleLinkedListNode[T]:
        node = DoubleLinkedListNode(data)

        if self.tail is not None:
            self._insert_after(self.tail, node)
        else:
            self.head = node
            self.tail = node

        self._size += 1
        return node

    def remove_front(self) -> Optional[T]:
        if self.head is None:
            return None

        node = self.head
        self._detach(node)
        self._size -= 1

        return node.data

    def remove_back(self) -> Optional[T]:
        if self.tail is None:
            return None

        node = self.tail
        self._detach(node)
        self._size -= 1

        return node.data

    def remove_node(self, node: DoubleLinkedListNode[T]) -> T:
        """
        Remove an existing node.

        Precondition:
            node belongs to this list.

        Postcondition:
            node.prev is None.
            node.next is None.
            _size decreases by one.
        """
        self._detach(node)
        self._size -= 1

        return node.data

    def move_to_front(self, node: DoubleLinkedListNode[T]) -> None:
        """
        Move an existing node to the front of the list.

        Precondition:
            node belongs to this list.

        Postcondition:
            node is self.head.
            _size remains unchanged.
        """
        if node is self.head:
            return

        head = self.head
        assert head is not None

        self._detach(node)
        self._insert_before(head, node)
    def __iter__(self)->Iterator[DoubleLinkedListNode[T]]:
        cur = self.head
        while (cur):
            yield cur
            cur = cur.next