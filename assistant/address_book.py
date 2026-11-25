"""Address book."""

from collections import UserDict
from datetime import date
from difflib import SequenceMatcher

from assistant.exceptions import ContactNotFoundError, ValidationError
from assistant.record import Record

FUZZY_CUTOFF = 0.75  # how similar a name must be to count as a typo (0..1)


def _birthday_in_year(birthday: date, year: int) -> date:
    """Same date in another year. 29.02 becomes 28.02 in a non-leap year."""
    try:
        return birthday.replace(year=year)
    except ValueError:
        return birthday.replace(year=year, day=28)


class AddressBook(UserDict):
    """Contacts by name: {name: Record}.

    Names are unique ignoring case. The name is stored as it was typed first.
    """

    def _stored_name(self, name: str) -> str | None:
        """The name as it is stored in the book (case ignored), or None."""
        for stored in self.data:
            if stored.lower() == name.lower():
                return stored
        return None

    def add_record(self, record: Record) -> None:
        """Add a new contact or raise ValidationError if the name is taken."""
        stored = self._stored_name(record.name.value)
        if stored is not None:
            raise ValidationError(f"Contact '{stored}' already exists.")
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        """Return the contact (case ignored) or raise ContactNotFoundError."""
        stored = self._stored_name(name)
        if stored is None:
            raise ContactNotFoundError(name)
        return self.data[stored]

    def delete(self, name: str) -> None:
        """Delete the contact (case ignored) or raise ContactNotFoundError."""
        del self.data[self.find(name).name.value]

    def search(self, query: str) -> list[Record]:
        """Contacts whose name, phone, email or address contains `query`.

        Case-insensitive, also finds names with small typos.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValidationError("Search query can't be empty.")
        query = query.strip().lower()
        found = []
        for record in self.data.values():
            fields = [record.name, *record.phones, record.email, record.address]
            name = record.name.value.lower()
            typo = SequenceMatcher(None, query, name).ratio() >= FUZZY_CUTOFF
            if typo or any(query in str(f).lower() for f in fields if f):
                found.append(record)
        return found

    def get_upcoming_birthdays(
        self, days: int = 7, today: date | None = None
    ) -> list[tuple[Record, date]]:
        """Contacts with a birthday in the next `days` days, today included.

        Returns (record, next birthday date) pairs sorted by date.
        `today` is for tests, by default the current date.
        """
        today = today or date.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = _birthday_in_year(record.birthday.value, today.year)
            if birthday < today:
                birthday = _birthday_in_year(record.birthday.value, today.year + 1)

            if (birthday - today).days < days:
                upcoming.append((record, birthday))

        upcoming.sort(key=lambda item: item[1])
        return upcoming

    def to_dict(self) -> dict:
        """Convert for JSON: {"contacts": [record, ...]}."""
        return {"contacts": [record.to_dict() for record in self.data.values()]}

    @classmethod
    def from_dict(cls, data: dict) -> "AddressBook":
        """Opposite of to_dict."""
        book = cls()
        for item in data.get("contacts", []):
            book.add_record(Record.from_dict(item))
        return book
