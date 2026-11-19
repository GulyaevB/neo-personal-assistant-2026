"""Contact commands.

Every handler takes (args, ctx) and returns a string to show.
On error raise AssistantError. Delete asks ui.confirm() first.
days: not a number or less than 1 -> ValidationError, default is 7.
"""

from assistant.context import Context


def add_contact(args: list[str], ctx: Context) -> str:
    """add <name> <phone>: create a contact or add a phone to it."""
    raise NotImplementedError  # TODO(T19)


def change_phone(args: list[str], ctx: Context) -> str:
    """change <name> <old_phone> <new_phone>: replace a phone."""
    raise NotImplementedError  # TODO(T19)


def remove_phone(args: list[str], ctx: Context) -> str:
    """remove-phone <name> <phone>: remove a phone."""
    raise NotImplementedError  # TODO(T19)


def add_email(args: list[str], ctx: Context) -> str:
    """add-email <name> <email>: set the email."""
    raise NotImplementedError  # TODO(T19)


def add_address(args: list[str], ctx: Context) -> str:
    """add-address <name> <address...>: set the address (can be several words)."""
    raise NotImplementedError  # TODO(T19)


def add_birthday(args: list[str], ctx: Context) -> str:
    """add-birthday <name> <DD.MM.YYYY>: set the birthday."""
    raise NotImplementedError  # TODO(T19)


def show_phone(args: list[str], ctx: Context) -> str:
    """phone <name>: show the phones of a contact."""
    raise NotImplementedError  # TODO(T19)


def show_birthday(args: list[str], ctx: Context) -> str:
    """show-birthday <name>: show the birthday of a contact."""
    raise NotImplementedError  # TODO(T19)


def show_all(args: list[str], ctx: Context) -> str:
    """all: show all contacts."""
    raise NotImplementedError  # TODO(T19)


def delete_contact(args: list[str], ctx: Context) -> str:
    """delete <name>: delete a contact (asks for confirmation)."""
    raise NotImplementedError  # TODO(T19, U4)


def search_contacts(args: list[str], ctx: Context) -> str:
    """search <query>: find contacts by name, phone, email or address."""
    raise NotImplementedError  # TODO(T20)


def birthdays(args: list[str], ctx: Context) -> str:
    """birthdays [days]: show birthdays in the next N days (default 7)."""
    raise NotImplementedError  # TODO(T20)
