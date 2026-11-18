"""Note commands. Same rules as in contact_handlers.py.

Note id comes as a string: int(), if it fails ->
ValidationError("Note id must be a number.").
"""

from assistant.context import Context


def add_note(args: list[str], ctx: Context) -> str:
    """add-note <text...>: create a note."""
    raise NotImplementedError  # TODO(T21)


def edit_note(args: list[str], ctx: Context) -> str:
    """edit-note <id> <text...>: replace the text of a note."""
    raise NotImplementedError  # TODO(T21)


def delete_note(args: list[str], ctx: Context) -> str:
    """delete-note <id>: delete a note (asks for confirmation)."""
    raise NotImplementedError  # TODO(T21, U4)


def show_all_notes(args: list[str], ctx: Context) -> str:
    """all-notes: show all notes."""
    raise NotImplementedError  # TODO(T21)


def search_notes(args: list[str], ctx: Context) -> str:
    """search-notes <query>: find notes by text."""
    raise NotImplementedError  # TODO(T21)
