# Demo dataset and setup

`demo/demo_commands.txt` fills the assistant with a reproducible demo dataset for the Live Demo:

- **10 contacts** with phone, email, address and birthday (Olivia and Lucas have two phones);
- **10 notes**, 8 of them tagged (`birthday`, `health`, `shopping`, `study`, `travel`, `work`), 2 without tags.

All data is **synthetic**: invented names, made-up phone numbers, `@example.com` emails and sample addresses.

The dataset is loaded into a **new, dedicated demo profile** in the temporary folder. The real data folder
`~/.personal_assistant` is used only if the profile check below is skipped or ignored, so **load and start the
demo only after the check prints `OK`**. Use a separate terminal for the demo and close it afterwards: the
profile change applies only to that terminal.

Run all commands from the **repository root**, after the [Quick start](../README.md#quick-start) installation
(virtual environment created and `python -m pip install .` done).

Checked on Windows 11 (PowerShell 5.1, Python 3.13) on top of `71552c0`.

## Profile check (used in steps 1 and 2)

The check passes only if the assistant's data folder is exactly `<demo profile>/.personal_assistant` and the
demo profile is an existing `pa-demo-*` folder. It prints `OK: <path>` or `STOP: <path>`.

```text
import os,sys,pathlib; from assistant.storage import DATA_DIR as d; e=os.environ.get('PA_DEMO_HOME',''); h=pathlib.Path(e).resolve(); ok=bool(e) and h.is_dir() and h.name.startswith('pa-demo-') and d.name=='.personal_assistant' and d.parent.resolve()==h; print(('OK: ' if ok else 'STOP: ')+str(d)); sys.exit(0 if ok else 1)
```

The commands below already contain it; you do not need to copy it separately.

## 1. Create a demo profile and load the dataset

### Windows PowerShell (regular window, repository root)

Create a new profile (fails if the folder cannot be created) and note the printed path:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\.venv\Scripts\Activate.ps1
$demoHome = Join-Path $env:TEMP ("pa-demo-" + (Get-Date -Format yyyyMMdd-HHmmss))
New-Item -ItemType Directory -Path $demoHome -ErrorAction Stop | Out-Null
$env:PA_DEMO_HOME = $demoHome
$env:USERPROFILE = $demoHome
$demoHome
```

Verify the profile:

```powershell
python -c "import os,sys,pathlib; from assistant.storage import DATA_DIR as d; e=os.environ.get('PA_DEMO_HOME',''); h=pathlib.Path(e).resolve(); ok=bool(e) and h.is_dir() and h.name.startswith('pa-demo-') and d.name=='.personal_assistant' and d.parent.resolve()==h; print(('OK: ' if ok else 'STOP: ')+str(d)); sys.exit(0 if ok else 1)"; $demoOk = ($LASTEXITCODE -eq 0)
```

Load the dataset (runs only after `OK`):

```powershell
if ($demoOk) { cmd /c "assistant < demo\demo_commands.txt" } else { "STOP: demo profile not verified, nothing loaded" }
```

### macOS / Linux (bash or zsh, repository root)

```bash
source .venv/bin/activate
DEMO_HOME="$(mktemp -d "${TMPDIR:-/tmp}/pa-demo-XXXXXX")" && echo "$DEMO_HOME"
export PA_DEMO_HOME="$DEMO_HOME" HOME="$DEMO_HOME"
```

Verify the profile:

```bash
python -c "import os,sys,pathlib; from assistant.storage import DATA_DIR as d; e=os.environ.get('PA_DEMO_HOME',''); h=pathlib.Path(e).resolve(); ok=bool(e) and h.is_dir() and h.name.startswith('pa-demo-') and d.name=='.personal_assistant' and d.parent.resolve()==h; print(('OK: ' if ok else 'STOP: ')+str(d)); sys.exit(0 if ok else 1)"; demo_ok=$?
```

Load the dataset (runs only after `OK`):

```bash
if [ "$demo_ok" -eq 0 ]; then assistant < demo/demo_commands.txt; else echo "STOP: demo profile not verified, nothing loaded"; fi
```

The load should report 10 contacts, 10 notes and 10 tags added, without errors.
Load the dataset into a profile **only once**: running it again adds the same notes a second time (IDs 11–20).

## 2. Start the demo (new terminal)

The data stays in the demo profile between sessions. In a new terminal, point it at the **same** profile
(the path printed in step 1), verify it again and only then start the assistant.

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\.venv\Scripts\Activate.ps1
$demoHome = "<path printed in step 1>"
$env:PA_DEMO_HOME = $demoHome
$env:USERPROFILE = $demoHome
python -c "import os,sys,pathlib; from assistant.storage import DATA_DIR as d; e=os.environ.get('PA_DEMO_HOME',''); h=pathlib.Path(e).resolve(); ok=bool(e) and h.is_dir() and h.name.startswith('pa-demo-') and d.name=='.personal_assistant' and d.parent.resolve()==h; print(('OK: ' if ok else 'STOP: ')+str(d)); sys.exit(0 if ok else 1)"; $demoOk = ($LASTEXITCODE -eq 0)
if ($demoOk) { assistant } else { "STOP: demo profile not verified" }
```

macOS / Linux:

```bash
source .venv/bin/activate
DEMO_HOME="<path printed in step 1>"
export PA_DEMO_HOME="$DEMO_HOME" HOME="$DEMO_HOME"
python -c "import os,sys,pathlib; from assistant.storage import DATA_DIR as d; e=os.environ.get('PA_DEMO_HOME',''); h=pathlib.Path(e).resolve(); ok=bool(e) and h.is_dir() and h.name.startswith('pa-demo-') and d.name=='.personal_assistant' and d.parent.resolve()==h; print(('OK: ' if ok else 'STOP: ')+str(d)); sys.exit(0 if ok else 1)"; demo_ok=$?
if [ "$demo_ok" -eq 0 ]; then assistant; else echo "STOP: demo profile not verified"; fi
```

If the check prints `STOP`, do not start the assistant: fix the path and run the check again.

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

## 4. Start over with a clean dataset

Do not delete or reuse a profile to reset it. Close the demo terminal, open a new one and repeat **step 1**:
it creates a new, empty `pa-demo-<timestamp>` profile and loads the dataset there. Use the new path in step 2.

Old `pa-demo-*` profiles contain only synthetic demo data. They stay in the temporary folder until you remove
them manually after checking the exact path, or until the system cleans the temporary folder.
