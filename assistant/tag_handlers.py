"""Tag commands (T22, bonus).

Same rules as in note_handlers.py: every handler takes (args, ctx),
returns a string and raises AssistantError on bad input.
The note id is parsed with parse_id() from note_handlers (T21).
"""

from assistant import ui
from assistant.commands import command
from assistant.context import Context
from assistant.decorators import input_error
from assistant.note_handlers import _require, parse_id


@command("add-tag")
@input_error
def add_tag(args: list[str], ctx: Context) -> str:
    """add-tag <id> <tag>: add a tag to a note."""
    _require(args, 2, "add-tag <id> <tag>")
    note_id = parse_id(args[0])
    tag = args[1]
    ctx.notes.find(note_id).add_tag(tag)
    return f"Tag '{tag.lower()}' added to note {note_id}."


@command("remove-tag")
@input_error
def remove_tag(args: list[str], ctx: Context) -> str:
    """remove-tag <id> <tag>: remove a tag from a note."""
    _require(args, 2, "remove-tag <id> <tag>")
    note_id = parse_id(args[0])
    tag = args[1]
    ctx.notes.find(note_id).remove_tag(tag)
    return f"Tag '{tag.lower()}' removed from note {note_id}."


@command("search-tag")
@input_error
def search_tag(args: list[str], ctx: Context) -> str:
    """search-tag <tag>: show notes with this tag."""
    _require(args, 1, "search-tag <tag>")
    tag = args[0]
    found = ctx.notes.find_by_tag(tag)
    if not found:
        return f"No notes with tag '{tag.lower()}'."
    return "\n".join(ui.format_note(note) for note in found)


@command("sort-notes")
@input_error
def sort_notes(args: list[str], ctx: Context) -> str:
    """sort-notes: show notes sorted by tags."""
    if not ctx.notes:
        return "No notes yet. Add one with: add-note <text>"
    return "\n".join(ui.format_note(note) for note in ctx.notes.sort_by_tags())
