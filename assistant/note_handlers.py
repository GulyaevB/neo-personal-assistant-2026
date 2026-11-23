"""Note commands (T21).

Every handler takes (args, ctx) and returns a string to show.
On error it raises AssistantError, cli shows it in red.
The note id comes as a string, parse_id() turns it into an int.
Commands are registered with @command (T18); @input_error is below it.
"""

from assistant import ui
from assistant.commands import command
from assistant.context import Context
from assistant.decorators import input_error
from assistant.exceptions import ValidationError


def parse_id(value: str) -> int:
    """Note id from a command argument: "3" -> 3.

    Not a whole number -> ValidationError. Also used by tag_handlers (T22).
    """
    try:
        return int(value)
    except ValueError:
        raise ValidationError(f"Invalid note id '{value}'. Use a number.") from None


def _require(args: list[str], count: int, usage: str) -> None:
    """Not enough arguments -> ValidationError that shows the right format."""
    if len(args) < count:
        raise ValidationError(f"Missing arguments. Use: {usage}")


@command("add-note")
@input_error
def add_note(args: list[str], ctx: Context) -> str:
    """add-note <text...>: create a note."""
    _require(args, 1, "add-note <text>")
    note = ctx.notes.add_note(" ".join(args))
    return f"Note {note.id} added."


@command("edit-note")
@input_error
def edit_note(args: list[str], ctx: Context) -> str:
    """edit-note <id> <text...>: replace the text of a note."""
    _require(args, 2, "edit-note <id> <text>")
    note_id = parse_id(args[0])
    ctx.notes.edit(note_id, " ".join(args[1:]))
    return f"Note {note_id} updated."


@command("delete-note")
@input_error
def delete_note(args: list[str], ctx: Context) -> str:
    """delete-note <id>: delete a note."""
    _require(args, 1, "delete-note <id>")
    note_id = parse_id(args[0])
    # TODO(U4): ask ui.confirm() before deleting
    ctx.notes.delete(note_id)
    return f"Note {note_id} deleted."


@command("all-notes")
@input_error
def show_all_notes(args: list[str], ctx: Context) -> str:
    """all-notes: show all notes."""
    if not ctx.notes:
        return "No notes yet. Add one with: add-note <text>"
    notes = sorted(ctx.notes.values(), key=lambda note: note.id)
    return "\n".join(ui.format_note(note) for note in notes)


@command("search-notes")
@input_error
def search_notes(args: list[str], ctx: Context) -> str:
    """search-notes <query>: find notes by text."""
    _require(args, 1, "search-notes <text>")
    query = " ".join(args)
    found = ctx.notes.search(query)
    if not found:
        return f"No notes found for '{query}'."
    return "\n".join(ui.format_note(note) for note in found)
