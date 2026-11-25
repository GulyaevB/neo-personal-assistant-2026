# Acceptance checklist (T28)

Final acceptance of the Personal Assistant before submission.
Owner: Kate (Tests & Features). Planned run: **27 Nov 2026**.

Sources:

- Neoversity technical task ("ТЗ Персональний помічник"): 8 requirements + bonus checklist
- Neoversity acceptance criteria ("TECH-Критерії прийняття проєкту"): 14 general + 2 bonus criteria
- Team project plan and agreements in `CONTRIBUTING.md`

## How to run

1. Fresh clone of `main`, new virtual environment:

   ```bash
   git clone https://github.com/GulyaevB/neo-personal-assistant-2026.git
   cd neo-personal-assistant-2026
   python3 -m venv .venv && source .venv/bin/activate
   pip install .
   ```

   On Windows activate with `.venv\Scripts\activate` instead of `source ...`.

2. Back up and remove existing data so the run starts clean:

   ```bash
   mv ~/.personal_assistant ~/.personal_assistant.backup 2>/dev/null
   ```

3. Birthday checks depend on the run date. For a run on **27 Nov 2026** (Friday)
   use: `add-birthday John 30.11.1990` (in 3 days, C24) and
   `add-birthday Anna 28.11.1990` (Saturday, C26). C25 and C27 can't be
   reproduced by hand on that date; they are covered by unit tests in
   `tests/test_birthdays.py`, so check that those tests pass.
4. Capture evidence: record the commit (`git log --oneline -1`) and the latest
   `main` CI run, and save a screenshot of the terminal for every ❌ and ⚠️
   (and for key ✅ checks: E2, E6, F7). Attach them to the T28 card.
5. Go through every check below. Expected messages are copied from the app
   (`main`, 25 Nov); if a message changes later, the meaning must stay the same.
6. Mark each row: ✅ pass, ❌ fail, ⚠️ known issue / note.
7. For every ❌ create a Trello card `BUG: <short title>` with: steps,
   expected result, actual result, check ID. Link the card in the
   "Defect" column.
8. Restore your data afterwards:

   ```bash
   rm -rf ~/.personal_assistant
   mv ~/.personal_assistant.backup ~/.personal_assistant
   ```

9. Retest: when #34 (strict email + recovery policy) or README PR #28 is merged
   after the run, retest C7, E10 and A2/A3 on the new commit and update their
   status. Rows stay open until checked on a real run; green CI alone is not
   acceptance.

Source codes: **TZ-n** = technical task requirement n, **TZ-B** = bonus checklist,
**AC-n** = acceptance criterion n, **AC-Bn** = bonus acceptance criterion n,
**PL** = team plan.

## A. Repository, documentation, installation

