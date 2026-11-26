"""Tests for the CLI parser and application lifecycle (T17)."""

import json
from pathlib import Path

import pytest

from assistant import cli, storage
from assistant.address_book import AddressBook
from assistant.notes import NoteBook


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ADD John 0501234567", ("add", ["John", "0501234567"])),
        ("EXIT", ("exit", [])),
        ("phone John", ("phone", ["John"])),
        ("  add-note Buy milk  ", ("add-note", ["Buy", "milk"])),
        ("   ", ("", [])),
    ],
)
def test_parse_input(text, expected):
    assert cli.parse_input(text) == expected


@pytest.mark.parametrize("exit_mode", ["exit", "close", "ctrl_c", "ctrl_d"])
def test_main_saves_on_exit(monkeypatch, exit_mode):
    book = AddressBook()
    notes = NoteBook()
    saved = []

    monkeypatch.setattr(cli, "load_book", lambda: book)
    monkeypatch.setattr(cli, "load_notes", lambda: notes)
    monkeypatch.setattr(cli, "save_book", lambda value: saved.append(("book", value)))
    monkeypatch.setattr(cli, "save_notes", lambda value: saved.append(("notes", value)))

    monkeypatch.setattr(cli.ui, "show", lambda message: None)
    monkeypatch.setattr(cli.ui, "success", lambda message: None)
    monkeypatch.setattr(cli.ui, "set_completion_source", lambda source: None)

    def fake_read_command():
        if exit_mode == "ctrl_c":
            raise KeyboardInterrupt
        if exit_mode == "ctrl_d":
            raise EOFError
        return exit_mode

    monkeypatch.setattr(cli.ui, "read_command", fake_read_command)

    cli.main()

    assert saved == [("book", book), ("notes", notes)]


def test_autocomplete_uses_current_contacts(monkeypatch):
    book = AddressBook()
    captured = []

    monkeypatch.setattr(cli, "load_book", lambda: book)
    monkeypatch.setattr(cli, "load_notes", NoteBook)
    monkeypatch.setattr(cli, "save_book", lambda value: None)
    monkeypatch.setattr(cli, "save_notes", lambda value: None)
    monkeypatch.setattr(cli.ui, "show", lambda message: None)
    monkeypatch.setattr(cli.ui, "success", lambda message: None)
    monkeypatch.setattr(cli.ui, "read_command", lambda: "exit")
    monkeypatch.setattr(cli.ui, "set_completion_source", captured.append)

    cli.main()

    assert len(captured) == 1
    assert list(captured[0]()) == []


# Real storage: skipped contacts and a broken notes file are both reported,
# .bak files from an earlier run are not (T34).
def test_main_reports_skipped_contacts_and_broken_file(tmp_path, monkeypatch):
    errors = []
    contacts = tmp_path / "contacts.json"
    notes = tmp_path / "notes.json"
    legacy = [{"name": "John"}, {"name": "Bob", "email": "a..b@c.com"}]
    contacts.write_text(json.dumps({"contacts": legacy}), encoding="utf-8")
    notes.write_text("{not json", encoding="utf-8")

    storage.backups.append((Path("old.bak"), []))
    monkeypatch.setattr(cli, "load_book", lambda: storage.load_book(contacts))
    monkeypatch.setattr(cli, "load_notes", lambda: storage.load_notes(notes))
    monkeypatch.setattr(cli, "save_book", lambda value: None)
    monkeypatch.setattr(cli, "save_notes", lambda value: None)
    monkeypatch.setattr(cli.ui, "show", lambda message: None)
    monkeypatch.setattr(cli.ui, "success", lambda message: None)
    monkeypatch.setattr(cli.ui, "error", errors.append)
    monkeypatch.setattr(cli.ui, "read_command", lambda: "exit")
    monkeypatch.setattr(cli.ui, "set_completion_source", lambda source: None)

    cli.main()

    [contacts_bak] = tmp_path.glob("contacts.*.bak")
    [notes_bak] = tmp_path.glob("notes.*.bak")
    assert errors == [
        f"Contacts not loaded: Bob. Original file copied to: {contacts_bak}",
        f"Data file was broken, starting empty. Old data is in: {notes_bak}",
    ]
