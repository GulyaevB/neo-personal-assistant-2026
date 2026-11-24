"""Save and load data in ~/.personal_assistant (contacts.json, notes.json).

A broken file is renamed to name.YYYYMMDD-HHMMSS.bak and the app starts
with an empty book. Saving goes through a temp file, so a crash can't leave
half a file.
"""

import json
from datetime import datetime
from pathlib import Path

from assistant.address_book import AddressBook
from assistant.exceptions import ValidationError
from assistant.notes import NoteBook

DATA_DIR = Path.home() / ".personal_assistant"
CONTACTS_FILE = DATA_DIR / "contacts.json"
NOTES_FILE = DATA_DIR / "notes.json"

# Bad JSON (JSONDecodeError is a ValueError), wrong types, missing keys,
# huge numbers, bad values
BROKEN_DATA_ERRORS = (ValueError, TypeError, KeyError, OverflowError, ValidationError)


def _backup(path: Path) -> None:
    """Rename a broken file to name.YYYYMMDD-HHMMSS.bak."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path.replace(path.with_name(f"{path.stem}.{stamp}.bak"))


def _load(path: Path, book_class, key: str):
    """Read the file into book_class. A broken file goes to .bak."""
    if not path.exists():
        return book_class()
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict) or not isinstance(data.get(key), list):
            raise ValueError
        book = book_class.from_dict(data)
        if len(book) != len(data[key]):  # same name or id twice
            raise ValueError
        return book
    except BROKEN_DATA_ERRORS:
        _backup(path)
        return book_class()


def _save(path: Path, data: dict) -> None:
    """Write to a temp file first, then replace the old file with it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def load_book(path: Path = CONTACTS_FILE) -> AddressBook:
    """Load contacts. Empty book if the file is missing or broken."""
    return _load(path, AddressBook, "contacts")


def save_book(book: AddressBook, path: Path = CONTACTS_FILE) -> None:
    """Save contacts."""
    _save(path, book.to_dict())


def load_notes(path: Path = NOTES_FILE) -> NoteBook:
    """Load notes. Empty notebook if the file is missing or broken."""
    return _load(path, NoteBook, "notes")


def save_notes(notes: NoteBook, path: Path = NOTES_FILE) -> None:
    """Save notes."""
    _save(path, notes.to_dict())
