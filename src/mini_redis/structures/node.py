from typing import Generic
from src.type_defs import T, K

class DoubleLinkedListNode(Generic[T]):
    __slots__ = ("data", "prev", "next")
    def __init__(self, data: T):
        self.data = data
        self.prev: DoubleLinkedListNode[T] | None = None
        self.next: DoubleLinkedListNode[T] | None = None

class HashNode(Generic[T, K]):
    __slots__ = ("key", "data", "next", "hash")
    def __init__(self, data:T, hash:int, key:K, next:HashNode[T, K] | None=None):
        self.data: T = data
        self.key: K = key
        self.hash: int = hash
        self.next : HashNode[T, K] | None= next