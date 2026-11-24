"""Tests for search and birthdays commands (T20)."""

from datetime import date

import pytest

from assistant import contact_handlers as ch
from assistant.address_book import AddressBook
from assistant.commands import COMMANDS
from assistant.context import Context
from assistant.exceptions import ValidationError
from assistant.notes import NoteBook
from assistant.record import Record


@pytest.fixture
def ctx():
    book = AddressBook()
    for name, phone in [("John", "0501234567"), ("anna", "0671234567")]:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    return Context(book=book, notes=NoteBook())


# search


def test_search_sorted_by_name(ctx):
    lines = ch.search_contacts(["0"], ctx).split("\n")
    assert lines[0].startswith("Contact name: anna")
    assert lines[1].startswith("Contact name: John")


def test_search_by_phone(ctx):
    assert ch.search_contacts(["0501"], ctx).startswith("Contact name: John")


def test_search_nothing_found(ctx):
    assert ch.search_contacts(["xyz"], ctx) == "No contacts found for 'xyz'."


def test_search_without_query(ctx):
    with pytest.raises(ValidationError, match="Use: search <query>"):
        ch.search_contacts([], ctx)


# parse_days


def test_days_default_is_7():
    assert ch.parse_days([]) == 7


def test_days_number():
    assert ch.parse_days(["30"]) == 30


@pytest.mark.parametrize("value", ["abc", "0", "-3", "1.5"])
def test_days_invalid(value):
    with pytest.raises(
        ValidationError, match=f"Invalid days '{value}'. Use a positive number."
    ):
        ch.parse_days([value])


# birthdays


def test_birthdays_format(ctx, monkeypatch):
    john = ctx.book.find("John")
    day = date(2026, 11, 25)
    monkeypatch.setattr(ctx.book, "get_upcoming_birthdays", lambda days: [(john, day)])
    assert ch.birthdays([], ctx) == (
        "Birthdays in the next 7 days:\n25.11.2026 (Wed)  John"
    )


def test_birthdays_passes_days(ctx, monkeypatch):
    seen = []
    monkeypatch.setattr(
        ctx.book, "get_upcoming_birthdays", lambda days: seen.append(days) or []
    )
    ch.birthdays(["30"], ctx)
    assert seen == [30]


def test_birthdays_none_in_period(ctx):
    assert ch.birthdays(["7"], ctx) == "No birthdays in the next 7 days."


def test_birthdays_today_with_real_model(ctx):
    today = date.today()
    ctx.book.find("John").set_birthday(f"{today:%d.%m}.2000")
    result = ch.birthdays(["1"], ctx)
    assert result.startswith("Birthdays today:")
    assert "John" in result


def test_birthdays_invalid_days(ctx):
    with pytest.raises(ValidationError, match="Invalid days 'abc'"):
        ch.birthdays(["abc"], ctx)


@pytest.mark.parametrize("name", ["search", "birthdays"])
def test_commands_are_registered(name):
    assert name in COMMANDS
