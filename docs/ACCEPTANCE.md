# Acceptance checklist (T28)

Final acceptance of the Personal Assistant before submission.
Owner: Kate (Tests & Features). Planned run: **27 Nov 2026**.

Testers (team sync, 26 Nov): **macOS: Kate** (all sections),
**Windows: Oksana** (A7, B, G, H3 and the Windows commands of E).
Kate coordinates and collects the evidence. Each OS gets its own evidence
and its own line in "Run log".

Sources:

- Neoversity technical task ("ТЗ Персональний помічник"): 8 requirements + bonus checklist
- Neoversity acceptance criteria ("TECH-Критерії прийняття проєкту"): 14 general + 2 bonus criteria
- Lead's T28 gates from the Trello card and team agreements in `CONTRIBUTING.md`

Source codes: **TZ-n** = technical task requirement n, **TZ-B** = bonus checklist,
**AC-n** = acceptance criterion n, **AC-Bn** = bonus acceptance criterion n,
**PL** = team plan / Lead's gate.

## Statuses

| Mark | Meaning |
|------|---------|
| ⬜ Not run | Not checked yet (default) |
| ✅ Pass | Result matches "Expected" |
| ❌ Fail | Result differs or the app crashes: create a Trello `BUG:` card |
| ⚠️ Known issue | Current behaviour is documented in "Known issues"; the decision is not final |
| ⛔ Blocked | Can't be checked yet: a dependency is not merged or not available |
| ⏭ Deferred | Agreed with the Lead to check or fix after submission |

Every row that is not ⬜ needs evidence in the last column: a screenshot name,
a link to the T28 card attachment, a CI run link or a `BUG:` card. Green CI
alone is not acceptance: a row is ✅ only after it was checked on a real run.

## How to run

### 1. Isolated environment (your real data is never touched)

The app keeps data in the user's home folder (`~/.personal_assistant`).
For the run, the home folder of **this terminal only** points to a new empty
temporary folder. Nothing is moved or deleted in your real home folder, so no
backup and no restore are needed.

**macOS / Linux (zsh or bash):**

```bash
git clone https://github.com/GulyaevB/neo-personal-assistant-2026.git acceptance-run
cd acceptance-run
python3 -m venv .venv
source .venv/bin/activate
pip install .

export ACCEPTANCE_RUN="$(mktemp -d)"
section() {
  export HOME="$ACCEPTANCE_RUN/$1"
  mkdir -p "$HOME"
  DATA="$(python -c 'from assistant.storage import DATA_DIR; print(DATA_DIR)')"
  case "$DATA" in
    "$ACCEPTANCE_RUN"/*) echo "OK, test data folder: $DATA" ;;
    *) echo "STOP: $DATA is not inside $ACCEPTANCE_RUN"; DATA="" ;;
  esac
}
section A
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/GulyaevB/neo-personal-assistant-2026.git acceptance-run
cd acceptance-run
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install .

$env:ACCEPTANCE_RUN = Join-Path $env:TEMP "pa-acceptance-$(Get-Date -Format yyyyMMdd-HHmmss)"
function section($name) {
  $env:USERPROFILE = Join-Path $env:ACCEPTANCE_RUN $name
  $env:HOME = $env:USERPROFILE
  New-Item -ItemType Directory -Force $env:USERPROFILE | Out-Null
  $global:DATA = python -c "from assistant.storage import DATA_DIR; print(DATA_DIR)"
  if ($global:DATA.StartsWith($env:ACCEPTANCE_RUN)) { "OK, test data folder: $global:DATA" }
  else { "STOP: $global:DATA is not inside $env:ACCEPTANCE_RUN"; $global:DATA = $null }
}
section A
```

If `Activate.ps1` is blocked, run `Set-ExecutionPolicy -Scope Process RemoteSigned`
first (only for this PowerShell window).

