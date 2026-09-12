from dataclasses import dataclass
from typing import Any, Callable
from src.redis import Redis
Validator = Callable[[str], bool]
Handler = Callable[..., Any]


# =========================
# Validators
# =========================

def validate_string(value: str) -> bool:
    """
    SET key value 등에 사용.
    구체적인 길이 제한 등이 필요하면 이후 추가.
    """
    return True


def validate_non_negative_int(value: str) -> bool:
    """
    CONFIG SET maxmemory bytes

    bytes >= 0
    0은 unlimited.
    """
    try:
        result = int(value)
    except ValueError:
        raise ValueError("value must be an integer")

    if result < 0:
        raise ValueError("value must be >= 0")
    return True


def validate_int(value: str) -> bool:
    """
    EXPIRE seconds

    EXPIRE는 0 이하도 허용해야 한다.
    <= 0이면 handler가 즉시 만료 처리.
    """
    try:
        int(value)
        return True
    except ValueError:
        raise ValueError("value must be an integer")


# =========================
# Parsed command
# =========================

@dataclass
class ParsedCommand:
    command: tuple[str, ...]
    pos: dict[str, Any]

class Dispatcher:
    def __init__(self, redis:Redis):
        self.redis = redis

    def dispatch(self, cmd:list[str], sep:int):
        handler_name = "_".join(token.lower() for token in cmd[:sep]) + "_"
        handler = getattr(self.redis,handler_name,None)
        if handler is None:
            raise RuntimeError(f"handler not implemented: {handler_name}")
        return handler(*cmd[sep:])

COMMANDS: dict[tuple[str,...], dict[str, Validator]] = {
    ("SET",): {
            "key": validate_string,
            "value": validate_string,
    },

    ("GET",): {
            "key": validate_string,
    },

    ("DEL",): {
            "key": validate_string,
    },

    ("EXISTS",): {
            "key": validate_string,
    },

    ("DBSIZE",): {
    },

    ("KEYS",): {
    },

    ("CONFIG", "SET", "MAXMEMORY"): {
            "bytes": validate_non_negative_int,
    },

    ("INFO", "MEMORY"): {
    },

    ("EXPIRE",): {
            "key": validate_string,
            "seconds": validate_int,
    },

    ("TTL",): {
            "key": validate_string,
    },
    ("QUIT",): 
    {
    },
    ("EXIT",): 
    {
    },
        ("VISUALIZE",): 
    {
    }
}