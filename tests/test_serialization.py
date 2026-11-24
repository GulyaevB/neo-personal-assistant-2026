"""to_dict / from_dict for Record and AddressBook (T15)."""

import json

import pytest

from assistant.address_book import AddressBook
from assistant.exceptions import ValidationError
from assistant.record import Record


@pytest.fixture
def john():
    record = Record("John")
    record.add_phone("0501234567")
    record.add_phone("0631234567")
    record.set_email("john@example.com")
    record.set_address("Kyiv, Khreshchatyk 1")
    record.set_birthday("15.03.1990")
    return record


def test_record_to_dict(john):
    assert john.to_dict() == {
        "name": "John",
        "phones": ["0501234567", "0631234567"],
        "email": "john@example.com",
        "address": "Kyiv, Khreshchatyk 1",
        "birthday": "15.03.1990",
    }


def test_record_without_fields_to_dict():
    assert Record("Ann").to_dict() == {
        "name": "Ann",
        "phones": [],
        "email": None,
        "address": None,
        "birthday": None,
    }


def test_book_roundtrip_through_json(john):
    book = AddressBook()
    book.add_record(john)
    book.add_record(Record("Ann"))

    data = json.loads(json.dumps(book.to_dict()))
    restored = AddressBook.from_dict(data)

    assert restored.to_dict() == book.to_dict()
    assert str(restored.find("John")) == str(john)


def test_from_empty_dict_gives_empty_book():
    assert len(AddressBook.from_dict({})) == 0


@pytest.mark.parametrize(
    "item, error",
    [
        ({"phones": []}, KeyError),
        ({"name": "John", "phones": ["123"]}, ValidationError),
        ({"name": "John", "birthday": "31.02.2000"}, ValidationError),
    ],
)
def test_bad_data_raises(item, error):
    with pytest.raises(error):
        AddressBook.from_dict({"contacts": [item]})
