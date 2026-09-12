# ADR-004: HashMap과 Redis 정책 분리

## 결정

HashMap은 Redis semantics, LRU, TTL, memory policy를 알지 않는다.

## HashMap 책임

- key hashing
- bucket indexing
- collision chain
- get
- put
- remove
- contains
- resize

## 상위 Database 책임

- SET overwrite semantics
- used_memory
- maxmemory
- eviction
- LRU
- TTL
- lazy expiration

## 이유

자료구조와 서비스 정책을 분리하면:

- 테스트가 쉬워진다.
- HashMap을 독립적으로 검증할 수 있다.
- LRU/TTL 구현이 HashMap 내부로 침투하지 않는다.
- 각 클래스의 invariant가 단순해진다.

## 최종 관계

```text
Database
   |
   +-- HashMap
   +-- DoublyLinkedList
   +-- MinHeap
```
