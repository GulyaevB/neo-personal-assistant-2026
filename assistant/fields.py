"""Contact fields. Each field checks its value and raises ValidationError."""

import re
from datetime import date, datetime

from assistant.exceptions import ValidationError

MIN_BIRTH_YEAR = 1900
DATE_FORMAT = "%d.%m.%Y"
# Name part: dots only between other characters, never two in a row
EMAIL_PATTERN = re.compile(r"[\w+-]+(\.[\w+-]+)*@[\w-]+(\.[\w-]+)*\.[A-Za-z]{2,}")


class Field:
    """Base field."""

    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Contact name with at least one letter, also the key in AddressBook.

    Spaces around are removed.
    """

    def __init__(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Name can't be empty.")
        if not any(char.isalpha() for char in value):
            raise ValidationError(f"Invalid name '{value}'. Use at least one letter.")
        super().__init__(value.strip())


class Phone(Field):
    """Phone number, exactly 10 digits."""

    def __init__(self, value: str):
        digits = isinstance(value, str) and value.isascii() and value.isdigit()
        if not digits or len(value) != 10:
            raise ValidationError(f"Invalid phone '{value}'. Use 10 digits.")
        super().__init__(value)


class Email(Field):
    """Email address, checked with EMAIL_PATTERN."""

    def __init__(self, value: str):
        if not isinstance(value, str) or not EMAIL_PATTERN.fullmatch(value):
            raise ValidationError(f"Invalid email '{value}'. Use name@domain.com.")
        super().__init__(value)


class Address(Field):
    """Address, any text except blank. Spaces around are removed."""

    def __init__(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Address can't be empty.")
        super().__init__(value.strip())


class Birthday(Field):
    """Date in DD.MM.YYYY from MIN_BIRTH_YEAR to today, stored as date."""

    def __init__(self, value: str):
        try:
            birthday = datetime.strptime(value, DATE_FORMAT).date()
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid date '{value}'. Use DD.MM.YYYY.") from None
        if birthday > date.today():
            raise ValidationError(f"Birthday '{value}' is in the future.")
        if birthday.year < MIN_BIRTH_YEAR:
            raise ValidationError(
                f"Birthday '{value}' is too old. Use {MIN_BIRTH_YEAR} or later."
            )
        super().__init__(birthday)

    def __str__(self) -> str:
        return self.value.strftime(DATE_FORMAT)
