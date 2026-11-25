"""Main loop.

Import contact_handlers, note_handlers and tag_handlers here, otherwise
COMMANDS stays empty. Show results with ui.show(), AssistantError with
ui.error(). Save data on exit and on Ctrl+C.

Any other Exception in a command is a bug: the user gets a short message,
the traceback goes to the log file, and the CLI keeps running (T32).

The log has code locations and exception types, but not exception messages
or command arguments, since they may contain names, phones or emails.
Still look through the log before sharing it.
"""

import logging
import traceback
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


class _QuietLogHandler(RotatingFileHandler):
    """Log file handler that never prints its own errors (T32).

    If writing or rotating the file fails, the standard handleError()
    prints a traceback to stderr. Here we only remember the failure, so the
    user is told the truth and the console stays clean.
    """

    failed = False

    def handleError(self, record: logging.LogRecord) -> None:  # noqa: N802
        self.failed = True


def _describe_exception(exc: BaseException) -> str:
    """Traceback frames and exception types, without exception messages.

    Messages are hidden because they may contain personal data
    ("Contact 'John' ..."). Chained exceptions are included the same way.
    """
    parts = []
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        frames = "".join(traceback.format_tb(current.__traceback__))
        parts.append(
            "Traceback (most recent call last):\n"
            f"{frames}{type(current).__name__}: <message hidden>"
        )
        if current.__cause__ is not None:
            current = current.__cause__
        elif not current.__suppress_context__:
            current = current.__context__
        else:
            current = None
    return "\nCaused by:\n".join(parts)


class _HiddenMessageFormatter(logging.Formatter):
    """Formats exceptions with _describe_exception()."""

    def format(self, record: logging.LogRecord) -> str:
        # Another handler may have cached the full exception text on the
        # record (record.exc_text); ignore it and format our own version.
        cached = record.exc_text
        record.exc_text = None
        try:
            return super().format(record)
        finally:
            record.exc_text = cached

    def formatException(self, ei) -> str:  # noqa: N802
        return _describe_exception(ei[1])


def _log_unexpected_error(label: str) -> bool:
    """Write the current exception to LOG_FILE. True only if it was saved.

    The file is opened on the first unexpected error, so a normal run never
    creates it. If it can't be opened or written, nothing is printed and the
    CLI keeps running.
    """
    global _log_handler
    if _log_handler is None:
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            handler: logging.Handler = _QuietLogHandler(
                LOG_FILE, maxBytes=1_000_000, backupCount=1, encoding="utf-8"
            )
            handler.setFormatter(
                _HiddenMessageFormatter("%(asctime)s %(levelname)s %(message)s")
            )
        except OSError:
            handler = logging.NullHandler()
        _log_handler = handler
        logger.addHandler(handler)

    if not isinstance(_log_handler, _QuietLogHandler):
        return False  # the log file could not be opened
    _log_handler.failed = False
    logger.exception("Unexpected error in command %r", label)
    return not _log_handler.failed


def _close_log() -> None:
    """Close the log file on exit, so the next run starts clean."""
    global _log_handler
    if _log_handler is not None:
        logger.removeHandler(_log_handler)
        _log_handler.close()
        _log_handler = None


def unexpected_error_message(command: str, logged: bool = True) -> str:
    """Short text for the user (T32).

    Says where the details are only if they were really saved.
    """
    what = f"running '{command}'" if command else "running this command"
    message = f"Something went wrong while {what}. Please try again."
    if logged:
        message += f" Details were saved to {LOG_FILE}"
    return message


def report_unexpected_error(command: str) -> None:
    """Log the current exception and tell the user (T32).

    `command` is "" when the input could not even be parsed.
    Arguments are never logged: they may contain phones, emails or addresses.
    """
    logged = _log_unexpected_error(command or "<unparsed input>")
    ui.error(unexpected_error_message(command, logged))


def handle_line(command: str, args: list[str], ctx: Context) -> bool:
    """Run one parsed command. Return False when the user wants to exit."""
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
            command = ""  # label for the error message if parsing fails
            try:
                command, args = parse_input(line)
                keep_running = handle_line(command, args, ctx)
            except Exception:
                # Last resort (T32): a bug in one command must not close the
                # app. KeyboardInterrupt and SystemExit are not Exception,
                # so Ctrl+C still exits below and data is still saved.
                # The input is parsed only once, so a failing parser can't
                # raise again here.
                report_unexpected_error(command)
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
