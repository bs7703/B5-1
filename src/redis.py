from dataclasses import dataclass
from typing import Optional
import time
from src.mini_redis.structures.heap import Heap
from src.mini_redis.structures.double_linked_list import DoubleLinkedList
from src.mini_redis.structures.hash_map import HashMap
from src.mini_redis.structures.node import DoubleLinkedListNode
from src.utils.hash_func import hashfunc
from src.mini_redis.error import CLIExit
from src.visualizer import Visualizer

BASIC_MAX_MEMORY = 100 #(64MB)
TO_NANO_SEC = 1_000_000_000
@dataclass
class Entry():
    value:str
    lru_node:DoubleLinkedListNode[str]
    expire_at:Optional[int]=None
@dataclass
class TTL():
    key:str
    expire_at:int
def TTL_COMPARATOR(a:TTL, b:TTL):
    return a.expire_at - b.expire_at

class Redis():
    def __init__(self):
        self._hashmap = HashMap[Entry](hashfunc)
        self._lru = DoubleLinkedList[str]()
        self._ttl = Heap[TTL]("MIN", TTL_COMPARATOR)
        self._start_time = time.monotonic_ns()
        self._max_memory:int = BASIC_MAX_MEMORY
        self._used_memory:int = 0
        self._evicted_keys = 0
        self._stored = 0
    def _now(self) -> int:
        return time.monotonic_ns() - self._start_time
    def visualize_(self)->str:
        hashmap = Visualizer.hashmap(self._hashmap)
        heap = Visualizer.heap(self._ttl)
        lru = Visualizer.doubly_linked_list(self._lru, value_attr="data")

        return (
            "\n"
            "================ HASHMAP ================\n"
            f"{hashmap}\n"
            "\n"
            "================ TTL HEAP ================\n"
            f"{heap}\n"
            "\n"
            "================ LRU =====================\n"
            f"{lru}\n"
        )
    def del_(self, key:str)->int:
        removed = self._hashmap.remove(key)
        if (removed):
            self._used_memory -= self._memory_size(key, removed.value)
            self._stored -= 1
            self._lru.remove_node(removed.lru_node)
            return 1
        return 0
    def trim_ttl(self):
        now = self._now()
        ttl = self._ttl.peek()

        while ttl and ttl.expire_at <= now:
            self._ttl.pop()
            entry = self._hashmap.get(ttl.key)

            if entry and entry.expire_at == ttl.expire_at:
                self.del_(ttl.key)

            ttl = self._ttl.peek()
    def _evict(self) -> None:
        while self._max_memory > 0 and self._used_memory > self._max_memory:
            key = self._lru.remove_back()

            if key is None:
                raise RuntimeError("LRU is empty while memory exceeds maxmemory")

            entry = self._hashmap.remove(key)

            if entry is None:
                raise RuntimeError("LRU and HashMap are out of sync")
            self._stored -= 1
            self._used_memory -= self._memory_size(key, entry.value)
            self._evicted_keys += 1
    def _memory_size(self, key: str, value: str) -> int:
        return len(key.encode("utf-8")) + len(value.encode("utf-8"))
    def set_(self, key: str, value: str):
        if self._max_memory > 0 and self._memory_size(key, value) > self._max_memory:
            raise ValueError("OOM")
        entry = self._hashmap.get(key)
        if entry is not None:
            old_size = len(entry.value.encode("utf-8"))
            new_size = len(value.encode("utf-8"))

            self._used_memory += new_size - old_size

            entry.value = value
            entry.expire_at = None

            self._lru.move_to_front(entry.lru_node)

        else:
            lru_node = self._lru.insert_front(key)
            self._hashmap.put(key, Entry(value, lru_node=lru_node))
            self._used_memory += self._memory_size(key, value)
            self._stored += 1
        if self._used_memory > self._max_memory:
            self._evict()

        return "OK"
    def get_(self, key:str)->str:
        entry = self._hashmap.get(key)
        if entry is not None:
            if (entry.expire_at is not None) and (entry.expire_at <= self._now()):
                self.del_(key)
                raise ValueError("(nil)")
            self._lru.move_to_front(entry.lru_node)
            return entry.value
        else:
            raise ValueError("(nil)")
    def keys_(self)->str:
        mystr:str = ""
        for a in self._lru:
            mystr += a.data + "\n"
        return mystr if mystr != "" else "(empty array)"
    def exists_(self, key:str)->int:
        return 1 if self._hashmap.contains(key) is True else 0
    def config_set_maxmemory_(self, maxm:str)->str:
        self._max_memory = int(maxm)
        if self._max_memory > 0 and self._used_memory > self._max_memory:
            self._evict()
        return "OK"
    def expire_(self, key:str, sec:str)->int:
        entry = self._hashmap.get(key)
        ttl = int(sec) * TO_NANO_SEC
        if (entry is None):
            return 0
        if (ttl <= 0):
            self.del_(key)
        else:
            t = self._now()
            entry.expire_at = (t + ttl)
            self._ttl.insert(TTL(key,t + ttl))
        return 1
    def dbsize_(self)->int:
        return self._stored
    def ttl_(self, key: str) -> int:
        entry = self._hashmap.get(key)

        if entry is None:
            return -2

        if entry.expire_at is None:
            return -1

        now = self._now()

        if entry.expire_at <= now:
            self.del_(key)
            return -2

        return (entry.expire_at - now) // TO_NANO_SEC
    def info_memory_(self)->str:
        return f"used_memory:{self._used_memory}\nmaxmemory:{self._max_memory}\nevicted_keys:{self._evicted_keys}"
    def exit_(self):
        raise CLIExit
    def quit_(self):
        raise CLIExit