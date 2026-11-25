"""Tests for tag commands (T22)."""

import pytest

from assistant import tag_handlers as th
from assistant.address_book import AddressBook
from assistant.commands import COMMANDS
from assistant.context import Context
from assistant.exceptions import NoteNotFoundError, ValidationError
from assistant.notes import NoteBook


@pytest.fixture
def ctx():
    # Three notes: 1 has no tags, 2 has "work", 3 has "home".
    notes = NoteBook()
    notes.add_note("Buy milk")
    notes.add_note("Call boss").add_tag("work")
    notes.add_note("Fix sink").add_tag("home")
    return Context(book=AddressBook(), notes=notes)


# --- add-tag ---


# A tag is saved on the note and the answer names it.
def test_add_tag(ctx):
    assert th.add_tag(["1", "shop"], ctx) == "Tag 'shop' added to note 1."
    assert ctx.notes.find(1).tags == {"shop"}


# Tags are stored in lower case, the answer shows the stored form.
def test_add_tag_lowercases(ctx):
    assert th.add_tag(["1", "Shop"], ctx) == "Tag 'shop' added to note 1."
    assert "shop" in ctx.notes.find(1).tags


# The same tag twice is an error from the model (T13).
def test_add_tag_duplicate(ctx):
    with pytest.raises(ValidationError, match="already has tag 'work'"):
        th.add_tag(["2", "work"], ctx)


# Not enough arguments shows the right format.
@pytest.mark.parametrize("args", [[], ["1"]])
def test_add_tag_missing_args(ctx, args):
    with pytest.raises(ValidationError, match="Use: add-tag <id> <tag>"):
        th.add_tag(args, ctx)


# The id must be a number (parse_id from T21).
def test_add_tag_bad_id(ctx):
    with pytest.raises(ValidationError, match="Invalid note id 'abc'"):
        th.add_tag(["abc", "work"], ctx)


# A note that doesn't exist.
def test_add_tag_unknown_note(ctx):
    with pytest.raises(NoteNotFoundError):
        th.add_tag(["99", "work"], ctx)


# A tag with a space or a symbol is rejected by the model.
def test_add_tag_invalid_tag(ctx):
    with pytest.raises(ValidationError, match="Invalid tag"):
        th.add_tag(["1", "#work!"], ctx)


# --- remove-tag ---


# The tag is gone after removing.
def test_remove_tag(ctx):
    assert th.remove_tag(["2", "work"], ctx) == "Tag 'work' removed from note 2."
    assert ctx.notes.find(2).tags == set()


# Removing a tag the note doesn't have is an error.
def test_remove_tag_not_there(ctx):
    with pytest.raises(ValidationError, match="has no tag 'home'"):
        th.remove_tag(["2", "home"], ctx)


@pytest.mark.parametrize("args", [[], ["2"]])
def test_remove_tag_missing_args(ctx, args):
    with pytest.raises(ValidationError, match="Use: remove-tag <id> <tag>"):
        th.remove_tag(args, ctx)


def test_remove_tag_unknown_note(ctx):
    with pytest.raises(NoteNotFoundError):
        th.remove_tag(["99", "work"], ctx)


# --- search-tag ---


# Only notes with this tag are shown, in the ui.format_note style.
def test_search_tag(ctx):
    assert th.search_tag(["work"], ctx) == "2: Call boss [work]"


# Search ignores case: "WORK" finds "work".
def test_search_tag_case_insensitive(ctx):
    assert th.search_tag(["WORK"], ctx) == "2: Call boss [work]"


# Several matches come one per line.
def test_search_tag_several_notes(ctx):
    th.add_tag(["1", "work"], ctx)
    assert th.search_tag(["work"], ctx) == "1: Buy milk [work]\n2: Call boss [work]"


# No matches gives a friendly message, not an error.
def test_search_tag_no_matches(ctx):
    assert th.search_tag(["travel"], ctx) == "No notes with tag 'travel'."


def test_search_tag_missing_args(ctx):
    with pytest.raises(ValidationError, match="Use: search-tag <tag>"):
        th.search_tag([], ctx)


# --- sort-notes ---


# Tagged notes A-Z by tag (home, work), untagged notes at the end.
def test_sort_notes(ctx):
    assert th.sort_notes([], ctx) == (
        "3: Fix sink [home]\n2: Call boss [work]\n1: Buy milk"
    )


# Empty notebook gives a hint instead of an empty line.
def test_sort_notes_empty():
    empty = Context(book=AddressBook(), notes=NoteBook())
    assert th.sort_notes([], empty) == "No notes yet. Add one with: add-note <text>"


# --- registration (T18) ---


@pytest.mark.parametrize("name", ["add-tag", "remove-tag", "search-tag", "sort-notes"])
def test_tag_commands_are_registered(name):
    assert name in COMMANDS
    assert COMMANDS[name].help_text.startswith(name)
