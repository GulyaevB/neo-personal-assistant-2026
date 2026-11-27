# Neo Personal Assistant 2026

A team-built Python command-line application for managing contacts, birthdays, notes, and tags. Developed as the Neoversity **Python Programming: Foundations and Best Practices** final group project.

- **Contacts:** add, update, search, list, and delete contacts; manage phones, email, addresses, and birthdays.
- **Birthdays:** view upcoming birthdays for a configurable number of days.
- **Notes and tags:** create, edit, search, list, and delete notes; add/remove tags, find notes by tag, and sort by tags.
- **CLI usability:** generated `help`, case-insensitive contact lookup, command and contact-name Tab completion, colored messages in a terminal, typo suggestions, and plain input/output for redirected sessions.
- **Data and safety:** local JSON persistence, deletion confirmation, backup notifications, and recovery from unexpected command errors.
- **Packaging:** install a Python package and launch with either `assistant` or `python -m assistant`.

> **Development status (26 November 2026):** This guide describes the integrated application at `246e183`, including strict email validation and unified contact recovery ([PR #34](https://github.com/GulyaevB/neo-personal-assistant-2026/pull/34)). Feature development is complete for the planned release; final acceptance on macOS and Windows is in progress. Data is saved on exit, not after each command. This is a student project, not a production backup system.

## Requirements

- Python **3.12 or newer** (the project CI exercises Python 3.12 and 3.15).
- Git, if cloning the repository.
- A terminal (Windows PowerShell / Command Prompt, macOS, or Linux).
- Internet access for the initial installation of Python dependencies.

### Libraries

| Type | Libraries and purpose |
| --- | --- |
| Runtime dependency | `prompt_toolkit>=3.0` — interactive input, completion and terminal formatting; installed automatically. |
| Python standard library | `json`, `pathlib`, `shutil` — persistence and backups; `datetime` — dates and timestamps; `re` — validation; `difflib` — fuzzy matching and suggestions; `collections.UserDict`, `collections.abc`, `dataclasses` — models and interfaces; `logging`, `traceback` — diagnostics; `sys`, `inspect`, `importlib` — terminal behavior and command registration. No separate installation required. |
| Development and testing | `ruff` — linting and formatting; `pytest` — automated tests. Install these only for development/testing. |
| Build tooling | `setuptools>=68` — package build backend, managed by pip during installation. |

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/GulyaevB/neo-personal-assistant-2026.git
cd neo-personal-assistant-2026
```

### 2. Create and activate a virtual environment (recommended)

On macOS or Linux (check `python3 --version` is 3.12+ first):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell (confirm the version reported by `py -3 --version` is 3.12 or newer before creating the environment):

```powershell
py -3 --version
py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process RemoteSigned
.\.venv\Scripts\Activate.ps1
```

`Set-ExecutionPolicy -Scope Process` allows the activation script only in the current PowerShell window (answer `Y` if PowerShell asks to confirm); run it again in each new window before activating.

On Windows Command Prompt (perform the same version check):

```bat
py -3 --version
py -3 -m venv .venv
.venv\Scripts\activate.bat
```

The Windows `py -3` launcher selects an installed Python 3 runtime, so a separate Python 3.12 installation is not required when a compatible newer version is available. If the reported version is below 3.12, select an installed compatible version explicitly (for example, `py -3.13`) or install Python 3.12 or newer before continuing. If `py` is unavailable, use a verified `python --version` (3.12+) followed by `python -m venv .venv`. After activation, check `python --version` again to confirm the environment uses a compatible interpreter.

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
- **Email validation:** `add-email` validates a supported subset of email syntax, not mailbox existence or deliverability. Before `@`, Unicode word characters (letters, digits, underscore), `+`, `-`, and single dots between non-dot groups are supported. Domain labels use word characters and hyphens, separated by dots, ending in at least two ASCII letters. For example, `first.last+tag@example.com` is accepted; `a..b@c.com`, `.a@c.com`, `a.@c.com`, and `a@b..com` are rejected. A rejected update leaves the existing email unchanged. This is not a full RFC email validator.
- **Addresses:** a non-blank address may contain multiple words.
- **Errors:** expected validation and not-found errors display readable messages. Unexpected exceptions during parsing or command execution are reported without a console traceback, and the CLI continues. Diagnostics are written when possible (see [Diagnostic logging](#diagnostic-logging)).

### Tab completion and helpful feedback

Press **Tab** to complete a command name. For contact commands that accept a name as the first argument, Tab can also suggest existing contact names. The assistant highlights recognized commands and colored error/success messages. Unknown command names may produce a `Did you mean ...?` suggestion.

### Terminal compatibility

Interactive input (Tab completion and history) requires both stdin and stdout to be terminals. Otherwise, the CLI uses plain `input()`; redirected stdout is plain text without color escape codes. When stdout remains a terminal, output may still be styled even if stdin is redirected. This supports Windows and non-interactive environments without requiring a console for piped input/output.

### Deletion confirmation

`delete <name>` and `delete-note <id>` check that the target exists, then ask for confirmation. Only `y` (case-insensitive, surrounding whitespace ignored) confirms. Empty input, `n`, `yes`, any other response, Ctrl+C, or EOF cancels deletion. Contact prompts use the stored name, for example `Delete contact 'John'? (y/n):` even if you typed `delete john`. Removing a phone or tag is not subject to this contact/note deletion confirmation.

## Example interactive session

The following commands are typed **inside** the assistant. First use an isolated test profile (see [Cross-platform release testing](#cross-platform-release-testing)), not real personal records. For this example, assume an empty address book and notebook; if you already have data, choose unique names and use the note ID actually returned by `add-note`.

```text
help
add John 0501234567
add john 0631234567
add-email John john@example.com
add-email John a..b@c.com
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

**Expected results:** the second email command is rejected and `all` still shows `john@example.com`. `phone JOHN` shows `John: 0501234567; 0631234567`, with one contact named `John`. Both deletion requests are cancelled by `n`. After `exit`, launch the assistant again and enter `phone john`, `all-notes`, and `search-tag demo` to verify both phones, the note, and its tag were restored. Data is written on exit, not immediately after each command.

### Demo dataset

A reproducible demo dataset (10 synthetic contacts and 10 notes with tags) and loading instructions for Windows and macOS/Linux are in [demo/DEMO_SETUP.md](demo/DEMO_SETUP.md). It uses a separate temporary profile and does not touch real data.

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

The application distinguishes individual invalid contacts from files that cannot be reconstructed as a collection.

| Situation | Recovery |
| --- | --- |
| Contact list has individual invalid records (including invalid email, name, birthday or phone) | Load valid records, skip each invalid record as a whole, and **copy** the original contacts file byte-for-byte to a timestamped backup. |
| Case-variant duplicate contact names, such as John and john | Keep the first successfully loaded record; skip the conflicting record. Do not merge or normalize it silently. The original file is copied to backup. |
| Malformed JSON, invalid top-level structure, or a notes collection that fails validation (including duplicate note IDs) | **Move** the entire affected file to a timestamped backup and start that collection empty. |

For skipped contacts, startup reports the names (or `?` when unavailable) and the backup path:

```text
Contacts not loaded: Bob. Original file copied to: <backup path>
```

For whole-file recovery, startup reports:

```text
Data file was broken, starting empty. Old data is in: <backup path>
```

The unaffected collection is loaded normally. Skipped records are not available via normal commands until manually recovered; no fields are silently discarded or corrected within a loaded record. On normal exit, successfully loaded records and new changes are saved to the working JSON file. If every contact is invalid, the working address book starts empty but the original is copied before saving.

Backup names use a local timestamp, for example `contacts.20261125-191500.bak`; sequential recoveries with the same timestamp get `-1`, `-2`, etc. before `.bak`. Existing backups are retained in sequential use. The application is intended for **one active session per data directory**; filename existence checks and JSON writes are not concurrency-safe.

**Manual recovery:**

1. Note the backup path and exit the application before editing its files.
2. Copy the timestamped `.bak` to a separate safe location. Also preserve any current working JSON, which may contain newly entered data.
3. Inspect a copy of the backup and correct or reconcile records deliberately. For case-variant duplicates, review both contacts and retain all intended information; never guess which email or phone is correct. Keep the original backup intact.
4. With the assistant stopped, place the corrected JSON at the corresponding `contacts.json` or `notes.json` path only after preserving the current file. If needed, reconcile new and old records manually rather than overwriting new data.
5. Restart, inspect the restored records, exit normally, and restart again to verify persistence. If validation still fails, preserve the new backup and review the data again.

Expected JSON/schema/validation failures trigger recovery; unrelated programming and filesystem errors can propagate. Do not rely on automatic repair, and do not use concurrent sessions sharing one data directory. Backups can contain personal information: keep them private.

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
| Persistence | `assistant/storage.py` | Load/save local JSON, recover valid contacts individually, preserve originals in timestamped backups, and use atomic file replacement. |
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

The GitHub Actions workflow `.github/workflows/ci.yml` runs linting, formatting checks, and pytest on **Python 3.12 and 3.15** for PRs targeting `main` and pushes to `main`. The Python 3.12 job also verifies a regular (non-editable) `python -m pip install .`. Package smoke tests cover both launch commands from a working directory outside the repository. **Current CI runs on Ubuntu, not macOS or Windows.** T33 adds plain-I/O fallback for non-terminal sessions, but green Linux CI is not evidence of macOS or Windows acceptance. The team agreed on 25 November to actively test both desktop platforms; record evidence separately for each.

Tests are under `tests/test_*.py`. Storage-related tests must use pytest's `tmp_path` to avoid modifying a real user's home directory. The full team contribution workflow and Ruff conventions are documented in [CONTRIBUTING.md](CONTRIBUTING.md).

### Cross-platform release testing

Use a disposable terminal and a new temporary home for manual tests. Install the project first (see Quick start); leave the virtual environment active. Do not move or delete any real application data.

macOS / Linux (bash or zsh):

```bash
TEST_HOME="$(mktemp -d)" || exit 1
export HOME="$TEST_HOME"
python -c 'from assistant.storage import DATA_DIR; print(DATA_DIR); assert DATA_DIR.parent == __import__("pathlib").Path.home()'
```

Windows PowerShell:

```powershell
$testHome = Join-Path $env:TEMP ("pa-test-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $testHome -ErrorAction Stop | Out-Null
$env:USERPROFILE = $testHome
python -c "from assistant.storage import DATA_DIR; print(DATA_DIR)"
```

In either shell, **stop unless the printed DATA_DIR is exactly the new temporary directory plus `.personal_assistant`**. Use the explicit printed path for all filesystem operations; in PowerShell do not use `~` or `$HOME` after changing USERPROFILE. Close the disposable terminal after testing to discard the environment changes; leave the temporary test files intact unless you have separately verified their location.

On each platform, record OS and Python version, Git commit, CI link and results. Verify installation, both launch entry points from outside the repository, interactive completion/colors, redirected input/output, invalid-input handling, contact/note/tag CRUD, cancellation, restart, Unicode and recovery. Run Ruff and pytest using the same Python environment. For plain-I/O smoke testing:

```bash
# macOS / Linux
printf 'help\nexit\n' | assistant
printf 'exit\n' | python -m assistant
```

```powershell
# Windows PowerShell
"help", "exit" | assistant
"exit" | python -m assistant
```

The T28 acceptance checklist is the detailed test register; see [T28 in Trello](https://trello.com/c/EzirCCpd). Report failures with reproduction steps and evidence. Do not mark cross-platform acceptance complete merely because Ubuntu CI passed.

## Team and responsibilities

| Team member | Project responsibility |
| --- | --- |
| **Boris** | Team Lead; repository governance, CLI foundations, error handling, packaging, documentation, final presentation. |
| **Yuliia** | Backend; domain models, validation, address book, serialization and persistent storage. |
| **Oksana** | UX and CLI; interactive handlers, user-facing commands, completion, deletion confirmation and error resilience; colored output (U2), typo suggestions (U3), and Windows/non-interactive plain-I/O compatibility (T33). |
| **Kate** | Tests & Features; notes/tag models and commands, CI, test coverage and final acceptance testing. |

Work is organized through the [Trello project board](https://trello.com/b/lYqKSQAW/neo-personal-assistant-group) and reviewed in [GitHub Pull Requests](https://github.com/GulyaevB/neo-personal-assistant-2026/pulls). Team conventions require one task per branch/PR, passing CI, and at least one reviewer approval before the Team Lead performs a Squash Merge.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `assistant: command not found` | Activate the environment in which the package was installed; try `python -m assistant`. |
| `No module named assistant` | Run `python -m pip install .` from the cloned repository using the same Python interpreter. |
| Python version error during installation | Verify with `python --version`; use Python 3.12 or newer. On Windows, check `py -3 --version`; do not require a specific minor version unless selecting a known installed interpreter. |
| `Invalid email ... Use name@domain.com.` | Check supported syntax; remove leading, trailing or consecutive dots only if you know the correct email address. |
| `Invalid phone ... Use 10 digits.` | Enter exactly ten ASCII digits without formatting characters. |
| A contact name works in `search` but not `phone` | Exact lookups ignore case but do not use fuzzy matching; use `all` to inspect the stored name. |
| Notes or contacts appear missing after restarting | Verify that you exited normally and are using the same OS user account; check `~/.personal_assistant/contacts.json`, `notes.json`, and any timestamped `.bak` files. If a backup warning appeared, preserve the backup and follow the manual recovery steps above; some contacts may have been skipped, or a whole affected collection may have started empty. The warning distinguishes these cases. |
| Tag command is reported as unknown | Check `help` for `add-tag`, `remove-tag`, `search-tag`, and `sort-notes`; reinstall from the current version if necessary. |
| Deletion cancelled | Only `y` confirms contact/note deletion; any other input cancels. |
| Tab completion or colors are unavailable with redirected I/O | This is expected: use a real terminal for interactive completion and history; redirected stdout is plain text. |
| Unexpected command error | Retry; if a log path is shown, review `assistant.log` before sharing. Keep a copy of your data before troubleshooting. |

## Delivery

This repository is the shared source for the Neoversity group project. The final submission and mentor handoff are tracked in Trello task T30. Follow the course submission instructions for individual team uploads.
