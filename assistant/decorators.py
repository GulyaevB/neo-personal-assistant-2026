"""Consistent handling of expected user input errors in command handlers."""

from functools import wraps

from assistant.context import Handler
from assistant.exceptions import ValidationError

MISSING_ARGUMENTS_MESSAGE = (
    "Not enough arguments. Type 'help' to see the command format."
)


def input_error(func: Handler) -> Handler:
    """Translate missing arguments and preserve application error messages.

    Expected domain errors remain AssistantError subclasses so the CLI
    displays their original messages via ui.error(), rather than ui.show().
    Unexpected programming errors are not swallowed.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            raise ValidationError(MISSING_ARGUMENTS_MESSAGE) from None

    return inner
