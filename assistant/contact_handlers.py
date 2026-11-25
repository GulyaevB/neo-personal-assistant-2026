"""Contact commands (T19, T20).

Every handler takes (args, ctx) and returns a string to show.
On error it raises AssistantError, cli shows it in red.
Commands are registered with @command (T18); @input_error is below it.
"""

from assistant import ui
from assistant.commands import command
from assistant.context import Context
from assistant.decorators import input_error
from assistant.exceptions import ContactNotFoundError, ValidationError
from assistant.record import Record

DEFAULT_DAYS = 7


def _require(args: list[str], count: int, usage: str) -> None:
    """Not enough arguments -> ValidationError that shows the right format."""
    if len(args) < count:
        raise ValidationError(f"Missing arguments. Use: {usage}")


@command("add")
@input_error
def add_contact(args: list[str], ctx: Context) -> str:
    """add <name> <phone>: create a contact or add a phone to it."""
    _require(args, 2, "add <name> <phone>")
    name, phone = args[0], args[1]
    try:
        # Case is ignored (T34): "john" finds "John". Only "not found" means
        # a new contact; a bad phone below is a real error, not "not found".
        record = ctx.book.find(name)
    except ContactNotFoundError:
        record = Record(name)
        record.add_phone(phone)  # check the phone before the contact is saved
        ctx.book.add_record(record)
        return f"Contact '{record.name.value}' added."
    record.add_phone(phone)
    return f"Phone added to '{record.name.value}'."


@command("change")
@input_error
def change_phone(args: list[str], ctx: Context) -> str:
    """change <name> <old_phone> <new_phone>: replace a phone."""
    _require(args, 3, "change <name> <old_phone> <new_phone>")
    name, old_phone, new_phone = args[0], args[1], args[2]
    record = ctx.book.find(name)
    record.edit_phone(old_phone, new_phone)
    return f"Phone updated for '{record.name.value}'."


@command("remove-phone")
@input_error
def remove_phone(args: list[str], ctx: Context) -> str:
    """remove-phone <name> <phone>: remove a phone."""
    _require(args, 2, "remove-phone <name> <phone>")
    name, phone = args[0], args[1]
    record = ctx.book.find(name)
    record.remove_phone(phone)
    return f"Phone removed from '{record.name.value}'."


@command("add-email")
@input_error
def add_email(args: list[str], ctx: Context) -> str:
    """add-email <name> <email>: set the email."""
    _require(args, 2, "add-email <name> <email>")
    record = ctx.book.find(args[0])
    record.set_email(args[1])
    return f"Email set for '{record.name.value}'."


@command("add-address")
@input_error
def add_address(args: list[str], ctx: Context) -> str:
    """add-address <name> <address...>: set the address (can be several words)."""
    _require(args, 2, "add-address <name> <address>")
    record = ctx.book.find(args[0])
    record.set_address(" ".join(args[1:]))
    return f"Address set for '{record.name.value}'."


@command("add-birthday")
@input_error
def add_birthday(args: list[str], ctx: Context) -> str:
    """add-birthday <name> <DD.MM.YYYY>: set the birthday."""
    _require(args, 2, "add-birthday <name> <DD.MM.YYYY>")
    record = ctx.book.find(args[0])
    record.set_birthday(args[1])
    return f"Birthday set for '{record.name.value}'."


@command("phone")
@input_error
def show_phone(args: list[str], ctx: Context) -> str:
    """phone <name>: show the phones of a contact."""
    _require(args, 1, "phone <name>")
    record = ctx.book.find(args[0])
    if not record.phones:
        return f"Contact '{record.name}' has no phones."
    return f"{record.name}: " + "; ".join(phone.value for phone in record.phones)


@command("show-birthday")
@input_error
def show_birthday(args: list[str], ctx: Context) -> str:
    """show-birthday <name>: show the birthday of a contact."""
    _require(args, 1, "show-birthday <name>")
    record = ctx.book.find(args[0])
    if record.birthday is None:
        return f"Contact '{record.name}' has no birthday."
    return f"{record.name}: {record.birthday}"


@command("all")
@input_error
def show_all(args: list[str], ctx: Context) -> str:
    """all: show all contacts."""
    if not ctx.book:
        return "No contacts yet. Add one with: add <name> <phone>"
    records = sorted(ctx.book.values(), key=lambda record: record.name.value.lower())
    return "\n".join(ui.format_contact(record) for record in records)


@command("delete")
@input_error
def delete_contact(args: list[str], ctx: Context) -> str:
    """delete <name>: delete a contact (asks for confirmation)."""
    _require(args, 1, "delete <name>")
    record = ctx.book.find(args[0])  # unknown contact -> error, no question
    name = record.name.value  # as stored: "John", even if "john" was typed
    if not ui.confirm(f"Delete contact '{name}'?"):
        return "Deletion cancelled."
    ctx.book.delete(name)
    return f"Contact '{name}' deleted."


@command("search")
@input_error
def search_contacts(args: list[str], ctx: Context) -> str:
    """search <query>: find contacts by name, phone, email or address."""
    _require(args, 1, "search <query>")
    query = " ".join(args)
    found = ctx.book.search(query)
    if not found:
        return f"No contacts found for '{query}'."
    records = sorted(found, key=lambda record: record.name.value.lower())
    return "\n".join(ui.format_contact(record) for record in records)


def parse_days(args: list[str]) -> int:
    """Days for `birthdays`: no argument -> 7, not a number or < 1 -> error."""
    if not args:
        return DEFAULT_DAYS
    value = args[0]
    try:
        days = int(value)
    except ValueError:
        days = 0
    if days < 1:
        raise ValidationError(f"Invalid days '{value}'. Use a positive number.")
    return days


@command("birthdays")
@input_error
def birthdays(args: list[str], ctx: Context) -> str:
    """birthdays [days]: show birthdays in the next N days (default 7)."""
    days = parse_days(args)
    upcoming = ctx.book.get_upcoming_birthdays(days)
    period = "today" if days == 1 else f"in the next {days} days"
    if not upcoming:
        return f"No birthdays {period}."
    lines = [f"Birthdays {period}:"]
    for record, day in upcoming:
        lines.append(f"{day:%d.%m.%Y} ({day:%a})  {record.name}")
    return "\n".join(lines)
