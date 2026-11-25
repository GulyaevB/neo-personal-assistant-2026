"""Tests for the plain input/output fallback in ui.py (T33).

Without a real terminal (Windows without a console, pipes, captured output)
prompt_toolkit can't be used, so ui falls back to input() and print().
"""

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from assistant import ui

REPO_ROOT = Path(__file__).resolve().parents[1]


class FakeStream:
    """A stream whose isatty() answer we choose."""

    def __init__(self, tty: bool):
        self.tty = tty

    def isatty(self) -> bool:
        return self.tty


class ClosedStream:
    """isatty() on a closed file raises ValueError."""

    def isatty(self) -> bool:
        raise ValueError("I/O operation on closed file")


# --- _is_tty ---


@pytest.mark.parametrize(
    ("stream", "expected"),
    [
        (FakeStream(True), True),
        (FakeStream(False), False),
        (io.StringIO(), False),  # like captured output in tests
        (None, False),  # pythonw on Windows has no stdout
        (object(), False),  # no isatty() at all
        (ClosedStream(), False),
    ],
)
def test_is_tty(stream, expected):
    assert ui._is_tty(stream) is expected


# Interactive only when both input and output are a terminal.
@pytest.mark.parametrize(
    ("stdin_tty", "stdout_tty", "expected"),
    [
        (True, True, True),
        (True, False, False),
        (False, True, False),  # "assistant < commands.txt"
        (False, False, False),
    ],
)
def test_is_interactive(monkeypatch, stdin_tty, stdout_tty, expected):
    monkeypatch.setattr(sys, "stdin", FakeStream(stdin_tty))
    monkeypatch.setattr(sys, "stdout", FakeStream(stdout_tty))
    assert ui._is_interactive() is expected


# --- read_command ---


# No terminal: plain input() with the same prompt, no PromptSession.
def test_read_command_without_terminal_uses_input(monkeypatch):
    monkeypatch.setattr(ui, "_is_interactive", lambda: False)
    monkeypatch.setattr(ui, "_session", None)
    prompts = []

    def fake_input(prompt):
        prompts.append(prompt)
        return "add John 0501234567"

    monkeypatch.setattr("builtins.input", fake_input)

    assert ui.read_command() == "add John 0501234567"
    assert prompts == ["Enter a command: "]
    assert ui._session is None


# Ctrl+D / end of a piped file still ends the CLI the usual way.
def test_read_command_without_terminal_passes_eof(monkeypatch):
    monkeypatch.setattr(ui, "_is_interactive", lambda: False)

    def fake_input(prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)

    with pytest.raises(EOFError):
        ui.read_command()


# Real terminal: PromptSession with Tab completion, created once.
def test_read_command_in_terminal_uses_prompt_session(monkeypatch):
    created = []

    class FakeSession:
        def __init__(self, **kwargs):
            created.append(kwargs)

        def prompt(self, prompt):
            return f"typed after '{prompt}'"

    monkeypatch.setattr(ui, "_is_interactive", lambda: True)
    monkeypatch.setattr(ui, "_session", None)
    monkeypatch.setattr(ui, "PromptSession", FakeSession)

    assert ui.read_command() == "typed after 'Enter a command: '"
    assert ui.read_command() == "typed after 'Enter a command: '"
    assert len(created) == 1
    assert isinstance(created[0]["completer"], ui.AssistantCompleter)


# --- show / success / error ---


@pytest.fixture
def no_terminal(monkeypatch):
    """Output is not a terminal; colored printing must not be used."""
    monkeypatch.setattr(ui, "_is_tty", lambda stream: False)

    def fail(*args, **kwargs):
        raise AssertionError("print_formatted_text must not be called")

    monkeypatch.setattr(ui, "print_formatted_text", fail)


@pytest.mark.parametrize("func", [ui.show, ui.success, ui.error])
def test_output_without_terminal_is_plain_text(no_terminal, capsys, func):
    func("1: Buy milk [home]")
    assert capsys.readouterr().out == "1: Buy milk [home]\n"


def test_multiline_output_without_terminal(no_terminal, capsys):
    ui.show("1: Buy milk\n2: Call Anna")
    assert capsys.readouterr().out == "1: Buy milk\n2: Call Anna\n"


# Real terminal: colors as before (U2).
@pytest.mark.parametrize(
    ("func", "styler"),
    [
        (ui.show, ui.highlight),
        (ui.success, ui.style_success),
        (ui.error, ui.style_error),
    ],
)
def test_output_in_terminal_is_colored(monkeypatch, capsys, func, styler):
    printed = []
    monkeypatch.setattr(ui, "_is_tty", lambda stream: True)
    monkeypatch.setattr(ui, "print_formatted_text", printed.append)

    func("Contact added.")

    assert printed == [styler("Contact added.")]
    assert capsys.readouterr().out == ""


# --- confirm ---
# Plain input() in every mode, so it is the same with and without a console.
# Ctrl+C or the end of piped input must never count as "yes".


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("y", True),
        ("Y", True),
        (" y ", True),
        ("n", False),
        ("", False),
        ("yes", False),
    ],
)
def test_confirm_answers(monkeypatch, answer, expected):
    monkeypatch.setattr("builtins.input", lambda prompt: answer)
    assert ui.confirm("Delete contact 'John'?") is expected


def test_confirm_shows_question_with_hint(monkeypatch):
    prompts = []

    def fake_input(prompt):
        prompts.append(prompt)
        return "n"

    monkeypatch.setattr("builtins.input", fake_input)
    ui.confirm("Delete note 1?")
    assert prompts == ["Delete note 1? (y/n): "]


@pytest.mark.parametrize("exc", [EOFError, KeyboardInterrupt])
def test_confirm_interrupted_means_no(monkeypatch, capsys, exc):
    def fake_input(prompt):
        raise exc

    monkeypatch.setattr("builtins.input", fake_input)
    assert ui.confirm("Delete contact 'John'?") is False
    assert capsys.readouterr().out == "\n"


# --- the whole app without a console ---


def run_cli(tmp_path: Path, user_input: str) -> subprocess.CompletedProcess:
    """Run the real CLI with piped input, like on Windows without a console.

    Doesn't need the package to be installed, and keeps data in tmp_path,
    so the user's real ~/.personal_assistant is not touched.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)
    env["USERPROFILE"] = str(tmp_path)
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(REPO_ROOT), env.get("PYTHONPATH")])
    )
    return subprocess.run(
        [sys.executable, "-m", "assistant"],
        input=user_input,
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=env,
        timeout=20,
        check=False,
    )


def test_cli_runs_with_piped_input(tmp_path):
    result = run_cli(tmp_path, "add-note Buy milk\nall-notes\nxyz\nexit\n")

    assert result.returncode == 0, result.stderr
    assert "Personal Assistant is running" in result.stdout
    assert "Note 1 added." in result.stdout
    assert "1: Buy milk" in result.stdout
    assert "Unknown command 'xyz'." in result.stdout
    assert "Goodbye!" in result.stdout
    assert "\x1b[" not in result.stdout  # no color escape codes in a pipe


# End of piped input without "exit" still exits cleanly and saves the data.
def test_cli_exits_and_saves_on_end_of_input(tmp_path):
    result = run_cli(tmp_path, "add-note Buy milk\n")

    assert result.returncode == 0, result.stderr
    assert "Goodbye!" in result.stdout
    notes_file = tmp_path / ".personal_assistant" / "notes.json"
    assert "Buy milk" in notes_file.read_text(encoding="utf-8")
