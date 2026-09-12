# HashMap Design Notes

이 문서는 `src/mini_redis/structures/hashmap.py`의 상세 설계 의도와 학습 내용을 기록한다.

실제 구현 파일에는 짧은 주석만 두고, 자료구조의 원리·불변식(invariant)·시간복잡도·설계 선택의 이유는 이 문서에 분리한다.

---

## 1. 목적

이 `HashMap`은 Python의 `dict`를 사용하지 않고 직접 구현하는 **separate chaining 기반 hash table**이다.

핵심 흐름은 다음과 같다.

```text
key
 ↓
hash_func(key)
 ↓
hash value
 ↓
hash % capacity
 ↓
bucket index
 ↓
HashNode -> HashNode -> HashNode -> None
```

각 bucket에는 하나의 `HashNode` 또는 `None`이 저장된다.

충돌이 발생하면 같은 bucket 안에서 singly linked list 형태로 연결한다.

---

## 2. 주요 상태

```text
_hash_func / hash_func
_capacity
_buckets
_size
_load_factor
```

### `hash_func`

문자열 key를 UTF-8 bytes로 변환한 뒤 hash 값을 계산한다.

HashMap은 hash 함수의 구체적인 구현을 몰라도 되며, 외부에서 주입받는다.

이렇게 하면 자료구조와 hashing 정책이 분리된다.

### `_capacity`

현재 bucket 개수다.

이 구현에서는 초기값이 64이고, resize마다 2배 증가한다.

따라서 항상 2의 거듭제곱이다.

### `_buckets`

실제 bucket array다.

```python
[None] * capacity
```

형태로 미리 모든 bucket slot을 확보한다.

각 slot은 chain의 head만 가리킨다.

### `_size`

현재 HashMap에 실제로 들어 있는 entry/node 개수다.

### `_load_factor`

```text
size / capacity
```

로 정의한다.

현재 기준값은 `0.75`다.

---

## 3. Class Invariants

HashMap이 정상 상태라면 다음 조건이 항상 성립해야 한다.

### 구조 invariant

1. `len(_buckets) == _capacity`
2. `_capacity > 0`
3. `_capacity`는 항상 2의 거듭제곱
4. 각 bucket은 `None` 또는 유효한 singly linked chain의 head
5. 각 chain의 마지막 `next`는 `None`

### 데이터 invariant

6. 동일한 key는 HashMap 안에 최대 하나만 존재
7. `_size`는 실제 저장된 node 수와 일치
8. 모든 node는 자기 hash에 맞는 bucket에 존재

```text
node.hash % _capacity == bucket_index
```

### resize invariant

9. resize 전후로 모든 key-value mapping은 유지
10. node 자체는 새로 생성하지 않고 기존 node를 재연결할 수 있음
11. 기존 bucket의 node는 resize 후 정확히 두 위치 중 하나로 이동

```text
old_index
old_index + old_capacity
```

---

## 4. Separate Chaining

충돌이 발생하면 같은 bucket에 linked chain으로 저장한다.

예:

```text
bucket[3]
   |
   v
[A] -> [B] -> [C] -> None
```

A, B, C는 서로 다른 key일 수 있지만 동일한 bucket index를 가진다.

장점:

- 구현이 단순함
- bucket이 꽉 찬다는 개념이 없음
- 삭제가 자연스러움
- resize 정책과 분리하기 쉬움

단점:

- node 객체가 추가로 필요함
- pointer chasing 발생
- cache locality가 open addressing보다 좋지 않을 수 있음

---

## 5. Cached Hash

`HashNode`는 key/value뿐 아니라 hash 값도 저장한다.

개념적으로:

```text
HashNode
├── key
├── data
├── hash
└── next
```

hash를 node에 저장하는 이유:

1. resize 때 key를 다시 hash할 필요가 없음
2. chain 검색에서 hash를 먼저 비교 가능
3. power-of-two resize 최적화에 활용 가능

검색:

```python
if node.hash == h and node.key == key:
```

hash는 key equality를 대체하지 않는다.

다른 key가 같은 hash를 가질 수 있기 때문에 최종적으로 key 비교도 반드시 필요하다.

---

## 6. `_find`

`_find`는 bucket chain 내부 검색을 담당한다.

반환값:

```text
(prev, node)
```

찾은 경우:

```text
A -> B -> C

B 검색
=> (A, B)
```

head를 찾은 경우:

```text
A -> B

A 검색
=> (None, A)
```

찾지 못한 경우:

```text
(None, None)
```

`prev`를 같이 반환하는 이유는 `remove()`에서 predecessor가 필요하기 때문이다.

singly linked list에서는 현재 node만 알고 있으면 이전 node의 `next`를 수정할 수 없다.

---

## 7. `get`

흐름:

```text
key
 ↓
hash
 ↓
index
 ↓
bucket head
 ↓
_find
 ↓
node.data
```

평균 시간복잡도:

```text
O(1)
```

정확히는 평균 chain 길이가 load factor에 비례하므로:

```text
O(1 + α)
```

여기서:

```text
α = size / capacity
```

이다.

---

## 8. `contains`

현재 구현은:

```python
return self.get(key) is not None
```

으로 `get()`을 재사용한다.

이 방식은 **value로 `None`을 저장하지 않는다는 전제**에서만 의미적으로 안전하다.

