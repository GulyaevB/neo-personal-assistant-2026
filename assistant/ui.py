"""Input and output.

For now it's just input/print. UX (U1-U4) will change what's inside,
but not the function names and arguments.
"""

from assistant.notes import Note
from assistant.record import Record


def read_command(prompt: str = "Enter a command: ") -> str:
    """Read a command (U1: Tab autocomplete)."""
    return input(prompt)


def show(text: str) -> None:
    """Show a command result (U2: highlight commands and tags)."""
    print(text)


def success(text: str) -> None:
    """Messages from cli itself, like "Good bye!" (U2: green)."""
    print(text)


def error(text: str) -> None:
    """Show an error (U2: red)."""
    print(text)


def confirm(question: str) -> bool:
    """Ask y/n (U4)."""
    return input(f"{question} (y/n): ").strip().lower() == "y"


def suggest(word: str, commands: list[str]) -> list[str]:
    """Similar commands for a typo (U3: difflib)."""
    return []


def format_contact(record: Record) -> str:
    """Contact as text."""
    return str(record)


def format_note(note: Note) -> str:
    """Note as text (U2: highlight tags)."""
    tags = ", ".join(sorted(note.tags))
    return f"{note.id}: {note.text} [{tags}]"
