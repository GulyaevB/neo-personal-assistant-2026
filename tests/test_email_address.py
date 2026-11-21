"""Email and Address fields (T06)."""

import pytest

from assistant.exceptions import ValidationError
from assistant.fields import Address, Email
from assistant.record import Record


@pytest.mark.parametrize(
    "value", ["john@example.com", "john.smith+work@mail.co.uk", "a_b-c@my-site.org"]
)
def test_valid_email(value):
    assert Email(value).value == value


@pytest.mark.parametrize(
    "value",
    [
        "bad",
        "john@",
        "@mail.com",
        "john@mail",
        "john@mail.c",
        "john doe@mail.com",
        None,
    ],
)
def test_bad_email(value):
    with pytest.raises(ValidationError, match=f"Invalid email '{value}'"):
        Email(value)


def test_valid_address_is_stripped():
    assert Address("  Kyiv, Khreshchatyk 1 ").value == "Kyiv, Khreshchatyk 1"


@pytest.mark.parametrize("value", ["   ", None])
def test_blank_address(value):
    with pytest.raises(ValidationError, match="Address can't be empty"):
        Address(value)


def test_record_keeps_old_email_after_bad_one():
    john = Record("John")
    john.set_email("john@example.com")
    with pytest.raises(ValidationError):
        john.set_email("bad")
    assert john.email.value == "john@example.com"
