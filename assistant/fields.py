"""Contact fields. Each field checks its value and raises ValidationError."""

from datetime import datetime

from assistant.exceptions import ValidationError

DATE_FORMAT = "%d.%m.%Y"


class Field:
    """Base field."""

    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Contact name, also the key in AddressBook."""

    def __init__(self, value: str):
        # TODO(T07): empty name
        super().__init__(value)


class Phone(Field):
    """Phone number, exactly 10 digits."""

    def __init__(self, value: str):
        digits = isinstance(value, str) and value.isascii() and value.isdigit()
        if not digits or len(value) != 10:
            raise ValidationError(f"Invalid phone '{value}'. Use 10 digits.")
        super().__init__(value)


class Email(Field):
    """Email address."""

    def __init__(self, value: str):
        # TODO(T06): check the format (regex)
        super().__init__(value)


class Address(Field):
    """Address, any text."""

    def __init__(self, value: str):
        # TODO(T06): empty address
        super().__init__(value)


class Birthday(Field):
    """Date in DD.MM.YYYY, stored as date."""

    def __init__(self, value: str):
        try:
            birthday = datetime.strptime(value, DATE_FORMAT).date()
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid date '{value}'. Use DD.MM.YYYY.") from None
        # TODO(T07): date in the future
        super().__init__(birthday)

    def __str__(self) -> str:
        return self.value.strftime(DATE_FORMAT)
