"""T32: an unexpected error in a command must not close the CLI.

The user gets a short message, the traceback goes to the log file,
and the next command still works. Expected errors (T23) are unchanged.
"""

import logging
import logging.handlers

import pytest

from assistant import cli
from assistant.address_book import AddressBook
from assistant.commands import CommandInfo
from assistant.decorators import MISSING_ARGUMENTS_MESSAGE, input_error
from assistant.exceptions import ValidationError
from assistant.notes import NoteBook


@pytest.fixture(autouse=True)
def log_file(tmp_path, monkeypatch):
    """Log to tmp_path and start every test without log handlers."""
    path = tmp_path / "assistant.log"
    monkeypatch.setattr(cli, "LOG_FILE", path)
    cli._close_log()
    yield path
    cli._close_log()


class Recorder:
    """What the CLI showed and saved during one run."""

    def __init__(self):
        self.errors: list[str] = []
        self.shown: list[str] = []
        self.goodbyes: list[str] = []
        self.saved: list[str] = []


@pytest.fixture
def run(monkeypatch):
    """Run cli.main() with the given input lines (or exceptions to raise)."""
    rec = Recorder()

    monkeypatch.setattr(cli, "load_book", AddressBook)
    monkeypatch.setattr(cli, "load_notes", NoteBook)
    monkeypatch.setattr(cli, "save_book", lambda book: rec.saved.append("book"))
    monkeypatch.setattr(cli, "save_notes", lambda notes: rec.saved.append("notes"))
    monkeypatch.setattr(cli.ui, "show", rec.shown.append)
    monkeypatch.setattr(cli.ui, "success", rec.goodbyes.append)
    monkeypatch.setattr(cli.ui, "error", rec.errors.append)
    monkeypatch.setattr(cli.ui, "set_completion_source", lambda get_names: None)

    def _run(*lines) -> Recorder:
        inputs = iter(lines)

        def read_command():
            item = next(inputs)
            if isinstance(item, BaseException) or (
                isinstance(item, type) and issubclass(item, BaseException)
            ):
                raise item
            return item

        monkeypatch.setattr(cli.ui, "read_command", read_command)
        cli.main()
        return rec

    _run.rec = rec  # for tests where main() raises
    return _run


def register(monkeypatch, name: str, handler) -> None:
    monkeypatch.setitem(cli.COMMANDS, name, CommandInfo(name, handler, ""))


def broken(args, ctx):
    raise RuntimeError("Developer bug")


def echo(args, ctx):
    return "echo: " + " ".join(args)


# --- unexpected errors ---


# The acceptance test from the card: a RuntimeError is reported safely
# and the next command still runs.
def test_runtime_error_is_reported_and_cli_keeps_running(run, monkeypatch):
    register(monkeypatch, "boom", broken)
    register(monkeypatch, "echo", echo)

    rec = run("boom", "echo hi", "exit")

    assert rec.errors == [cli.unexpected_error_message("boom")]
    assert rec.shown[-1] == "echo: hi"
    assert rec.goodbyes == ["Goodbye!"]
    assert rec.saved == ["book", "notes"]


def test_message_is_short_and_has_no_traceback(run, monkeypatch):
    register(monkeypatch, "boom", broken)

    rec = run("boom", "exit")

    message = rec.errors[0]
    assert "Traceback" not in message
    assert "Developer bug" not in message
    assert "RuntimeError" not in message
    assert "'boom'" in message
    assert str(cli.LOG_FILE) in message


# Different kinds of bugs are all caught, many times in a row.
@pytest.mark.parametrize(
    "error", [KeyError("x"), TypeError("x"), ZeroDivisionError(), AttributeError()]
)
def test_any_exception_is_caught(run, monkeypatch, error):
    def handler(args, ctx):
        raise error

    register(monkeypatch, "boom", handler)

    rec = run("boom", "boom", "exit")

    assert rec.errors == [cli.unexpected_error_message("boom")] * 2
    assert rec.saved == ["book", "notes"]


# An error while showing the result is caught too, not only in the handler.
def test_error_while_showing_result_is_caught(run, monkeypatch):
    register(monkeypatch, "echo", echo)
    shown = []

    def bad_show(text):
        if text.startswith("echo"):
            raise ValueError("cannot show")
        shown.append(text)

    monkeypatch.setattr(cli.ui, "show", bad_show)

    rec = run("echo hi", "exit")

    assert rec.errors == [cli.unexpected_error_message("echo")]
    assert rec.goodbyes == ["Goodbye!"]


