"""Tests for Tab completion in ui.py (U1).

The completer is tested directly, without a terminal,
so these tests also run in CI.
"""

import pytest
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document

from assistant import ui


@pytest.fixture(autouse=True)
def test_command_registry(monkeypatch):
    """Simulate handlers registered by T19/T20; UI uses live registry keys."""
    monkeypatch.setattr(
        ui,
        "COMMANDS",
        dict.fromkeys(("add", "add-note", "birthdays", "exit", "help", "phone")),
    )


@pytest.fixture(autouse=True)
def contact_names(monkeypatch):
    """Every test sees the same three contacts; restored after the test."""
    monkeypatch.setattr(ui, "_get_names", lambda: ["John", "Anna", "Johanna"])


def complete(text: str) -> list[str]:
    """Texts of all suggestions for `text` (cursor at the end)."""
    completer = ui.AssistantCompleter()
    completions = completer.get_completions(Document(text), CompleteEvent())
    return [c.text for c in completions]


def test_bi_completes_to_birthdays():
    """Acceptance criterion of U1: bi + Tab -> birthdays."""
    assert complete("bi") == ["birthdays"]


def test_command_completion_is_case_insensitive():
    assert complete("BI") == ["birthdays"]


def test_completion_replaces_typed_part():
    completer = ui.AssistantCompleter()
    [completion] = completer.get_completions(Document("bi"), CompleteEvent())
    assert completion.start_position == -2


def test_empty_input_suggests_all_commands():
    assert complete("") == ui._command_names()


def test_second_word_completes_contact_names():
    assert complete("phone jo") == ["Johanna", "John"]


def test_second_word_after_space_shows_all_names():
    assert complete("phone ") == ["Anna", "Johanna", "John"]


def test_name_completion_is_case_insensitive():
    assert complete("PHONE AN") == ["Anna"]


def test_no_names_for_commands_without_name_argument():
    assert complete("add-note jo") == []


def test_third_word_has_no_suggestions():
    assert complete("add John ") == []


def test_unknown_prefix_has_no_suggestions():
    assert complete("xyz") == []


def test_set_completion_source_changes_names():
    ui.set_completion_source(lambda: ["Zed"])
    assert complete("phone z") == ["Zed"]
