# Demo dataset and setup

`demo/demo_commands.txt` fills the assistant with a reproducible demo dataset for the Live Demo:

- **10 contacts** with phone, email, address and birthday (Olivia and Lucas have two phones);
- **10 notes**, 8 of them tagged (`birthday`, `health`, `shopping`, `study`, `travel`, `work`), 2 without tags.

All data is **synthetic**: invented names, made-up phone numbers, `@example.com` emails and sample addresses.

The dataset is loaded into a **separate demo profile** in the temporary folder, so your real data in
`~/.personal_assistant` is never touched. Run all commands from the **repository root**, after the
[Quick start](../README.md#quick-start) installation (virtual environment created and `python -m pip install .` done).

Checked on Windows 11 (PowerShell 5.1, Python 3.13) at commit `71552c0`.

## 1. Load the dataset (once)

Windows PowerShell (regular window, from the repository root):

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\.venv\Scripts\Activate.ps1
$env:USERPROFILE = Join-Path $env:TEMP "pa-demo"
New-Item -ItemType Directory -Force $env:USERPROFILE | Out-Null
python -c "from assistant.storage import DATA_DIR; print(DATA_DIR)"
cmd /c "assistant < demo\demo_commands.txt"
```

macOS / Linux (bash or zsh, from the repository root):

```bash
source .venv/bin/activate
export HOME="${TMPDIR:-/tmp}/pa-demo"
mkdir -p "$HOME"
python -c 'from assistant.storage import DATA_DIR; print(DATA_DIR)'
assistant < demo/demo_commands.txt
```

Continue only if the printed path is inside the `pa-demo` folder and ends with `.personal_assistant`.

Load the dataset **only once**: running it again adds the same notes a second time (IDs 11–20).
To start over, see [Reset](#4-reset-to-a-clean-dataset).

## 2. Start the demo (any new terminal)

The data stays in the demo profile between sessions. Point the terminal at it again and start the assistant:

```powershell
# Windows PowerShell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\.venv\Scripts\Activate.ps1
$env:USERPROFILE = Join-Path $env:TEMP "pa-demo"
assistant
```

```bash
# macOS / Linux
source .venv/bin/activate
export HOME="${TMPDIR:-/tmp}/pa-demo"
assistant
```

Changing `USERPROFILE` / `HOME` affects only this terminal. Close it after the demo.

## 3. Quick check

| Command | Expected |
|---|---|
| `all` | 10 contacts: Ava, Emma, Ethan, Liam, Lucas, Mason, Mia, Noah, Olivia, Sophia |
| `phone olivia` | `Olivia: 0501112233; 0671112233` |
| `search kyiv` | Mason, Olivia |
| `birthdays` | on 30.11: Ava (30.11), Olivia (01.12), Liam (03.12), Noah (05.12) |
| `all-notes` | 10 notes, IDs 1–10 |
| `search-notes buy` | notes 1 and 5 |
| `search-tag work` | notes 2, 6, 8 |
| `sort-notes` | order 1, 3, 5, 2, 4, 7, 6, 8, 9, 10 (by first tag: birthday, health, shopping, study, travel, work; untagged last) |

`birthdays` depends on the current date. The birthdays are chosen for the defence on 30 November;
on another day use `birthdays 10` or another number of days.

## 4. Reset to a clean dataset

```powershell
# Windows PowerShell
Remove-Item -Recurse -Force (Join-Path $env:TEMP "pa-demo")
```

```bash
# macOS / Linux
rm -rf "${TMPDIR:-/tmp}/pa-demo"
```

Then repeat step 1.
