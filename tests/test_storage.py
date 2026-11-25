"""Saving and loading contacts and notes (T16)."""

import json
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


@pytest.mark.parametrize(
    "text",
    [
        "{not json",
        "",
        "[]",
        '{"notes": []}',
        '{"contacts": "John"}',
        '{"contacts": [{"phones": []}]}',
        '{"contacts": [{"name": "John", "phones": ["123"]}]}',
        '{"contacts": [{"name": "John", "phones": null}]}',
        '{"contacts": ["John"]}',
        '{"contacts": [{"name": "John"}, {"name": " John "}]}',
        '{"contacts": [{"name": "John"}, {"name": "john"}]}',
    ],
)
def test_broken_contacts_file_goes_to_bak(tmp_path, text):
    path = tmp_path / "contacts.json"
    path.write_text(text, encoding="utf-8")

    assert len(load_book(path)) == 0
    assert not path.exists()
    [backup] = backups(tmp_path)
    assert backup.read_text(encoding="utf-8") == text


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
    assert storage.backups == [backup]  # cli shows it to the user (T34)


@pytest.mark.parametrize("error", [RuntimeError("bug"), ContactNotFoundError("John")])
def test_programming_errors_are_not_hidden(tmp_path, monkeypatch, error):
    path = tmp_path / "contacts.json"
    save_book(make_book(), path)

    def bug(data):
        raise error

    monkeypatch.setattr(storage.AddressBook, "from_dict", bug)
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
