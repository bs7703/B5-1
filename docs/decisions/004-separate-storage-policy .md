# ADR-002: Capacity를 2의 거듭제곱으로 유지

## 결정

초기 capacity를 2의 거듭제곱으로 두고 resize 시 항상 2배 증가시킨다.

## 이유

old capacity가 `m`일 때 `m -> 2m` resize를 하면 기존 bucket의 node는:

```text
old_index
old_index + m
```

둘 중 하나로만 이동한다.

판별은:

```python
node.hash & m
```

로 가능하다.

따라서 key를 다시 hash하지 않고 cached hash의 새 bit 하나만 확인하면 된다.

## 예시

```text
m = 8 = 1000₂
```

resize 후 16이 되면 기존 하위 3bit에 새 bit 하나만 추가된다.

## Trade-off

- 임의 capacity를 선택할 수 없다.
- 대신 resize 구조가 단순해지고 bit 기반 최적화가 가능하다.
