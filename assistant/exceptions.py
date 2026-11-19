"""Our exceptions. cli shows the message to the user, so keep it short."""


class AssistantError(Exception):
    """Base class for our errors."""


class ValidationError(AssistantError):
    """Wrong value: bad phone, phone not found, etc."""


class ContactNotFoundError(AssistantError):
    """No contact with this name."""

    def __init__(self, name: str):
        super().__init__(f"Contact '{name}' not found.")
        self.name = name


class NoteNotFoundError(AssistantError):
    """No note with this id."""

    def __init__(self, note_id: int):
        super().__init__(f"Note with id {note_id} not found.")
        self.note_id = note_id
