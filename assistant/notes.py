"""Notes and tags."""

from collections import UserDict
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Note:
    """A note.

    Text can't be empty. Tag: one word (letters, digits, _ or -),
    lowercase, no duplicates. Wrong values -> ValidationError.
    """

    id: int
    text: str
    tags: set[str] = field(default_factory=set)
    created: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Check the rules (works for from_dict too)."""
        # TODO(T11): empty text -> ValidationError, tags to lowercase

    def edit(self, text: str) -> None:
        """Change the text."""
        raise NotImplementedError  # TODO(T11)

    def add_tag(self, tag: str) -> None:
        """Add a tag."""
        raise NotImplementedError  # TODO(T13)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag."""
        raise NotImplementedError  # TODO(T13)

    def to_dict(self) -> dict:
        """Convert for JSON:

        {"id": 1, "text": "Buy milk", "tags": ["home", "shopping"],
         "created": "2026-11-18T10:15:00"}

        Tags are sorted, created is in ISO format.
        """
        raise NotImplementedError  # TODO(T11)

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        """Opposite of to_dict."""
        raise NotImplementedError  # TODO(T11)


class NoteBook(UserDict):
    """Notes by id: {id: Note}.

    Ids start at 1 and are never reused. next_id is saved to the file too.
    """

    def __init__(self):
        super().__init__()
        self.next_id = 1

    def add_note(self, text: str) -> Note:
        """Create a note with the next id."""
        raise NotImplementedError  # TODO(T11)

    def find(self, note_id: int) -> Note:
        """Return the note or raise NoteNotFoundError."""
        raise NotImplementedError  # TODO(T11)

    def edit(self, note_id: int, text: str) -> None:
        """Change the text or raise NoteNotFoundError."""
        raise NotImplementedError  # TODO(T11)

    def delete(self, note_id: int) -> None:
        """Delete the note or raise NoteNotFoundError."""
        raise NotImplementedError  # TODO(T11)

    def search(self, query: str) -> list[Note]:
        """Notes that contain `query`, case-insensitive."""
        raise NotImplementedError  # TODO(T12)

    def find_by_tag(self, tag: str) -> list[Note]:
        """Notes with this tag, case-insensitive."""
        raise NotImplementedError  # TODO(T13)

    def sort_by_tags(self) -> list[Note]:
        """Notes sorted by tag A-Z, notes without tags at the end.

        If a note has several tags, use the first one in A-Z order.
        """
        raise NotImplementedError  # TODO(T14)

    def to_dict(self) -> dict:
        """Convert for JSON: {"next_id": 4, "notes": [note, ...]}."""
        raise NotImplementedError  # TODO(T11)

    @classmethod
    def from_dict(cls, data: dict) -> "NoteBook":
        """Opposite of to_dict."""
        raise NotImplementedError  # TODO(T11)
