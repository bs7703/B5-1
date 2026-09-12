from src.type_defs import T
from typing import Generic, Callable, Literal

COMPARATOR = Callable[[T, T], int]
HeapMode = Literal["MIN", "MAX"]

class Heap(Generic[T]):
    def __init__(self, mode:HeapMode, comp:COMPARATOR[T]) -> None:
        self._data:list[T] = list[T]()
        self.comp:COMPARATOR[T] = comp
        self._mode:str = mode
    def insert(self, value:T):
        self._data.append(value)
        self._shift_up(len(self._data) - 1)
    def _heapify(self, mode: HeapMode) -> None:
        if self._mode == mode:
            return
        self._mode = mode
        # 마지막 non-leaf node부터 root까지 재정렬
        for index in range(len(self._data) // 2 - 1, -1, -1):
            self._shift_down(index)
    def _compare(self, a: T, b: T) -> int:
        result = self.comp(a, b)
        if self._mode == "MAX":
            return result
        return -result
    def peek(self) -> T | None:
        return self._data[0] if self._data else None
    def pop(self) -> T:
        if not self._data:
            raise IndexError("pop from empty heap")
        result = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._shift_down(0)
        return result
    def _parent(self, index:int)->int:
        return (index - 1) // 2
    def _left(self, index: int) -> int | None:
        child = index * 2 + 1
        return child if child < len(self._data) else None
    def _right(self, index: int) -> int | None:
        child = index * 2 + 2
        return child if child < len(self._data) else None
    def _shift_up(self, index:int):
        while (index > 0):
            to_up = self._compare(self._data[index], self._data[self._parent(index)]) < 0
            if not (to_up):
                break
            self._swap(index, self._parent(index))
            index = self._parent(index)
    def _shift_down(self, index:int):
        while (True):
            to_left = self._left(index)
            to_right = self._right(index)
            to_swp = None
            if (to_right is not None and (self._compare(self._data[index], self._data[to_right]) > 0)):
                to_swp = to_right
            if (to_left is not None and (self._compare(self._data[index], self._data[to_left]) > 0)):
                if (to_swp is None or self._compare(self._data[to_left], self._data[to_swp]) < 0):
                    to_swp = to_left
            if to_swp is None:
                break
            self._swap(index, to_swp)
            index = to_swp
    def _swap(self, i:int, j:int):
        a = self._data[i]
        self._data[i] = self._data[j]
        self._data[j] = a