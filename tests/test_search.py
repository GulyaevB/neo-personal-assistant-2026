"""AddressBook.search (T09)."""

import pytest

from assistant.address_book import AddressBook
from assistant.exceptions import ValidationError
from assistant.record import Record


@pytest.fixture
def book():
    book = AddressBook()
    for name, phone, email, address in [
        ("John", "0501234567", "john@example.com", "Kyiv, Khreshchatyk 1"),
        ("Anna", "0631112233", "anna@mail.com", "Lviv, Rynok 5"),
        ("Dan", "0997654321", "dan@example.com", "Odesa, Derybasivska 3"),
    ]:
        record = Record(name)
        record.add_phone(phone)
        record.set_email(email)
        record.set_address(address)
        book.add_record(record)
    return book


@pytest.mark.parametrize(
    "query, names",
    [
        ("JO", ["John"]),
        ("1122", ["Anna"]),
        ("@MAIL", ["Anna"]),
        ("kyiv", ["John"]),
        ("example", ["John", "Dan"]),
        ("jhon", ["John"]),
        ("ann", ["Anna"]),
        ("zzz", []),
    ],
)
def test_search(book, query, names):
    assert [r.name.value for r in book.search(query)] == names


def test_search_empty_query(book):
    with pytest.raises(ValidationError, match="Search query can't be empty"):
        book.search("  ")
