import json

from src.mini_redis.commands.dispatcher import Reply
from src.mini_redis.commands.schema import ReplyKind
from src.mini_redis.error import RedisCommandError

def format_error(error: RedisCommandError) -> str:
    return "(error) {}".format(error)
def format_reply(reply: Reply) -> str:
    if reply.kind is ReplyKind.SIMPLE:
        return str(reply.value)

    if reply.kind is ReplyKind.BULK:
        if reply.value is None:
            return "(nil)"
        return json.dumps(reply.value, ensure_ascii=False)

    if reply.kind is ReplyKind.INTEGER:
        return f"(integer) {reply.value}"

    if reply.kind is ReplyKind.ARRAY:
        if not reply.value:
            return "(empty array)"

        return "\n".join(
            f"{index}. {json.dumps(value, ensure_ascii=False)}"
            for index, value in enumerate(reply.value, start=1)
        )

    if reply.kind is ReplyKind.TEXT:
        return str(reply.value)

    raise RuntimeError(f"unknown reply kind: {reply.kind}")