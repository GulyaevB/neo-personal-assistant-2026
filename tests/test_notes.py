"""Tests for the notes model (T11: Note and NoteBook basics)."""

from datetime import datetime

import pytest

from assistant.exceptions import NoteNotFoundError, ValidationError
from assistant.notes import Note, NoteBook


@pytest.fixture
def book():
    """Notebook with three notes (ids 1, 2, 3)."""

    notebook = NoteBook()
    notebook.add_note("Buy a gift for Anna")
    notebook.add_note("Prepare slides for demo day")
    notebook.add_note("Call the dentist")
    return notebook


# --- Note ---
def test_note_text_is_stripped():
    assert Note(id=1, text="  hello  ").text == "hello"


# Empty, spaces-only or missing text must be rejected
@pytest.mark.parametrize("text", ["", "  ", None])
def test_note_with_empty_text_raises_validation_error(text):
    with pytest.raises(ValidationError):
        Note(id=1, text=text)


# Tags are normalized on creation: "Work" and " HOME " -> "work", "home".
def test_note_tags_are_lowercased():
    assert Note(id=1, text="text", tags={"Work", " HOME "}).tags == {"work", "home"}


# `created` is filled with the current time when it is not passed.
def test_note_created_is_set_automatically():
    assert isinstance(Note(id=1, text="text").created, datetime)


# edit() replaces the text and cleans it the same way as on creation.
def test_note_edit_changes_text():
    note = Note(id=1, text="old")
    note.edit("  new  ")
    assert note.text == "new"


# A failed edit must not damage the note: the old text stays.
def test_note_edit_with_empty_text_keeps_old_text():
    note = Note(id=1, text="old")
    with pytest.raises(ValidationError):
        note.edit(" ")
    assert note.text == "old"


# to_dict() matches the agreed notes.json format: sorted tags, ISO date.
def test_note_to_dict_format():
    note = Note(
        id=1,
        text="Buy milk",
        tags={"shopping", "home"},
        created=datetime(2026, 11, 18, 10, 15),
    )
    assert note.to_dict() == {
        "id": 1,
        "text": "Buy milk",
        "tags": ["home", "shopping"],
        "created": "2026-11-18T10:15:00",
    }


# Round-trip: to_dict -> from_dict gives the same note (date saved to seconds).
def test_note_from_dict_restores_note():
    note = Note(id=7, text="Hello", tags={"a", "b"})
    restored = Note.from_dict(note.to_dict())
    assert restored.id == 7
    assert restored.text == "Hello"
    assert restored.tags == {"a", "b"}
    assert restored.created == note.created.replace(microsecond=0)


# Rules also apply when loading from a file: bad data -> ValidationError.
def test_note_from_dict_with_empty_text_raises_validation_error():
    data = {"id": 1, "text": "", "tags": [], "created": "2026-11-18T10:15:00"}
    with pytest.raises(ValidationError):
        Note.from_dict(data)


# --- NoteBook: add / find / edit / delete ---


# Ids are auto-incremented from 1; next_id points to the next free id.
def test_add_note_gives_sequential_ids_from_1(book):
    assert list(book.keys()) == [1, 2, 3]
    assert book.next_id == 4


# add_note() returns the new note, so handlers can show its id to the user.
def test_add_note_returns_the_note():
    note = NoteBook().add_note("first")
    assert (note.id, note.text) == (1, "first")


# A failed add must not change the notebook or waste an id.
def test_add_note_with_empty_text_raises_and_keeps_next_id():
    notebook = NoteBook()
    with pytest.raises(ValidationError):
        notebook.add_note("  ")
    assert len(notebook) == 0
    assert notebook.next_id == 1


# find() returns the right note by id (middle one, to avoid lucky passes).
def test_find_returns_note(book):
    assert book.find(2).text == "Prepare slides for demo day"


# Unknown id -> NoteNotFoundError with that id in the message.
def test_find_unknown_id_raises_note_not_found(book):
    with pytest.raises(NoteNotFoundError, match="99"):
        book.find(99)


# NoteBook.edit() finds the note by id and updates its text in place.
def test_edit_changes_text(book):
    book.edit(1, "Buy flowers")
    assert book.find(1).text == "Buy flowers"


# edit() reuses find(), so an unknown id raises NoteNotFoundError too.
def test_edit_unknown_id_raises_note_not_found(book):
    with pytest.raises(NoteNotFoundError):
        book.edit(99, "text")


# A failed edit through the notebook keeps the stored note unchanged.
def test_edit_with_empty_text_keeps_old_text(book):
    with pytest.raises(ValidationError):
        book.edit(1, "")
    assert book.find(1).text == "Buy a gift for Anna"


# delete() really removes the note: it's gone from the dict and find() fails.
def test_delete_removes_note(book):
    book.delete(2)
    assert 2 not in book
    with pytest.raises(NoteNotFoundError):
        book.find(2)


# delete() checks the id first, so it raises NoteNotFoundError, not KeyError.
def test_delete_unknown_id_raises_note_not_found(book):
    with pytest.raises(NoteNotFoundError):
        book.delete(99)


# Ids are never reused: after deleting the last note, the next id is still 4.
def test_ids_are_not_reused_after_delete(book):
    book.delete(3)
    assert book.add_note("new").id == 4


# --- NoteBook: to_dict / from_dict (used by storage) ---


# Notebook JSON shape agreed with Back-end: {"next_id": ..., "notes": [...]}.
def test_notebook_to_dict_format(book):
    data = book.to_dict()
    assert data["next_id"] == 4
    assert [note["id"] for note in data["notes"]] == [1, 2, 3]


# Round-trip of the whole notebook (compared as dicts to include next_id).
def test_notebook_roundtrip(book):
    restored = NoteBook.from_dict(book.to_dict())
    assert restored.to_dict() == book.to_dict()


# next_id survives save/load, so ids are not reused even after a restart.
def test_roundtrip_keeps_next_id_after_delete(book):
    book.delete(3)
    restored = NoteBook.from_dict(book.to_dict())
    assert restored.add_note("new").id == 4


# Edge case: an empty dict loads as a fresh notebook that starts from id 1.
def test_from_empty_dict_gives_empty_notebook():
    notebook = NoteBook.from_dict({})
    assert len(notebook) == 0
    assert notebook.add_note("first").id == 1


# Safety net: if next_id is missing, use biggest id + 1 so no note is overwritten.
def test_from_dict_without_next_id_uses_biggest_id_plus_one():
    data = {
        "notes": [{"id": 5, "text": "x", "tags": [], "created": "2026-11-18T10:15:00"}]
    }
    assert NoteBook.from_dict(data).add_note("new").id == 6