**Safety rule:** `section` asks the app itself where it will keep data
(`assistant.storage.DATA_DIR`) and stores this path in `$DATA`. It must print
`OK, test data folder: ...` with a path inside the temporary folder. If it prints
`STOP`, do not continue.

**All file operations in this checklist use `$DATA`, never `~`.** In PowerShell,
`~` keeps pointing to your real home folder even after `USERPROFILE` is changed,
so a command like `Set-Content ~/.personal_assistant/...` could overwrite real
data. Before any command that creates or changes a file, check `$DATA` again:
`echo "$DATA"` / `$DATA`.

Use only this terminal for the run. Other terminals and your normal use of
the app keep working with your real data.

### 2. One fresh data folder per section

Each section starts with `section <letter>` (e.g. `section C`), which runs the
safety check. This gives the section its own empty data folder, so the sections don't
depend on each other. Inside a section, run the rows **in the order shown**:
later rows use the data created by earlier rows of the same section.

### 3. Birthday dates

The birthday rows are written for a run on **Friday 27 Nov 2026**:
John `30.11.1990` (Monday, in 3 days), Anna `28.11.1990` (Saturday).
On another day, use a date 3 days after the run for John and the next
Saturday within 7 days for Anna, and update "Expected" accordingly.

### 4. Evidence

- Before starting, fill in your line in "Run log" at the end of this file:
  OS and version, shell, `python --version`, commit (`git log --oneline -1`)
  and the link to the CI run of that commit.
- All rows of one run must be checked on **the same commit**. A result from an
  older commit counts only after a retest on the commit under acceptance.
- Take a screenshot for every ❌, ⚠️, ⛔ row and for E2, E6, F10.
  Attach them to the T28 card and put the file name in the last column.

### 5. Bugs

For every ❌ create a Trello card `BUG: <short title>` with: check ID, commit,
steps, expected result, actual result, screenshot, owner of the module.
Put the card name in the last column and post it in Slack.

### 6. Retest

If a fix is merged after the run, retest only the affected rows on the new
commit and update their status and evidence. #34 (strict email + legacy-data
recovery) and README #28 are already in `main` (12319c5), so A2, A3, C7 and
E8–E12 are checked in the normal run.

### 7. Clean up

Close the terminal. Optionally delete the temporary folder:
`rm -rf "$ACCEPTANCE_RUN"` (macOS/Linux) or
`Remove-Item -Recurse -Force $env:ACCEPTANCE_RUN` (PowerShell).
This removes only the test data of the run.

## A. Repository, documentation, installation

Setup: `section A`.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| A1 | Open the GitHub repo in a private browser window | Repo is public | AC-1 | T01 | ⬜ | |
| A2 | Follow only `README.md` ("Quick start") to install and start the app | Install and run steps work as written | AC-2 | T27 | ⬜ | |
| A3 | Compare README "Command reference" with `help` | All 25 commands from `help` are documented with an example | AC-2, PL | T27 | ⬜ | |
| A4 | `pip install .` in a clean venv | Installs without errors, pulls `prompt_toolkit` | PL | T26 | ⬜ | |
| A5 | From another folder (`cd ~`) run `assistant`, `exit`, then `python -m assistant`, `exit` | Both entry points start the app and say `Goodbye!` | PL | T26 | ⬜ | |
| A6 | Public classes and functions have docstrings | Spot check models, handlers, cli | AC-2 | all | ⬜ | |
| A7 | Windows: steps from "How to run" in PowerShell, then `assistant` | Starts, colors and Tab work | PL | T33 | ⬜ | |

## B. CLI loop and usability

