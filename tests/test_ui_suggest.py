"""Tests for typo suggestions in ui.py (U3)."""

import pytest

from assistant import ui

COMMANDS = ["add", "add-note", "all", "birthdays", "change", "phone", "exit"]


@pytest.fixture(autouse=True)
def registered_commands(monkeypatch):
    """Typos are suggested only for names present in the live registry."""
    monkeypatch.setattr(ui, "COMMANDS", dict.fromkeys(COMMANDS))



def test_ad_suggests_add():
    """Acceptance criterion of U3: ad -> add."""
    assert ui.suggest("ad", COMMANDS)[0] == "add"


def test_swapped_letters_are_found():
    assert ui.suggest("phnoe", COMMANDS) == ["phone"]


def test_suggestion_is_case_insensitive():
    assert ui.suggest("AD", COMMANDS)[0] == "add"


def test_surrounding_spaces_are_ignored():
    assert ui.suggest("  birthdys ", COMMANDS) == ["birthdays"]


def test_nothing_similar_gives_empty_list():
    assert ui.suggest("xyz", COMMANDS) == []


def test_empty_word_gives_empty_list():
    assert ui.suggest("", COMMANDS) == []


def test_empty_command_list_gives_empty_list():
    assert ui.suggest("add", []) == []


def test_at_most_three_suggestions():
    many = ["add1", "add2", "add3", "add4", "add5"]
    assert len(ui.suggest("add", many)) <= 3


def test_unknown_command_message_with_hint():
    assert ui.unknown_command_message("ad") == (
        "Unknown command 'ad'. Did you mean: add?"
    )


def test_unknown_command_message_without_hint():
    assert ui.unknown_command_message("xyz") == "Unknown command 'xyz'."