# --- the log file ---


def test_traceback_is_written_to_log(run, monkeypatch, log_file):
    register(monkeypatch, "boom", broken)

    run("boom", "exit")

    text = log_file.read_text(encoding="utf-8")
    assert "Unexpected error in command 'boom'" in text
    assert "Traceback" in text
    assert "in broken" in text  # the code location is kept
    assert "RuntimeError: <message hidden>" in text
    assert "RuntimeError: Developer bug" not in text


# Exception messages may contain personal data, so they are not logged,
# also for chained exceptions. Types and code locations stay.
def test_exception_messages_are_not_logged(run, monkeypatch, log_file):
    def leaky(args, ctx):
        try:
            raise KeyError(args[0])
        except KeyError as exc:
            raise ValueError(f"{args[1]} {args[2]}") from exc

    register(monkeypatch, "boom", leaky)

    run("boom John john@example.com 0501234567", "exit")

    text = log_file.read_text(encoding="utf-8")
    assert "ValueError: <message hidden>" in text
    assert "Caused by:" in text
    assert "KeyError: <message hidden>" in text
    assert "in leaky" in text
    for secret in ("John", "john@example.com", "0501234567"):
        assert secret not in text


# Arguments may contain personal data, so only the command name is logged.
def test_arguments_are_not_logged(run, monkeypatch, log_file):
    register(monkeypatch, "boom", broken)

    run("boom John 0501234567", "exit")

    text = log_file.read_text(encoding="utf-8")
    assert "0501234567" not in text
    assert "John" not in text


# The log file is closed on exit, so nothing stays open after main().
def test_log_is_closed_on_exit(run, monkeypatch):
    register(monkeypatch, "boom", broken)

    run("boom", "exit")

    assert cli._log_handler is None
    assert not any(
        isinstance(h, logging.handlers.RotatingFileHandler) for h in cli.logger.handlers
    )


# A normal run never creates the log file.
def test_no_log_file_without_errors(run, monkeypatch, log_file):
    register(monkeypatch, "echo", echo)

    run("echo hi", "exit")

    assert not log_file.exists()


# If the log file can't be opened, the message must not claim it was saved.
def test_log_cannot_be_opened(run, monkeypatch, tmp_path, capsys):
    blocker = tmp_path / "not_a_dir"
    blocker.write_text("file, not a folder")
    monkeypatch.setattr(cli, "LOG_FILE", blocker / "assistant.log")
    register(monkeypatch, "boom", broken)
    register(monkeypatch, "echo", echo)

    rec = run("boom", "echo hi", "exit")

    assert rec.errors == [cli.unexpected_error_message("boom", logged=False)]
    assert "saved" not in rec.errors[0]
    assert str(cli.LOG_FILE) not in rec.errors[0]
    assert rec.shown[-1] == "echo: hi"
    assert rec.saved == ["book", "notes"]
    assert capsys.readouterr().err == ""


class BrokenStream:
    """A log file whose writes fail, like a full disk."""

    def __init__(self, fail_times=None):
        self.fail_times = fail_times  # None = always fail
        self.written = []

    def write(self, text):
        if self.fail_times is None or self.fail_times > 0:
            if self.fail_times:
                self.fail_times -= 1
            raise OSError("disk full")
        self.written.append(text)

    def flush(self):
        pass

    def close(self):
        pass

    def tell(self):
        return 0  # used by the rollover check

    def seek(self, *args):
        return 0


def _fail(*args, **kwargs):
    raise OSError("disk full")


