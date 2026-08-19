"""Safe pip command construction and streaming execution; no shell is used."""
from __future__ import annotations

import re
import subprocess
from collections.abc import Callable

_REQUIREMENT = re.compile(
    r'^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?'
    r'(?:\[[A-Za-z0-9]+(?:[A-Za-z0-9._-]*[A-Za-z0-9])?'
    r'(?:,[A-Za-z0-9]+(?:[A-Za-z0-9._-]*[A-Za-z0-9])?)*\])?'
    r'(?:(?:===|==|!=|<=|>=|~=|<|>)[A-Za-z0-9][A-Za-z0-9.*+!._-]*)?$'
)
MIRRORS = {
    "",
    "https://pypi.org/simple",
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple/",
    "https://pypi.mirrors.ustc.edu.cn/simple/",
    "https://mirrors.huaweicloud.com/repository/pypi/simple/",
}
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def validate_requirement(value):
    return isinstance(value, str) and bool(_REQUIREMENT.fullmatch(value))


def validate_mirror(value):
    return value in MIRRORS


def pip_available(python):
    result = subprocess.run(
        [python, "-m", "pip", "--version"],
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=CREATE_NO_WINDOW,
    )
    return result.returncode == 0


def install(python: str, requirement: str, mirror: str, cwd, on_output: Callable[[str, str], None] | None = None):
    """Run one safe pip install command and stream merged output line by line."""
    if not validate_requirement(requirement):
        raise ValueError("Invalid package requirement.")
    if not validate_mirror(mirror):
        raise ValueError("Unsupported package index.")

    argv = [python, "-m", "pip", "install", "--disable-pip-version-check", "--no-input", requirement]
    if mirror:
        argv.extend(["--index-url", mirror])

    process = subprocess.Popen(
        argv,
        shell=False,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        creationflags=CREATE_NO_WINDOW,
    )
    output = []
    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\r\n")
        if not line:
            continue
        output.append(line)
        if on_output:
            on_output("error" if line.startswith(("ERROR:", "WARNING:")) else "output", line)
    return_code = process.wait()
    transcript = "\n".join(output)
    return return_code, transcript[-4000:]
