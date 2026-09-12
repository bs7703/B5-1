# Mini Redis - HashMap Documentation Set

이 폴더는 현재 직접 구현 중인 HashMap의 코드와 설계 문서를 분리해 정리한 버전이다.

## 파일

```text
src/mini_redis/structures/hashmap.py
    실제 구현
    로직은 원본 그대로 유지하고 짧은 주석만 추가

docs/structures/hashmap.md
    HashMap 전체 구조
    invariant
    search / insert / remove
    load factor
    resize
    complexity
    Mini Redis와의 관계

docs/decisions/
    001-separate-chaining.md
    002-power-of-two-capacity.md
    003-cache-full-hash.md
    004-separate-storage-policy.md
```

## 권장 읽기 순서

1. `hashmap.py`
2. `docs/structures/hashmap.md`
3. 필요한 설계 결정만 `docs/decisions/`에서 확인

실제 코드는 짧게 유지하고, 왜 이렇게 구현했는지는 문서에 남기는 구조다.
