"""Personal Assistant: contacts, birthdays and notes in the command line.

Layers:
    models    fields, record, address_book, notes, exceptions
    storage   storage
    handlers  contact_handlers, note_handlers, tag_handlers
    cli       cli, commands, decorators, ui, context

Models don't print anything. Handlers return a string or raise
AssistantError. Only cli talks to the user, through ui.
"""

__version__ = "0.1.0"
