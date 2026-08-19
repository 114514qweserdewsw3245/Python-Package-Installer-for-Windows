"""Windows-only Python environment detection for V0.7.3."""
from __future__ import annotations
import os, platform, shutil, subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ALLOWED_COMMANDS = ("python", "py", "python3")

@dataclass
class PythonEnvironment:
    available: bool
    command: str | None
    executable: str | None
    version: str | None
    pip_available: bool
    pip_version: str | None
    architecture: str
    platform: str
    windows_only: bool
    error: str | None
    solutions: list[str]
    def to_dict(self) -> dict[str, Any]: return asdict(self)

def _run(argv: list[str], timeout: float = 10.0):
    return subprocess.run(argv, shell=False, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

def _empty(command, error, solutions):
    return PythonEnvironment(False, command, None, None, False, None, platform.architecture()[0], platform.platform(), os.name == "nt", error, solutions)

def detect_python(preferred: str | None = None) -> PythonEnvironment:
    if os.name != "nt": return _empty(None, "This installer agent supports Windows only.", ["Run Python-Package-Installer-for-Windows on Windows 10 or Windows 11."])
    if preferred and preferred not in ALLOWED_COMMANDS: return _empty(preferred, "Unsupported Python command.", ["Choose python, py, or python3."])
    candidates = ([preferred] if preferred else []) + [x for x in ALLOWED_COMMANDS if x != preferred]
    for command in candidates:
        executable = shutil.which(command)
        if not executable: continue
        try: vr = _run([executable, "--version"])
        except (OSError, subprocess.SubprocessError): continue
        version = (vr.stdout or vr.stderr).strip()
        if vr.returncode != 0 or not version: continue
        try: pr = _run([executable, "-m", "pip", "--version"]); pip_text = (pr.stdout or pr.stderr).strip(); pip_ok = pr.returncode == 0
        except (OSError, subprocess.SubprocessError): pip_text, pip_ok = "", False
        solutions = [] if pip_ok else ["Run: " + executable + " -m ensurepip --upgrade", "Then run: " + executable + " -m pip install --upgrade pip"]
        return PythonEnvironment(True, command, str(Path(executable).resolve()), version, pip_ok, pip_text or None, platform.architecture()[0], platform.platform(), True, None if pip_ok else "Python was found, but pip is unavailable.", solutions)
    return _empty(preferred, "Python was not found.", ["Install Python for Windows from https://www.python.org/downloads/windows/.", "Select Add python.exe to PATH during installation.", "Restart the Agent after installation."])

if __name__ == "__main__":
    import json
    print(json.dumps(detect_python().to_dict(), ensure_ascii=False, indent=2))
