"""Tag commands (bonus). Same rules as in contact_handlers.py."""

from assistant.context import Context


def add_tag(args: list[str], ctx: Context) -> str:
    """add-tag <id> <tag>: add a tag to a note."""
    raise NotImplementedError  # TODO(T22)


def remove_tag(args: list[str], ctx: Context) -> str:
    """remove-tag <id> <tag>: remove a tag from a note."""
    raise NotImplementedError  # TODO(T22)


def search_tag(args: list[str], ctx: Context) -> str:
    """search-tag <tag>: show notes with this tag."""
    raise NotImplementedError  # TODO(T22)


def sort_notes(args: list[str], ctx: Context) -> str:
    """sort-notes: show notes sorted by tags."""
    raise NotImplementedError  # TODO(T22)
