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
        """Add a phone."""
        # TODO(T07): error if the contact already has this phone
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        """Remove a phone."""
        # TODO(T07): error if there is no such phone
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Replace old_phone with new_phone."""
        # TODO(T07): error if new_phone is already in the list
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValidationError(f"Phone {old_phone} not found.")

    def find_phone(self, phone: str) -> Phone | None:
        """Return the Phone or None."""
        for p in self.phones:
            if p.value == phone:
                return p
        return None

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
        """Convert for JSON:

        {"name": "John", "phones": ["0501234567"], "email": None,
         "address": None, "birthday": "15.03.1990"}
        """
        raise NotImplementedError  # TODO(T15)

    @classmethod
    def from_dict(cls, data: dict) -> "Record":
        """Opposite of to_dict."""
        raise NotImplementedError  # TODO(T15)

    def __str__(self) -> str:
        parts = [f"Contact name: {self.name}"]
        parts.append(f"phones: {'; '.join(p.value for p in self.phones)}")
        if self.email:
            parts.append(f"email: {self.email}")
        if self.address:
            parts.append(f"address: {self.address}")
        if self.birthday:
            parts.append(f"birthday: {self.birthday}")
        return ", ".join(parts)
