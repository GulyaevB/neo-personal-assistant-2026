# Neo Personal Assistant 2026

A team-built Python command-line application for managing contacts, birthdays, and notes. Developed as the Neoversity **Python Programming: Foundations and Best Practices** final group project.

- **Contacts:** add, update, search, list, and delete contacts; manage phones, email, addresses, and birthdays.
- **Birthdays:** view upcoming birthdays for a configurable number of days.
- **Notes:** add, edit, search, list, and delete notes.
- **CLI usability:** generated `help`, command and contact-name Tab completion, colored messages, and suggestions for mistyped commands.
- **Packaging:** install a Python package and launch with either `assistant` or `python -m assistant`.

> **Development status (24 November 2026):** All commands documented below are implemented on `main`. Disk persistence is **not yet implemented** in `assistant/storage.py` (T16); data created in the CLI is currently kept only in memory and will **not survive restarting the application**. The current delete commands execute **without confirmation** (U4 is pending). CLI tag commands are planned separately under T22 and are not available yet. Do not use this development build for important data.

## Requirements

- Python **3.12 or newer** (the project CI exercises Python 3.12 and 3.15).
- Git, if cloning the repository.
- A terminal (Windows PowerShell / Command Prompt, macOS, or Linux).
- Internet access for the initial installation of Python dependencies.

The package installs `prompt_toolkit` automatically for interactive input and completion. Ruff and pytest are needed only for development and testing.

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/GulyaevB/neo-personal-assistant-2026.git
cd neo-personal-assistant-2026
```

### 2. Create and activate a virtual environment (recommended)

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On Windows Command Prompt:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
```

If your Python executable is not named `python` or `python3`, use the path or launcher appropriate for your environment, ensuring its version is at least 3.12.

### 3. Install the project

```bash
python -m pip install .
```

For editable development installation instead:

```bash
python -m pip install -e .
```

### 4. Start the assistant

Either command works **from any working directory** after installation in the active Python environment:

```bash
assistant
# Alternatively:
python -m assistant
```

The app displays `Personal Assistant is running. Type 'exit' to quit.` Type `help` for the dynamically generated command list. Type `exit` or `close` to end the session. Ctrl+C and EOF also end the interactive loop.

## Command reference

Enter each command at the assistant's prompt, not at your system shell. Angle-bracketed items (for example, `<name>`) mean **required arguments**; square-bracketed items (for example, `[days]`) are **optional**. Do not type the brackets themselves.

### Contact management

| Command | Purpose | Example |
| --- | --- | --- |
| `add <name> <phone>` | Create a contact or add another phone to an existing contact. | `add John 0501234567` |
| `change <name> <old_phone> <new_phone>` | Replace an existing phone number. | `change John 0501234567 0671234567` |
| `remove-phone <name> <phone>` | Remove a phone number. | `remove-phone John 0671234567` |
| `add-email <name> <email>` | Set a contact's email address. | `add-email John john@example.com` |
| `add-address <name> <address...>` | Set an address; the address may contain spaces. | `add-address John 12 Main Street Kyiv` |
| `add-birthday <name> <DD.MM.YYYY>` | Store a birthday using day.month.year. | `add-birthday John 15.05.1990` |
| `phone <name>` | Show all phone numbers for a contact. | `phone John` |
| `show-birthday <name>` | Show one contact's birthday. | `show-birthday John` |
| `all` | List all contacts sorted by name. | `all` |
| `search <query...>` | Find contacts by name, phone, email, or address. | `search john` |
| `birthdays [days]` | Show upcoming birthdays; defaults to seven days. | `birthdays 30` |
| `delete <name>` | Delete a contact. **No confirmation yet.** | `delete John` |

### Notes

| Command | Purpose | Example |
| --- | --- | --- |
| `add-note <text...>` | Create a note; multiword text is preserved. | `add-note Buy milk after work` |
| `edit-note <id> <text...>` | Replace the text of a note. | `edit-note 1 Buy oat milk` |
| `all-notes` | List notes sorted by numeric ID. | `all-notes` |
| `search-notes <query...>` | Search note text, case-insensitively. | `search-notes milk` |
| `delete-note <id>` | Delete a note by ID. **No confirmation yet.** | `delete-note 1` |

