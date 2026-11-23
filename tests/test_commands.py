"""Tests for T18 command registration and generated help."""

import pytest

from assistant import commands
from assistant.context import Context


@pytest.fixture
def isolated_registry(monkeypatch):
    """Each registry test runs without changing the real built-in commands."""
    registry = {}
    monkeypatch.setattr(commands, "COMMANDS", registry)
    return registry


def test_decorator_registers_original_handler(isolated_registry):
    @commands.command("example")
    def example(args: list[str], ctx: Context) -> str:
        """example <text>: demonstrate a registered command."""
        return " ".join(args)

    info = isolated_registry["example"]
    assert info.name == "example"
    assert info.handler is example
    assert info.help_text == "example <text>: demonstrate a registered command."


def test_generated_help_is_sorted_and_uses_docstrings(isolated_registry):
    @commands.command("zeta")
    def zeta(args: list[str], ctx: Context) -> str:
        """zeta: last command."""
        return ""

    @commands.command("alpha")
    def alpha(args: list[str], ctx: Context) -> str:
        """alpha: first command.

        An additional docstring line is not part of short help.
        """
        return ""

    expected = "Available commands:\nalpha: first command.\nzeta: last command."
    assert commands.get_help() == expected


def test_duplicate_command_is_rejected(isolated_registry):
    @commands.command("example")
    def first(args: list[str], ctx: Context) -> str:
        """example: first handler."""
        return ""

    with pytest.raises(ValueError, match="already registered"):

        @commands.command("example")
        def second(args: list[str], ctx: Context) -> str:
            """example: duplicate handler."""
            return ""

    assert isolated_registry["example"].handler is first


@pytest.mark.parametrize("name", ["", "BadName", "two words", " add", "add_foo"])
def test_invalid_command_name_is_rejected(name):
    with pytest.raises(ValueError, match="Command name"):
        commands.command(name)


def test_missing_docstring_is_rejected(isolated_registry):
    with pytest.raises(ValueError, match="help docstring"):

        @commands.command("no-docs")
        def no_docs(args: list[str], ctx: Context) -> str:
            return ""


def test_help_when_registry_is_empty(isolated_registry):
    assert commands.get_help() == "No commands are registered."


def test_builtin_commands_are_registered():
    for name in ("help", "hello", "exit", "close"):
        assert name in commands.COMMANDS

    output = commands.COMMANDS["help"].handler([], None)
    assert "help: show available commands" in output
    assert "exit: save data and quit" in output
    assert commands.COMMANDS["hello"].handler([], None) == "How can I help you?"


def test_help_lists_new_commands_automatically(isolated_registry):
    @commands.command("demo")
    def demo(args: list[str], ctx: Context) -> str:
        """demo: a dynamically installed command."""
        return "Done"

    assert "demo: a dynamically installed command." in commands.get_help()
