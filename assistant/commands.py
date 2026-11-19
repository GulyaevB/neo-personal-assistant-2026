"""Command registry. help is built from COMMANDS, so no long if/elif.

Put @command("name") and @input_error on every handler. The help text is
the first line of the handler's docstring.
"""

from collections.abc import Callable
from dataclasses import dataclass

from assistant.context import Handler


@dataclass
class CommandInfo:
    """One command: name, handler and help line."""

    name: str
    handler: Handler
    help_text: str


COMMANDS: dict[str, CommandInfo] = {}


def command(name: str) -> Callable[[Handler], Handler]:
    """Decorator: register the function as command `name`."""
    raise NotImplementedError  # TODO(T18)


def get_help() -> str:
    """Help for all commands."""
    raise NotImplementedError  # TODO(T18)