Mini Redis의 string value 모델에서는 이 전제를 둘 수 있다.

범용 HashMap으로 확장한다면 `_find()`를 직접 호출하는 방식이 더 엄밀하다.

---

## 9. `put`

현재 삽입 방식은 **head insertion**이다.

기존:

```text
A -> B -> C
```

새 node N 삽입:

```text
N -> A -> B -> C
```

장점:

- tail 탐색 불필요
- 실제 연결 연산 자체는 O(1)
- 구현 단순

단, duplicate key 확인을 위해 chain 탐색은 여전히 필요하다.

---

## 10. Load Factor

load factor:

```text
α = size / capacity
```

현재 threshold:

```text
0.75
```

즉 평균적으로 bucket 4개당 entry 약 3개 수준에서 resize를 수행한다.

load factor가 너무 높아지면 chain이 길어지고 검색 성능이 악화될 수 있다.

좋은 hash 함수가 있더라도 capacity가 너무 작으면 충돌 자체는 피할 수 없다.

---

## 11. Resize 핵심 아이디어

이 구현의 가장 중요한 부분 중 하나다.

기존 capacity를 `m`이라고 하자.

resize 후:

```text
m -> 2m
```

capacity가 항상 2의 거듭제곱이므로 기존 bucket index는 hash의 하위 bit들로 결정된다.

예:

```text
capacity = 8 = 1000₂
```

기존 index는 hash의 하위 3bit를 사용한다.

resize:

```text
8 -> 16
```

이제 하위 4bit가 필요하다.

즉 새로 추가되는 bit 하나만 확인하면 된다.

검사:

```python
node.hash & old_capacity
```

결과가 0이면:

```text
old_index
```

결과가 1이면:

```text
old_index + old_capacity
```

로 이동한다.

---

## 12. `_renode`

기존 하나의 bucket chain을 두 개로 분해한다.

```text
old chain

A -> B -> C -> D
```

새 bit 기준:

```text
A = low
B = high
C = low
D = high
```

결과:

```text
low:
A -> C -> None

high:
B -> D -> None
```

각각 head와 tail을 유지하는 이유는 append를 O(1)에 수행하기 위해서다.

```text
low_head
low_tail

high_head
high_tail
```

---

## 13. 왜 `next_node`를 먼저 저장하는가

linked structure를 재배선할 때 가장 중요한 패턴이다.

```python
next_node = node.next
```

를 먼저 저장한다.

그 후:

```python
tail.next = node
```

같은 연결 변경을 수행한다.

그렇지 않으면 원래 chain의 다음 node를 잃어버릴 수 있다.

이 패턴은 linked list, tree rotation, graph adjacency 구조 등에서도 반복해서 등장한다.

---

## 14. Resize Complexity

모든 old bucket을 확인하므로:

```text
O(capacity)
```

모든 node를 한 번씩 재배치하므로:

```text
O(n)
```

총합:

```text
O(capacity + n)
```

load factor를 일정하게 유지한다면 capacity와 n이 같은 차수이므로 실질적으로:

```text
O(n)
```

으로 볼 수 있다.

resize 자체는 비싸지만 capacity를 2배로 늘리므로 자주 발생하지 않는다.

따라서 일반적인 insertion은 amortized O(1)로 볼 수 있다.

---

## 15. Remove

삭제에는 이전 node가 필요하다.

일반 삭제:

```text
A -> B -> C
     ↑
   delete
```

필요한 작업:

```text
A.next = C
```

head 삭제:

```text
A -> B -> C
↑
delete
```

필요한 작업:

```text
bucket[index] = B
```

삭제 후:

```python
node.next = None
```

로 끊어 두면 node가 chain에 더 이상 연결되지 않았다는 상태가 명확해진다.

---

## 16. 시간복잡도

평균적인 경우:

| 연산 | 복잡도 |
|---|---:|
| get | O(1) |
| contains | O(1) |
| put | amortized O(1) |
| remove | O(1) |
| resize | O(n) |

최악의 경우 모든 key가 하나의 bucket에 몰리면:

```text
O(n)
```

이 될 수 있다.

---

## 17. 현재 구현에서 중요한 설계 선택

### 직접 hash function 주입

HashMap과 hash algorithm을 분리한다.

### power-of-two capacity

resize를 단순화하고 bit split을 가능하게 한다.

### full hash caching

resize 시 재hash를 피하고 검색 prefilter로 활용한다.

### singly linked chaining

bucket당 별도의 LinkedList 객체를 만들지 않고 head node만 저장한다.

### head insertion

추가 연결 비용을 최소화한다.

### predecessor 반환

remove 구현을 단순화한다.

---

## 18. 향후 Mini Redis와 연결

이 HashMap은 Redis semantics를 직접 알 필요가 없다.

상위 계층에서 다음과 같이 조합될 수 있다.

```text
Database
   |
   +-- HashMap
   |     key -> Entry
   |
   +-- Doubly Linked List
   |     LRU order
   |
   +-- Min Heap
         TTL expiration
```

HashMap의 책임:

```text
key -> value/Entry 저장
검색
삽입
삭제
resize
```

HashMap이 몰라도 되는 것:

```text
LRU
TTL
used_memory
maxmemory
eviction policy
CLI command
Redis SET semantics
```

이 책임 분리를 유지하는 것이 중요하다.
