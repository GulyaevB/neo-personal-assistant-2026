"""Decorators for handlers."""

from functools import wraps

from assistant.context import Handler
from assistant.exceptions import ValidationError


def input_error(func: Handler) -> Handler:
    """Not enough arguments (IndexError) -> ValidationError with a hint.

    Other AssistantError go up to cli, it shows them.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            raise ValidationError(
                "Not enough arguments. Type 'help' to see the command format."
            ) from None
        # TODO(T23): same message style everywhere, maybe more error types

    return inner
