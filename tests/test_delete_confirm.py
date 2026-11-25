"""Tests for confirmation before deleting (U4)."""

import builtins

import pytest

from assistant import contact_handlers as ch
from assistant import note_handlers as nh
from assistant import ui
from assistant.address_book import AddressBook
from assistant.context import Context
from assistant.exceptions import ContactNotFoundError, NoteNotFoundError
from assistant.notes import NoteBook


def answer(monkeypatch, text: str) -> list[str]:
    """Make input() return `text`; return the list of asked questions."""
    asked: list[str] = []

    def fake_input(prompt: str) -> str:
        asked.append(prompt)
        return text

    monkeypatch.setattr(builtins, "input", fake_input)
    return asked


@pytest.fixture
def ctx():
    context = Context(book=AddressBook(), notes=NoteBook())
    ch.add_contact(["John", "0501234567"], context)
    nh.add_note(["Buy", "milk"], context)
    return context


# ui.confirm


@pytest.mark.parametrize("text", ["y", "Y", "  y  "])
def test_confirm_yes(monkeypatch, text):
    asked = answer(monkeypatch, text)
    assert ui.confirm("Delete?") is True
    assert asked == ["Delete? (y/n): "]


@pytest.mark.parametrize("text", ["", "n", "no", "yes", "yy", "д"])
def test_confirm_anything_else_is_no(monkeypatch, text):
    answer(monkeypatch, text)
    assert ui.confirm("Delete?") is False


@pytest.mark.parametrize("error", [KeyboardInterrupt, EOFError])
def test_confirm_ctrl_c_or_ctrl_d_is_no(monkeypatch, error):
    def fake_input(prompt: str) -> str:
        raise error

    monkeypatch.setattr(builtins, "input", fake_input)
    assert ui.confirm("Delete?") is False


# delete (contact)


def test_delete_contact_after_y(ctx, monkeypatch):
    asked = answer(monkeypatch, "y")
    assert ch.delete_contact(["John"], ctx) == "Contact 'John' deleted."
    assert asked == ["Delete contact 'John'? (y/n): "]
    assert "John" not in ctx.book


@pytest.mark.parametrize("text", ["", "n", "yes"])
def test_delete_contact_cancelled(ctx, monkeypatch, text):
    answer(monkeypatch, text)
    assert ch.delete_contact(["John"], ctx) == "Deletion cancelled."
    assert "John" in ctx.book


def test_delete_unknown_contact_does_not_ask(ctx, monkeypatch):
    asked = answer(monkeypatch, "y")
    with pytest.raises(ContactNotFoundError):
        ch.delete_contact(["Ann"], ctx)
    assert asked == []


# delete-note


def test_delete_note_after_y(ctx, monkeypatch):
    asked = answer(monkeypatch, "y")
    assert nh.delete_note(["1"], ctx) == "Note 1 deleted."
    assert asked == ["Delete note 1: Buy milk? (y/n): "]
    assert not ctx.notes


@pytest.mark.parametrize("text", ["", "n", "yes"])
def test_delete_note_cancelled(ctx, monkeypatch, text):
    answer(monkeypatch, text)
    assert nh.delete_note(["1"], ctx) == "Deletion cancelled."
    assert ctx.notes.find(1).text == "Buy milk"


def test_delete_unknown_note_does_not_ask(ctx, monkeypatch):
    asked = answer(monkeypatch, "y")
    with pytest.raises(NoteNotFoundError):
        nh.delete_note(["7"], ctx)
    assert asked == []