Note IDs begin at `1` and increase as notes are added. Use `all-notes` to find the ID of a note before editing or deleting it. IDs are not reused within the current notebook.

### Application commands

| Command | Purpose |
| --- | --- |
| `help` | Display available commands and usage based on registered handler docstrings. |
| `hello` | Display a greeting. |
| `exit` | Exit the CLI. |
| `close` | Exit the CLI (alternative to `exit`). |

### Command input and validation

- **Contact names:** exact lookup commands such as `phone John` use the stored spelling and are currently case-sensitive. `search john` is case-insensitive and tolerates some name typos.
- **Whitespace:** the command parser separates tokens on spaces. Use a single token for `<name>`; commands ending in `<text...>`, `<address...>`, or `<query...>` combine all remaining words. Shell-style quotation marks are not parsed specially.
- **Phone numbers:** exactly **10 ASCII digits**, without country prefix, spaces, plus signs, or dashes; duplicate phones on a record are rejected.
- **Birthdays:** `DD.MM.YYYY` using valid dates no later than today. `birthdays` looks ahead seven calendar days by default (including today); `birthdays 1` looks only at today, and the day-count argument must be a positive integer. Birthdays are shown on their **actual calendar dates** without weekend shifting.
- **Notes:** blank note text is rejected. Note IDs must be numeric and must identify an existing note for edit/delete.
- **Errors:** expected validation and not-found errors display readable messages instead of successful-result text. The broader unexpected-error recovery task is T32 and is not yet merged.

### Tab completion and helpful feedback

Press **Tab** to complete a command name. For contact commands that accept a name as the first argument, Tab can also suggest existing contact names. The assistant highlights recognized commands and colored error/success messages. Unknown command names may produce a `Did you mean ...?` suggestion.

### Planned commands (not yet available)

T22 covers the optional tag CLI workflow: `add-tag`, `remove-tag`, `search-tag`, and `sort-notes`. The underlying `Note` and `NoteBook` model already supports tags, but their interactive handlers are still placeholders. Do not expect these commands to appear in `help` until the T22 PR is merged.

## Example interactive session

The following is a sequence of commands typed **inside** the assistant. Responses and the contents of `all` depend on the current in-memory data:

```text
help
add John 0501234567
add-email John john@example.com
add-address John 12 Main Street Kyiv
add-birthday John 15.05.1990
phone John
search john
birthdays 30
add-note Prepare Neoversity demo
all-notes
search-notes demo
edit-note 1 Prepare final Neoversity demo
all
exit
```

**Data safety:** Until T16 is completed, reopening the assistant starts with empty contacts and notes. Do not rely on this build to retain the example data.

## Data storage and reliability

The storage module defines the intended local data location:

| Planned file | Purpose |
| --- | --- |
| `~/.personal_assistant/contacts.json` | Serialized contacts/address book |
| `~/.personal_assistant/notes.json` | Serialized notes, tags, and next-note ID |

**Current implementation:** `assistant/storage.py` has placeholder `load_book`, `load_notes`, `save_book`, and `save_notes` functions. Loading currently creates empty collections and saving does nothing. The completed T15 and T11 models expose `to_dict()` / `from_dict()` serialization methods, but those methods do not themselves persist information to disk.

**Planned T16 implementation:** create the data directory, save JSON through a temporary file followed by atomic replacement, preserve corrupted input as a `.bak` file, recover safely from missing or invalid files, and validate persistence between application restarts. Update this section and rerun storage acceptance tests when T16 merges.

## Project architecture

The code follows a layered design: **CLI / UI → command handlers → domain models**, with a separate storage layer.

