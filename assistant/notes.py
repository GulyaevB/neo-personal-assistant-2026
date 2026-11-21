"""Notes and tags."""

from collections import UserDict
from dataclasses import dataclass, field
from datetime import datetime

from assistant.exceptions import NoteNotFoundError, ValidationError


def _clean_text(text: str) -> str:
    """Return the text without surrounding spaces, or raise ValidationError."""
    if not isinstance(text, str) or not text.strip():
        raise ValidationError("Note text can't be empty.")
    return text.strip()


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
        self.text = _clean_text(self.text)
        self.tags = {tag.strip().lower() for tag in self.tags}

    def edit(self, text: str) -> None:
        """Change the text. The old text stays if the new one is empty."""
        self.text = _clean_text(text)

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
        return {
            "id": self.id,
            "text": self.text,
            "tags": sorted(self.tags),
            "created": self.created.isoformat(timespec="seconds"),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        """Opposite of to_dict."""
        return cls(
            id=int(data["id"]),
            text=data["text"],
            tags=set(data.get("tags", [])),
            created=datetime.fromisoformat(data["created"]),
        )


class NoteBook(UserDict):
    """Notes by id: {id: Note}.

    Ids start at 1 and are never reused. next_id is saved to the file too.
    """

    def __init__(self):
        super().__init__()
        self.next_id = 1

    def add_note(self, text: str) -> Note:
        """Create a note with the next id."""
        note = Note(id=self.next_id, text=text)
        self.data[note.id] = note
        self.next_id += 1
        return note

    def find(self, note_id: int) -> Note:
        """Return the note or raise NoteNotFoundError."""
        if note_id not in self.data:
            raise NoteNotFoundError(note_id)
        return self.data[note_id]

    def edit(self, note_id: int, text: str) -> None:
        """Change the text or raise NoteNotFoundError."""
        self.find(note_id).edit(text)

    def delete(self, note_id: int) -> None:
        """Delete the note or raise NoteNotFoundError."""
        self.find(note_id)
        del self.data[note_id]

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
        return {
            "next_id": self.next_id,
            "notes": [note.to_dict() for note in self.data.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NoteBook":
        """Opposite of to_dict.

        next_id is never smaller than the biggest id + 1, so ids are not
        reused even if next_id is missing in the file.
        """
        book = cls()
        for item in data.get("notes", []):
            note = Note.from_dict(item)
            book.data[note.id] = note
        biggest_id = max(book.data, default=0)
        book.next_id = max(int(data.get("next_id", 1)), biggest_id + 1)
        return book
