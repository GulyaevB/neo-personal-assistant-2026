"""Field validation and Record edge cases (T24).

Complements test_record, test_contact_errors and test_email_address
with boundaries they don't cover.
"""

import re
from datetime import date

import pytest

from assistant.exceptions import ValidationError
from assistant.fields import Address, Birthday, Email, Field, Name, Phone
from assistant.record import Record

# --- Inheritance ---


# Every field is a Field: inheritance is part of the OOP criterion.
@pytest.mark.parametrize(
    "field",
    [
        Name("John"),
        Phone("0501234567"),
        Email("a@b.com"),
        Address("Kyiv"),
        Birthday("01.01.2000"),
    ],
)
def test_all_fields_inherit_from_field(field):
    assert isinstance(field, Field)


# --- Name ---


# Spaces around the name are removed, so " John " and "John" are the same key.
def test_name_spaces_are_trimmed():
    assert Name("  John  ").value == "John"
    assert Record("  John  ").name.value == "John"


# A name needs at least one letter, any alphabet (T34).
@pytest.mark.parametrize("value", ["John2", "Анна-Марія", "O'Neil", "J"])
def test_name_with_letters_is_accepted(value):
    assert Name(value).value == value


@pytest.mark.parametrize("value", ["123", "@#$", "0501234567", "-"])
def test_name_without_letters_is_rejected(value):
    with pytest.raises(ValidationError, match="Use at least one letter"):
        Name(value)


# --- Phone ---


# Only plain 10 digits: no spaces, dashes, country code or other digit systems.
@pytest.mark.parametrize(
    "value",
    ["050 123 4567", "050-123-4567", "+380501234567", " 0501234567", "٠٥٠١٢٣٤٥٦٧"],
)
def test_phone_rejects_formatted_numbers(value):
    with pytest.raises(ValidationError):
        Phone(value)


# Boundaries: 9 and 11 digits are rejected, exactly 10 is accepted.
@pytest.mark.parametrize(
    ("value", "valid"),
    [("050123456", False), ("0501234567", True), ("05012345678", False)],
)
def test_phone_length_boundaries(value, valid):
    if valid:
        assert Phone(value).value == value
    else:
        with pytest.raises(ValidationError):
            Phone(value)


# The error shows what the user typed, in the team message style.
def test_phone_error_shows_value():
    with pytest.raises(ValidationError, match="Invalid phone '123'"):
        Phone("123")


# --- Email ---


@pytest.mark.parametrize(
    "value", ["A@B.COM", "first.last+tag@sub.domain.com", "a.b.c@mail.com"]
)
def test_email_accepts_common_formats(value):
    assert Email(value).value == value


# Dots: not two in a row, not at the start or end of a part (T34).
@pytest.mark.parametrize(
    "value", ["a..b@c.com", ".a@c.com", "a.@c.com", ".@c.com", "a@b..com", "a@.b.com"]
)
def test_email_rejects_bad_dots(value):
    with pytest.raises(ValidationError, match=re.escape(f"Invalid email '{value}'")):
        Email(value)


# Spaces around the email are not accepted (the user must fix the input).
def test_email_with_spaces_is_rejected():
    with pytest.raises(ValidationError):
        Email(" a@b.com ")


# --- Birthday ---


# Leap day exists only in leap years; a non-existing date is an error.
@pytest.mark.parametrize(
    ("value", "valid"),
    [("29.02.2024", True), ("29.02.2023", False), ("31.04.1990", False)],
)
def test_birthday_real_dates_only(value, valid):
    if valid:
        assert str(Birthday(value)) == value
    else:
        with pytest.raises(ValidationError):
            Birthday(value)


# Only DD.MM.YYYY is accepted.
@pytest.mark.parametrize("value", ["15/05/1990", "1990-05-15", "15.05.90", ""])
def test_birthday_other_formats_are_rejected(value):
    with pytest.raises(ValidationError):
        Birthday(value)


# Birthday is stored as a date and printed back as DD.MM.YYYY.
def test_birthday_is_stored_as_date():
    birthday = Birthday("05.01.2000")
    assert birthday.value == date(2000, 1, 5)
    assert str(birthday) == "05.01.2000"


# The year can't be before MIN_BIRTH_YEAR (T34).
@pytest.mark.parametrize(
    ("value", "valid"),
    [("01.01.1900", True), ("31.12.1899", False), ("01.01.0001", False)],
)
def test_birthday_year_lower_limit(value, valid):
    if valid:
        assert str(Birthday(value)) == value
    else:
        with pytest.raises(ValidationError, match="is too old"):
            Birthday(value)


# --- Record ---


# A failed setter keeps the old value (no half-updated contact).
@pytest.mark.parametrize(
    ("setter", "attribute", "good", "bad"),
    [
        ("set_address", "address", "Kyiv", "   "),
        ("set_birthday", "birthday", "15.05.1990", "31.02.1990"),
    ],
)
def test_record_keeps_old_value_after_bad_input(setter, attribute, good, bad):
    record = Record("John")
    getattr(record, setter)(good)
    with pytest.raises(ValidationError):
        getattr(record, setter)(bad)
    assert str(getattr(record, attribute)) == good


# A bad phone is not added, the list stays the same.
def test_record_bad_phone_is_not_added():
    record = Record("John")
    record.add_phone("0501234567")
    with pytest.raises(ValidationError):
        record.add_phone("123")
    assert [phone.value for phone in record.phones] == ["0501234567"]


# Changing a phone to the same number is allowed (no false duplicate error).
def test_edit_phone_to_same_number():
    record = Record("John")
    record.add_phone("0501234567")
    record.edit_phone("0501234567", "0501234567")
    assert [phone.value for phone in record.phones] == ["0501234567"]


# find_phone returns None for a missing phone instead of raising.
def test_find_missing_phone_returns_none():
    assert Record("John").find_phone("0501234567") is None