# The file opens, but writing or rotating fails later: no traceback on the
# console, an honest message, and the next command still runs.
@pytest.mark.parametrize("failure", ["write", "rollover check", "rollover"])
def test_log_write_or_rollover_fails(run, monkeypatch, capsys, failure):
    if failure == "write":
        monkeypatch.setattr(cli._QuietLogHandler, "_open", lambda self: BrokenStream())
    elif failure == "rollover check":
        monkeypatch.setattr(cli._QuietLogHandler, "shouldRollover", _fail)
    else:
        monkeypatch.setattr(
            cli._QuietLogHandler, "shouldRollover", lambda self, record: True
        )
        monkeypatch.setattr(cli._QuietLogHandler, "doRollover", _fail)
    register(monkeypatch, "boom", broken)
    register(monkeypatch, "echo", echo)

    rec = run("boom", "echo hi", "exit")

    assert rec.errors == [cli.unexpected_error_message("boom", logged=False)]
    assert rec.shown[-1] == "echo: hi"
    assert rec.saved == ["book", "notes"]
    assert capsys.readouterr().err == ""


# After a failed write the next error is logged normally again.
def test_log_works_again_after_a_failed_write(run, monkeypatch):
    stream = BrokenStream(fail_times=1)
    monkeypatch.setattr(cli._QuietLogHandler, "_open", lambda self: stream)
    register(monkeypatch, "boom", broken)

    rec = run("boom", "boom", "exit")

    assert rec.errors == [
        cli.unexpected_error_message("boom", logged=False),
        cli.unexpected_error_message("boom"),
    ]
    assert "Unexpected error in command 'boom'" in "".join(stream.written)


# --- the parser ---


# A failing parser is called only once: the error is reported with a
# generic label, the next command runs and exit still saves.
def test_parser_failure_is_reported_once(run, monkeypatch, log_file):
    register(monkeypatch, "echo", echo)
    real_parse = cli.parse_input
    calls = []

    def flaky_parse(line):
        calls.append(line)
        if line == "bad input":
            raise ValueError("cannot parse")
        return real_parse(line)

    monkeypatch.setattr(cli, "parse_input", flaky_parse)

    rec = run("bad input", "echo hi", "exit")

    assert rec.errors == [cli.unexpected_error_message("")]
    assert "this command" in rec.errors[0]
    assert calls.count("bad input") == 1
    assert rec.shown[-1] == "echo: hi"
    assert rec.goodbyes == ["Goodbye!"]
    assert rec.saved == ["book", "notes"]
    assert "<unparsed input>" in log_file.read_text(encoding="utf-8")


# --- expected errors (T23) stay as they were ---


def test_assistant_error_keeps_its_own_message(run, monkeypatch, log_file):
    def invalid(args, ctx):
        raise ValidationError("Invalid phone 'abc'. Use 10 digits.")

    register(monkeypatch, "bad", invalid)

    rec = run("bad", "exit")

    assert rec.errors == ["Invalid phone 'abc'. Use 10 digits."]
    assert not log_file.exists()


def test_missing_arguments_message_is_unchanged(run, monkeypatch):
    @input_error
    def needs_name(args, ctx):
        return args[0]

    register(monkeypatch, "need", needs_name)

    rec = run("need", "exit")

    assert rec.errors == [MISSING_ARGUMENTS_MESSAGE]


def test_unknown_command_message_is_unchanged(run):
    rec = run("xyz", "exit")

    assert rec.errors == ["Unknown command 'xyz'."]


# --- lifecycle: exit, Ctrl+C, EOF, saving ---


@pytest.mark.parametrize("last", ["exit", "close", KeyboardInterrupt, EOFError])
def test_lifecycle_after_an_unexpected_error(run, monkeypatch, last):
    register(monkeypatch, "boom", broken)

    rec = run("boom", last)

    assert rec.goodbyes == ["Goodbye!"]
    assert rec.saved == ["book", "notes"]


# Ctrl+C inside a command is not swallowed: the app exits and saves.
def test_keyboard_interrupt_in_command_still_exits(run, monkeypatch):
    def interrupted(args, ctx):
        raise KeyboardInterrupt

    register(monkeypatch, "wait", interrupted)

    rec = run("wait", "never reached")

    assert rec.errors == []
    assert rec.goodbyes == ["Goodbye!"]
    assert rec.saved == ["book", "notes"]


# SystemExit is not Exception, so it is not caught; data is still saved.
def test_system_exit_is_not_swallowed(run, monkeypatch):
    def quit_now(args, ctx):
        raise SystemExit(3)

    register(monkeypatch, "quit-now", quit_now)

    with pytest.raises(SystemExit):
        run("quit-now", "never reached")
    assert run.rec.saved == ["book", "notes"]
