"""Command registry and generated help.

Handlers register with @command("name") and @input_error.
The help text comes from the first line of the handler's docstring.

Use this decorator order for feature handlers:
    @command("add")
    @input_error
    def add_contact(args, ctx):
        ...
"""

import inspect
import re
from collections.abc import Callable
from dataclasses import dataclass

from assistant.context import Context, Handler


@dataclass(frozen=True)
class CommandInfo:
    """One command: name, handler, and help line."""

    name: str
    handler: Handler
    help_text: str


COMMANDS: dict[str, CommandInfo] = {}


def command(name: str) -> Callable[[Handler], Handler]:
    """Register a handler and its first docstring line under a command name."""
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        raise ValueError("Command name must contain lowercase letters, digits, or '-'.")

    def register(handler: Handler) -> Handler:
        if name in COMMANDS:
            raise ValueError(f"Command '{name}' is already registered.")

        docstring = inspect.getdoc(handler)
        if not docstring:
            raise ValueError(f"Command '{name}' must have a help docstring.")

        COMMANDS[name] = CommandInfo(
            name=name,
            handler=handler,
            help_text=docstring.splitlines()[0],
        )
        return handler

    return register


def get_help() -> str:
    """Generate help from registered commands, sorted by command name."""
    if not COMMANDS:
        return "No commands are registered."
    lines = [COMMANDS[name].help_text for name in sorted(COMMANDS)]
    return "Available commands:\n" + "\n".join(lines)


@command("help")
def help_command(_args: list[str], _ctx: Context) -> str:
    """help: show available commands and usage."""
    return get_help()


@command("hello")
def hello_command(_args: list[str], _ctx: Context) -> str:
    """hello: greet the assistant."""
    return "How can I help you?"


# These two commands are intercepted by the CLI to save data before exit.
# Register them as well so generated help and completion stay consistent.
@command("exit")
def exit_command(_args: list[str], _ctx: Context) -> str:
    """exit: save data and quit the assistant."""
    return "Goodbye!"


@command("close")
def close_command(_args: list[str], _ctx: Context) -> str:
    """close: save data and quit the assistant."""
    return "Goodbye!"
