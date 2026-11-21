"""Error paths of the contact models (T05)."""

import pytest

from assistant.address_book import AddressBook
from assistant.exceptions import ContactNotFoundError, ValidationError
from assistant.fields import Birthday, Phone
from assistant.record import Record


@pytest.fixture
def book():
    john = Record("John")
    john.add_phone("0501234567")
    book = AddressBook()
    book.add_record(john)
    return book


@pytest.mark.parametrize(
    "value",
    ["123", "05012345678", "050123456a", "０５０１２３４５６７", None, 501234567],
)
def test_bad_phone(value):
    with pytest.raises(ValidationError, match=f"Invalid phone '{value}'"):
        Phone(value)


@pytest.mark.parametrize("value", ["31.02.2000", "abc", None])
def test_bad_birthday(value):
    with pytest.raises(ValidationError, match=f"Invalid date '{value}'"):
        Birthday(value)


def test_edit_missing_phone(book):
    with pytest.raises(ValidationError, match="'John' has no phone '0000000000'"):
        book.find("John").edit_phone("0000000000", "0631234567")


def test_edit_phone_to_bad_value_keeps_old_phone(book):
    john = book.find("John")
    with pytest.raises(ValidationError):
        john.edit_phone("0501234567", "12")
    assert [p.value for p in john.phones] == ["0501234567"]


def test_find_missing_contact(book):
    with pytest.raises(ContactNotFoundError, match="'Ann' not found"):
        book.find("Ann")


def test_delete_missing_contact_keeps_book(book):
    with pytest.raises(ContactNotFoundError):
        book.delete("Ann")
    assert list(book) == ["John"]
