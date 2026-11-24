"""Tests for note commands (T21)."""

import pytest

from assistant import note_handlers as nh
from assistant.address_book import AddressBook
from assistant.commands import COMMANDS
from assistant.context import Context
from assistant.exceptions import NoteNotFoundError, ValidationError
from assistant.notes import NoteBook


@pytest.fixture
def ctx():
    return Context(book=AddressBook(), notes=NoteBook())


# parse_id


def test_parse_id_number():
    assert nh.parse_id("3") == 3


@pytest.mark.parametrize("value", ["abc", "1.5", ""])
def test_parse_id_not_a_number(value):
    with pytest.raises(ValidationError, match=f"Invalid note id '{value}'"):
        nh.parse_id(value)


# add-note


def test_add_note_joins_all_words(ctx):
    assert nh.add_note(["Buy", "milk"], ctx) == "Note 1 added."
    assert ctx.notes.find(1).text == "Buy milk"


def test_add_note_ids_go_up(ctx):
    nh.add_note(["first"], ctx)
    assert nh.add_note(["second"], ctx) == "Note 2 added."


def test_add_note_without_text(ctx):
    with pytest.raises(ValidationError, match="Use: add-note <text>"):
        nh.add_note([], ctx)


# edit-note


def test_edit_note(ctx):
    nh.add_note(["old"], ctx)
    assert nh.edit_note(["1", "new", "text"], ctx) == "Note 1 updated."
    assert ctx.notes.find(1).text == "new text"


def test_edit_note_without_text(ctx):
    nh.add_note(["old"], ctx)
    with pytest.raises(ValidationError, match="Use: edit-note <id> <text>"):
        nh.edit_note(["1"], ctx)


def test_edit_note_bad_id(ctx):
    with pytest.raises(ValidationError, match="Invalid note id 'x'"):
        nh.edit_note(["x", "text"], ctx)


def test_edit_note_missing_note(ctx):
    with pytest.raises(NoteNotFoundError):
        nh.edit_note(["7", "text"], ctx)


# delete-note


def test_delete_note(ctx):
    nh.add_note(["temp"], ctx)
    assert nh.delete_note(["1"], ctx) == "Note 1 deleted."
    assert not ctx.notes


def test_delete_note_without_id(ctx):
    with pytest.raises(ValidationError, match="Use: delete-note <id>"):
        nh.delete_note([], ctx)


def test_delete_note_missing_note(ctx):
    with pytest.raises(NoteNotFoundError):
        nh.delete_note(["5"], ctx)


# all-notes


def test_all_notes_empty(ctx):
    assert nh.show_all_notes([], ctx).startswith("No notes yet.")


def test_all_notes_one_per_line_by_id(ctx):
    nh.add_note(["first"], ctx)
    nh.add_note(["second"], ctx)
    assert nh.show_all_notes([], ctx) == "1: first\n2: second"


# search-notes (NoteBook.search comes in T12, so it is replaced here)


def test_search_notes_found(ctx, monkeypatch):
    nh.add_note(["Buy milk"], ctx)
    note = ctx.notes.find(1)
    monkeypatch.setattr(ctx.notes, "search", lambda query: [note])
    assert nh.search_notes(["milk"], ctx) == "1: Buy milk"


def test_search_notes_nothing_found(ctx, monkeypatch):
    monkeypatch.setattr(ctx.notes, "search", lambda query: [])
    assert nh.search_notes(["xyz"], ctx) == "No notes found for 'xyz'."


def test_search_notes_without_query(ctx):
    with pytest.raises(ValidationError, match="Use: search-notes <text>"):
        nh.search_notes([], ctx)


# registration (T18)


@pytest.mark.parametrize(
    "name", ["add-note", "edit-note", "delete-note", "all-notes", "search-notes"]
)
def test_note_commands_are_registered(name):
    assert name in COMMANDS
    assert COMMANDS[name].help_text.startswith(name)


def test_registered_handler_runs(ctx):
    assert COMMANDS["add-note"].handler(["Buy", "milk"], ctx) == "Note 1 added."
