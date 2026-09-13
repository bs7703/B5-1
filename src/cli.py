import sys

from src.mini_redis.commands.dispatcher import Dispatcher
from src.mini_redis.commands.parse import parse_command
from src.mini_redis.error import CLIExit, RedisCommandError
from src.mini_redis.formatter import format_error, format_reply
from src.redis import Redis


def cli() -> None:
    dispatcher = Dispatcher(Redis())

    while True:
        try:
            line = input("mini-redis>").strip()
            tokens = line.split()
            parsed = parse_command(tokens)
            reply = dispatcher.dispatch(parsed)
            print(format_reply(reply))
        except CLIExit:
            sys.exit(0)
        except RedisCommandError as error:
            print(format_error(error))