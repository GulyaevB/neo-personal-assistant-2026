"""Context passed to every handler."""

from collections.abc import Callable
from dataclasses import dataclass

from assistant.address_book import AddressBook
from assistant.notes import NoteBook


@dataclass
class Context:
    """Data a handler can use."""

    book: AddressBook
    notes: NoteBook


# handler(args, ctx) -> str, args are the words after the command name
Handler = Callable[[list[str], Context], str]
