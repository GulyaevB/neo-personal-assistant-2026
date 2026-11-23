"""Input and output.

UX (U1-U4) changes what's inside the functions,
but not the function names and arguments.
"""

import difflib
import re
from collections.abc import Callable, Iterable

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText

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

# Colors (prompt_toolkit style strings).
SUCCESS_STYLE = "ansigreen"
ERROR_STYLE = "ansired"
COMMAND_STYLE = "ansicyan bold"
TAG_STYLE = "ansimagenta"

# Tags at the end of a line: "... [home, work]".
_TAGS_RE = re.compile(r"^(.*?)(\[[^\]]+\])\s*$")

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


def style_success(text: str) -> FormattedText:
    """Green text for success messages."""
    return FormattedText([(SUCCESS_STYLE, text)])


def style_error(text: str) -> FormattedText:
    """Red text for errors."""
    return FormattedText([(ERROR_STYLE, text)])


def _highlight_line(line: str) -> list[tuple[str, str]]:
    """Split one line into styled parts.

    A known command at the start of the line (e.g. in help) is highlighted,
    and tags in square brackets at the end of the line too.
    """
    parts: list[tuple[str, str]] = []
    first = re.match(r"\S+", line)
    if first and first.group().rstrip(":") in _command_names():
        parts.append((COMMAND_STYLE, first.group()))
        line = line[first.end() :]

    tags = _TAGS_RE.match(line)
    if tags:
        parts.append(("", tags.group(1)))
        parts.append((TAG_STYLE, tags.group(2)))
    else:
        parts.append(("", line))
    return [(style, text) for style, text in parts if text]


def highlight(text: str) -> FormattedText:
    """Highlight commands and tags in a multi-line text."""
    parts: list[tuple[str, str]] = []
    for i, line in enumerate(text.split("\n")):
        if i:
            parts.append(("", "\n"))
        parts.extend(_highlight_line(line))
    return FormattedText(parts)


def show(text: str) -> None:
    """Show a command result with commands and tags highlighted (U2)."""
    print_formatted_text(highlight(text))


def success(text: str) -> None:
    """Messages from cli itself, like "Good bye!" (U2: green)."""
    print_formatted_text(style_success(text))


def error(text: str) -> None:
    """Show an error in red (U2)."""
    print_formatted_text(style_error(text))


def confirm(question: str) -> bool:
    """Ask y/n (U4)."""
    return input(f"{question} (y/n): ").strip().lower() == "y"


def suggest(word: str, commands: list[str]) -> list[str]:
    """Commands similar to a mistyped word, best match first (U3).

    "ad" -> ["add"], "phnoe" -> ["phone"], "xyz" -> [].
    """
    word = word.strip().lower()
    if not word:
        return []
    return difflib.get_close_matches(word, commands, n=3, cutoff=0.6)


def unknown_command_message(command: str) -> str:
    """Error text for an unknown command, with a hint if one is close (U3).

    "ad" -> "Unknown command 'ad'. Did you mean: add?"
    """
    message = f"Unknown command '{command}'."
    matches = suggest(command, _command_names())
    if matches:
        message += f" Did you mean: {', '.join(matches)}?"
    return message


def format_contact(record: Record) -> str:
    """Contact as text."""
    return str(record)


def format_note(note: Note) -> str:
    """Note as text; tags in [] at the end are highlighted by show() (U2)."""
    if not note.tags:
        return f"{note.id}: {note.text}"
    tags = ", ".join(sorted(note.tags))
    return f"{note.id}: {note.text} [{tags}]"
