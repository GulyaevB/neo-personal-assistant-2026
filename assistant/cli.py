"""Main loop.

Import contact_handlers, note_handlers and tag_handlers here, otherwise
COMMANDS stays empty. Show results with ui.show(), AssistantError with
ui.error(). Save data on exit and on Ctrl+C.
"""


def parse_input(line: str) -> tuple[str, list[str]]:
    """'ADD John 0501234567' -> ('add', ['John', '0501234567'])."""
    raise NotImplementedError  # TODO(T17)


def main() -> None:
    """Run until exit or close."""
    raise NotImplementedError  # TODO(T17)
