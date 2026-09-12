from typing import Generic, Optional
from src.type_defs import T, K

class DoubleLinkedListNode(Generic[T]):
    __slots__ = ("data", "prev", "next")
    def __init__(self, data: T):
        self.data = data
        self.prev: Optional["DoubleLinkedListNode[T]"] = None
        self.next: Optional["DoubleLinkedListNode[T]"] = None

class HashNode(Generic[T, K]):
    __slots__ = ("key", "data", "next", "hash")
    def __init__(self, data:T, hash:int, key:K, next:Optional["HashNode[T, K]"]=None):
        self.data: T = data
        self.key: K = key
        self.hash: int = hash
        self.next: Optional["HashNode[T, K]"] = next