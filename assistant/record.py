"""Contact record."""

from assistant.exceptions import ValidationError
from assistant.fields import Address, Birthday, Email, Name, Phone


class Record:
    """A contact: name, phones, email, address, birthday.

    Made of Field objects, they do the validation.
    """

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.email: Email | None = None
        self.address: Address | None = None
        self.birthday: Birthday | None = None

    def add_phone(self, phone: str) -> None:
        """Add a phone. The same phone can't be added twice."""
        new_phone = Phone(phone)
        if self.find_phone(phone) is not None:
            raise ValidationError(f"Contact '{self.name}' already has phone '{phone}'.")
        self.phones.append(new_phone)

    def remove_phone(self, phone: str) -> None:
        """Remove a phone or raise ValidationError."""
        self.phones.remove(self._get_phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Replace old_phone with new_phone or raise ValidationError."""
        index = self.phones.index(self._get_phone(old_phone))
        phone = Phone(new_phone)
        if new_phone != old_phone and self.find_phone(new_phone) is not None:
            raise ValidationError(
                f"Contact '{self.name}' already has phone '{new_phone}'."
            )
        self.phones[index] = phone

    def find_phone(self, phone: str) -> Phone | None:
        """Return the Phone or None."""
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def _get_phone(self, phone: str) -> Phone:
        """Return the Phone or raise ValidationError."""
        found = self.find_phone(phone)
        if found is None:
            raise ValidationError(f"Contact '{self.name}' has no phone '{phone}'.")
        return found

    def set_email(self, email: str) -> None:
        """Set the email."""
        self.email = Email(email)

    def set_address(self, address: str) -> None:
        """Set the address."""
        self.address = Address(address)

    def set_birthday(self, birthday: str) -> None:
        """Set the birthday, DD.MM.YYYY."""
        self.birthday = Birthday(birthday)

    def to_dict(self) -> dict:
        """Convert for JSON: name, phones, email, address, birthday (DD.MM.YYYY).

        Missing fields are None.
        """
        raise NotImplementedError  # TODO(T15)

    @classmethod
    def from_dict(cls, data: dict) -> "Record":
        """Opposite of to_dict."""
        raise NotImplementedError  # TODO(T15)

    def __str__(self) -> str:
        phones = "; ".join(p.value for p in self.phones) or "-"
        return (
            f"Contact name: {self.name}, phones: {phones}, "
            f"email: {self.email or '-'}, address: {self.address or '-'}, "
            f"birthday: {self.birthday or '-'}"
        )
