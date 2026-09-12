# ADR-003: HashNode에 full hash 저장

## 결정

각 HashNode에 key/value뿐 아니라 계산된 full hash를 저장한다.

## 이유

1. resize 때 key를 다시 hash하지 않는다.
2. chain 탐색에서 hash를 먼저 비교할 수 있다.
3. power-of-two resize 시 bit split에 바로 사용한다.

## 정확성

hash equality는 key equality를 의미하지 않는다.

따라서 검색은:

```python
node.hash == h and node.key == key
```

를 사용한다.

## 대안

### key만 저장

장점:
- node 필드 감소

단점:
- resize 시 재hash 필요

### truncated fingerprint 저장

장점:
- C 같은 저수준 구현에서는 메모리 절감 가능

단점:
- Python에서는 int object/reference overhead 때문에 절감 효과가 제한적
- false fingerprint match 증가

현재 Python 학습 프로젝트에서는 full hash caching이 가장 명확하다.
