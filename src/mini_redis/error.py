class CLIExit(Exception):
    """Signal to terminate the CLI loop."""
    pass
class RedisCommandError(Exception):
    pass

def unknown_command(command: str) -> RedisCommandError:
    return RedisCommandError(
        "ERR unknown command '{}'".format(command)
    )


def wrong_number_of_arguments(command: str) -> RedisCommandError:
    return RedisCommandError(
        "ERR wrong number of arguments for '{}' command".format(command)
    )


def invalid_integer() -> RedisCommandError:
    return RedisCommandError(
        "ERR value is not an integer or out of range"
    )


def out_of_memory() -> RedisCommandError:
    return RedisCommandError(
        "OOM command not allowed when used_memory > 'maxmemory'"
    )