"""Save and load data in ~/.personal_assistant (contacts.json, notes.json).

A file that can't be read is renamed to name.YYYYMMDD-HHMMSS.bak and the app
starts with an empty book. Contacts that fail the current checks are skipped,
the rest are loaded and the original file is copied to .bak as is.
New .bak files go to `backups` for cli to show.
Saving goes through a temp file, so a crash can't leave half a file.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from assistant.address_book import AddressBook
from assistant.exceptions import ValidationError
from assistant.notes import NoteBook
from assistant.record import Record

DATA_DIR = Path.home() / ".personal_assistant"
CONTACTS_FILE = DATA_DIR / "contacts.json"
NOTES_FILE = DATA_DIR / "notes.json"

# Bad JSON (JSONDecodeError is a ValueError), wrong types, missing keys,
# huge numbers, bad values
BROKEN_DATA_ERRORS = (ValueError, TypeError, KeyError, OverflowError, ValidationError)

# (.bak file, names of skipped contacts) made while loading; no names means
# the whole file was moved. cli reads this list, so clear it, don't reassign
backups: list[tuple[Path, list[str]]] = []


def _backup(path: Path, skipped: list[str] | None = None) -> None:
    """Move to name.YYYYMMDD-HHMMSS.bak, or copy if contacts were skipped."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.stem}.{stamp}.bak")
    if skipped:
        shutil.copyfile(path, backup)
    else:
        path.replace(backup)
    backups.append((backup, skipped or []))


def _read(path: Path, key: str) -> dict | None:
    """The file data, or None if there is no file.

    A file that can't be read is moved to .bak and None is returned.
    """
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except ValueError:
        data = None
    if not isinstance(data, dict) or not isinstance(data.get(key), list):
        _backup(path)
        return None
    return data


def _save(path: Path, data: dict) -> None:
    """Write to a temp file first, then replace the old file with it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def load_book(path: Path = CONTACTS_FILE) -> AddressBook:
    """Load contacts. Bad contacts are skipped and the file is copied to .bak."""
    book = AddressBook()
    data = _read(path, "contacts")
    if data is None:
        return book
    skipped = []
    for item in data["contacts"]:
        try:
            book.add_record(Record.from_dict(item))
        except BROKEN_DATA_ERRORS:
            name = item.get("name") if isinstance(item, dict) else None
            skipped.append(str(name or "?"))
    if skipped:
        _backup(path, skipped)
    return book


def save_book(book: AddressBook, path: Path = CONTACTS_FILE) -> None:
    """Save contacts."""
    _save(path, book.to_dict())


def load_notes(path: Path = NOTES_FILE) -> NoteBook:
    """Load notes. Empty notebook if the file is missing or broken."""
    data = _read(path, "notes")
    if data is None:
        return NoteBook()
    try:
        notes = NoteBook.from_dict(data)
        if len(notes) != len(data["notes"]):  # same id twice
            raise ValueError
        return notes
    except BROKEN_DATA_ERRORS:
        _backup(path)
        return NoteBook()


def save_notes(notes: NoteBook, path: Path = NOTES_FILE) -> None:
    """Save notes."""
    _save(path, notes.to_dict())