| ID | Check | Expected | Source | Task | Status | Defect |
|----|-------|----------|--------|------|--------|--------|
| A1 | Open the GitHub repo without logging in | Repo is public | AC-1 | T01 | | |
| A2 | Read `README.md` only and install the app | Install and run steps work as written (README PR #28 merged) | AC-2 | T27 | | |
| A3 | README lists every command with an example | All 25 commands from `help` are documented | AC-2, PL | T27 | | |
| A4 | `pip install .` in a clean venv | Installs without errors, pulls `prompt_toolkit` | PL | T26 | | |
| A5 | From another folder (e.g. `cd ~`) run `assistant`, then `python -m assistant` | Both entry points start the app | PL | T26 | | |
| A6 | Public classes and functions have docstrings | Spot check models, handlers, cli | AC-2 | all | | |
| A7 | Windows: install and run `assistant` in PowerShell | Starts, colors and Tab work | PL | T33 | | |

## B. CLI loop and usability

| ID | Check | Expected | Source | Task | Status | Defect |
|----|-------|----------|--------|------|--------|--------|
| B1 | Start the app | `Personal Assistant is running. Type 'exit' to quit.` shown **once** | AC-6 | T17 | | |
| B2 | Run 3 commands in a row | Greeting is **not** repeated after each command | AC-6 | T17 | | |
| B3 | `help` | `Available commands:` + 25 commands with a short description | AC-6, PL | T18 | | |
| B4 | Press Enter on empty input | Nothing happens, prompt is shown again | AC-10 | T17 | | |
| B5 | Unknown command `xyz` | `Unknown command 'xyz'.`, app keeps running | AC-10 | T17 | | |
| B6 | `add` without arguments | `Missing arguments. Use: add <name> <phone>`, no traceback | AC-10 | T23 | | |
| B7 | `bi` + Tab | Completes to `birthdays` | AC-6 | U1 | | |
| B8 | `phone J` + Tab (contact John exists) | Completes to `phone John` | AC-6 | U1 | | |
| B9 | Success / error output | Success green, errors red, commands and tags highlighted | AC-6 | U2 | | |
| B10 | `exit` and `close` | `Goodbye!`, app stops | AC-7 | T17 | | |
| B11 | Ctrl+C and Ctrl+D at the prompt | App stops without traceback | AC-9 | T17 | | |
| B12 | Run without a console: `printf 'help\nexit\n' \| assistant` (macOS/Linux) or `assistant < commands.txt` (Windows) | Works with plain input/output, no `NoConsoleScreenBufferError` | AC-9 | T33 | | |

## C. Contacts

| ID | Check | Expected | Source | Task | Status | Defect |
|----|-------|----------|--------|------|--------|--------|
| C1 | `add John 0501234567` | `Contact 'John' added.` | TZ-1 | T19 | | |
| C2 | `add john 0671112233` (other case) | `Phone added to 'John'.`, still **one** contact | TZ-1 | T35 | | |
| C2a | `add John 0501234567` again (same phone) | `Contact 'John' already has phone '0501234567'.` | AC-12 | T35 | | |
| C3 | `add Anna 123` | `Invalid phone '123'. Use 10 digits.` | TZ-3, AC-12 | T05, T19 | | |
| C4 | `add 123 0501234567` | `Invalid name '123'. Use at least one letter.` | AC-12 | T34 | | |
| C5 | `add-email John john@mail.com` | `Email set for 'John'.` | TZ-1 | T06, T19 | | |
| C6 | `add-email John john@mail` | `Invalid email 'john@mail'. Use name@domain.com.`, contact unchanged | TZ-3, AC-12 | T06 | | |
| C7 | `add-email John a..b@c.com` | Rejected as invalid (after #34 is merged) | AC-12 | T34 | | |
| C8 | `add-address John Kyiv, Khreshchatyk 1` | Multi-word address saved | TZ-1 | T06, T19 | | |
| C9 | `add-birthday John 15.05.1990` | Birthday saved | TZ-1 | T07, T19 | | |
| C10 | `add-birthday John 31.02.1990` / `1990-05-15` | `Invalid date '...'. Use DD.MM.YYYY.` | AC-12 | T05, T07 | | |
| C11 | `add-birthday John 01.01.2090` | `Birthday '01.01.2090' is in the future.` | AC-12, PL | T07 | | |
| C12 | `add-birthday John 01.01.1899` | `Birthday '01.01.1899' is too old. Use 1900 or later.` | AC-12 | T34 | | |
| C13 | `phone john`, `show-birthday JOHN` (other case) | John's phones / birthday are shown | TZ-1 | T34 | | |
| C14 | `all` | All contacts with all fields | TZ-1 | T19 | | |
| C15 | `search john` (other case) | John is found | TZ-4 | T09, T20 | | |
| C16 | `search 050123`, `search mail.com`, `search Kyiv` | Search by phone, email, address works | TZ-4 | T09 | | |
| C17 | `search jhon` (typo) | John is found (fuzzy) | TZ-4, PL | T09 | | |
| C18 | `change John 0501234567 0509998877` | Phone replaced | TZ-5 | T19 | | |
| C19 | `change John 1111111111 0509998877` | `Contact 'John' has no phone '1111111111'.` | TZ-5, AC-10 | T05 | | |
| C20 | `remove-phone John 0671112233` | Phone removed | TZ-5 | T07, T19 | | |
| C21 | `delete John` → `n` (also Enter, Ctrl+C) | `Deletion cancelled.`, contact kept | TZ-5 | U4 | | |
| C22 | `delete John` → `y` | `Contact 'John' deleted.`, `phone John` → `Contact 'John' not found.` | TZ-5 | T08, U4 | | |
| C23 | `delete Nobody` | `Contact 'Nobody' not found.` | AC-10 | T08 | | |
| C24 | `birthdays 7` with a birthday in 3 days (`30.11.1990` on 27 Nov) | `Birthdays in the next 7 days:` + `30.11.2026 (Mon)  John` | TZ-2 | T10, T20 | | |
| C25 | `birthdays 10` on 25 Dec with a birthday on 2 Jan | Listed (year boundary). Unit test `test_january_birthdays_on_25_december` | TZ-2, PL | T10 | | |
| C26 | Birthday on a weekend (`28.11.1990`, Saturday) | `28.11.2026 (Sat)  Anna`: the **real** date, no shift to Monday (team decision in T10) | PL | T10 | | |
| C27 | Birthday on 29 Feb, non-leap year | Shown on 28 Feb, no error. Unit test `test_leap_day_birthday` | PL | T10 | | |
| C28 | `birthdays` (no argument) | Default 7 days | PL | T20 | | |
| C29 | `birthdays abc`, `birthdays 0` | `Invalid days 'abc'. Use a positive number.` | AC-10, PL | T20 | | |

## D. Notes

| ID | Check | Expected | Source | Task | Status | Defect |
|----|-------|----------|--------|------|--------|--------|
| D1 | `add-note Buy a gift for Anna` | `Note 1 added.`, full multi-word text saved | TZ-6 | T11, T21 | | |
| D2 | `add-note` with empty text | `Missing arguments. Use: add-note <text>`, nothing saved | AC-12 | T11, T21 | | |
| D3 | `all-notes` | All notes with id, text, tags | TZ-6 | T21 | | |
| D4 | `search-notes GIFT` | Case-insensitive, finds part of a word | TZ-7 | T12, T21 | | |
| D5 | `search-notes python` (no matches) | `No notes found for 'python'.` (not an error) | TZ-7 | T12, T21 | | |
| D6 | `edit-note 1 Buy flowers` | Text changed, tags kept | TZ-8 | T11, T21 | | |
| D7 | `edit-note 1` without text | `Missing arguments. Use: edit-note <id> <text>`, old text kept | AC-10 | T11, T21 | | |
| D8 | `edit-note 99 text`, `delete-note 99` | `Note with id 99 not found.` | AC-10 | T11 | | |
| D9 | `edit-note abc text` | `Invalid note id 'abc'. Use a number.` | AC-10, PL | T21 | | |
| D10 | `delete-note 1` → `n`, then → `y` | `Deletion cancelled.` on `n`, deleted on `y` | TZ-8 | T21, U4 | | |
| D11 | Add a note after deleting the last one | New id is not reused (e.g. 4, not 3) | PL | T11 | | |
| D12 | Cyrillic: `add-note Купити молоко` | Saved and shown correctly | PL | T25 | | |

## E. Persistence

| ID | Check | Expected | Source | Task | Status | Defect |
|----|-------|----------|--------|------|--------|--------|
| E1 | First start without `~/.personal_assistant` | App starts with empty data, folder is created on exit | TZ-data, PL | T16 | | |
| E2 | Add contacts and notes, `exit`, start again | All contacts and notes are there | TZ-data, AC-8 | T16, T17 | | |
| E3 | Same as E2 but stop with Ctrl+C | Data is saved | AC-8, PL | T17 | | |
| E4 | After restart, add a note | Id continues (`next_id` kept) | PL | T11, T16 | | |
| E5 | Open `~/.personal_assistant/contacts.json`, `notes.json` | Readable JSON, Cyrillic stored as letters (not `\u0406` escapes) | TZ-data | T16, T25 | | |
| E6 | Break `notes.json` by hand (`echo "{not json" > ~/.personal_assistant/notes.json`), start | `Data file was broken, starting empty. Old data is in: .../notes.<date>-<time>.bak`, app keeps running | AC-9, PL | T16, T34 | | |
| E7 | After E6, `exit` | New valid `notes.json` written, `.bak` kept | PL | T16 | | |
| E8 | Old `contacts.json` with `John` and `john` as two contacts (see Known issues) | Whole file moved to `.bak`, app starts with empty contacts and shows the message | PL | T34 | | ⚠️ known issue |
| E9 | Old `contacts.json` where **one** contact breaks a new rule (name `123`, birthday `01.01.1899`, phone `123`) next to a valid contact `Bob` | Today: whole file → `.bak`, Bob is not visible either (see KI-2). Expected after the recovery policy is agreed: valid contacts load | PL | T34 | | ⚠️ known issue |
| E10 | Old `contacts.json` with email `a..b@c.com` (valid before #34) | Today: loads. After #34: the contact is **not lost** and the original data is kept, as agreed in #34 | PL | T34 | | |

## F. Bonus: tags (10 points)

| ID | Check | Expected | Source | Task | Status | Defect |
|----|-------|----------|--------|------|--------|--------|
| F1 | `add-tag 1 Shopping` | `Tag 'shopping' added to note 1.` | TZ-B, AC-B1 | T13, T22 | | |
| F2 | `add-tag 1 shopping` again | `Note 1 already has tag 'shopping'.` | AC-B1 | T13, T22 | | |
| F3 | `add-tag 1 #tag!` | `Invalid tag '#tag!'. Use one word: letters, digits, _ or -.` | AC-12 | T13 | | |
| F4 | `remove-tag 1 shopping`, then again | `Tag 'shopping' removed from note 1.` / `Note 1 has no tag 'shopping'.` | AC-B1 | T13, T22 | | |
| F5 | `search-tag SHOPPING` | Only notes with exactly this tag, any case | TZ-B, AC-B2 | T13, T22 | | |
| F6 | `search-tag travel` (no matches) | `No notes with tag 'travel'.` | AC-B2 | T22 | | |
| F7 | `sort-notes` | Notes sorted by tag A-Z, untagged at the end | TZ-B, AC-B2 | T14, T22 | | |
| F8 | Restart after adding tags | Tags are kept | AC-8 | T16 | | |

## G. Bonus: intelligent analysis

| ID | Check | Expected | Source | Task | Status | Defect |
|----|-------|----------|--------|------|--------|--------|
| G1 | Typo `ad John 0501234567` | `Unknown command 'ad'. Did you mean: add?` | TZ-B | U3 | | |
| G2 | Typo `birthdys 7` | Suggests `birthdays` first | TZ-B | U3 | | |
| G3 | Nonsense `qwerty` | `Unknown command 'qwerty'.`, no wrong suggestion | TZ-B | U3 | | |

## H. Code quality

| ID | Check | Expected | Source | Task | Status | Defect |
|----|-------|----------|--------|------|--------|--------|
| H1 | CI on the last `main` commit | `lint-and-test (3.12)` and `(3.15)` green | AC-13 | T04 | | |
| H2 | `ruff check .` and `ruff format --check .` locally | Clean | AC-13 | T03 | | |
| H3 | `pytest` locally (macOS/Linux **and** Windows) | All tests pass | AC-9 | T24, T25, T33 | | |
| H4 | OOP: `Field` → `Name`/`Phone`/`Email`/`Address`/`Birthday`; `AssistantError` → errors; `AddressBook`/`NoteBook` → `UserDict` | Inheritance used as planned | AC-11 | T02–T11 | | |
| H5 | Composition: `Record` has fields, `AddressBook` has `Record`, `NoteBook` has `Note`, `Context` has both books | Composition used as planned | AC-11 | T02 | | |
| H6 | Validation lives in field / model classes, not in handlers | Confirmed by code review | AC-12, PL | all | | |
| H7 | No `TODO` / `NotImplementedError` left in `assistant/` | `grep -rnE "TODO\|NotImplementedError" assistant/` prints nothing | AC-3 | all | | |
| H8 | Unexpected error inside a command (covered by tests in T32) | CLI keeps running; details go to `~/.personal_assistant/assistant.log` without personal data | AC-9 | T32 | | |
| H9 | No traceback during the whole run A–G | Confirmed | AC-9 | all | | |

## I. Submission

| ID | Check | Expected | Source | Task | Status | Defect |
|----|-------|----------|--------|------|--------|--------|
| I1 | All Trello cards in Done (except T29, T30) | Confirmed | Team | Lead | | |
| I2 | Mentor code review of the final version | Done before submission | AC-14 | Lead | | |
| I3 | Zip of the repo + GitHub link uploaded to LMS by every member | Before 29 Nov, 17:00 Kyiv | Course | T30 | | |

## Known issues / technical debt

### KI-1. Old data files with the same name in different case (E8)

- **What:** before T34/T35, `add John ...` and `add john ...` created two contacts.
  Since T34/T35 names are compared without case, so `John` and `john` are one contact.
- **Effect:** an old `contacts.json` that has both `John` and `john` can't be loaded
  into one address book. Storage treats the whole file as broken: it is renamed to
  `contacts.<date>-<time>.bak`, the app starts with empty contacts and shows
  `Data file was broken, starting empty. Old data is in: ...`. No data is lost,
  but it is not visible in the app.
- **Who is affected:** only data created by development builds before 25 Nov
  (team members' local files). A clean install is not affected.
- **Workaround:** open the `.bak` file, merge or rename the duplicate contact,
  save it as `~/.personal_assistant/contacts.json`.
- **Possible fix (after submission):** when loading, merge contacts whose names
  differ only in case instead of moving the whole file to `.bak`.
- **Decision:** documented, not fixed before submission (Lead, 25 Nov).

### KI-2. One invalid old contact hides the whole address book (E9)

- **What:** T34 added new rules (name needs a letter, birthday from 1900).
  Old data created before these rules can break them.
- **Effect:** checked on `main` 26c5eb5: a `contacts.json` with one contact named
  `123` (or with birthday `01.01.1899`, or phone `123`) and a valid contact `Bob`
  is moved to `.bak` as a whole. The app starts with empty contacts, so Bob is
  not visible either. No data is lost: it is in the `.bak` file.
- **Who is affected:** only data created by development builds before T34.
- **Workaround:** fix or remove the invalid contact in the `.bak` file and save it
  as `~/.personal_assistant/contacts.json`.
- **Open question:** recovery policy for old data is discussed in #34 (Lead review):
  load valid contacts and keep the original file. Update E9/E10 after #34.

## Result

| Section | Pass | Fail | Known issue | Notes |
|---------|------|------|-------------|-------|
| A. Repository, docs, install | | | | |
| B. CLI loop and usability | | | | |
| C. Contacts | | | | |
| D. Notes | | | | |
| E. Persistence | | | | |
| F. Bonus: tags | | | | |
| G. Bonus: intelligent analysis | | | | |
| H. Code quality | | | | |
| I. Submission | | | | |

Run by: ______  Date: ______  Commit: ______
