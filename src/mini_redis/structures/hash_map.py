from src.mini_redis.structures.node import HashNode
from src.type_defs import T
from src.utils.hash_func import HashFunction
from typing import Generic

BASIC_BUCKET_SIZE = 64
BUCKET_MAX_SIZE = 1024 * 128

class HashMap(Generic[T]):
    def __init__(self, hash_func:HashFunction):
        # 외부에서 주입된 hash 함수 사용
        self.hash_func:HashFunction = hash_func

        # resize 기준 load factor
        self._load_factor:float = 0.75

        # bucket 수는 2의 거듭제곱으로 유지
        self._capacity = BASIC_BUCKET_SIZE

        # 각 index는 singly linked chain의 head를 보관
        self._buckets: list[HashNode[T, str] | None] = [None] * self._capacity

        # 실제 저장된 node 수
        self._size:int = 0

    def size(self):
        return self._size

    def _renode(self, node: HashNode[T, str] | None) -> tuple[HashNode[T, str] | None, HashNode[T, str] | None]:
        # resize 시 기존 한 bucket chain을 low/high 두 chain으로 분리
        low_head = low_tail = None
        high_head = high_tail = None

        while node is not None:
            # next를 재연결하기 전에 원래 chain의 다음 node를 보존
            next_node = node.next

            # capacity가 2배가 될 때 새로 추가되는 상위 1bit 검사
            if (node.hash & self._capacity) == 0:
                if low_head is None:
                    low_head = node
                else:
                    low_tail.next = node
                low_tail = node
            else:
                if high_head is None:
                    high_head = node
                else:
                    high_tail.next = node
                high_tail = node

            node = next_node

        # 기존 chain 연결이 남지 않도록 각 새 chain의 tail 종료
        if low_tail is not None:
            low_tail.next = None
        if high_tail is not None:
            high_tail.next = None

        return low_head, high_head

    def _resize(self):
        # 현재 capacity의 2배 크기로 새 bucket 배열 생성
        new_buckets: list[HashNode[T, str] | None] = [None] * (self._capacity * 2)

        for i in range(self._capacity):
            if (self._buckets[i]):
                # 기존 bucket chain은 i 또는 capacity+i로만 이동
                low,high = self._renode(self._buckets[i])

                new_buckets[i] = low
                new_buckets[self._capacity + i] = high

                # 기존 bucket 참조 해제
                self._buckets[i] = None

        self._capacity *= 2
        self._buckets = new_buckets

    # bucket chain에서 key를 찾고, 삭제를 위해 prev도 함께 반환
    def _find(self, start_node:HashNode[T,str] | None, key:str, h:int)->tuple[HashNode[T,str] | None, HashNode[T,str] | None]:
        prev: HashNode[T, str] | None = None
        node = start_node

        while node is not None:
            # cached hash로 먼저 좁힌 뒤 실제 key까지 확인
            if node.hash == h and node.key == key:
                return prev, node

            prev = node
            node = node.next

        return None, None

    def get(self, key:str)->T | None:
        h = self.hash_func(key.encode("utf-8"))
        idx = h % self._capacity
        start_node = self._buckets[idx]

        _, match = self._find(start_node, key, h)

        if (match):
            return match.data

        return None

    def contains(self, key:str)->bool:
        # 현재 설계에서는 None을 value로 저장하지 않는다는 전제
        return self.get(key) is not None

    def put(self, key:str, data:T)->bool:
        # 저장 가능한 최대 entry 수 제한
        if ((self._size + 1) > BUCKET_MAX_SIZE):
            raise IndexError("더이상 추가 불가능합니다.")

        h = self.hash_func(key.encode("utf-8"))
        idx = h % self._capacity

        # 동일 key가 이미 존재하면 삽입하지 않음
        entry = self._find(self._buckets[idx], key, h)[1]
        if entry is not None:
            entry.data = data
            return True

        n = HashNode(key=key, hash=h, data=data)

        # head insertion: O(1)
        n.next = self._buckets[idx]
        self._buckets[idx] = n
        self._size += 1        

        # load factor 초과 시 먼저 resize
        if (self._size / self._capacity) > (self._load_factor):
            self._resize()
        return True

    def remove(self, key:str)->T | None:
        h = self.hash_func(key.encode("utf-8"))
        idx = h % self._capacity
        start_node = self._buckets[idx]

        prev, node = self._find(start_node, key, h)
        if not node:
            return None
        data = node.data
        # head가 아닌 경우 predecessor의 next를 우회 연결
        if prev:
            prev.next = node.next
        else:
            # head 삭제
            self._buckets[idx] = node.next

        node.next = None
        self._size -= 1

        return data