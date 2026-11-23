"""AddressBook.get_upcoming_birthdays (T10)."""

from datetime import date

import pytest

from assistant.address_book import AddressBook
from assistant.record import Record


def upcoming(birthdays, today, days=7):
    book = AddressBook()
    for name, birthday in birthdays.items():
        record = Record(name)
        if birthday:
            record.set_birthday(birthday)
        book.add_record(record)
    return [
        (record.name.value, day)
        for record, day in book.get_upcoming_birthdays(days, today)
    ]


def test_january_birthdays_on_25_december():
    birthdays = {"Ann": "01.01.1990", "Bob": "03.01.1985", "Max": "04.01.1990"}
    assert upcoming(birthdays, date(2026, 12, 25), days=10) == [
        ("Ann", date(2027, 1, 1)),
        ("Bob", date(2027, 1, 3)),
    ]


def test_period_includes_today_but_not_last_day():
    birthdays = {"Today": "23.11.1990", "Day6": "29.11.1990", "Day7": "30.11.1990"}
    assert upcoming(birthdays, date(2026, 11, 23)) == [
        ("Today", date(2026, 11, 23)),
        ("Day6", date(2026, 11, 29)),
    ]


def test_passed_birthday_is_not_shown():
    assert upcoming({"Ann": "22.11.1990"}, date(2026, 11, 23)) == []


def test_weekend_birthday_is_not_moved():
    assert upcoming({"Ann": "28.11.1990"}, date(2026, 11, 23)) == [
        ("Ann", date(2026, 11, 28))
    ]


@pytest.mark.parametrize(
    "today, expected",
    [(date(2027, 2, 20), date(2027, 2, 28)), (date(2028, 2, 20), date(2028, 2, 29))],
)
def test_leap_day_birthday(today, expected):
    assert upcoming({"Ann": "29.02.2000"}, today, days=10) == [("Ann", expected)]


def test_results_are_sorted_and_contacts_without_birthday_skipped():
    birthdays = {"Late": "27.11.1990", "NoBirthday": None, "Soon": "24.11.1990"}
    assert upcoming(birthdays, date(2026, 11, 23)) == [
        ("Soon", date(2026, 11, 24)),
        ("Late", date(2026, 11, 27)),
    ]
