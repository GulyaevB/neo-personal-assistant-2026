"""Save and load data in ~/.personal_assistant (contacts.json, notes.json).

TODO(T16): rename a broken file to .bak before starting with an empty book,
save through a temp file and Path.replace().
"""

from pathlib import Path

from assistant.address_book import AddressBook
from assistant.notes import NoteBook

DATA_DIR = Path.home() / ".personal_assistant"
CONTACTS_FILE = DATA_DIR / "contacts.json"
NOTES_FILE = DATA_DIR / "notes.json"


def load_book(path: Path = CONTACTS_FILE) -> AddressBook:
    """Load contacts. Empty book if there is no valid file."""
    # TODO(T16)
    return AddressBook()


def save_book(book: AddressBook, path: Path = CONTACTS_FILE) -> None:
    """Save contacts."""
    # TODO(T16)


def load_notes(path: Path = NOTES_FILE) -> NoteBook:
    """Load notes. Empty notebook if there is no valid file."""
    # TODO(T16)
    return NoteBook()


def save_notes(notes: NoteBook, path: Path = NOTES_FILE) -> None:
    """Save notes."""
    # TODO(T16)
