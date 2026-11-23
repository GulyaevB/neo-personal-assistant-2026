"""T23: expected input errors must not terminate the CLI."""

from types import SimpleNamespace

import pytest

from assistant import cli
from assistant.address_book import AddressBook
from assistant.decorators import MISSING_ARGUMENTS_MESSAGE, input_error
from assistant.exceptions import (
    AssistantError,
    ContactNotFoundError,
    NoteNotFoundError,
    ValidationError,
)
from assistant.notes import NoteBook


def test_missing_argument_becomes_validation_error():
    @input_error
    def need_two_arguments(args, ctx):
        """demo <first> <second>: demonstrate usage."""
        return args[1]

    with pytest.raises(ValidationError) as captured:
        need_two_arguments(["one"], None)

    assert str(captured.value) == MISSING_ARGUMENTS_MESSAGE
    assert need_two_arguments.__name__ == "need_two_arguments"
    assert need_two_arguments.__doc__.startswith("demo <first> <second>")


@pytest.mark.parametrize(
    "error",
    [
        ValidationError("Invalid phone 'abc'."),
        ContactNotFoundError("Unknown"),
        NoteNotFoundError(100),
        AssistantError("Expected user error."),
    ],
)
def test_domain_errors_preserve_class_and_message(error):
    @input_error
    def broken_handler(args, ctx):
        """demo: test a domain error."""
        raise error

    with pytest.raises(type(error)) as captured:
        broken_handler([], None)

    assert str(captured.value) == str(error)


def test_unexpected_programming_errors_are_not_silenced():
    @input_error
    def broken_handler(args, ctx):
        """demo: test an unexpected error."""
        raise RuntimeError("Developer bug")

    with pytest.raises(RuntimeError, match="Developer bug"):
        broken_handler([], None)


def _run_cli(monkeypatch, handler, user_commands):
    errors = []
    messages = []
    goodbyes = []
    saved = []

    monkeypatch.setattr(cli, "COMMANDS", {"demo": SimpleNamespace(handler=handler)})
    monkeypatch.setattr(cli, "load_book", AddressBook)
    monkeypatch.setattr(cli, "load_notes", NoteBook)
    monkeypatch.setattr(cli, "save_book", lambda _: saved.append("book"))
    monkeypatch.setattr(cli, "save_notes", lambda _: saved.append("notes"))
    monkeypatch.setattr(cli.ui, "read_command", lambda: next(user_commands))
    monkeypatch.setattr(cli.ui, "set_completion_source", lambda _: None)
    monkeypatch.setattr(cli.ui, "error", errors.append)
    monkeypatch.setattr(cli.ui, "show", messages.append)
    monkeypatch.setattr(cli.ui, "success", goodbyes.append)

    cli.main()
    return errors, messages, goodbyes, saved


@pytest.mark.parametrize("decorated", [True, False])
def test_cli_handles_missing_arguments_and_keeps_running(monkeypatch, decorated):
    def missing_argument(args, ctx):
        """demo <name>: require a name."""
        return args[0]

    handler = input_error(missing_argument) if decorated else missing_argument
    errors, messages, goodbyes, saved = _run_cli(
        monkeypatch, handler, iter(["demo", "demo", "exit"])
    )

    assert errors == [MISSING_ARGUMENTS_MESSAGE] * 2
    assert all(MISSING_ARGUMENTS_MESSAGE not in msg for msg in messages)
    assert goodbyes == ["Goodbye!"]
    assert saved == ["book", "notes"]


def test_cli_shows_domain_error_in_error_channel(monkeypatch):
    @input_error
    def missing_contact(args, ctx):
        """demo: test missing contact."""
        raise ContactNotFoundError("Someone")

    errors, messages, goodbyes, saved = _run_cli(
        monkeypatch, missing_contact, iter(["demo", "exit"])
    )

    assert errors == ["Contact 'Someone' not found."]
    assert all("Someone" not in msg for msg in messages)
    assert goodbyes == ["Goodbye!"]
    assert saved == ["book", "notes"]
