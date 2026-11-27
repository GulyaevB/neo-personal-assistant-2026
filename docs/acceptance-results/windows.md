# Acceptance results — Windows (T28)

Tester: Oksana · Windows 11 (build 26100) · Windows PowerShell 5.1.26100.9818 · Python 3.13.14
Commit: `cfc8074` (fresh clone, `pip install .` in a new venv) · Run folder: `%TEMP%\pa-acceptance-20261126-155218`
Date: Thu 26 Nov 2026 · Scope: "Platform coverage", Windows column
Retest: **A2 on `71552c0`** (after README PR #41; code unchanged since `cfc8074`), fresh clone in `%TEMP%\a2-check`, Fri 27 Nov 2026

Summary: all Windows rows ✅, including A2 after the README fix (#41) and retest on `71552c0`. No app defects found.
Rows outside the Windows scope are marked `—`.

## Notes for the checklist / README

- **N1 (A2, README T27):** in a regular Windows PowerShell window, `.\.venv\Scripts\Activate.ps1` from README Quick start fails with
  "running scripts is disabled on this system" (default ExecutionPolicy). The checklist mentions
  `Set-ExecutionPolicy -Scope Process RemoteSigned`, the README does not. (In the PyCharm terminal it works,
  so it is easy to miss.) Suggested README line before activation:
  `Set-ExecutionPolicy -Scope Process RemoteSigned` (this window only), or use `cmd` + `activate.bat`.
  **Resolved:** README PR #41 (`71552c0`) adds this line; A2 retested on Windows on `71552c0` ✅.
- **N2 (E12 appendix, PowerShell):** the multi-line `if { } / else { }` block fails when pasted into PowerShell 5.1
  (`else : The term 'else' is not recognized`), because the `if` line runs on its own. Working one-line version:
  `need-data; $baks = @(Get-ChildItem -LiteralPath $DATA -Filter 'contacts.*.bak'); if ($baks.Count -ne 1) { "FAIL: expected 1 backup, found $($baks.Count)" } else { $orig = (Get-FileHash -Algorithm SHA256 (Join-Path $env:USERPROFILE original-contacts.json)).Hash; $bak = (Get-FileHash -Algorithm SHA256 $baks[0].FullName).Hash; if ($orig -eq $bak) { "OK: identical, $bak" } else { "FAIL: $orig != $bak" } }`
- **N3 (H7, PowerShell):** `-Pattern "TODO\|NotImplementedError"` searches for a literal `|`, so it prints nothing even if a TODO exists.
  Correct: `-Pattern "TODO|NotImplementedError"` (used in this run).
- **Dates (step 3):** the run was on Thursday 26 Nov, so John's birthday was `29.11.1990` (Sun) instead of `30.11.1990`;
  Anna `28.11.1990` (Sat) unchanged.

---

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
| ⛔ Blocked | Can't be checked: a dependency is missing or a safety check printed `STOP` |
| ⏭ Exception | The Lead approved this row as an exception; the link to the decision is in the evidence column |

Every row that is not ⬜ needs evidence in the last column: a screenshot name,
a link to the T28 card attachment, a CI run link or a `BUG:` card. Green CI
alone is not acceptance: a row is ✅ only after it was checked on a real run.

**Sign-off rule.** T28 is Done only when, **on every platform** in "Platform
coverage", every row assigned to that platform is ✅ with evidence, or ⏭ with
an individually documented Lead-approved exception. Any ⬜, ⛔ or ❌ left in a
row assigned to a platform blocks sign-off. Accepted limitations (see the end
of the file) are expected behaviour: their rows are ✅ when the behaviour
matches.

## Platform coverage

Each platform keeps its **own** results: fill a copy of this file per platform
(`docs/acceptance-results/macos.md`, `docs/acceptance-results/windows.md`)
in the results PR. This file stays the empty template.

| Section | macOS (Kate) | Windows (Oksana) |
|---------|--------------|------------------|
| A. Repository, install | A1–A6 | A2, A4, A5, A7 |
| B. CLI loop | B1–B14 (`printf` pipe in B12, B14) | B1–B14 (PowerShell pipe and `cmd.exe` in B12, B14) |
| C. Contacts (E2E) | all | all |
| D. Notes (E2E) | all | all |
| E. Persistence and old data (E2E) | all, bash commands | all, PowerShell commands |
| F. Tags (E2E) | all | all |
| G. Command suggestions | all | all |
| H. Code quality | H1–H11 | H2, H3, H7, H8, H10, H11 |
| I. Release gates | Kate with the Lead | — |

Mapping to the cross-platform checklist on the Trello card T28:

| Trello item | Rows |
|-------------|------|
| Testers, OS/version, Python, exact commit | Run log, "How to run" step 4 |
| Safety preflight, isolated `DATA_DIR`, verified paths | "How to run" step 1, `section` on every section |
| Clean install, both entry points outside the repo | A2, A4, A5 (A7 on Windows) |
| Interactive Tab / colors / history, redirected stdin/stdout | B7–B9, B13, B12, B14 |
| Contacts, birthdays, notes, tags, invalid input, cancellation, Cyrillic | C, D, F (C26, D10 cancellation; D1, D3, E5 Cyrillic) |
| Persistence / restart and #34 recovery | E1–E13 |
| Ruff lint/format and pytest | H2, H3 |
| README-only onboarding on both platforms | A2 |
| BUG cards, owners, retest on the affected OS, Lead decisions | "How to run" steps 5–6, ⏭ exceptions |
| Final sign-off, hand-off to T29 | Sign-off rule, I1–I5 |

If the Trello checklist changes, update this table and the rows before the run.

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
python3 --version          # must be 3.12 or newer
python3 -m venv .venv
source .venv/bin/activate
pip install .

ACCEPTANCE_RUN="$(mktemp -d)" && [ -d "$ACCEPTANCE_RUN" ] \
  && export ACCEPTANCE_RUN && echo "Run folder: $ACCEPTANCE_RUN" \
  || { ACCEPTANCE_RUN=""; echo "STOP: mktemp failed"; }

section() {
  DATA=""
  [ -n "$ACCEPTANCE_RUN" ] && [ -d "$ACCEPTANCE_RUN" ] || { echo "STOP: no run folder"; return 1; }
  export HOME="$ACCEPTANCE_RUN/$1"
  mkdir -p "$HOME" || { echo "STOP: mkdir failed"; return 1; }
  expected="$HOME/.personal_assistant"
  actual="$(python -c 'from assistant.storage import DATA_DIR; print(DATA_DIR)')" \
    || { echo "STOP: python failed"; return 1; }
  if [ "$actual" = "$expected" ]; then
    DATA="$actual"; echo "OK, test data folder: $DATA"
  else
    echo "STOP: app uses $actual, expected $expected"; return 1
  fi
}
section A
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/GulyaevB/neo-personal-assistant-2026.git acceptance-run
cd acceptance-run
py -3 --version            # must be 3.12 or newer (see README)
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install .

$env:ACCEPTANCE_RUN = Join-Path $env:TEMP "pa-acceptance-$(Get-Date -Format yyyyMMdd-HHmmss)"
try { New-Item -ItemType Directory $env:ACCEPTANCE_RUN -ErrorAction Stop | Out-Null; "Run folder: $env:ACCEPTANCE_RUN" }
catch { $env:ACCEPTANCE_RUN = $null; "STOP: New-Item failed" }

function need-data { if (-not $global:DATA) { throw "STOP: `$DATA is not verified, run section first" } }

function section($name) {
  $global:DATA = $null
  if (-not $env:ACCEPTANCE_RUN -or -not (Test-Path -LiteralPath $env:ACCEPTANCE_RUN -PathType Container)) { "STOP: no run folder"; return }
  $dir = Join-Path $env:ACCEPTANCE_RUN $name
  try { New-Item -ItemType Directory -Force $dir -ErrorAction Stop | Out-Null } catch { "STOP: New-Item failed"; return }
  $env:USERPROFILE = $dir
  $env:HOME = $dir
  $expected = Join-Path $dir ".personal_assistant"
  $actual = python -c "from assistant.storage import DATA_DIR; print(DATA_DIR)"
  if ($LASTEXITCODE -ne 0) { "STOP: python failed"; return }
  if ($actual -eq $expected) { $global:DATA = $actual; "OK, test data folder: $DATA" }
  else { "STOP: app uses $actual, expected $expected" }
}
section A
```

If `Activate.ps1` is blocked, run `Set-ExecutionPolicy -Scope Process RemoteSigned`
first (only for this PowerShell window).

**Safety rule (fail closed):** `section` asks the app itself where it will keep
data (`assistant.storage.DATA_DIR`) and accepts it only if it is **exactly**
`<run folder>/<section>/.personal_assistant`. Only then `$DATA` is set and it
prints `OK, test data folder: ...`. If `mktemp`/`New-Item`, `mkdir` or Python
fails, or the path is different, it prints `STOP` and `$DATA` stays empty.
After `STOP`, do not continue: mark the rows ⛔ and report it.

**All file operations in this checklist use the verified `$DATA`, never `~`.**
In PowerShell, `~` keeps pointing to your real home folder even after
`USERPROFILE` is changed. The commands are written so they **refuse to run**
without a verified path: bash uses `"${DATA:?}"` (error if `$DATA` is empty),
PowerShell starts each file command with `need-data`.

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
- Take a screenshot for every ❌, ⛔, ⏭ row and for E2, E6, F10.
  Attach them to the T28 card and put the file name in the last column.

### 5. Bugs

For every ❌ create a Trello card `BUG: <short title>` with: check ID, platform,
commit, steps, expected result, actual result, screenshot, owner of the module.
Put the card name in the last column and post it in Slack. After the fix, retest
the row **on the platform where it failed** (and on the other one if the fix
touches shared code). A deferral needs an explicit Lead decision, linked in the
row (⏭).

### 6. Retest

If a fix is merged after the run, retest only the affected rows on the new
commit and update their status and evidence. #34 (strict email + legacy-data
recovery) and README #28 are already in `main` (12319c5), so A2, A3, C7 and
E8–E13 are checked in the normal run.

### 7. Clean up

Close the terminal. No cleanup command is part of this checklist: the run
folder is in the system temp folder and is cleaned by the OS. If you want to
delete it earlier, do it by hand in Finder / Explorer after checking that the
path is the one printed as `Run folder:` at the start.

## A. Repository, documentation, installation

Setup: `section A`.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| A1 | Open the GitHub repo in a private browser window | Repo is public | AC-1 | T01 | — | not in Windows scope (Platform coverage) |
| A2 | Follow only `README.md` ("Quick start") to install and start the app | Install and run steps work as written | AC-2 | T27 | ✅ | Retest on `71552c0` (after #41): fresh clone, README Windows PowerShell Quick start step by step (incl. `Set-ExecutionPolicy`), venv activated, `pip install .`, isolated `DATA_DIR`, both entry points with piped input from `%TEMP%` work. win_A2-retest-1.png, win_A2-retest-2.png. On `cfc8074` activation failed without `Set-ExecutionPolicy` (note N1) |
| A3 | Compare README "Command reference" with `help` | All 25 commands from `help` are documented with an example | AC-2, PL | T27 | — | not in Windows scope (Platform coverage) |
| A4 | `pip install .` in a clean venv | Installs without errors, pulls `prompt_toolkit` | PL | T26 | ✅ | console log |
| A5 | From another folder (`cd ~`) run `assistant`, `exit`, then `python -m assistant`, `exit` | Both entry points start the app and say `Goodbye!` | PL | T26 | ✅ | console log (`cd ~` = C:\Users\Administrator) |
| A6 | Public classes and functions have docstrings | Spot check models, handlers, cli | AC-2 | all | — | not in Windows scope (Platform coverage) |
| A7 | Windows: steps from "How to run" in PowerShell, then `assistant` | Starts, colors and Tab work | PL | T33 | ✅ | A7-windows-colors.png; Tab, colors |

## B. CLI loop and usability

Setup: `section B`, start `assistant`. Before B8 run `add John 0501234567`.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| B1 | Start the app | `Personal Assistant is running. Type 'exit' to quit.` shown **once** | AC-6 | T17 | ✅ | console log |
| B2 | Run 3 commands in a row (`help`, `all`, `all-notes`) | Greeting is **not** repeated after each command | AC-6 | T17 | ✅ | console log |
| B3 | `help` | `Available commands:` + 25 commands with a short description | AC-6, PL | T18 | ✅ | console log |
| B4 | Press Enter on empty input | Nothing happens, prompt is shown again | AC-10 | T17 | ✅ | console log |
| B5 | `xyz` | `Unknown command 'xyz'.`, app keeps running | AC-10 | T17 | ✅ | console log |
| B6 | `add` without arguments | `Missing arguments. Use: add <name> <phone>`, no traceback | AC-10 | T23 | ✅ | console log |
| B7 | `bi` + Tab | Completes to `birthdays` | AC-6 | U1 | ✅ | Tab checked by tester |
| B8 | `phone J` + Tab | Completes to `phone John` | AC-6 | U1 | ✅ | Tab checked by tester |
| B9 | Look at B5, B6, B8 output | Success green, errors red, commands and tags highlighted | AC-6 | U2 | ✅ | colors checked by tester |
| B10 | `exit`; start again, `close` | `Goodbye!`, app stops (both commands) | AC-7 | T17 | ✅ | console log |
| B11 | Start, press Ctrl+C; start, press Ctrl+D | App stops without traceback | AC-9 | T17 | ✅ | console log |
| B12 | Without a console. macOS/Linux: `printf 'help\nexit\n' \| assistant`. PowerShell: `"help","exit" \| assistant`. cmd.exe: `assistant < commands.txt` | Help and `Goodbye!` printed, no `NoConsoleScreenBufferError`, no traceback | AC-9 | T33 | ✅ | PowerShell pipe and `cmd /c "assistant < commands.txt"` |
| B13 | Interactive console: run `help`, `all`, then press ↑ twice | The previous commands come back (`all`, then `help`); Enter runs the shown command | AC-6 | U1 | ✅ | history ↑ checked by tester |
| B14 | Redirected stdout. macOS/Linux: `printf 'help\nexit\n' \| assistant > "$HOME/out.txt"; cat "$HOME/out.txt"`. PowerShell: `"help","exit" \| assistant > (Join-Path $env:USERPROFILE out.txt); Get-Content (Join-Path $env:USERPROFILE out.txt)` | The file has the help text and `Goodbye!`, no traceback, the console stays clean | AC-9 | T33 | ✅ | console log |

## C. Contacts

Setup: `section C`, start `assistant`, run the rows in this order without restarting.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| C1 | `add John 0501234567` | `Contact 'John' added.` | TZ-1 | T19 | ✅ | console log |
| C2 | `add john 0671112233`, then `all` | `Phone added to 'John'.`; `all` shows **one** John with `0501234567; 0671112233` | TZ-1 | T35 | ✅ | console log |
| C3 | `add John 0501234567` (same phone) | `Contact 'John' already has phone '0501234567'.` | AC-12 | T35 | ✅ | console log |
| C4 | `add Anna 123` | `Invalid phone '123'. Use 10 digits.` (Anna is not created) | TZ-3, AC-12 | T05, T19 | ✅ | console log |
| C5 | `add 123 0501234567` | `Invalid name '123'. Use at least one letter.` | AC-12 | T34 | ✅ | console log |
| C6 | `add-email John john@mail.com` | `Email set for 'John'.` | TZ-1 | T06, T19 | ✅ | console log |
| C7 | `add-email John john@mail` | `Invalid email 'john@mail'. Use name@domain.com.`, email stays `john@mail.com` | TZ-3, AC-12 | T06 | ✅ | console log |
| C7b | `add-email John a..b@c.com`, then `all` | `Invalid email 'a..b@c.com'. Use name@domain.com.`; `all` still shows `john@mail.com`. If the email **was** changed (❌), run `add-email John john@mail.com` before C15, so the next rows are not affected | AC-12 | T34 | ✅ | console log |
| C8 | `add-address John Kyiv, Khreshchatyk 1` | `Address set for 'John'.` | TZ-1 | T06, T19 | ✅ | console log |
| C9 | `add-birthday John 30.11.1990` | `Birthday set for 'John'.` | TZ-1 | T07, T19 | ✅ | run on Thu 26 Nov: John `29.11.1990` (step 3 rule) |
| C10 | `add-birthday John 31.02.1990`, `add-birthday John 1990-05-15` | `Invalid date '...'. Use DD.MM.YYYY.` | AC-12 | T05, T07 | ✅ | console log |
| C11 | `add-birthday John 01.01.2090` | `Birthday '01.01.2090' is in the future.` | AC-12, PL | T07 | ✅ | console log |
| C12 | `add-birthday John 01.01.1899` | `Birthday '01.01.1899' is too old. Use 1900 or later.` | AC-12 | T34 | ✅ | console log |
| C13 | `phone john`, `show-birthday JOHN` | `John: 0501234567; 0671112233`, `John: 30.11.1990` (C10–C12 did not change it) | TZ-1 | T34 | ✅ | `John: 29.11.1990` (run on 26 Nov) |
| C14 | `add Anna 0931112233`, `add-birthday Anna 28.11.1990`, `all` | Anna and John with all their fields | TZ-1 | T19 | ✅ | console log |
| C15 | `search john` | John is found | TZ-4 | T09, T20 | ✅ | console log |
| C16 | `search 050123`, `search mail.com`, `search Kyiv` | John is found each time | TZ-4 | T09 | ✅ | console log |
| C17 | `search jhon` (typo) | John is found (fuzzy) | TZ-4, PL | T09 | ✅ | console log |
| C18 | `birthdays 7` | `Birthdays in the next 7 days:`, `28.11.2026 (Sat)  Anna`, `30.11.2026 (Mon)  John` | TZ-2 | T10, T20 | ✅ | `28.11.2026 (Sat)  Anna`, `29.11.2026 (Sun)  John` (run on 26 Nov) |
| C19 | Anna's line in C18 | Real date on Saturday, no shift to Monday (team decision in T10) | PL | T10 | ✅ | console log |
| C20 | `birthdays` (no argument) | Same list as C18 (default 7 days) | PL | T20 | ✅ | console log |
| C21 | `birthdays abc`, `birthdays 0` | `Invalid days 'abc'. Use a positive number.` / `Invalid days '0'. ...` | AC-10, PL | T20 | ✅ | console log |
| C22 | Year boundary (25 Dec → 2 Jan) and 29 Feb in a non-leap year | Can't be reproduced by hand on 27 Nov: `pytest tests/test_birthdays.py -v` passes `test_january_birthdays_on_25_december` and `test_leap_day_birthday` | TZ-2, PL | T10 | ✅ | 7 passed, incl. both named tests |
| C23 | `change John 0501234567 0509998877` | `Phone updated for 'John'.` | TZ-5 | T19 | ✅ | console log |
| C24 | `change John 1111111111 0509998877` | `Contact 'John' has no phone '1111111111'.` | TZ-5, AC-10 | T05 | ✅ | console log |
| C25 | `remove-phone John 0671112233`, `phone John` | `Phone removed from 'John'.`, `John: 0509998877` | TZ-5 | T07, T19 | ✅ | console log |
| C26 | `delete John` → `n`; repeat with Enter and with Ctrl+C | `Deletion cancelled.`, `phone John` still works | TZ-5 | U4 | ✅ | console log |
| C27 | `delete John` → `y`, then `phone John` | `Contact 'John' deleted.`, then `Contact 'John' not found.` | TZ-5 | T08, U4 | ✅ | console log |
| C28 | `delete Nobody` | `Contact 'Nobody' not found.` | AC-10 | T08 | ✅ | console log |

## D. Notes

Setup: `section D`, start `assistant`, run the rows in this order.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| D1 | `add-note Buy a gift for Anna`, `add-note Call the dentist`, `add-note Купити молоко` | `Note 1 added.`, `Note 2 added.`, `Note 3 added.` | TZ-6 | T11, T21 | ✅ | console log |
| D2 | `add-note` | `Missing arguments. Use: add-note <text>`, nothing saved | AC-12 | T11, T21 | ✅ | console log |
| D3 | `all-notes` | `1: Buy a gift for Anna`, `2: Call the dentist`, `3: Купити молоко` (Cyrillic shown correctly) | TZ-6 | T21, T25 | ✅ | console log |
| D4 | `search-notes GIFT` | `1: Buy a gift for Anna` (any case, part of a word) | TZ-7 | T12, T21 | ✅ | console log |
| D5 | `search-notes python` | `No notes found for 'python'.` (not an error) | TZ-7 | T12, T21 | ✅ | console log |
| D6 | `edit-note 1 Buy flowers` | `Note 1 updated.` | TZ-8 | T11, T21 | ✅ | console log |
| D7 | `edit-note 1` | `Missing arguments. Use: edit-note <id> <text>`, text stays `Buy flowers` | AC-10 | T11, T21 | ✅ | console log |
| D8 | `edit-note 99 text`, `delete-note 99` | `Note with id 99 not found.` | AC-10 | T11 | ✅ | console log |
| D9 | `edit-note abc text` | `Invalid note id 'abc'. Use a number.` | AC-10, PL | T21 | ✅ | console log |
| D10 | `delete-note 3` → `n`, then `delete-note 3` → `y` | `Delete note 3: Купити молоко? (y/n)`; `Deletion cancelled.`; then `Note 3 deleted.` | TZ-8 | T21, U4 | ✅ | rerun in `section D2` (first run answered n twice) |
| D11 | `add-note New note`, `all-notes` | `Note 4 added.` (id 3 is not reused); list 1, 2, 4 | PL | T11 | ✅ | rerun in `section D2`: `Note 4 added.`, list 1, 2, 4 |

## E. Persistence and old data

### E1–E7: saving and loading

Setup: `section E`. Check that the data folder does not exist yet:
`ls -a "${DATA:?}"` ("No such file") / `need-data; Test-Path $DATA` (`False`).

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| E1 | Start the app, `exit`, then `ls "${DATA:?}"` / `need-data; Get-ChildItem $DATA` | Starts with empty data; after exit the folder has `contacts.json` and `notes.json` | TZ-data, PL | T16 | ✅ | console log |
| E2 | Start, `add John 0501234567`, `add-note Купити молоко`, `exit`; start again, `all`, `all-notes` | John and `1: Купити молоко` are there | TZ-data, AC-8 | T16, T17 | ✅ | win_E2.png |
| E3 | `add Anna 0931112233`, then Ctrl+C; start again, `phone Anna` | `Anna: 0931112233` (saved on Ctrl+C) | AC-8, PL | T17 | ✅ | console log |
| E4 | `add-note Second` | `Note 2 added.` (`next_id` kept after restart) | PL | T11, T16 | ✅ | console log |
| E5 | `exit`; `cat "${DATA:?}/contacts.json" "${DATA:?}/notes.json"` / `need-data; Get-Content -Encoding utf8 (Join-Path $DATA notes.json)` | Readable JSON, Cyrillic stored as letters (not `\u0406` escapes) | TZ-data | T16, T25 | ✅ | console log |
| E6 | Break notes: `echo "{not json" > "${DATA:?}/notes.json"` (PowerShell: `need-data; Set-Content -Path (Join-Path $DATA notes.json) -Value "{not json"`), start, `all`, `all-notes` | `Data file was broken, starting empty. Old data is in: .../notes.<date>-<time>.bak`; contacts still load; `No notes yet. ...` | AC-9, PL | T16, T34 | ✅ | win_E6.png; `notes.20261126-174644.bak` |
| E7 | `exit`, `ls "${DATA:?}"` / `need-data; Get-ChildItem $DATA` | New valid `notes.json` (empty list), the `.bak` file with `{not json` is kept | PL | T16 | ✅ | console log |

### E8–E13: old data files (legacy)

Recovery contract accepted by the Lead in the #34 review and merged
(`main` 12319c5): valid contacts are loaded, contacts that break the current
rules are **skipped**, the startup message names them and the original file is
**copied** to `.bak`; an unreadable file is **moved** to `.bak`. These rows
check that contract; KI-1 and KI-2 are accepted limitations of it.

Setup for each row: `section E8`, `section E9a`, ... (a new empty folder each
time, `OK` required), create both fixtures from the appendix (`contacts.json`
for the row + the shared `notes.json`), start the app, `all`, `all-notes`,
`exit`, then run the E12 backup check from the appendix.

| ID | Fixture | Expected | Source | Task | Status | Evidence / Defect |
|----|---------|----------|--------|------|--------|-------------------|
| E8 | `John` and `john` as two contacts (created before T34/T35) | Startup: `Contacts not loaded: john. Original file copied to: .../contacts.<date>-<time>.bak`; `all` shows John with `0501234567` only (see KI-1) | PL | T34, T35 | ✅ | `Contacts not loaded: john.` |
| E9a | Name `123` (valid before T34) next to valid `Bob` | `Contacts not loaded: 123. ...`; `all` shows Bob | PL | T34 | ✅ | `Contacts not loaded: 123.` |
| E9b | Birthday `01.01.1899` (valid before T34) next to valid `Bob` | `Contacts not loaded: Ann. ...`; `all` shows Bob | PL | T34 | ✅ | `Contacts not loaded: Ann.` |
| E10 | Email `a..b@c.com` (valid before #34) next to valid `Bob` | `Contacts not loaded: John. ...`; `all` shows Bob; John is in the `.bak` copy | PL | T34 | ✅ | `Contacts not loaded: John.`; win_E10.png (E10, E11: `OK: identical` SHA-256, one `.bak`) |
| E11 | Phone `123` next to valid `Bob` (this phone was **always** invalid, a damaged record, not old data) | `Contacts not loaded: Ann. ...`; `all` shows Bob | AC-9 | T16, T34 | ✅ | `Contacts not loaded: Ann.`; win_E10.png |
| E12 | For each of E8–E11 | Notes are not affected: `all-notes` shows `1: Keep me [home]`, no `notes.*.bak`. After `exit`: `contacts.json` has only the loaded contacts; exactly **one** `contacts.*.bak`, and its SHA-256 equals the SHA-256 of the fixture (appendix: `shasum -a 256` / `Get-FileHash`) | PL | T16, T34 | ✅ | E8–E11: `OK: identical` (SHA-256), one `contacts.*.bak`, no `notes.*.bak`; check run as one line (note N2) |
| E13 | `pytest tests/test_storage.py -k test_backups_in_same_second_are_all_kept -v` | `2 passed`: two backups in the same second are both kept, for the **move** path (unreadable file) and the **copy** path (skipped contacts); each `.bak` keeps its original bytes | PL | T34 | ✅ | 2 passed |

## F. Bonus: tags (10 points)

Setup: `section F`, start `assistant`, `add-note Buy milk`, `add-note Call boss`,
`add-note Read book` (notes 1, 2, 3). Run the rows in this order.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| F1 | `add-tag 1 Shopping` | `Tag 'shopping' added to note 1.` | TZ-B, AC-B1 | T13, T22 | ✅ | win_F.png |
| F2 | `add-tag 1 shopping` | `Note 1 already has tag 'shopping'.` | AC-B1 | T13, T22 | ✅ | win_F.png |
| F3 | `add-tag 1 #tag!` | `Invalid tag '#tag!'. Use one word: letters, digits, _ or -.` | AC-12 | T13 | ✅ | win_F.png |
| F4 | `add-tag 2 work` | `Tag 'work' added to note 2.` | AC-B1 | T13, T22 | ✅ | win_F.png |
| F5 | `search-tag SHOPPING` | Only `1: Buy milk [shopping]` | TZ-B, AC-B2 | T13, T22 | ✅ | win_F.png |
| F6 | `search-tag travel` | `No notes with tag 'travel'.` | AC-B2 | T22 | ✅ | win_F.png |
| F7 | `sort-notes` | `1: Buy milk [shopping]`, `2: Call boss [work]`, `3: Read book` (untagged last) | TZ-B, AC-B2 | T14, T22 | ✅ | win_F.png |
| F8 | `edit-note 1 Buy oat milk`, `all-notes` | `1: Buy oat milk [shopping]` (tags kept after edit) | TZ-8 | T11, T21 | ✅ | win_F.png |
| F9 | `remove-tag 1 shopping`, then again | `Tag 'shopping' removed from note 1.` / `Note 1 has no tag 'shopping'.` | AC-B1 | T13, T22 | ✅ | win_F.png |
| F10 | `exit`, start again, `all-notes` | `2: Call boss [work]` (tags kept after restart) | AC-8 | T16 | ✅ | win_F.png (F1–F10 in one session, restart shows `2: Call boss [work]`) |

## G. Bonus: intelligent analysis

Setup: `section G`, start `assistant`.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| G1 | `ad John 0501234567` | `Unknown command 'ad'. Did you mean: add?` | TZ-B | U3 | ✅ | console log |
| G2 | `birthdys 7` | `Unknown command 'birthdys'. Did you mean: birthdays, ...?` (`birthdays` first) | TZ-B | U3 | ✅ | console log |
| G3 | `qwerty` | `Unknown command 'qwerty'.`, no wrong suggestion | TZ-B | U3 | ✅ | console log |

## H. Code quality and diagnostics

Run in the `acceptance-run` folder.

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| H1 | CI on the last `main` commit | `lint-and-test (3.12)` and `(3.15)` green (add the run link) | AC-13 | T04 | — | not in Windows scope (Platform coverage) |
| H2 | `pip install ruff pytest`, `ruff check .`, `ruff format --check .` | Clean | AC-13 | T03 | ✅ | `All checks passed!`, `44 files already formatted` |
| H3 | `pytest` on macOS/Linux **and** on Windows | All tests pass on both | AC-9 | T24, T25, T33 | ✅ | 493 passed (Windows) |
| H4 | OOP: `Field` → `Name`/`Phone`/`Email`/`Address`/`Birthday`; `AssistantError` → errors; `AddressBook`/`NoteBook` → `UserDict` | Inheritance used as planned | AC-11 | T02–T11 | — | not in Windows scope (Platform coverage) |
| H5 | Composition: `Record` has fields, `AddressBook` has `Record`, `NoteBook` has `Note`, `Context` has both books | Composition used as planned | AC-11 | T02 | — | not in Windows scope (Platform coverage) |
| H6 | Validation lives in field / model classes, not in handlers | Confirmed by code review | AC-12, PL | all | — | not in Windows scope (Platform coverage) |
| H7 | `grep -rnE "TODO\|NotImplementedError" assistant/` (PowerShell: `Select-String -Path assistant\*.py -Pattern "TODO\|NotImplementedError"`) | Prints nothing | AC-3 | all | ✅ | prints nothing with `-Pattern "TODO|NotImplementedError"` (note N3) |
| H8 | Unexpected error inside a command: `pytest tests/test_cli_errors.py -v` | All pass, including: traceback goes to `assistant.log` (`test_traceback_is_written_to_log`); no exception messages or arguments in the log (`test_exception_messages_are_not_logged`, `test_arguments_are_not_logged`); log can't be opened, or writing / rotation fails → CLI keeps running, nothing is printed to the console and the message does **not** say details were saved (`test_log_cannot_be_opened`, `test_log_write_or_rollover_fails`); logging works again after a failure (`test_log_works_again_after_a_failed_write`) | AC-9 | T32 | ✅ | 27 passed |
| H9 | Code review of `assistant/cli.py` | Log rotates: `RotatingFileHandler(maxBytes=1_000_000, backupCount=1)`; the log file is created only on the first unexpected error | PL | T32 | — | not in Windows scope (Platform coverage) |
| H10 | After sections A–G, list each section's data folder | No `assistant.log` after a normal run (no unexpected errors) | PL | T32 | ✅ | no `assistant.log` in any section folder |
| H11 | Whole run A–G | No traceback in the console | AC-9 | all | ✅ | no traceback in A–G |

## I. Release gates for T28 sign-off

| ID | Check | Expected | Source | Task | Status | Evidence / Defect |
|----|-------|----------|--------|------|--------|-------------------|
| I1 | Trello board | All mandatory cards are Done, **except** T28 itself, downstream T29/T30 and optional T31 | Team | Lead | ⬜ | |
| I2 | Legacy-data recovery contract (#34) and README (#28) | Merged in 12319c5; recovery contract accepted by the Lead in the #34 review (link in evidence); E8–E13 pass on both platforms | PL | T34, T27 | ⬜ | |
| I3 | Mentor code review of the final version | Project sent to the mentor in Slack by **Fri 27 Nov, 19:00**; comments handled or recorded | AC-14 | Lead | ⬜ | |
| I4 | Every row in "Platform coverage", per platform | ✅ with evidence, or ⏭ with a Lead-approved exception; no ⬜, ⛔ or ❌ left (sign-off rule) | PL | T28 | ⬜ | |
| I5 | Hand-off to T29 | The accepted commit (same on both platforms, final `main` CI green) is written on the T29 card and posted in Slack | PL | T28, T29 | ⬜ | |

T28 is Done only when I1–I5 are complete for both platforms and the evidence is recorded.

## J. After acceptance: delivery gates (not part of T28 sign-off)

| ID | Check | Expected | Task | Status | Evidence |
|----|-------|----------|------|--------|----------|
| J1 | Demo | Demo of the accepted version; demo day (project defence) on 30 Nov | T29 | ⬜ | |
| J2 | LMS submission | Zip of the repo + GitHub link uploaded by every member before 29 Nov, 17:00 Kyiv | T30 | ⬜ | |

## Accepted limitations

Part of the recovery contract accepted by the Lead in the #34 review (checked on
`main` 12319c5). They are expected behaviour, not open defects: the rows E8–E12
are ✅ when the behaviour matches.

### KI-1. Duplicate names in an old file are not merged (E8)

- **Behaviour:** before T34/T35 `add John ...` and `add john ...` created two
  contacts. Now names are compared without case, so on load the second one
  (`john`) is skipped and named in the startup message. Its phone `0671112233`
  is not in the app, only in the `.bak` copy.
- **Who is affected:** data created by development builds before T34/T35.
  A clean install is not affected.
- **Manual recovery:** open the `.bak` file and add the missing phones with
  `add John <phone>`.

### KI-2. Skipped old contacts are only in the `.bak` copy (E9a–E11)

- **Behaviour:** contacts that break the current rules are skipped and listed
  in the startup message; the original file is copied to `.bak`. When the user
  exits, the new `contacts.json` no longer has them.
- **Manual recovery:** take the data from the `.bak` file and add the contact
  again with valid values.

## Appendix: fixtures for E8–E12

Run `section <row>` first and continue only after `OK`. The commands refuse to
run without a verified `$DATA`.

macOS / Linux:

```bash
mkdir -p "${DATA:?}"
cat > "${DATA:?}/notes.json" <<'JSON'
{"next_id": 2, "notes": [{"id": 1, "text": "Keep me", "tags": ["home"], "created": "2026-11-20T10:00:00"}]}
JSON
cat > "${DATA:?}/contacts.json" <<'JSON'
<one fixture from below>
JSON
cp "${DATA:?}/contacts.json" "$HOME/original-contacts.json"   # for E12
```

Windows PowerShell:

```powershell
need-data
New-Item -ItemType Directory -Force $DATA | Out-Null
Set-Content -Encoding ascii -Path (Join-Path $DATA notes.json) -Value '{"next_id": 2, "notes": [{"id": 1, "text": "Keep me", "tags": ["home"], "created": "2026-11-20T10:00:00"}]}'
Set-Content -Encoding ascii -Path (Join-Path $DATA contacts.json) -Value '<one fixture from below>'
Copy-Item (Join-Path $DATA contacts.json) (Join-Path $env:USERPROFILE original-contacts.json)   # for E12
```

E12 backup check, after `exit` (raw bytes, SHA-256):

```bash
ls "${DATA:?}"/contacts.*.bak | wc -l          # must print 1
shasum -a 256 "$HOME/original-contacts.json" "${DATA:?}"/contacts.*.bak   # both hashes must be equal
```

```powershell
need-data
$baks = @(Get-ChildItem -LiteralPath $DATA -Filter 'contacts.*.bak')
if ($baks.Count -ne 1) { "FAIL: expected 1 backup, found $($baks.Count)" }
else {
  $orig = (Get-FileHash -Algorithm SHA256 (Join-Path $env:USERPROFILE original-contacts.json)).Hash
  $bak = (Get-FileHash -Algorithm SHA256 $baks[0].FullName).Hash
  if ($orig -eq $bak) { "OK: identical, $bak" } else { "FAIL: $orig != $bak" }
}
```

Contact fixtures (one line each):

- E8: `{"contacts": [{"name": "John", "phones": ["0501234567"], "email": null, "address": null, "birthday": null}, {"name": "john", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`
- E9a: `{"contacts": [{"name": "123", "phones": [], "email": null, "address": null, "birthday": null}, {"name": "Bob", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`
- E9b: `{"contacts": [{"name": "Ann", "phones": [], "email": null, "address": null, "birthday": "01.01.1899"}, {"name": "Bob", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`
- E10: `{"contacts": [{"name": "John", "phones": ["0501234567"], "email": "a..b@c.com", "address": null, "birthday": null}, {"name": "Bob", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`
- E11: `{"contacts": [{"name": "Ann", "phones": ["123"], "email": null, "address": null, "birthday": null}, {"name": "Bob", "phones": ["0671112233"], "email": null, "address": null, "birthday": null}]}`

## Result

| Section | ✅ | ❌ | ⛔ | ⏭ | ⬜ | Notes |
|---------|----|----|----|----|----|-------|
| A. Repository, docs, install | | | | | | |
| B. CLI loop and usability | | | | | | |
| C. Contacts | | | | | | |
| D. Notes | | | | | | |
| E. Persistence and old data | | | | | | |
| F. Bonus: tags | | | | | | |
| G. Bonus: intelligent analysis | | | | | | |
| H. Code quality and diagnostics | | | | | | |
| I. Release gates | | | | | | |

## Run log

| Tester | OS and version | Shell | Python | Commit | CI run | Sections | Date |
|--------|----------------|-------|--------|--------|--------|----------|------|
| Kate | macOS | zsh | | | | A–I | |
| Oksana | Windows 11 (build 26100) | Windows PowerShell 5.1.26100.9818 | 3.13.14 | cfc8074 | [CI #127](https://github.com/GulyaevB/neo-personal-assistant-2026/actions/runs/45813181777) | A2, A4, A5, A7, B1–B14, C, D, E, F, G, H2, H3, H7, H8, H10, H11 | 26 Nov 2026 |
| Oksana (A2 retest) | Windows 11 (build 26100) | Windows PowerShell 5.1.26100.9818 | 3.13.14 | 71552c0 | [CI ✓ 2/2 on 71552c0](https://github.com/GulyaevB/neo-personal-assistant-2026/commit/71552c0c71eef0e6c3d81ab93948bab017e0b2e6) | A2 | 27 Nov 2026 |