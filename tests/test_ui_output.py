"""Tests for colored output in ui.py (U2).

Only the pure styling functions are tested, so no terminal is needed.
"""

from types import SimpleNamespace

import pytest

from assistant import ui


@pytest.fixture(autouse=True)
def registered_commands(monkeypatch):
    """Test highlighting using live command names from the registry."""
    monkeypatch.setattr(ui, "COMMANDS", dict.fromkeys(("add", "phone")))


def parts(formatted) -> list[tuple[str, str]]:
    """FormattedText as a plain list of (style, text) pairs."""
    return [tuple(item[:2]) for item in formatted]


def test_success_is_green():
    assert parts(ui.style_success("Contact added.")) == [
        (ui.SUCCESS_STYLE, "Contact added.")
    ]


def test_error_is_red():
    assert parts(ui.style_error("Contact not found.")) == [
        (ui.ERROR_STYLE, "Contact not found.")
    ]


def test_success_and_error_look_different():
    assert ui.SUCCESS_STYLE != ui.ERROR_STYLE


def test_plain_text_is_not_styled():
    assert parts(ui.highlight("John: 0501234567")) == [("", "John: 0501234567")]


def test_command_at_line_start_is_highlighted():
    assert parts(ui.highlight("add <name> <phone>: Add a contact.")) == [
        (ui.COMMAND_STYLE, "add"),
        ("", " <name> <phone>: Add a contact."),
    ]


def test_command_with_colon_is_highlighted():
    assert parts(ui.highlight("phone: Show phones.")) == [
        (ui.COMMAND_STYLE, "phone:"),
        ("", " Show phones."),
    ]


def test_word_that_is_not_a_command_is_not_highlighted():
    assert parts(ui.highlight("Hello world")) == [("", "Hello world")]


def test_tags_at_line_end_are_highlighted():
    assert parts(ui.highlight("1: Buy milk [home, shop]")) == [
        ("", "1: Buy milk "),
        (ui.TAG_STYLE, "[home, shop]"),
    ]


def test_multiline_text_keeps_line_breaks():
    result = parts(ui.highlight("1: Buy milk [home]\n2: Call Anna"))
    assert result == [
        ("", "1: Buy milk "),
        (ui.TAG_STYLE, "[home]"),
        ("", "\n"),
        ("", "2: Call Anna"),
    ]


def test_format_note_with_tags():
    note = SimpleNamespace(id=1, text="Buy milk", tags={"shop", "home"})
    assert ui.format_note(note) == "1: Buy milk [home, shop]"


def test_format_note_without_tags_has_no_empty_brackets():
    note = SimpleNamespace(id=2, text="Call Anna", tags=set())
    assert ui.format_note(note) == "2: Call Anna"