| Layer | Files | Responsibility |
| --- | --- | --- |
| Entry points | `assistant/__main__.py`, `pyproject.toml` | Launch `assistant.cli:main` as a console script or Python module. |
| CLI and presentation | `assistant/cli.py`, `assistant/ui.py` | Read commands, present results/errors, provide completion and styling, manage the session lifecycle. |
| Dispatch and context | `assistant/commands.py`, `assistant/context.py`, `assistant/decorators.py` | Register commands, generate help, provide shared application state, standardize expected input errors. |
| Contact handlers | `assistant/contact_handlers.py` | Convert CLI arguments into contact and birthday model operations. |
| Note handlers | `assistant/note_handlers.py` | Convert CLI arguments into note operations; parse note IDs. |
| Tag handlers (planned) | `assistant/tag_handlers.py` | T22: command-layer integration for tag operations. |
| Domain models | `assistant/fields.py`, `assistant/record.py`, `assistant/address_book.py`, `assistant/notes.py`, `assistant/exceptions.py` | Enforce validation, contact and note business rules, search and serialization. |
| Persistence (in progress) | `assistant/storage.py` | T16: implement JSON I/O and recovery. |
| Verification | `tests/`, `.github/workflows/ci.yml` | pytest regression tests, Ruff lint/format checks, supported Python versions. |

Each command handler accepts `(args: list[str], ctx: Context)` and returns text for the CLI to display, or raises an application-specific error. The `Context` holds the address book (`ctx.book`) and notebook (`ctx.notes`). `@command` registers handlers, `@input_error` normalizes certain argument errors, and `ui` owns text/color formatting.

## Development, testing, and CI

Install the project in editable mode and install development tools:

```bash
python -m pip install -e .
python -m pip install ruff pytest
```

Run the checks from the repository root:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

The GitHub Actions workflow `.github/workflows/ci.yml` runs linting, formatting checks, and pytest on **Python 3.12 and 3.15** for PRs targeting `main` and pushes to `main`. The Python 3.12 job also verifies a regular (non-editable) `python -m pip install .`. Package smoke tests cover both launch commands from a working directory outside the repository.

Tests are under `tests/test_*.py`. Storage-related tests must use pytest's `tmp_path` to avoid modifying a real user's home directory. The full team contribution workflow and Ruff conventions are documented in [CONTRIBUTING.md](CONTRIBUTING.md).

## Team and responsibilities

| Team member | Project responsibility |
| --- | --- |
| **Boris** | Team Lead; repository governance, CLI foundations, error handling, packaging, documentation, final presentation. |
| **Yuliia** | Backend; domain models, validation, address book, serialization and persistent storage. |
| **Oksana** | UX and CLI; interactive handlers, user-facing commands, completion, deletion confirmation and error resilience. |
| **Kate** | Tests & Features; notes/tag models and commands, CI, test coverage and final acceptance testing. |

Work is organized through the [Trello project board](https://trello.com/b/lYqKSQAW/neo-personal-assistant-group) and reviewed in [GitHub Pull Requests](https://github.com/GulyaevB/neo-personal-assistant-2026/pulls). Team conventions require one task per branch/PR, passing CI, and at least one reviewer approval before the Team Lead performs a Squash Merge.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `assistant: command not found` | Activate the environment in which the package was installed; try `python -m assistant`. |
| `No module named assistant` | Run `python -m pip install .` from the cloned repository using the same Python interpreter. |
| Python version error during installation | Verify with `python --version`; use Python 3.12 or newer. |
| `Invalid phone ... Use 10 digits.` | Enter exactly ten ASCII digits without formatting characters. |
| A contact name works in `search` but not `phone` | Exact contact lookups currently require the stored capitalization; use `all` to inspect names. |
| Notes and contacts disappear after restarting | Expected until T16 persistence is implemented and merged. |
| Tag command is reported as unknown | Tag CLI handlers are pending under optional T22; use `help` for available commands. |
| Delete command removes data immediately | Confirmation is still pending under U4; avoid destructive commands until that feature is merged. |

## Delivery

This repository is the shared source for the Neoversity group project. The final submission and mentor handoff are tracked in Trello task T30. Follow the course submission instructions for individual team uploads.
