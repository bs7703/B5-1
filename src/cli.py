import sys

from src.mini_redis.commands.dispatcher import Dispatcher
from src.mini_redis.commands.parse import parse_commands
from src.redis import Redis
from src.mini_redis.error import CLIExit


def cli():
    mini_redis = Dispatcher(Redis())
    while True:
        try:
            str = input().strip()
            cmd = str.split()
            sep = parse_commands(cmd)
            res = mini_redis.dispatch(cmd, sep)
            print(res)
        except CLIExit:
            sys.exit(1)
        except ValueError as v:
            print(v)
        except IndexError as e:
            print(e)
        except RuntimeError as r:
            print(r)
