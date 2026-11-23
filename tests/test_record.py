"""Record fields and mutation methods (T07)."""

from datetime import date, timedelta

import pytest

from assistant.exceptions import ValidationError
from assistant.fields import DATE_FORMAT, Birthday, Name
from assistant.record import Record


@pytest.fixture
def john():
    record = Record("John")
    record.add_phone("0501234567")
    return record


def phones(record):
    return [p.value for p in record.phones]


@pytest.mark.parametrize("value", ["   ", None])
def test_empty_name(value):
    with pytest.raises(ValidationError, match="Name can't be empty"):
        Name(value)


def test_name_is_stripped():
    assert Name("  John ").value == "John"


def test_birthday_in_future():
    tomorrow = (date.today() + timedelta(days=1)).strftime(DATE_FORMAT)
    with pytest.raises(ValidationError, match="is in the future"):
        Birthday(tomorrow)


def test_birthday_today_is_ok():
    assert Birthday(date.today().strftime(DATE_FORMAT)).value == date.today()


def test_add_same_phone_twice(john):
    with pytest.raises(ValidationError, match="already has phone '0501234567'"):
        john.add_phone("0501234567")
    assert phones(john) == ["0501234567"]


def test_remove_phone(john):
    john.add_phone("0631234567")
    john.remove_phone("0501234567")
    assert phones(john) == ["0631234567"]


def test_remove_missing_phone(john):
    with pytest.raises(ValidationError, match="'John' has no phone '0000000000'"):
        john.remove_phone("0000000000")
    assert phones(john) == ["0501234567"]


def test_edit_phone(john):
    john.add_phone("0631234567")
    john.edit_phone("0501234567", "0991234567")
    assert phones(john) == ["0991234567", "0631234567"]
    assert "phones: 0991234567; 0631234567," in str(john)


def test_edit_phone_to_existing_phone(john):
    john.add_phone("0631234567")
    with pytest.raises(ValidationError, match="already has phone '0631234567'"):
        john.edit_phone("0501234567", "0631234567")
    assert phones(john) == ["0501234567", "0631234567"]


def test_str_shows_all_fields(john):
    john.set_email("john@example.com")
    john.set_address("Kyiv, Khreshchatyk 1")
    john.set_birthday("15.03.1990")
    assert str(john) == (
        "Contact name: John, phones: 0501234567, email: john@example.com, "
        "address: Kyiv, Khreshchatyk 1, birthday: 15.03.1990"
    )


def test_str_shows_missing_fields():
    assert str(Record("Ann")) == (
        "Contact name: Ann, phones: -, email: -, address: -, birthday: -"
    )
