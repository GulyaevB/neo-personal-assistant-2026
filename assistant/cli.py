"""Main loop.

Import contact_handlers, note_handlers and tag_handlers here, otherwise
COMMANDS stays empty. Show results with ui.show(), AssistantError with
ui.error(). Save data on exit and on Ctrl+C.

Any other Exception in a command is a bug: the user gets a short message,
the traceback goes to the log file, and the CLI keeps running (T32).
"""

import logging
from importlib import import_module
from logging.handlers import RotatingFileHandler

from assistant import ui
from assistant.commands import COMMANDS
from assistant.context import Context
from assistant.exceptions import AssistantError
from assistant.storage import (
    DATA_DIR,
    backups,
    load_book,
    load_notes,
    save_book,
    save_notes,
)

LOG_FILE = DATA_DIR / "assistant.log"

# Own logger, not the root one, so tracebacks never reach the console.
logger = logging.getLogger("assistant")
logger.propagate = False
logger.setLevel(logging.ERROR)

# The file handler, created on the first unexpected error.
_log_handler: logging.Handler | None = None


def parse_input(line: str) -> tuple[str, list[str]]:
    """'ADD John 0501234567' -> ('add', ['John', '0501234567'])."""

    parts = line.strip().split()

    if not parts:
        return "", []

    return parts[0].lower(), parts[1:]


def _get_logger() -> logging.Logger:
    """Logger that writes to LOG_FILE, set up on the first unexpected error.

    Set up lazily, so a normal run never creates the log file. If the file
    can't be opened, errors are dropped instead of crashing the CLI.
    """
    global _log_handler
    if _log_handler is None:
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            _log_handler = RotatingFileHandler(
                LOG_FILE, maxBytes=1_000_000, backupCount=1, encoding="utf-8"
            )
            _log_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
        except OSError:
            _log_handler = logging.NullHandler()
        logger.addHandler(_log_handler)
    return logger


def _close_log() -> None:
    """Close the log file on exit, so the next run starts clean."""
    global _log_handler
    if _log_handler is not None:
        logger.removeHandler(_log_handler)
        _log_handler.close()
        _log_handler = None


def unexpected_error_message(command: str) -> str:
    """Short text for the user; the details are in the log file (T32)."""
    return (
        f"Something went wrong while running '{command}'. Please try again. "
        f"Details were saved to {LOG_FILE}"
    )


def report_unexpected_error(command: str) -> None:
    """Log the current exception with its traceback and tell the user (T32).

    Only the command name is logged, not its arguments: they may contain
    phones, emails or addresses.
    """
    _get_logger().exception("Unexpected error in command %r", command)
    ui.error(unexpected_error_message(command))


def handle_line(line: str, ctx: Context) -> bool:
    """Run one input line. Return False when the user wants to exit."""
    command, args = parse_input(line)

    if not command:
        return True

    if command in ("exit", "close"):
        ui.success("Goodbye!")
        return False

    # Find a registered command.
    command_info = COMMANDS.get(command)

    if command_info is None:
        ui.error(ui.unknown_command_message(command))
        return True

    # Execute the handler with its arguments and shared context.
    try:
        result = command_info.handler(args, ctx)
    except AssistantError as exc:
        ui.error(str(exc))
    else:
        if result:
            ui.show(result)
    return True


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
    backups.clear()
    ctx = Context(
        book=load_book(),
        notes=load_notes(),
    )
    for backup in backups:
        ui.error(f"Data file was broken, starting empty. Old data is in: {backup}")

    # Connect U1 autocomplete to the current contact list.
    ui.set_completion_source(lambda: ctx.book.keys())

    ui.show("Personal Assistant is running. Type 'exit' to quit.")

    try:
        while True:
            line = ui.read_command()
            try:
                keep_running = handle_line(line, ctx)
            except Exception:
                # Last resort (T32): a bug in one command must not close the
                # app. KeyboardInterrupt and SystemExit are not Exception,
                # so Ctrl+C still exits below and data is still saved.
                report_unexpected_error(parse_input(line)[0])
                continue
            if not keep_running:
                break

    except (KeyboardInterrupt, EOFError):
        ui.success("Goodbye!")

    finally:
        # Save on any exit; notes are saved even if contacts fail.
        try:
            save_book(ctx.book)
        finally:
            try:
                save_notes(ctx.notes)
            finally:
                _close_log()
