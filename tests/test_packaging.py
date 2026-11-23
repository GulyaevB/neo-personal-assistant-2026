"""Installation and executable entry-point smoke tests (T26).

CI installs the package before running pytest. The launch tests deliberately
use a different working directory to verify both supported entry points.
"""

import os
import shutil
import subprocess
import sys
from importlib.metadata import distribution

import pytest

from assistant.cli import main


def test_console_script_metadata_points_to_cli_main():
    package = distribution("neo-personal-assistant")
    scripts = [
        entry
        for entry in package.entry_points
        if entry.group == "console_scripts" and entry.name == "assistant"
    ]

    assert len(scripts) == 1
    assert scripts[0].value == "assistant.cli:main"
    assert scripts[0].load() is main
    assert package.metadata["Requires-Python"] == ">=3.10"


@pytest.mark.parametrize("entrypoint", ["console", "module"])
def test_installed_app_launches_outside_repository(tmp_path, entrypoint):
    if entrypoint == "console":
        executable = shutil.which("assistant")
        assert executable is not None, "Installed 'assistant' command not found"
        command = [executable]
    else:
        command = [sys.executable, "-m", "assistant"]

    # Use an isolated home directory to avoid touching the user's data files.
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)
    env["USERPROFILE"] = str(tmp_path)

    result = subprocess.run(
        command,
        input="exit\n",
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=env,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, (
        f"{entrypoint} entry point failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "Personal Assistant is running" in result.stdout
    assert "Goodbye!" in result.stdout
