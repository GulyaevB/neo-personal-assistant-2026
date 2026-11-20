# Contributing

Team guide: how we set up the project, write code and open PRs.
Questions about Ruff, tests or CI: ask Kate (Tests & Features).

## One-time setup

Requires Python 3.12 or newer.

```bash
git clone https://github.com/GulyaevB/neo-personal-assistant-2026.git
cd neo-personal-assistant-2026
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .                 # the project and its dependencies
pip install ruff pytest          # dev tools
```

Recommended: install the **Ruff** extension in VS Code and enable
"Format on Save". Your code will be formatted automatically.

## Workflow

1. Take a card from **To Do** in Trello and move it to **In Progress**
   (one card in progress per person).
2. Create a branch from the latest `main`:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/T11-notes-model
   ```

   Prefixes: `feature/` new functionality, `fix/` bug fix, `chore/` setup
   and tooling. Always include the task id.
3. One task = one branch = one PR. Do not mix tasks in one PR.
4. Run the checks below, then push and open a PR:
   - title: `[T11] Implement Note and NoteBook model`;
   - fill in the PR template, including the Trello card link;
   - add a reviewer in the GitHub **Reviewers** panel;
   - attach the PR to the Trello card (GitHub Power-Up) and move the card to
     **Review**.
5. Merge needs **1 approval** and **green CI**. Lead does the final merge.
   Move the card to **Done** only after the merge.

Everything in the repository is in English: code, comments, docstrings,
messages, commits, PRs.

## Before every PR

Run these commands from the project root:

```bash
ruff check --fix .     # fix what can be fixed automatically
ruff format .          # format the code
ruff check .           # must print "All checks passed!"
pytest                 # all tests must pass
```

If all of them are green, CI will be green too. CI runs the same checks on
every PR to `main` (Python 3.12).

## Ruff rules

Settings live in `pyproject.toml` (`[tool.ruff]`): rules E, W, F, I, N, B, UP,
line length 88, target Python 3.12. Change them only via a PR.

Ruff shows the file, line and rule code, for example:

```
E501 Line too long (95 > 88)
  --> assistant/fields.py:22:89
```

Common cases that need a manual fix:

| Code | Meaning | How to fix |
|------|---------|------------|
| E501 | Line longer than 88 characters | Split the line (Python joins strings in brackets) |
| F401 | Import is not used | Delete the import |
| F841 | Variable is assigned but never used | Delete the variable or use it |
| B904 | `raise` inside `except` without `from` | Add `from None` or `from err` |
| N802 | Function name is not snake_case | Rename: `getName` -> `get_name` |
| N818 | Exception name has no `Error` suffix | Rename: `NoteNotFound` -> `NoteNotFoundError` |

Look up any other rule: `ruff rule E501`. Do not silence a rule with `# noqa`
without a comment explaining why.

## Code agreements

Layers (see `assistant/__init__.py`):

| Layer | Files | Rule |
|-------|-------|------|
| models | `fields`, `record`, `address_book`, `notes`, `exceptions` | Store and validate data. Never `print()` or `input()`. Return objects. |
| storage | `storage` | Save and load JSON in `~/.personal_assistant/`. |
| handlers | `contact_handlers`, `note_handlers`, `tag_handlers` | One function per command. Return a string. |
| cli | `cli`, `commands`, `decorators`, `ui`, `context` | Main loop. Only this layer talks to the user, through `ui`. |

- **Handler signature:** `handler(args: list[str], ctx: Context) -> str`.
  `ctx.book` is the address book, `ctx.notes` is the notebook.
- **Registering a command:** add `@command("name")` and `@input_error` to the
  handler. The first line of the docstring is the help text.
- **Errors:** raise a subclass of `AssistantError` (`ValidationError`,
  `ContactNotFoundError`, `NoteNotFoundError`). Never raise plain
  `ValueError` / `KeyError` from models. `cli` shows the message with
  `ui.error()`.
- **Ids:** models take `int`. Handlers convert user input with `parse_id()`
  from `note_handlers.py`.
- **Output:** formatting and colors live in `ui.py` (`format_note`,
  `format_contact`). Delete commands ask `ui.confirm()` first.
- **Stubs:** unfinished code raises `NotImplementedError` with a
  `TODO(Txx)` comment. When you implement it, remove that `TODO`. Do not
  touch `TODO`s of other tasks.
- **Docstrings:** public classes and functions have English docstrings.

## Tests

- Tests live in `tests/`, files are named `test_*.py`.
- Models need tests; CLI commands can be checked by hand (describe how in the
  PR).
- Tests must not touch the real `~/.personal_assistant/` folder: use the
  `tmp_path` fixture for files.
- Cover edge cases: empty input, wrong id, wrong format, missing data.
