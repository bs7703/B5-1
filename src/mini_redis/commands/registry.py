from src.mini_redis.commands.schema import CommandSpec, ReplyKind
from src.mini_redis.commands.validators import (validate_int,validate_non_negative_int,validate_string)


COMMAND_SPECS = (
    CommandSpec(("SET",), (validate_string, validate_string), "set_", ReplyKind.SIMPLE),
    CommandSpec(("GET",), (validate_string,), "get_", ReplyKind.BULK),
    CommandSpec(("DEL",), (validate_string,), "del_", ReplyKind.INTEGER),
    CommandSpec(("EXISTS",), (validate_string,), "exists_", ReplyKind.INTEGER),
    CommandSpec(("DBSIZE",), (), "dbsize_", ReplyKind.INTEGER),
    CommandSpec(("KEYS",), (), "keys_", ReplyKind.ARRAY),
    CommandSpec(("EXPIRE",), (validate_string, validate_int), "expire_", ReplyKind.INTEGER),
    CommandSpec(("TTL",), (validate_string,), "ttl_", ReplyKind.INTEGER),
    CommandSpec(
        ("CONFIG", "SET", "MAXMEMORY"),
        (validate_non_negative_int,),
        "config_set_maxmemory_",
        ReplyKind.SIMPLE,
    ),
    CommandSpec(("INFO", "MEMORY"), (), "info_memory_", ReplyKind.TEXT),
    CommandSpec(("QUIT",), (), "quit_", ReplyKind.SIMPLE),
    CommandSpec(("EXIT",), (), "exit_", ReplyKind.SIMPLE),
   # CommandSpec(("VISUALIZE",), (), "visualize_", ReplyKind.SIMPLE)
)