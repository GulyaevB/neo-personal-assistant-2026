"""Input and output.

UX (U1-U4) changes what's inside the functions,
but not the function names and arguments.
"""

from collections.abc import Callable, Iterable

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

from assistant.commands import COMMANDS
from assistant.notes import Note
from assistant.record import Record

# Used while COMMANDS is still empty (T18 not merged yet).
# TODO(U1): remove after T18, then commands come only from COMMANDS.
FALLBACK_COMMANDS = (
    "add", "change", "remove-phone", "add-email", "add-address",
    "add-birthday", "phone", "show-birthday", "all", "search", "delete",
    "birthdays", "add-note", "edit-note", "delete-note", "all-notes",
    "search-notes", "add-tag", "remove-tag", "search-tag", "sort-notes",
    "help", "hello", "exit", "close",
)  # fmt: skip

# Commands whose first argument is a contact name.
NAME_COMMANDS = frozenset(
    {
        "add",
        "change",
        "remove-phone",
        "add-email",
        "add-address",
        "add-birthday",
        "phone",
        "show-birthday",
        "delete",
    }
)


def _no_names() -> Iterable[str]:
    """Default source of contact names: nothing to suggest."""
    return ()


_get_names: Callable[[], Iterable[str]] = _no_names
_session: PromptSession | None = None


def set_completion_source(get_names: Callable[[], Iterable[str]]) -> None:
    """Tell ui where to take contact names for Tab completion.

    cli calls it once after loading the book:
    ui.set_completion_source(lambda: ctx.book.keys())
    """
    global _get_names
    _get_names = get_names


def _command_names() -> list[str]:
    """Names of all commands, sorted."""
    names = COMMANDS.keys() if COMMANDS else FALLBACK_COMMANDS
    return sorted(names)


def _word_index(text: str) -> int:
    """Index of the word under the cursor: 0 = command, 1 = first argument.

    "bi" -> 0, "phone " -> 1, "phone jo" -> 1, "add John " -> 2.
    """
    words = text.split()
    if not words or text[-1].isspace():
        return len(words)
    return len(words) - 1


class AssistantCompleter(Completer):
    """Tab completion: commands for the 1st word, contact names for the 2nd."""

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """Yield suggestions for the word before the cursor."""
        text = document.text_before_cursor
        word = document.get_word_before_cursor(WORD=True)
        index = _word_index(text)

        if index == 0:
            candidates = _command_names()
        elif index == 1 and text.split()[0].lower() in NAME_COMMANDS:
            candidates = sorted(_get_names())
        else:
            return

        prefix = word.lower()
        for candidate in candidates:
            if candidate.lower().startswith(prefix):
                yield Completion(candidate, start_position=-len(word))


def read_command(prompt: str = "Enter a command: ") -> str:
    """Read a command with Tab completion (U1).

    Ctrl+C -> KeyboardInterrupt, Ctrl+D -> EOFError, same as input().
    cli handles them, so they are not caught here.
    """
    global _session
    if _session is None:
        _session = PromptSession(
            completer=AssistantCompleter(), complete_while_typing=False
        )
    return _session.prompt(prompt)


def show(text: str) -> None:
    """Show a command result (U2: highlight commands and tags)."""
    print(text)


def success(text: str) -> None:
    """Messages from cli itself, like "Goodbye!" (U2: green)."""
    print(text)


def error(text: str) -> None:
    """Show an error (U2: red)."""
    print(text)


def confirm(question: str) -> bool:
    """Ask y/n (U4)."""
    return input(f"{question} (y/n): ").strip().lower() == "y"


def suggest(word: str, commands: list[str]) -> list[str]:
    """Similar commands for a typo (U3: difflib)."""
    return []


def format_contact(record: Record) -> str:
    """Contact as text."""
    return str(record)


def format_note(note: Note) -> str:
    """Note as text (U2: highlight tags)."""
    tags = ", ".join(sorted(note.tags))
    return f"{note.id}: {note.text} [{tags}]"