Setup: `section B`, start `assistant`. Before B8 run `add John 0501234567`.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| B1 | Start the app | `Personal Assistant is running. Type 'exit' to quit.` shown **once** | AC-6 | T17 | ⬜ | |
| B2 | Run 3 commands in a row (`help`, `all`, `all-notes`) | Greeting is **not** repeated after each command | AC-6 | T17 | ⬜ | |
| B3 | `help` | `Available commands:` + 25 commands with a short description | AC-6, PL | T18 | ⬜ | |
| B4 | Press Enter on empty input | Nothing happens, prompt is shown again | AC-10 | T17 | ⬜ | |
| B5 | `xyz` | `Unknown command 'xyz'.`, app keeps running | AC-10 | T17 | ⬜ | |
| B6 | `add` without arguments | `Missing arguments. Use: add <name> <phone>`, no traceback | AC-10 | T23 | ⬜ | |
| B7 | `bi` + Tab | Completes to `birthdays` | AC-6 | U1 | ⬜ | |
| B8 | `phone J` + Tab | Completes to `phone John` | AC-6 | U1 | ⬜ | |
| B9 | Look at B5, B6, B8 output | Success green, errors red, commands and tags highlighted | AC-6 | U2 | ⬜ | |
| B10 | `exit`; start again, `close` | `Goodbye!`, app stops (both commands) | AC-7 | T17 | ⬜ | |
| B11 | Start, press Ctrl+C; start, press Ctrl+D | App stops without traceback | AC-9 | T17 | ⬜ | |
| B12 | Without a console. macOS/Linux: `printf 'help\nexit\n' \| assistant`. PowerShell: `"help","exit" \| assistant`. cmd.exe: `assistant < commands.txt` | Help and `Goodbye!` printed, no `NoConsoleScreenBufferError`, no traceback | AC-9 | T33 | ⬜ | |

## C. Contacts

