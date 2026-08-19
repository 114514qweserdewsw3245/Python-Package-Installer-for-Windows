"""Safe, bounded package-index latency checks for the Windows Agent."""
from __future__ import annotations

import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from .pip_manager import MIRRORS

MIRROR_LABELS = {
    "": "Official PyPI",
    "https://pypi.org/simple": "Official PyPI",
    "https://pypi.tuna.tsinghua.edu.cn/simple": "Tsinghua",
    "https://mirrors.aliyun.com/pypi/simple/": "Aliyun",
    "https://pypi.mirrors.ustc.edu.cn/simple/": "USTC",
    "https://mirrors.huaweicloud.com/repository/pypi/simple/": "Huawei",
}


def _probe(mirror: str) -> dict:
    base = mirror or "https://pypi.org/simple"
    url = base.rstrip("/") + "/pip/"
    started = time.perf_counter()
    request = urllib.request.Request(url, headers={"User-Agent": "Python-Package-Installer-for-Windows/0.7.5"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            status_code = response.status
            response.read(256)
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        return {"mirror": mirror, "label": MIRROR_LABELS[mirror], "available": 200 <= status_code < 400, "latency_ms": elapsed_ms, "status_code": status_code, "error": None}
    except (urllib.error.URLError, OSError, TimeoutError, KeyError) as exc:
        return {"mirror": mirror, "label": MIRROR_LABELS.get(mirror, mirror or "Official PyPI"), "available": False, "latency_ms": None, "status_code": None, "error": str(exc)[:240]}


def benchmark_mirrors() -> dict:
    """Probe only the fixed mirror allowlist; no package installation occurs."""
    mirrors = sorted(MIRRORS, key=lambda value: (value != "", value))
    with ThreadPoolExecutor(max_workers=len(mirrors)) as executor:
        results = list(executor.map(_probe, mirrors))
    results.sort(key=lambda item: (not item["available"], item["latency_ms"] if item["latency_ms"] is not None else float("inf")))
    recommended = next((item["mirror"] for item in results if item["available"]), "")
    return {"results": results, "recommended_mirror": recommended}
