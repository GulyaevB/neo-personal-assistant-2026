"""Main loop.

Import contact_handlers, note_handlers and tag_handlers here, otherwise
COMMANDS stays empty. Show results with ui.show(), AssistantError with
ui.error(). Save data on exit and on Ctrl+C.
"""

from importlib import import_module

from assistant import ui
from assistant.commands import COMMANDS, get_help
from assistant.context import Context
from assistant.exceptions import AssistantError
from assistant.storage import load_book, load_notes, save_book, save_notes


def parse_input(line: str) -> tuple[str, list[str]]:
    """'ADD John 0501234567' -> ('add', ['John', '0501234567'])."""
    words = line.split()
    if not words:
        return "", []
    return words[0].lower(), words[1:]


def main() -> None:
    """Run until exit or close."""
    for module in ("contact_handlers", "note_handlers", "tag_handlers"):
        import_module(f"assistant.{module}")

    ctx = Context(book=load_book(), notes=load_notes())
    ui.set_completion_source(lambda: ctx.book.keys())
    try:
        ui.show("Welcome to the assistant bot!")
        while True:
            try:
                command, args = parse_input(ui.read_command())
                if not command:
                    continue
                if command in {"exit", "close"}:
                    break
                if command == "hello":
                    ui.show("How can I help you?")
                elif command == "help":
                    ui.show(get_help())
                elif command in COMMANDS:
                    ui.show(COMMANDS[command].handler(args, ctx))
                else:
                    ui.error(f"Unknown command '{command}'. Type 'help' for commands.")
            except AssistantError as exc:
                ui.error(str(exc))
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        save_book(ctx.book)
        save_notes(ctx.notes)
    ui.success("Good bye!")
