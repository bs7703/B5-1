from src.mini_redis.error import invalid_integer


def validate_string(value: str) -> None:
    return None


def validate_int(value: str) -> None:
    try:
        int(value)
    except ValueError:
        raise invalid_integer()


def validate_non_negative_int(value: str) -> None:
    validate_int(value)

    if int(value) < 0:
        raise invalid_integer()