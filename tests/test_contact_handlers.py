"""Tests for contact commands (T19)."""

import pytest

from assistant import contact_handlers as ch
from assistant.address_book import AddressBook
from assistant.commands import COMMANDS
from assistant.context import Context
from assistant.exceptions import ContactNotFoundError, ValidationError
from assistant.notes import NoteBook


@pytest.fixture
def ctx():
    return Context(book=AddressBook(), notes=NoteBook())


@pytest.fixture
def john(ctx):
    """Context with John (one phone)."""
    ch.add_contact(["John", "0501234567"], ctx)
    return ctx


# add


def test_add_creates_contact(ctx):
    assert ch.add_contact(["John", "0501234567"], ctx) == "Contact 'John' added."
    assert [p.value for p in ctx.book.find("John").phones] == ["0501234567"]


def test_add_existing_contact_adds_phone(john):
    assert ch.add_contact(["John", "0671234567"], john) == "Phone added to 'John'."
    assert len(john.book.find("John").phones) == 2


def test_add_invalid_phone_does_not_create_contact(ctx):
    with pytest.raises(ValidationError, match="Invalid phone '123'"):
        ch.add_contact(["John", "123"], ctx)
    assert "John" not in ctx.book


def test_add_same_phone_twice(john):
    with pytest.raises(ValidationError, match="already has phone"):
        ch.add_contact(["John", "0501234567"], john)


def test_add_missing_phone(ctx):
    with pytest.raises(ValidationError, match="Use: add <name> <phone>"):
        ch.add_contact(["John"], ctx)


# change, remove-phone


def test_change_phone(john):
    result = ch.change_phone(["John", "0501234567", "0671234567"], john)
    assert result == "Phone updated for 'John'."
    assert [p.value for p in john.book.find("John").phones] == ["0671234567"]


def test_change_unknown_old_phone(john):
    with pytest.raises(ValidationError, match="has no phone '0000000000'"):
        ch.change_phone(["John", "0000000000", "0671234567"], john)


def test_change_unknown_contact(ctx):
    with pytest.raises(ContactNotFoundError):
        ch.change_phone(["Ann", "0501234567", "0671234567"], ctx)


def test_remove_phone(john):
    assert ch.remove_phone(["John", "0501234567"], john) == "Phone removed from 'John'."
    assert john.book.find("John").phones == []


# add-email, add-address, add-birthday


def test_add_email(john):
    assert ch.add_email(["John", "john@mail.com"], john) == "Email set for 'John'."
    assert john.book.find("John").email.value == "john@mail.com"


def test_add_invalid_email(john):
    with pytest.raises(ValidationError, match="Invalid email 'john@mail'"):
        ch.add_email(["John", "john@mail"], john)


def test_add_address_keeps_all_words(john):
    result = ch.add_address(["John", "Kyiv,", "Main", "St", "1"], john)
    assert result == "Address set for 'John'."
    assert john.book.find("John").address.value == "Kyiv, Main St 1"


def test_add_birthday(john):
    assert ch.add_birthday(["John", "15.05.1990"], john) == "Birthday set for 'John'."
    assert str(john.book.find("John").birthday) == "15.05.1990"


def test_add_invalid_birthday(john):
    with pytest.raises(ValidationError, match="Invalid date '31.04.1990'"):
        ch.add_birthday(["John", "31.04.1990"], john)


# phone, show-birthday


def test_show_phone(john):
    ch.add_contact(["John", "0671234567"], john)
    assert ch.show_phone(["John"], john) == "John: 0501234567; 0671234567"


def test_show_phone_without_phones(john):
    ch.remove_phone(["John", "0501234567"], john)
    assert ch.show_phone(["John"], john) == "Contact 'John' has no phones."


def test_show_birthday(john):
    ch.add_birthday(["John", "15.05.1990"], john)
    assert ch.show_birthday(["John"], john) == "John: 15.05.1990"


def test_show_birthday_not_set(john):
    assert ch.show_birthday(["John"], john) == "Contact 'John' has no birthday."


def test_show_phone_unknown_contact(ctx):
    with pytest.raises(ContactNotFoundError, match="Contact 'Ann' not found"):
        ch.show_phone(["Ann"], ctx)


# all, delete


def test_all_empty(ctx):
    assert ch.show_all([], ctx).startswith("No contacts yet.")


def test_all_sorted_by_name(john):
    ch.add_contact(["anna", "0671234567"], john)
    lines = ch.show_all([], john).split("\n")
    assert lines[0].startswith("Contact name: anna")
    assert lines[1].startswith("Contact name: John")


def test_delete(john, monkeypatch):
    monkeypatch.setattr(ch.ui, "confirm", lambda question: True)
    assert ch.delete_contact(["John"], john) == "Contact 'John' deleted."
    assert "John" not in john.book


def test_delete_unknown_contact(ctx):
    with pytest.raises(ContactNotFoundError):
        ch.delete_contact(["Ann"], ctx)


# registration (T18)


@pytest.mark.parametrize(
    "name",
    [
        "add",
        "change",
        "remove-phone",
        "add-email",
        "add-address",
        "add-birthday",
        "phone",
        "show-birthday",
        "all",
        "delete",
    ],
)
def test_contact_commands_are_registered(name):
    assert name in COMMANDS
    assert COMMANDS[name].help_text.startswith(name)
