from dataclasses import dataclass
from typing import Any
from src.redis import Redis
from src.mini_redis.commands.schema import ParsedCommand, ReplyKind


@dataclass(frozen=True)
class Reply:
    kind: ReplyKind
    value: Any


class Dispatcher:
    def __init__(self, redis:Redis):
        self.redis = redis

    def dispatch(self, parsed: ParsedCommand) -> Reply:
        self.redis.trim_ttl()

        handler = getattr(self.redis, parsed.spec.handler_name)
        value = handler(*parsed.args)

        return Reply(parsed.spec.reply_kind, value)