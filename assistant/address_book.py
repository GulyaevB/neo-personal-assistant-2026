"""Address book."""

from collections import UserDict
from datetime import date, timedelta

from assistant.exceptions import ContactNotFoundError
from assistant.record import Record


def _birthday_in_year(birthday: date, year: int) -> date:
    """Same date in another year. 29.02 becomes 28.02 in a non-leap year."""
    try:
        return birthday.replace(year=year)
    except ValueError:
        return birthday.replace(year=year, day=28)


class AddressBook(UserDict):
    """Contacts by name: {name: Record}."""

    def add_record(self, record: Record) -> None:
        """Add a contact. A contact with the same name is replaced."""
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        """Return the contact or raise ContactNotFoundError."""
        if name not in self.data:
            raise ContactNotFoundError(name)
        return self.data[name]

    def delete(self, name: str) -> None:
        """Delete the contact or raise ContactNotFoundError."""
        if name not in self.data:
            raise ContactNotFoundError(name)
        del self.data[name]

    def search(self, query: str) -> list[Record]:
        """Find contacts by name, phone, email or address.

        Case-insensitive, also finds names with small typos.
        """
        raise NotImplementedError  # TODO(T09)

    def get_upcoming_birthdays(self, days: int = 7) -> list[tuple[Record, date]]:
        """Contacts with a birthday in the next `days` days, today included.

        Weekend birthdays are moved to Monday.
        Returns (record, congratulation date) pairs sorted by date.
        """
        # TODO(T10): edge cases (end of year, 29.02) and tests
        # TODO(T10): on Monday we miss Saturday/Sunday birthdays,
        # but they should be congratulated today
        upcoming = []
        today = date.today()

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = _birthday_in_year(record.birthday.value, today.year)
            if birthday < today:
                birthday = _birthday_in_year(record.birthday.value, today.year + 1)

            if 0 <= (birthday - today).days < days:
                congrats = birthday
                if congrats.weekday() == 5:  # Saturday
                    congrats += timedelta(days=2)
                elif congrats.weekday() == 6:  # Sunday
                    congrats += timedelta(days=1)

                upcoming.append((record, congrats))

        upcoming.sort(key=lambda item: item[1])
        return upcoming

    def to_dict(self) -> dict:
        """Convert for JSON: {"contacts": [record, ...]}."""
        raise NotImplementedError  # TODO(T15)

    @classmethod
    def from_dict(cls, data: dict) -> "AddressBook":
        """Opposite of to_dict."""
        raise NotImplementedError  # TODO(T15)
