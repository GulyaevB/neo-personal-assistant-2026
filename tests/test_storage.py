"""Saving and loading contacts and notes (T16)."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from assistant import storage
from assistant.address_book import AddressBook
from assistant.exceptions import ContactNotFoundError
from assistant.notes import NoteBook
from assistant.record import Record
from assistant.storage import load_book, load_notes, save_book, save_notes


def make_book():
    record = Record("John")
    record.add_phone("0501234567")
    record.set_birthday("15.03.1990")
    book = AddressBook()
    book.add_record(record)
    return book


def backups(folder):
    return list(folder.glob("*.bak"))


def test_missing_file_gives_empty_book(tmp_path):
    assert len(load_book(tmp_path / "contacts.json")) == 0
    assert len(load_notes(tmp_path / "notes.json")) == 0
    assert list(tmp_path.iterdir()) == []


def test_contacts_survive_restart(tmp_path):
    path = tmp_path / "new_dir" / "contacts.json"
    save_book(make_book(), path)

    restored = load_book(path)
    assert restored.to_dict() == make_book().to_dict()
    assert [p.name for p in path.parent.iterdir()] == ["contacts.json"]


def test_notes_survive_restart(tmp_path):
    path = tmp_path / "notes.json"
    notes = NoteBook()
    notes.add_note("Buy milk").add_tag("home")
    notes.add_note("Call mom")
    notes.delete(2)
    save_notes(notes, path)

    restored = load_notes(path)
    assert restored.to_dict() == notes.to_dict()
    assert restored.add_note("Next").id == 3


def test_save_replaces_old_file(tmp_path):
    path = tmp_path / "contacts.json"
    save_book(make_book(), path)
    save_book(AddressBook(), path)
    assert json.loads(path.read_text(encoding="utf-8")) == {"contacts": []}


# A file that can't be read at all is moved to .bak.
@pytest.mark.parametrize(
    "text",
    ["{not json", "", "[]", '{"notes": []}', '{"contacts": "John"}'],
)
def test_unreadable_contacts_file_goes_to_bak(tmp_path, text):
    path = tmp_path / "contacts.json"
    path.write_text(text, encoding="utf-8")

    assert len(load_book(path)) == 0
    assert not path.exists()
    [backup] = backups(tmp_path)
    assert backup.read_text(encoding="utf-8") == text


# Bad contacts are skipped, good ones are loaded, the original is copied to .bak.
@pytest.mark.parametrize(
    ("bad", "name"),
    [
        ({"phones": []}, "?"),
        ({"name": "Bob", "phones": ["123"]}, "Bob"),
        ({"name": "Bob", "phones": None}, "Bob"),
        ("Bob", "?"),
        ({"name": " Ann "}, " Ann "),
        ({"name": "ann"}, "ann"),
    ],
)
def test_bad_contacts_are_skipped(tmp_path, monkeypatch, bad, name):
    monkeypatch.setattr(storage, "backups", [])
    path = tmp_path / "contacts.json"
    text = json.dumps({"contacts": [{"name": "Ann"}, bad]})
    path.write_text(text, encoding="utf-8")

    assert list(load_book(path)) == ["Ann"]
    [backup] = backups(tmp_path)
    assert backup.read_text(encoding="utf-8") == text
    assert path.read_text(encoding="utf-8") == text
    assert storage.backups == [(backup, [name])]


def test_all_contacts_bad_gives_empty_book_and_keeps_file(tmp_path):
    path = tmp_path / "contacts.json"
    text = json.dumps({"contacts": [{"name": "123"}, {"name": "Bob", "phones": [1]}]})
    path.write_text(text, encoding="utf-8")

    assert len(load_book(path)) == 0
    [backup] = backups(tmp_path)
    assert backup.read_text(encoding="utf-8") == text


# Data saved by an older version can fail newer checks (T34): the valid
# contacts stay, the original file is kept byte for byte, notes are not touched.
@pytest.mark.parametrize(
    "legacy",
    [
        {"name": "Bob", "email": "a..b@c.com"},
        {"name": "123"},
        {"name": "Bob", "birthday": "01.01.1850"},
        {"name": "john"},
    ],
)
def test_legacy_contact_does_not_hide_others(tmp_path, monkeypatch, legacy):
    monkeypatch.setattr(storage, "backups", [])
    contacts = tmp_path / "contacts.json"
    john = {"name": "John", "phones": ["0501234567"], "email": "john@mail.com"}
    original = json.dumps({"contacts": [john, legacy]}).encode()
    contacts.write_bytes(original)
    notes = tmp_path / "notes.json"
    old_notes = NoteBook()
    old_notes.add_note("Buy milk")
    save_notes(old_notes, notes)

    book = load_book(contacts)
    save_notes(load_notes(notes), notes)
    save_book(book, contacts)

    assert list(book) == ["John"]
    assert book.find("John").email.value == "john@mail.com"
    [backup] = backups(tmp_path)
    assert backup.read_bytes() == original
    assert storage.backups == [(backup, [legacy["name"]])]
    assert load_notes(notes).to_dict() == old_notes.to_dict()

    # Next start: only John, no new .bak, the first .bak is unchanged.
    assert list(load_book(contacts)) == ["John"]
    assert backups(tmp_path) == [backup]
    assert backup.read_bytes() == original


def note(**fields):
    return {"id": 1, "text": "Buy milk", "created": "2026-11-18T10:15:00", **fields}


@pytest.mark.parametrize(
    "data",
    [
        "{not json",
        {"contacts": []},
        {"notes": [note(text="")]},
        {"notes": [note(text="   ")]},
        {"notes": [note(text=5)]},
        {"notes": [{"id": 1, "created": "2026-11-18T10:15:00"}]},
        {"notes": [note(id="one")]},
        {"notes": [note(created="yesterday")]},
        {"notes": [note(tags=["two words"])]},
        {"notes": [note(), note(text="Second")]},
        {"next_id": float("inf"), "notes": []},
    ],
)
def test_broken_notes_file_goes_to_bak(tmp_path, data):
    path = tmp_path / "notes.json"
    text = data if isinstance(data, str) else json.dumps(data)
    path.write_text(text, encoding="utf-8")

    assert len(load_notes(path)) == 0
    assert not path.exists()
    [backup] = backups(tmp_path)
    assert backup.read_text(encoding="utf-8") == text


def test_file_with_bom_is_loaded(tmp_path):
    path = tmp_path / "contacts.json"
    path.write_text(json.dumps(make_book().to_dict()), encoding="utf-8-sig")
    assert list(load_book(path)) == ["John"]


def test_crash_during_save_keeps_old_file(tmp_path, monkeypatch):
    path = tmp_path / "contacts.json"
    save_book(make_book(), path)
    old = path.read_text(encoding="utf-8")

    def crash(self, target):
        raise OSError("crash before replace")

    monkeypatch.setattr(Path, "replace", crash)
    with pytest.raises(OSError):
        save_book(AddressBook(), path)
    assert path.read_text(encoding="utf-8") == old


def test_app_saves_after_broken_file_without_losing_it(tmp_path):
    path = tmp_path / "contacts.json"
    path.write_text("{not json", encoding="utf-8")

    save_book(load_book(path), path)

    assert json.loads(path.read_text(encoding="utf-8")) == {"contacts": []}
    assert backups(tmp_path)[0].read_text(encoding="utf-8") == "{not json"


def test_bak_name_has_date_and_time(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "backups", [])
    path = tmp_path / "contacts.json"
    path.write_text("{not json", encoding="utf-8")
    load_book(path)
    [backup] = backups(tmp_path)
    assert backup.name.startswith("contacts.20")
    assert len(backup.name) == len("contacts.YYYYMMDD-HHMMSS.bak")
    assert storage.backups == [(backup, [])]  # cli shows it to the user (T34)


class FrozenTime:
    """datetime replacement: now() is always the same second."""

    @staticmethod
    def now():
        return datetime(2026, 11, 25, 12, 0, 0)


# Two backups in the same second don't overwrite each other, both when the
# file is moved (unreadable) and when it is copied (skipped contacts) (T34).
@pytest.mark.parametrize(
    "first, second",
    [
        (b"{not json\r\n", b"{also not json\n"),
        (b'{"contacts": [{"name": "123"}]}\r\n', b'{"contacts": [{"name": "456"}]}'),
    ],
)
def test_backups_in_same_second_are_all_kept(tmp_path, monkeypatch, first, second):
    monkeypatch.setattr(storage, "datetime", FrozenTime)
    monkeypatch.setattr(storage, "backups", [])
    path = tmp_path / "contacts.json"
    for data in (first, second):
        path.write_bytes(data)
        load_book(path)

    saved = {bak.name: bak.read_bytes() for bak in backups(tmp_path)}
    assert saved == {
        "contacts.20261125-120000.bak": first,
        "contacts.20261125-120000-1.bak": second,
    }
    assert sorted(bak.name for bak, _ in storage.backups) == sorted(saved)


@pytest.mark.parametrize("error", [RuntimeError("bug"), ContactNotFoundError("John")])
def test_programming_errors_are_not_hidden(tmp_path, monkeypatch, error):
    path = tmp_path / "contacts.json"
    save_book(make_book(), path)

    def bug(data):
        raise error

    monkeypatch.setattr(storage.Record, "from_dict", bug)
    with pytest.raises(type(error)):
        load_book(path)
    assert path.exists()
    assert backups(tmp_path) == []


# --- T25: Cyrillic data (Ukrainian users) ---


# Cyrillic name and address come back the same and stay readable in the file.
def test_cyrillic_contact_survives_restart(tmp_path):
    path = tmp_path / "contacts.json"
    record = Record("Іван")
    record.add_phone("0501234567")
    record.set_address("Київ, вул. Хрещатик 1")
    book = AddressBook()
    book.add_record(record)
    save_book(book, path)

    restored = load_book(path)
    assert restored.find("Іван").address.value == "Київ, вул. Хрещатик 1"
    text = path.read_text(encoding="utf-8")
    assert "Іван" in text
    assert "\\u" not in text  # letters, not \u0406 escapes


# Cyrillic note text and tag come back the same, tag search still works.
def test_cyrillic_note_and_tag_survive_restart(tmp_path):
    path = tmp_path / "notes.json"
    notes = NoteBook()
    notes.add_note("Купити молоко").add_tag("Покупки")
    save_notes(notes, path)

    restored = load_notes(path)
    assert restored.find(1).text == "Купити молоко"
    assert restored.find(1).tags == {"покупки"}
    assert [note.id for note in restored.find_by_tag("ПОКУПКИ")] == [1]
    assert "Купити молоко" in path.read_text(encoding="utf-8")