Setup: `section C`, start `assistant`, run the rows in this order without restarting.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| C1 | `add John 0501234567` | `Contact 'John' added.` | TZ-1 | T19 | ⬜ | |
| C2 | `add john 0671112233`, then `all` | `Phone added to 'John'.`; `all` shows **one** John with `0501234567; 0671112233` | TZ-1 | T35 | ⬜ | |
| C3 | `add John 0501234567` (same phone) | `Contact 'John' already has phone '0501234567'.` | AC-12 | T35 | ⬜ | |
| C4 | `add Anna 123` | `Invalid phone '123'. Use 10 digits.` (Anna is not created) | TZ-3, AC-12 | T05, T19 | ⬜ | |
| C5 | `add 123 0501234567` | `Invalid name '123'. Use at least one letter.` | AC-12 | T34 | ⬜ | |
| C6 | `add-email John john@mail.com` | `Email set for 'John'.` | TZ-1 | T06, T19 | ⬜ | |
| C7 | `add-email John john@mail` | `Invalid email 'john@mail'. Use name@domain.com.`, email stays `john@mail.com` | TZ-3, AC-12 | T06 | ⬜ | |
| C7b | `add-email John a..b@c.com`, then `all` | `Invalid email 'a..b@c.com'. Use name@domain.com.`; `all` still shows `john@mail.com`. If the email **was** changed (❌), run `add-email John john@mail.com` before C15, so the next rows are not affected | AC-12 | T34 | ⬜ | |
| C8 | `add-address John Kyiv, Khreshchatyk 1` | `Address set for 'John'.` | TZ-1 | T06, T19 | ⬜ | |
| C9 | `add-birthday John 30.11.1990` | `Birthday set for 'John'.` | TZ-1 | T07, T19 | ⬜ | |
| C10 | `add-birthday John 31.02.1990`, `add-birthday John 1990-05-15` | `Invalid date '...'. Use DD.MM.YYYY.` | AC-12 | T05, T07 | ⬜ | |
| C11 | `add-birthday John 01.01.2090` | `Birthday '01.01.2090' is in the future.` | AC-12, PL | T07 | ⬜ | |
| C12 | `add-birthday John 01.01.1899` | `Birthday '01.01.1899' is too old. Use 1900 or later.` | AC-12 | T34 | ⬜ | |
| C13 | `phone john`, `show-birthday JOHN` | `John: 0501234567; 0671112233`, `John: 30.11.1990` (C10–C12 did not change it) | TZ-1 | T34 | ⬜ | |
| C14 | `add Anna 0931112233`, `add-birthday Anna 28.11.1990`, `all` | Anna and John with all their fields | TZ-1 | T19 | ⬜ | |
| C15 | `search john` | John is found | TZ-4 | T09, T20 | ⬜ | |
| C16 | `search 050123`, `search mail.com`, `search Kyiv` | John is found each time | TZ-4 | T09 | ⬜ | |
| C17 | `search jhon` (typo) | John is found (fuzzy) | TZ-4, PL | T09 | ⬜ | |
| C18 | `birthdays 7` | `Birthdays in the next 7 days:`, `28.11.2026 (Sat)  Anna`, `30.11.2026 (Mon)  John` | TZ-2 | T10, T20 | ⬜ | |
| C19 | Anna's line in C18 | Real date on Saturday, no shift to Monday (team decision in T10) | PL | T10 | ⬜ | |
| C20 | `birthdays` (no argument) | Same list as C18 (default 7 days) | PL | T20 | ⬜ | |
| C21 | `birthdays abc`, `birthdays 0` | `Invalid days 'abc'. Use a positive number.` / `Invalid days '0'. ...` | AC-10, PL | T20 | ⬜ | |
| C22 | Year boundary (25 Dec → 2 Jan) and 29 Feb in a non-leap year | Can't be reproduced by hand on 27 Nov: `pytest tests/test_birthdays.py -v` passes `test_january_birthdays_on_25_december` and `test_leap_day_birthday` | TZ-2, PL | T10 | ⬜ | |
| C23 | `change John 0501234567 0509998877` | `Phone updated for 'John'.` | TZ-5 | T19 | ⬜ | |
| C24 | `change John 1111111111 0509998877` | `Contact 'John' has no phone '1111111111'.` | TZ-5, AC-10 | T05 | ⬜ | |
| C25 | `remove-phone John 0671112233`, `phone John` | `Phone removed from 'John'.`, `John: 0509998877` | TZ-5 | T07, T19 | ⬜ | |
| C26 | `delete John` → `n`; repeat with Enter and with Ctrl+C | `Deletion cancelled.`, `phone John` still works | TZ-5 | U4 | ⬜ | |
| C27 | `delete John` → `y`, then `phone John` | `Contact 'John' deleted.`, then `Contact 'John' not found.` | TZ-5 | T08, U4 | ⬜ | |
| C28 | `delete Nobody` | `Contact 'Nobody' not found.` | AC-10 | T08 | ⬜ | |

## D. Notes

Setup: `section D`, start `assistant`, run the rows in this order.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| D1 | `add-note Buy a gift for Anna`, `add-note Call the dentist`, `add-note Купити молоко` | `Note 1 added.`, `Note 2 added.`, `Note 3 added.` | TZ-6 | T11, T21 | ⬜ | |
| D2 | `add-note` | `Missing arguments. Use: add-note <text>`, nothing saved | AC-12 | T11, T21 | ⬜ | |
| D3 | `all-notes` | `1: Buy a gift for Anna`, `2: Call the dentist`, `3: Купити молоко` (Cyrillic shown correctly) | TZ-6 | T21, T25 | ⬜ | |
| D4 | `search-notes GIFT` | `1: Buy a gift for Anna` (any case, part of a word) | TZ-7 | T12, T21 | ⬜ | |
| D5 | `search-notes python` | `No notes found for 'python'.` (not an error) | TZ-7 | T12, T21 | ⬜ | |
| D6 | `edit-note 1 Buy flowers` | `Note 1 updated.` | TZ-8 | T11, T21 | ⬜ | |
| D7 | `edit-note 1` | `Missing arguments. Use: edit-note <id> <text>`, text stays `Buy flowers` | AC-10 | T11, T21 | ⬜ | |
| D8 | `edit-note 99 text`, `delete-note 99` | `Note with id 99 not found.` | AC-10 | T11 | ⬜ | |
| D9 | `edit-note abc text` | `Invalid note id 'abc'. Use a number.` | AC-10, PL | T21 | ⬜ | |
| D10 | `delete-note 3` → `n`, then `delete-note 3` → `y` | `Delete note 3: Купити молоко? (y/n)`; `Deletion cancelled.`; then `Note 3 deleted.` | TZ-8 | T21, U4 | ⬜ | |
| D11 | `add-note New note`, `all-notes` | `Note 4 added.` (id 3 is not reused); list 1, 2, 4 | PL | T11 | ⬜ | |

