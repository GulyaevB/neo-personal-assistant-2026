# Neo Personal Assistant 2026

A team-built Python command-line application for managing contacts, birthdays, notes, and tags. Developed as the Neoversity **Python Programming: Foundations and Best Practices** final group project.

- **Contacts:** add, update, search, list, and delete contacts; manage phones, email, addresses, and birthdays.
- **Birthdays:** view upcoming birthdays for a configurable number of days.
- **Notes and tags:** create, edit, search, list, and delete notes; add/remove tags, find notes by tag, and sort by tags.
- **CLI usability:** generated `help`, case-insensitive contact lookup, command and contact-name Tab completion, colored messages in a terminal, typo suggestions, and plain input/output for redirected sessions.
- **Data and safety:** local JSON persistence, deletion confirmation, backup notifications, and recovery from unexpected command errors.
- **Packaging:** install a Python package and launch with either `assistant` or `python -m assistant`.

> **Development status (25 November 2026):** This guide describes the functionality integrated into `main` at `26c5eb5`, including contacts, birthdays, notes, tags, JSON persistence, case-insensitive exact lookup, deletion confirmation, and CLI error recovery. The remaining stricter email validation and legacy-data recovery decision ([PR #34](https://github.com/GulyaevB/neo-personal-assistant-2026/pull/34)) are still under review. Data is saved on exit, not after each command. This is a student project, not a production backup system.

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

The current command registry contains **25 commands**: 12 contact/birthday commands, 5 note commands, 4 tag commands, and 4 application commands. Enter each command at the assistant's prompt, not at your system shell. Angle-bracketed items (for example, `<name>`) mean **required arguments**; square-bracketed items (for example, `[days]`) are **optional**. Do not type the brackets themselves.

### Contact management

| Command | Purpose | Example |
| --- | --- | --- |
| `add <name> <phone>` | Create a contact or add another phone to an existing contact (case-insensitive name). | `add John 0501234567` |
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
| `delete <name>` | Delete a contact after confirmation. | `delete John` |

### Notes

| Command | Purpose | Example |
| --- | --- | --- |
| `add-note <text...>` | Create a note; multiword text is preserved. | `add-note Buy milk after work` |
| `edit-note <id> <text...>` | Replace the text of a note. | `edit-note 1 Buy oat milk` |
| `all-notes` | List notes sorted by numeric ID. | `all-notes` |
| `search-notes <query...>` | Search note text, case-insensitively. | `search-notes milk` |
| `delete-note <id>` | Delete a note by ID after confirmation. | `delete-note 1` |

Note IDs begin at `1` and increase as notes are added. Use `all-notes` to find the ID of a note before editing or deleting it. IDs are not reused within the current notebook.

### Tags

| Command | Purpose | Example |
| --- | --- | --- |
| `add-tag <id> <tag>` | Add a tag to an existing note. | `add-tag 1 study` |
| `remove-tag <id> <tag>` | Remove an existing tag from a note. | `remove-tag 1 study` |
| `search-tag <tag>` | Find notes with the exact tag, ignoring case. | `search-tag STUDY` |
| `sort-notes` | List notes by their alphabetically first tag; untagged notes last, ties by note ID. | `sort-notes` |

Tags are one word: Unicode letters, digits, underscores, or hyphens. They are normalized to lowercase; duplicate tags and removal of absent tags raise validation errors. `search-notes` searches note text, not tags; use `search-tag` for exact tag matching.

### Application commands

| Command | Purpose |
| --- | --- |
| `help` | Display available commands and usage based on registered handler docstrings. |
| `hello` | Display a greeting. |
| `exit` | Exit the CLI. |
| `close` | Exit the CLI (alternative to `exit`). |

### Command input and validation

- **Contact names:** use a non-empty name containing at least one Unicode letter. A single letter is valid; digits-only and punctuation-only names are invalid. Exact lookup and mutations ignore case while retaining the original stored spelling. `add John 0501234567` followed by `add john 0631234567` produces one contact named `John` with two phones. `phone JOHN` finds that record. A genuinely different name, such as `Jon`, remains a separate contact. `search` is case-insensitive and may match similar names, but mutations never use fuzzy matching.
- **Whitespace:** the command parser separates tokens on spaces. Use a single token for `<name>`; commands ending in `<text...>`, `<address...>`, or `<query...>` combine all remaining words. Shell-style quotation marks are not parsed specially.
- **Phone numbers:** exactly **10 ASCII digits**, without country prefix, spaces, plus signs, or dashes; duplicate phones on a record are rejected.
- **Birthdays:** `DD.MM.YYYY` using valid dates from 1900 through today (inclusive). `birthdays` looks ahead seven calendar days by default (including today); `birthdays 1` looks only at today, and the day-count argument must be a positive integer. Birthdays are shown on their calendar dates without weekend shifting; a 29 February birthday is observed on 28 February in non-leap years.
- **Notes:** blank note text is rejected. Note IDs must be numeric and must identify an existing note for edit/delete. IDs are persisted across restarts.
- **Email validation:** `add-email` checks basic syntax (for example, `john@example.com`); it does not verify mailbox existence or deliverability. The current validator still accepts some malformed local parts such as `a..b@c.com`. Stricter dot validation and legacy-data handling remain pending in PR #34.
- **Addresses:** a non-blank address may contain multiple words.
- **Errors:** expected validation and not-found errors display readable messages. Unexpected exceptions during parsing or command execution are reported without a console traceback, and the CLI continues. Diagnostics are written when possible (see [Diagnostic logging](#diagnostic-logging)).

### Tab completion and helpful feedback

Press **Tab** to complete a command name. For contact commands that accept a name as the first argument, Tab can also suggest existing contact names. The assistant highlights recognized commands and colored error/success messages. Unknown command names may produce a `Did you mean ...?` suggestion.

### Terminal compatibility

Interactive input (Tab completion and history) requires both stdin and stdout to be terminals. Otherwise, the CLI uses plain `input()`; redirected stdout is plain text without color escape codes. When stdout remains a terminal, output may still be styled even if stdin is redirected. This supports Windows and non-interactive environments without requiring a console for piped input/output.

### Deletion confirmation

`delete <name>` and `delete-note <id>` check that the target exists, then ask for confirmation. Only `y` (case-insensitive, surrounding whitespace ignored) confirms. Empty input, `n`, `yes`, any other response, Ctrl+C, or EOF cancels deletion. Contact prompts use the stored name, for example `Delete contact 'John'? (y/n):` even if you typed `delete john`. Removing a phone or tag is not subject to this contact/note deletion confirmation.

## Example interactive session

The following commands are typed **inside** the assistant. Use a fresh test profile or a backed-up test data directory, not real personal records. For this example, assume an empty address book and notebook; if you already have data, choose unique names and use the note ID actually returned by `add-note`.

```text
help
add John 0501234567
add john 0631234567
add-email John john@example.com
add-address John 12 Main Street Kyiv
add-birthday John 15.05.1990
phone JOHN
search john
birthdays 30
add-note Prepare Neoversity demo
all-notes
search-notes demo
edit-note 1 Prepare final Neoversity demo
add-tag 1 Study
search-tag study
sort-notes
remove-tag 1 study
add-tag 1 demo
delete john
n
delete-note 1
n
all
exit
```

**Expected results:** `phone JOHN` shows `John: 0501234567; 0631234567`, with one contact named `John`. Both deletion requests are cancelled by `n`. After `exit`, launch the assistant again and enter `phone john`, `all-notes`, and `search-tag demo` to verify both phones, the note, and its tag were restored. Data is written on exit, not immediately after each command.

## Data storage and reliability

The application stores data in a per-user directory under the home folder:

| File | Contents |
| --- | --- |
| `~/.personal_assistant/contacts.json` | Serialized contacts, including phones, email, address, and birthdays |
| `~/.personal_assistant/notes.json` | Serialized notes, tags, timestamps, and next-note ID |
| `~/.personal_assistant/assistant.log` | Diagnostic log, created only when an unexpected command error is successfully logged |

On Windows, `~` represents the current user's home directory (for example, `C:\Users\<username>`); the exact directory is resolved by Python's `Path.home()`.

### Saving and restoring

- **On startup:** `assistant.cli.main()` calls `load_book()` and `load_notes()`. If a file does not exist, the relevant collection starts empty.
- **On exit:** `exit`, `close`, Ctrl+C, and EOF cause the CLI to save the current address book and notebook. Notes are still attempted if saving contacts fails.
- **Atomic replacement:** `save_book()` and `save_notes()` create `~/.personal_assistant` if necessary, write UTF-8 JSON to a temporary `*.json.tmp` file, then replace the destination with `Path.replace()`. This protects the previous complete file from being partially overwritten if saving fails before replacement.
- **Non-ASCII text:** JSON is written with `ensure_ascii=False` and supports Unicode names and note text. Loading also accepts UTF-8 files with a byte-order mark (`utf-8-sig`).
- **Note IDs:** the next available note ID is stored in `notes.json`, so previously assigned IDs are not reused after restarting.

### Handling invalid saved files

If a JSON file is malformed or cannot be restored under the current schema or validation rules, the application moves the **entire original file** to a timestamped backup (for example, `contacts.20261125-191500.bak`) and initializes that collection as empty. Startup prints a warning containing the backup path:

```text
Data file was broken, starting empty. Old data is in: <backup path>
```

The other collection can still load normally. Previously accepted data can also fail validation after an upgrade: for example, contacts named both `John` and `john`, names containing no letters, or birthdays before 1900. Even otherwise valid contacts in the same file are unavailable until recovery. An empty working JSON file may be written on exit. The application does not automatically migrate or repair records.

**Manual recovery:**

1. Note the backup path and exit the application before editing its files.
2. Copy the timestamped `.bak` to a separate safe location. Also preserve any current working JSON, which may contain newly entered data.
3. Inspect a copy of the backup and correct or reconcile records deliberately. For case-variant duplicates, review both contacts and retain all intended information; never guess which email or phone is correct. Keep the original backup intact.
4. With the assistant stopped, place the corrected JSON at the corresponding `contacts.json` or `notes.json` path only after preserving the current file. If needed, reconcile new and old records manually rather than overwriting new data.
5. Restart, inspect the restored records, exit normally, and restart again to verify persistence. If validation still fails, preserve the new backup and review the data again.

Only expected JSON/schema/validation errors trigger this backup path; unrelated programming and filesystem errors are not silently ignored. Do not rely on automatic recovery or use the same data directory for concurrent sessions. The final email-related legacy-data policy is still pending PR #34.

**Limitations:** Changes made during a session are not saved until the session exits. An abrupt process termination can lose changes from that session; this mechanism is not a substitute for regular backups.

### Diagnostic logging

Unexpected exceptions during command parsing or handling are reported with a short retry message; the command loop continues. If logging succeeds, the message identifies `~/.personal_assistant/assistant.log`. A file is opened on the first unexpected error, with rotation at approximately 1 MB (1,000,000 bytes) and one rotated backup (`assistant.log.1`). If the log cannot be written, the CLI does not claim that details were saved. Expected validation errors do not create this diagnostic log.

Logs include command labels, exception types, and traceback frames but omit command arguments and exception messages, including chained exception messages. They may still contain local paths or source locations; review and redact before sharing. Error recovery is not a transaction rollback and does not guarantee recovery from startup, I/O, or process failures.

## Project architecture

The code follows a layered design: **CLI / UI → command handlers → domain models**, with a separate storage layer.

| Layer | Files | Responsibility |
| --- | --- | --- |
| Entry points | `assistant/__main__.py`, `pyproject.toml` | Launch `assistant.cli:main` as a console script or Python module. |
| CLI and presentation | `assistant/cli.py`, `assistant/ui.py` | Read commands, present results/errors, provide interactive or plain I/O, confirm deletion, manage the session lifecycle, and report unexpected errors. |
| Dispatch and context | `assistant/commands.py`, `assistant/context.py`, `assistant/decorators.py` | Register commands, generate help, provide shared application state, standardize expected input errors. |
| Contact handlers | `assistant/contact_handlers.py` | Convert CLI arguments into contact and birthday model operations. |
| Note handlers | `assistant/note_handlers.py` | Convert CLI arguments into note operations; parse note IDs. |
| Tag handlers | `assistant/tag_handlers.py` | Add/remove tags, find notes by tag, and sort notes by tags. |
| Domain models | `assistant/fields.py`, `assistant/record.py`, `assistant/address_book.py`, `assistant/notes.py`, `assistant/exceptions.py` | Enforce validation, contact and note business rules, search and serialization. |
| Persistence | `assistant/storage.py` | Load/save local JSON, use atomic replacement, and preserve invalid data in timestamped `.bak` files with startup notification. |
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

The GitHub Actions workflow `.github/workflows/ci.yml` runs linting, formatting checks, and pytest on **Python 3.12 and 3.15** for PRs targeting `main` and pushes to `main`. The Python 3.12 job also verifies a regular (non-editable) `python -m pip install .`. Package smoke tests cover both launch commands from a working directory outside the repository. **Current CI runs on Ubuntu, not Windows.** T33 adds plain-I/O fallback for non-terminal sessions, but green Linux CI is not evidence of a fresh Windows run; verify Windows console and redirected I/O separately during release acceptance.

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
| A contact name works in `search` but not `phone` | Exact lookups ignore case but do not use fuzzy matching; use `all` to inspect the stored name. |
| Notes or contacts appear missing after restarting | Verify that you exited normally and are using the same OS user account; check `~/.personal_assistant/contacts.json`, `notes.json`, and any timestamped `.bak` files. If a backup warning appeared, preserve the backup and follow the manual recovery steps above; the entire affected collection starts empty. |
| Tag command is reported as unknown | Check `help` for `add-tag`, `remove-tag`, `search-tag`, and `sort-notes`; reinstall from the current version if necessary. |
| Deletion cancelled | Only `y` confirms contact/note deletion; any other input cancels. |
| Tab completion or colors are unavailable with redirected I/O | This is expected: use a real terminal for interactive completion and history; redirected stdout is plain text. |
| Unexpected command error | Retry; if a log path is shown, review `assistant.log` before sharing. Keep a copy of your data before troubleshooting. |

## Delivery

This repository is the shared source for the Neoversity group project. The final submission and mentor handoff are tracked in Trello task T30. Follow the course submission instructions for individual team uploads.
