from dataclasses import dataclass
from enum import Enum
from typing import Callable, Tuple

Validator = Callable[[str], bool]


class ReplyKind(Enum):
    SIMPLE = "simple"      # OK
    BULK = "bulk"          # "value" / (nil)
    INTEGER = "integer"    # (integer) N
    ARRAY = "array"        # 1. "key"
    TEXT = "text"          # INFO memory


@dataclass(frozen=True)
class CommandSpec:
    tokens: Tuple[str, ...]
    validators: Tuple[Validator, ...]
    handler_name: str
    reply_kind: ReplyKind


@dataclass(frozen=True)
class ParsedCommand:
    spec: CommandSpec
    args: Tuple[str, ...]