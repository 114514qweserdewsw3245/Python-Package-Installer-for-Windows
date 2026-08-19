"""Safe Windows workspace and virtual-environment helpers."""
from __future__ import annotations
import subprocess
from pathlib import Path

class UnsafePathError(ValueError): pass

def safe_workspace(name: str, root: Path) -> Path:
    # UI only supplies a simple directory name; never accept arbitrary machine paths.
    if not isinstance(name,str) or not name or len(name)>64 or any(c in name for c in r'<>:"/\|?*') or name in ('.','..'):
        raise UnsafePathError('Workspace name is invalid.')
    root=root.resolve(); candidate=(root/name).resolve()
    if candidate.parent != root: raise UnsafePathError('Workspace must remain inside the application workspace root.')
    return candidate

def venv_python(venv_path: Path) -> Path: return venv_path/'Scripts'/'python.exe'
def validate_venv(venv_path: Path) -> Path:
    python=venv_python(venv_path.resolve())
    if not python.is_file(): raise UnsafePathError('Existing virtual environment does not contain Scripts\python.exe.')
    return python

def create_venv(base_python: str, workspace: Path) -> Path:
    workspace.mkdir(parents=True, exist_ok=True)
    venv=workspace/'.venv'; python=venv_python(venv)
    if python.is_file(): return python
    result=subprocess.run([base_python,'-m','venv',str(venv)],shell=False,cwd=str(workspace),capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode != 0 or not python.is_file():
        raise RuntimeError((result.stderr or result.stdout or 'Virtual environment creation failed.').strip()[:3000])
    return python
