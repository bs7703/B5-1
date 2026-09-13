# 파일 생성을 위한 내부 처리 (사용자에게는 다운로드 링크로 제공됨)
content = """# Mini Redis

해시맵, 이중 연결 리스트, 최소 힙을 직접 구현해 만든 CLI 기반 In-Memory Key-Value 저장소입니다.  
실제 Redis의 모든 기능을 복제하는 대신, 빠른 조회·LRU eviction·TTL 만료가 어떤 자료구조 조합으로 동작하는지 이해하는 데 초점을 둡니다.

## 미션 목표

이 프로젝트는 다음 질문에 구현 코드로 답하는 것을 목표로 합니다.

- 해시맵은 왜 평균 O(1)에 가깝게 키를 찾을 수 있는가?
- 해시맵과 이중 연결 리스트를 함께 쓰면 왜 O(1) LRU 추적이 가능한가?
- 만료 시각 관리에 왜 최소 힙이 적합한가?
- 메모리 제한을 넘겼을 때 어떤 순서로 키를 제거해야 하는가?

## 지원 명령어

| 분류 | 명령어 | 설명 |
|---|---|---|
| String | `SET key value` | 값을 저장하고 LRU 사용 시각을 갱신합니다. 기존 TTL은 제거됩니다. |
| String | `GET key` | 값을 조회합니다. 성공한 조회만 LRU를 갱신합니다. |
| String | `DEL key` | 키를 삭제하고 LRU·메모리 상태를 함께 갱신합니다. |
| String | `EXISTS key` | 키 존재 여부를 반환합니다. |
| String | `DBSIZE` | 현재 저장된 키 수를 반환합니다. |
| String | `KEYS` | 전체 키를 배열 형태로 출력합니다. |
| Memory | `CONFIG SET maxmemory bytes` | 최대 메모리를 UTF-8 바이트 단위로 설정합니다. `0`은 무제한입니다. |
| Memory | `INFO memory` | `used_memory`, `maxmemory`, `evicted_keys`를 출력합니다. |
| TTL | `EXPIRE key seconds` | 키의 만료 시간을 초 단위로 설정합니다. |
| TTL | `TTL key` | 남은 TTL을 반환합니다. |
| CLI | `QUIT`, `EXIT` | REPL을 종료합니다. |

명령어는 대소문자를 구분하지 않으며, 값은 큰따옴표로 감쌀 수 있습니다.

```text
mini-redis> SET user:1 "Alice Kim"
OK
mini-redis> GET user:1
"Alice Kim"
mini-redis> TTL user:1
(integer) -1
실행 방법
Python 3.8 이상에서 실행합니다.

bash
📋 복사
python main.py
핵심 구조
text
📋 복사
CLI
  -> Parser
  -> ParsedCommand
  -> Dispatcher
  -> Redis
       ├─ HashMap: key -> Entry
       ├─ DoublyLinkedList: LRU 순서
       └─ Min Heap: 가장 빠른 TTL
  -> Formatter
1. HashMap
해시 함수는 직접 구현합니다.
충돌은 separate chaining으로 해결합니다.
각 노드는 key, cached hash, value, next를 보관합니다.
load factor가 0.75를 넘으면 버킷 수를 2배로 확장합니다.
resize 시 cached hash의 다음 비트로 low/high chain을 분리합니다.
2. LRU: HashMap + Doubly Linked List
HashMap의 값은 단순 문자열이 아니라 Entry입니다.

python
📋 복사
Entry(
    value: str,
    lru_node: DoubleLinkedListNode[str],
    expire_at: Optional[int],
)
Entry가 자신의 LRU 노드를 직접 참조하므로, GET, SET, DEL, eviction 시 연결 리스트를 탐색할 필요가 없습니다.

GET 성공: 해당 노드를 front로 이동
SET 성공: 해당 노드를 front로 이동
메모리 초과: back의 키부터 제거
DEL/만료: HashMap과 LRU 노드를 함께 제거
따라서 LRU 갱신과 제거는 모두 O(1)입니다.

3. TTL: Min Heap + Lazy Deletion
TTL heap에는 다음 기록을 저장합니다.

python
📋 복사
TTL(key: str, expire_at: int)
동일 키에 EXPIRE를 다시 실행하거나 SET으로 TTL을 초기화해도 과거 heap 기록을 즉시 삭제하지 않습니다. 대신 heap 최상단을 꺼낼 때, 현재 Entry.expire_at과 heap 기록의 expire_at이 같은 경우에만 실제 키를 삭제합니다.

text
📋 복사
heap record가 최신 TTL인가?
  ├─ yes: HashMap + LRU에서 키 삭제
  └─ no : stale record이므로 버림
이 lazy deletion 방식은 heap의 임의 위치 삭제가 필요한 복잡도를 피하면서도, 가장 빠른 만료 항목을 O(1)에 확인하고 O(log n)에 제거할 수 있게 합니다.

4. 메모리 제한과 Eviction
논리적 메모리 사용량은 자료구조 자체의 오버헤드를 제외하고 다음처럼 계산합니다.

text
📋 복사
used_memory = Σ(UTF-8 key byte length + UTF-8 value byte length)
SET 뒤 maxmemory > 0이고 사용량이 한도를 넘으면, LRU tail부터 제거하여 사용량이 한도 이하가 될 때까지 eviction을 반복합니다.

단일 key/value 쌍 자체가 한도보다 크면 저장하지 않고 OOM 오류를 반환합니다.

명령 처리와 출력 분리
명령 처리는 다음 책임으로 나뉩니다.

구성 요소	책임
registry.py	명령 token, 인자 validator, handler, 응답 종류를 선언
parse.py	입력을 검증하고 ParsedCommand 생성
dispatcher.py	handler 호출 후 의미 있는 Reply 생성
redis.py	데이터 저장, TTL, LRU, eviction 정책 수행
formatter.py	원시 결과를 Redis 스타일 CLI 출력으로 변환
이 분리를 통해 저장소 로직은 (integer), (nil), (error) 같은 표시 형식에 의존하지 않습니다.

출력 규칙
text
📋 복사
SET user:1 Alice              -> OK
GET missing                   -> (nil)
DEL missing                   -> (integer) 0
TTL missing                   -> (integer) -2
CONFIG SET maxmemory invalid  -> (error) ERR value is not an integer or out of range
HELLO                         -> (error) ERR unknown command 'HELLO'
학습 포인트
이 프로젝트에서 중점적으로 확인한 내용입니다.

해시 충돌과 separate chaining
power-of-two capacity와 load factor 기반 resize
cached hash를 이용한 resize 재배치
이중 연결 리스트의 O(1) detach, insert, move
HashMap과 LRU 노드의 상태 불변식
최소 힙의 sift-up, sift-down과 TTL 우선순위
lazy deletion이 stale record를 안전하게 처리하는 방식
monotonic clock을 사용한 TTL 측정
CLI parsing, validation, dispatch, formatting의 책임 분리
메모리 한도와 LRU eviction의 상호작용
제한 사항
네트워크 서버 기능은 구현하지 않습니다.
데이터 영속성은 지원하지 않습니다.
String 타입만 지원합니다.
동시성 제어와 분산 환경은 범위에 포함하지 않습니다.
실제 Redis 프로토콜(RESP)을 구현하지 않고, Redis 스타일 CLI 출력만 제공합니다.
수동 검증 시나리오
text
📋 복사
CONFIG SET maxmemory 10
SET a aa
SET b bb
GET a
SET c cccc
GET b
GET a
EXPIRE a 1
GET a  # 1초 뒤 (nil)
INFO memory
위 흐름에서 GET a 이후 a가 최신 사용 키가 되므로, 이후 메모리 초과 시 b가 먼저 제거되는지 확인할 수 있습니다.

프로젝트 구조
text
📋 복사
main.py
src/
├─ cli.py
├─ redis.py
├─ mini_redis/
│  ├─ error.py
│  ├─ formatter.py
│  ├─ commands/
│  │  ├─ schema.py
│  │  ├─ registry.py
│  │  ├─ parse.py
│  │  ├─ dispatcher.py
│  │  └─ validators.py
│  └─ structures/
│     ├─ hash_map.py
│     ├─ double_linked_list.py
│     ├─ heap.py
│     └─ node.py
└─ docs/
   ├─ structures/
   └─ decisions/