## E. Persistence and old data

### E1–E7: saving and loading

Setup: `section E`. Check that the data folder does not exist yet:
`ls -a "$DATA"` ("No such file") / `Test-Path $DATA` (`False`).

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| E1 | Start the app, `exit`, then `ls "$DATA"` / `Get-ChildItem $DATA` | Starts with empty data; after exit the folder has `contacts.json` and `notes.json` | TZ-data, PL | T16 | ⬜ | |
| E2 | Start, `add John 0501234567`, `add-note Купити молоко`, `exit`; start again, `all`, `all-notes` | John and `1: Купити молоко` are there | TZ-data, AC-8 | T16, T17 | ⬜ | |
| E3 | `add Anna 0931112233`, then Ctrl+C; start again, `phone Anna` | `Anna: 0931112233` (saved on Ctrl+C) | AC-8, PL | T17 | ⬜ | |
| E4 | `add-note Second` | `Note 2 added.` (`next_id` kept after restart) | PL | T11, T16 | ⬜ | |
| E5 | `exit`; `cat "$DATA/contacts.json" "$DATA/notes.json"` / `Get-Content -Encoding utf8 (Join-Path $DATA notes.json)` | Readable JSON, Cyrillic stored as letters (not `І` escapes) | TZ-data | T16, T25 | ⬜ | |
| E6 | Check `$DATA`, then break notes: `echo "{not json" > "$DATA/notes.json"` (PowerShell: `Set-Content -Path (Join-Path $DATA notes.json) -Value "{not json"`), start, `all`, `all-notes` | `Data file was broken, starting empty. Old data is in: .../notes.<date>-<time>.bak`; contacts still load; `No notes yet. ...` | AC-9, PL | T16, T34 | ⬜ | |
| E7 | `exit`, `ls "$DATA"` / `Get-ChildItem $DATA` | New valid `notes.json` (empty list), the `.bak` file with `{not json` is kept | PL | T16 | ⬜ | |

### E8–E12: old data files (legacy)

Recovery behaviour from #34 (merged, checked on `main` 12319c5): valid contacts
are loaded, contacts that break the current rules are **skipped**, the startup
message names them and the original file is **copied** to `.bak`.
The Lead confirms that this is the final recovery contract (I2). Until then,
mark E8–E12 as ⛔ Blocked even if they pass, and write the observed result in
the evidence column.

Setup for each row: `section E8`, `section E9a`, ... (a new empty folder each
time), check `$DATA`, create the folder and both fixtures from the appendix
(`contacts.json` for the row + the shared `notes.json`), start the app, `all`,
`all-notes`, `exit`, then `ls "$DATA"` / `Get-ChildItem $DATA`.

