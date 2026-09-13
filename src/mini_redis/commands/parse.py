from typing import Sequence, Optional

from src.mini_redis.commands.registry import COMMAND_SPECS
from src.mini_redis.commands.schema import CommandSpec, ParsedCommand
from src.mini_redis.error import RedisCommandError,unknown_command,wrong_number_of_arguments


def parse_command(tokens:Sequence[str]):
    if not tokens:
        raise RedisCommandError("ERR empty command")

    spec = _find_command_spec(tokens)

    if spec is None:
        raise unknown_command(tokens[0])

    args = tuple(tokens[len(spec.tokens):])

    if len(args) != len(spec.validators):
        command_name = " ".join(spec.tokens)
        raise wrong_number_of_arguments(command_name)

    for value, validator in zip(args, spec.validators):
        validator(value)

    return ParsedCommand(spec=spec, args=args)


def _find_command_spec(tokens: Sequence[str]) -> Optional[CommandSpec]:
    matched_specs = []

    for spec in COMMAND_SPECS:
        command_length = len(spec.tokens)

        if len(tokens) < command_length:
            continue

        input_command = tuple(
            token.upper()
            for token in tokens[:command_length]
        )

        if input_command == spec.tokens:
            matched_specs.append(spec)

    if not matched_specs:
        return None

    return max(matched_specs, key=lambda spec: len(spec.tokens))