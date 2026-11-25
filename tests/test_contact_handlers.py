"""Tests for contact commands (T19)."""

import pytest

from assistant import contact_handlers as ch
from assistant import storage
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


# case-insensitive names (T35, uses find() from T34)


def phones(ctx, name):
    return [p.value for p in ctx.book.find(name).phones]


# The scenario from the T35 card: one contact "John" with both phones.
def test_add_other_case_adds_phone_to_same_contact(ctx):
    ch.add_contact(["John", "0501234567"], ctx)

    assert ch.add_contact(["john", "0631234567"], ctx) == "Phone added to 'John'."
    assert ch.show_phone(["JOHN"], ctx) == "John: 0501234567; 0631234567"
    assert list(ctx.book) == ["John"]


def test_add_new_contact_still_works(john):
    assert ch.add_contact(["Anna", "0671234567"], john) == "Contact 'Anna' added."
    assert sorted(john.book) == ["Anna", "John"]


# A similar name is a different person: no fuzzy matching in add.
def test_add_similar_name_creates_new_contact(john):
    assert ch.add_contact(["Jon", "0671234567"], john) == "Contact 'Jon' added."
    assert phones(john, "John") == ["0501234567"]
    assert phones(john, "Jon") == ["0671234567"]


def test_add_existing_phone_in_other_case_is_rejected(john):
    with pytest.raises(ValidationError, match="already has phone"):
        ch.add_contact(["JOHN", "0501234567"], john)
    assert phones(john, "John") == ["0501234567"]


def test_add_invalid_phone_in_other_case_changes_nothing(john):
    with pytest.raises(ValidationError, match="Invalid phone '123'"):
        ch.add_contact(["john", "123"], john)
    assert phones(john, "John") == ["0501234567"]
    assert list(john.book) == ["John"]


def test_add_other_case_keeps_other_fields(john):
    ch.add_email(["John", "john@example.com"], john)
    ch.add_address(["John", "Kyiv", "Main", "St", "1"], john)
    ch.add_birthday(["John", "15.03.1990"], john)

    ch.add_contact(["john", "0631234567"], john)

    record = john.book.find("John")
    assert record.name.value == "John"
    assert str(record.email) == "john@example.com"
    assert str(record.address) == "Kyiv Main St 1"
    assert str(record.birthday) == "15.03.1990"
    assert phones(john, "John") == ["0501234567", "0631234567"]


# Messages show the name as stored, whatever case was typed.
@pytest.mark.parametrize(
    ("handler", "args", "expected"),
    [
        (
            ch.change_phone,
            ["john", "0501234567", "0671234567"],
            "Phone updated for 'John'.",
        ),
        (ch.remove_phone, ["JOHN", "0501234567"], "Phone removed from 'John'."),
        (ch.add_email, ["john", "john@example.com"], "Email set for 'John'."),
        (ch.add_address, ["john", "Kyiv"], "Address set for 'John'."),
        (ch.add_birthday, ["jOhN", "15.03.1990"], "Birthday set for 'John'."),
    ],
)
def test_messages_use_stored_name(john, handler, args, expected):
    assert handler(args, john) == expected


# U4 confirmation still asks, with the stored name.
def test_delete_other_case_asks_with_stored_name(john, monkeypatch):
    questions = []

    def fake_confirm(question):
        questions.append(question)
        return True

    monkeypatch.setattr(ch.ui, "confirm", fake_confirm)

    assert ch.delete_contact(["john"], john) == "Contact 'John' deleted."
    assert questions == ["Delete contact 'John'?"]
    assert not john.book


def test_delete_other_case_cancelled_keeps_contact(john, monkeypatch):
    monkeypatch.setattr(ch.ui, "confirm", lambda question: False)

    assert ch.delete_contact(["JOHN"], john) == "Deletion cancelled."
    assert list(john.book) == ["John"]


# Save and load keeps one contact with both phones.
def test_save_and_load_keeps_one_contact(ctx, tmp_path):
    ch.add_contact(["John", "0501234567"], ctx)
    ch.add_contact(["john", "0631234567"], ctx)
    path = tmp_path / "contacts.json"

    storage.save_book(ctx.book, path)
    loaded = storage.load_book(path)

    assert list(loaded) == ["John"]
    assert [p.value for p in loaded.find("john").phones] == [
        "0501234567",
        "0631234567",
    ]
