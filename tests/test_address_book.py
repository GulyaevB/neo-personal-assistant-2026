"""AddressBook lookup, search and birthdays edge cases (T24).

Complements test_search, test_birthdays and test_contact_errors.
"""

from datetime import date

import pytest

from assistant.address_book import AddressBook
from assistant.exceptions import ContactNotFoundError
from assistant.record import Record


@pytest.fixture
def book():
    """Book with John (phone, email, address, birthday) and Anna (phone only)."""
    address_book = AddressBook()
    john = Record("John")
    john.add_phone("0501234567")
    john.set_email("john@mail.com")
    john.set_address("Kyiv, Khreshchatyk 1")
    john.set_birthday("15.05.1990")
    address_book.add_record(john)

    anna = Record("Anna")
    anna.add_phone("0671112233")
    address_book.add_record(anna)
    return address_book


# --- Lookup ---


def test_find_returns_record(book):
    assert book.find("Anna").phones[0].value == "0671112233"


# A name typed with spaces is trimmed on create, so it is found by the clean name.
def test_contact_added_with_spaces_is_found_by_clean_name():
    address_book = AddressBook()
    address_book.add_record(Record("  Olga  "))
    assert address_book.find("Olga").name.value == "Olga"


# Names are keys as typed: find() is exact, search() is the forgiving one.
def test_find_is_exact_but_search_is_case_insensitive(book):
    with pytest.raises(ContactNotFoundError):
        book.find("john")
    assert [record.name.value for record in book.search("john")] == ["John"]


# Deleting one contact keeps the others.
def test_delete_keeps_other_contacts(book):
    book.delete("John")
    assert list(book.keys()) == ["Anna"]


# --- Search ---


# Contacts with empty fields (no email, no address) are searched safely.
def test_search_contact_without_email_and_address(book):
    assert [record.name.value for record in book.search("067111")] == ["Anna"]


# Spaces around the query are ignored.
def test_search_ignores_spaces_around_query(book):
    assert [record.name.value for record in book.search("  kyiv  ")] == ["John"]


# No matches is not an error: handlers get an empty list.
def test_search_without_matches_returns_empty_list(book):
    assert book.search("zzzzzz") == []


# --- Birthdays ---


# days=1 means only today; days=0 shows nothing.
def test_upcoming_birthdays_period_edges(book):
    today = date(2026, 5, 15)  # John's birthday
    assert book.get_upcoming_birthdays(0, today) == []
    [(record, when)] = book.get_upcoming_birthdays(1, today)
    assert (record.name.value, when) == ("John", today)


# The actual date is shown, even on a weekend (no Monday shift, T10 decision).
def test_upcoming_birthday_on_weekend_keeps_real_date(book):
    today = date(2027, 5, 10)  # 15.05.2027 is a Saturday
    [(_, when)] = book.get_upcoming_birthdays(7, today)
    assert when == date(2027, 5, 15)
    assert when.weekday() == 5


# Empty book: no birthdays, no errors.
def test_upcoming_birthdays_on_empty_book():
    assert AddressBook().get_upcoming_birthdays(7, date(2026, 1, 1)) == []
