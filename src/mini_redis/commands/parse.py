from typing import List, Optional
from src.mini_redis.commands.dispatcher import COMMANDS

def parse_commands(lines: Optional[List[str]]) -> int:
    if not lines:
        raise ValueError("Input Empty Error")

    for cmd, pos in COMMANDS.items():
        if tuple(lines[:len(cmd)]) != cmd:
            continue
        if len(lines) != len(cmd) + len(pos):
            raise ValueError("Command Pos Num Is Not Equal")
        for value, validator in zip(lines[len(cmd):],pos.values()):
            if not validator(value):
                raise ValueError("Command Pos Value Is Not Valid")
        return len(cmd)
    raise ValueError("Command Is Not Valid")
"""
test_commands: List[List[str]] = [
    # 기본 key/value
    ["SET", "name", "alice", "DD"],
    ["SET", "age", "30"],
    ["SET", "counter", "100"],

    # key 조회
    ["GET", "name"],
    ["GET", "age"],
    ["GET", "counter"],

    # 삭제
    ["DEL", "name"],
    ["DEL", "age"],

    # TTL / expire
    ["EXPIRE", "name", "60"],
    ["EXPIRE", "session", "3600"],
    ["EXPIRE", "name"],
    ["TTL", "session"],

    # 존재 여부
    ["EXISTS", "name"],
    ["EXISTS", "unknown"],

    # 메모리/LRU 관련 명령이 있다면
    ["MAXMEMORY", "1000"],
    ["EVICTION", "lru"],

    # 단일 명령
    ["KEYS"],
    ["INFO", "MEMORY"],
]

for test in test_commands:
    try:
        result = parse_commands(test)
        print(f"{test} -> {result}")
    except Exception as e:
        print(f"{test} -> ERROR: {e}")
"""