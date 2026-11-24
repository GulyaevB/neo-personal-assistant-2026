"""Main loop.

Import contact_handlers, note_handlers and tag_handlers here, otherwise
COMMANDS stays empty. Show results with ui.show(), AssistantError with
ui.error(). Save data on exit and on Ctrl+C.
"""

from importlib import import_module

from assistant import ui
from assistant.commands import COMMANDS
from assistant.context import Context
from assistant.exceptions import AssistantError
from assistant.storage import load_book, load_notes, save_book, save_notes


def parse_input(line: str) -> tuple[str, list[str]]:
    """'ADD John 0501234567' -> ('add', ['John', '0501234567'])."""

    parts = line.strip().split()

    if not parts:
        return "", []

    return parts[0].lower(), parts[1:]


def main() -> None:
    """Run until exit or close."""

    # Import handler modules to register commands when T18 is ready.
    for module in (
        "contact_handlers",
        "note_handlers",
        "tag_handlers",
    ):
        import_module(f"assistant.{module}")

    # Load application data.
    ctx = Context(
        book=load_book(),
        notes=load_notes(),
    )

    # Connect U1 autocomplete to the current contact list.
    ui.set_completion_source(lambda: ctx.book.keys())

    ui.show("Personal Assistant is running. Type 'exit' to quit.")

    try:
        while True:
            command, args = parse_input(ui.read_command())

            if not command:
                continue

            if command in ("exit", "close"):
                ui.success("Goodbye!")
                break

            # Find a registered command.
            command_info = COMMANDS.get(command)

            if command_info is None:
                ui.error(ui.unknown_command_message(command))
                continue

            # Execute the handler with its arguments and shared context.
            try:
                result = command_info.handler(args, ctx)
            except AssistantError as exc:
                ui.error(str(exc))
            else:
                if result:
                    ui.show(result)

    except (KeyboardInterrupt, EOFError):
        ui.success("Goodbye!")

    finally:
        # Save on any exit; notes are saved even if contacts fail.
        try:
            save_book(ctx.book)
        finally:
            save_notes(ctx.notes)