| ID | Fixture | Expected | Source | Task | Status | Evidence / Defect |
|----|---------|----------|--------|------|--------|-------------------|
| E8 | `John` and `john` as two contacts (created before T34/T35) | Startup: `Contacts not loaded: john. Original file copied to: .../contacts.<date>-<time>.bak`; `all` shows John with `0501234567` only (see KI-1) | PL | T34, T35 | ⬜ | |
| E9a | Name `123` (valid before T34) next to valid `Bob` | `Contacts not loaded: 123. ...`; `all` shows Bob | PL | T34 | ⬜ | |
| E9b | Birthday `01.01.1899` (valid before T34) next to valid `Bob` | `Contacts not loaded: Ann. ...`; `all` shows Bob | PL | T34 | ⬜ | |
| E10 | Email `a..b@c.com` (valid before #34) next to valid `Bob` | `Contacts not loaded: John. ...`; `all` shows Bob; John is in the `.bak` copy | PL | T34 | ⬜ | |
| E11 | Phone `123` next to valid `Bob` (this phone was **always** invalid, a damaged record, not old data) | `Contacts not loaded: Ann. ...`; `all` shows Bob | AC-9 | T16, T34 | ⬜ | |
| E12 | For each of E8–E11 | Notes are not affected: `all-notes` shows `1: Keep me [home]`, no `notes.*.bak`. After `exit`: `contacts.json` has only the loaded contacts; the `.bak` copy is identical to the fixture (`cmp` / `Compare-Object`) | PL | T16, T34 | ⬜ | |

## F. Bonus: tags (10 points)

Setup: `section F`, start `assistant`, `add-note Buy milk`, `add-note Call boss`,
`add-note Read book` (notes 1, 2, 3). Run the rows in this order.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| F1 | `add-tag 1 Shopping` | `Tag 'shopping' added to note 1.` | TZ-B, AC-B1 | T13, T22 | ⬜ | |
| F2 | `add-tag 1 shopping` | `Note 1 already has tag 'shopping'.` | AC-B1 | T13, T22 | ⬜ | |
| F3 | `add-tag 1 #tag!` | `Invalid tag '#tag!'. Use one word: letters, digits, _ or -.` | AC-12 | T13 | ⬜ | |
| F4 | `add-tag 2 work` | `Tag 'work' added to note 2.` | AC-B1 | T13, T22 | ⬜ | |
| F5 | `search-tag SHOPPING` | Only `1: Buy milk [shopping]` | TZ-B, AC-B2 | T13, T22 | ⬜ | |
| F6 | `search-tag travel` | `No notes with tag 'travel'.` | AC-B2 | T22 | ⬜ | |
| F7 | `sort-notes` | `1: Buy milk [shopping]`, `2: Call boss [work]`, `3: Read book` (untagged last) | TZ-B, AC-B2 | T14, T22 | ⬜ | |
| F8 | `edit-note 1 Buy oat milk`, `all-notes` | `1: Buy oat milk [shopping]` (tags kept after edit) | TZ-8 | T11, T21 | ⬜ | |
| F9 | `remove-tag 1 shopping`, then again | `Tag 'shopping' removed from note 1.` / `Note 1 has no tag 'shopping'.` | AC-B1 | T13, T22 | ⬜ | |
| F10 | `exit`, start again, `all-notes` | `2: Call boss [work]` (tags kept after restart) | AC-8 | T16 | ⬜ | |

## G. Bonus: intelligent analysis

Setup: `section G`, start `assistant`.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| G1 | `ad John 0501234567` | `Unknown command 'ad'. Did you mean: add?` | TZ-B | U3 | ⬜ | |
| G2 | `birthdys 7` | `Unknown command 'birthdys'. Did you mean: birthdays, ...?` (`birthdays` first) | TZ-B | U3 | ⬜ | |
| G3 | `qwerty` | `Unknown command 'qwerty'.`, no wrong suggestion | TZ-B | U3 | ⬜ | |

## H. Code quality and diagnostics

Run in the `acceptance-run` folder.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| H1 | CI on the last `main` commit | `lint-and-test (3.12)` and `(3.15)` green (add the run link) | AC-13 | T04 | ⬜ | |
| H2 | `pip install ruff pytest`, `ruff check .`, `ruff format --check .` | Clean | AC-13 | T03 | ⬜ | |
| H3 | `pytest` on macOS/Linux **and** on Windows | All tests pass on both | AC-9 | T24, T25, T33 | ⬜ | |
| H4 | OOP: `Field` → `Name`/`Phone`/`Email`/`Address`/`Birthday`; `AssistantError` → errors; `AddressBook`/`NoteBook` → `UserDict` | Inheritance used as planned | AC-11 | T02–T11 | ⬜ | |
| H5 | Composition: `Record` has fields, `AddressBook` has `Record`, `NoteBook` has `Note`, `Context` has both books | Composition used as planned | AC-11 | T02 | ⬜ | |
| H6 | Validation lives in field / model classes, not in handlers | Confirmed by code review | AC-12, PL | all | ⬜ | |
| H7 | `grep -rnE "TODO\|NotImplementedError" assistant/` (PowerShell: `Select-String -Path assistant\*.py -Pattern "TODO\|NotImplementedError"`) | Prints nothing | AC-3 | all | ⬜ | |
| H8 | Unexpected error inside a command: `pytest tests/test_cli_errors.py -v` | All pass, including: traceback goes to `assistant.log` (`test_traceback_is_written_to_log`); no exception messages or arguments in the log (`test_exception_messages_are_not_logged`, `test_arguments_are_not_logged`); log can't be opened, or writing / rotation fails → CLI keeps running, nothing is printed to the console and the message does **not** say details were saved (`test_log_cannot_be_opened`, `test_log_write_or_rollover_fails`); logging works again after a failure (`test_log_works_again_after_a_failed_write`) | AC-9 | T32 | ⬜ | |
| H9 | Code review of `assistant/cli.py` | Log rotates: `RotatingFileHandler(maxBytes=1_000_000, backupCount=1)`; the log file is created only on the first unexpected error | PL | T32 | ⬜ | |
| H10 | After sections A–G, list each section's data folder | No `assistant.log` after a normal run (no unexpected errors) | PL | T32 | ⬜ | |
| H11 | Whole run A–G | No traceback in the console | AC-9 | all | ⬜ | |

## I. Release gates for T28 sign-off

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| I1 | Trello board | All mandatory cards are Done, **except** T28 itself, downstream T29/T30 and optional T31 | Team | Lead | ⬜ | |
| I2 | Legacy-data recovery contract (#34) and README (#28) | #34 and #28 merged (done: 12319c5); Lead confirms the #34 recovery behaviour as final; E8–E12 moved from ⛔ to their real status | PL | T34, T27 | ⬜ | |
| I3 | Mentor code review of the final version | Project sent to the mentor in Slack by **Fri 27 Nov, 19:00**; comments handled or recorded | AC-14 | Lead | ⬜ | |
| I4 | All ❌ rows | Fixed and retested, or moved to ⏭ Deferred with the Lead's decision recorded | PL | T28 | ⬜ | |

T28 is Done only when I1–I4 are complete and the evidence is recorded.

## J. After acceptance: delivery gates (not part of T28 sign-off)

| ID | Check | Expected | Task | Status | Evidence |
|----|-------|----------|------|--------|----------|
| J1 | Demo | Demo of the accepted version; demo day (project defence) on 30 Nov | T29 | ⬜ | |
| J2 | LMS submission | Zip of the repo + GitHub link uploaded by every member before 29 Nov, 17:00 Kyiv | T30 | ⬜ | |

## Known issues

Checked on `main` 12319c5, after #34. Open until the Lead confirms the recovery
contract (I2); not blockers for submission unless the Lead says otherwise.

### KI-1. Duplicate names in an old file are not merged (E8)

- **Current behaviour:** before T34/T35 `add John ...` and `add john ...` created two
  contacts. Now names are compared without case, so on load the second one
  (`john`) is skipped and named in the message. Its phone `0671112233` is not in
  the app, only in the `.bak` copy.
- **Who is affected:** data created by development builds before T34/T35.
  A clean install is not affected.
- **Manual recovery:** open the `.bak` file and add the missing phones with
  `add John <phone>`.
- **Possible improvement (after submission):** merge phones of contacts whose names
  differ only in case.

### KI-2. Skipped old contacts are only in the `.bak` copy (E9a–E11)

- **Current behaviour:** contacts that break the current rules are skipped and listed
  in the message; the original file is copied to `.bak`. When the user exits, the
  new `contacts.json` no longer has them.
- **Manual recovery:** take the data from the `.bak` file and add the contact again
  with valid values.

## Appendix: fixtures for E8–E11

Always write to `$DATA` (checked by `section`), never to `~`.

macOS / Linux:

```bash
mkdir -p "$DATA"
cat > "$DATA/notes.json" <<'JSON'
{"next_id": 2, "notes": [{"id": 1, "text": "Keep me", "tags": ["home"], "created": "2026-11-20T10:00:00"}]}
JSON
cat > "$DATA/contacts.json" <<'JSON'
<one fixture from below>
JSON
cp "$DATA/contacts.json" "$ACCEPTANCE_RUN/original-contacts.json"   # for E12
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force $DATA | Out-Null
Set-Content -Encoding ascii -Path (Join-Path $DATA notes.json) -Value '{"next_id": 2, "notes": [{"id": 1, "text": "Keep me", "tags": ["home"], "created": "2026-11-20T10:00:00"}]}'
Set-Content -Encoding ascii -Path (Join-Path $DATA contacts.json) -Value '<one fixture from below>'
Copy-Item (Join-Path $DATA contacts.json) (Join-Path $env:ACCEPTANCE_RUN original-contacts.json)   # for E12
```

E12 check after `exit`: `cmp "$DATA"/contacts.*.bak "$ACCEPTANCE_RUN/original-contacts.json"`
(prints nothing if identical) / `Compare-Object (Get-Content (Get-Item (Join-Path $DATA 'contacts.*.bak'))) (Get-Content (Join-Path $env:ACCEPTANCE_RUN original-contacts.json))` (prints nothing if identical).

Contact fixtures (one line each):

- E8: `{"contacts": [{"name": "John", "phones": ["0501234567"], "email": null, "address": null, "birthday": null}, {"name": "john", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`
- E9a: `{"contacts": [{"name": "123", "phones": [], "email": null, "address": null, "birthday": null}, {"name": "Bob", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`
- E9b: `{"contacts": [{"name": "Ann", "phones": [], "email": null, "address": null, "birthday": "01.01.1899"}, {"name": "Bob", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`
- E10: `{"contacts": [{"name": "John", "phones": ["0501234567"], "email": "a..b@c.com", "address": null, "birthday": null}, {"name": "Bob", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`
- E11: `{"contacts": [{"name": "Ann", "phones": ["123"], "email": null, "address": null, "birthday": null}, {"name": "Bob", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`

## Result

| Section | ✅ | ❌ | ⚠️ | ⛔ | ⏭ | ⬜ | Notes |
|---------|----|----|----|----|----|----|-------|
| A. Repository, docs, install | | | | | | | |
| B. CLI loop and usability | | | | | | | |
| C. Contacts | | | | | | | |
| D. Notes | | | | | | | |
| E. Persistence and old data | | | | | | | |
| F. Bonus: tags | | | | | | | |
| G. Bonus: intelligent analysis | | | | | | | |
| H. Code quality and diagnostics | | | | | | | |
| I. Release gates | | | | | | | |

## Run log

| Tester | OS and version | Shell | Python | Commit | CI run | Sections | Date |
|--------|----------------|-------|--------|--------|--------|----------|------|
| Kate | macOS | zsh | | | | A–I | |
| Oksana | Windows 11 | PowerShell 5.1 | | | | A7, B, G, H3, E (Windows commands) | |
