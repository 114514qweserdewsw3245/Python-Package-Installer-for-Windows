"""Thread-safe task state and append-only live events for V0.7.3."""
from __future__ import annotations

import copy
import threading
import uuid
from datetime import datetime, timezone


class TaskManager:
    def __init__(self):
        self._tasks = {}
        self._lock = threading.RLock()
        self._changed = threading.Condition(self._lock)

    @staticmethod
    def _timestamp():
        return datetime.now(timezone.utc).isoformat()

    def _emit_locked(self, task, level, message, package=None):
        task["next_event_id"] += 1
        event = {
            "id": task["next_event_id"],
            "time": self._timestamp(),
            "level": level,
            "message": str(message)[:4000],
            "package": package,
        }
        task["events"].append(event)
        # Enough diagnostic context without retaining unbounded pip output in RAM.
        if len(task["events"]) > 1500:
            task["events"] = task["events"][-1500:]
        self._changed.notify_all()
        return event

    def create(self, packages, mode, workspace):
        task_id = "ins_" + uuid.uuid4().hex[:12]
        task = {
            "id": task_id,
            "status": "queued",
            "created_at": self._timestamp(),
            "environment_mode": mode,
            "workspace": str(workspace),
            "python_executable": None,
            "current_package": None,
            "total": len(packages),
            "completed": 0,
            "success_count": 0,
            "failed_count": 0,
            "error": None,
            "next_event_id": 0,
            "events": [],
            "packages": [
                {"name": package, "status": "waiting", "return_code": None, "stderr": ""}
                for package in packages
            ],
        }
        with self._changed:
            self._tasks[task_id] = task
            self._emit_locked(task, "info", "Installation task queued.")
            return copy.deepcopy(task)

    def update(self, task_id, **values):
        with self._changed:
            task = self._tasks[task_id]
            task.update(values)
            self._changed.notify_all()
            return copy.deepcopy(task)

    def package(self, task_id, index, **values):
        with self._changed:
            task = self._tasks[task_id]
            task["packages"][index].update(values)
            task["completed"] = sum(item["status"] in ("success", "failed") for item in task["packages"])
            task["success_count"] = sum(item["status"] == "success" for item in task["packages"])
            task["failed_count"] = sum(item["status"] == "failed" for item in task["packages"])
            self._changed.notify_all()
            return copy.deepcopy(task)

    def emit(self, task_id, level, message, package=None):
        with self._changed:
            task = self._tasks[task_id]
            self._emit_locked(task, level, message, package)

    def get(self, task_id):
        with self._lock:
            task = self._tasks.get(task_id)
            return copy.deepcopy(task) if task else None

    def all(self):
        with self._lock:
            return [copy.deepcopy(task) for task in self._tasks.values()]

    def events_after(self, task_id, after_id, timeout=15):
        """Wait briefly for events after an event id, for the SSE endpoint."""
        with self._changed:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            if not any(event["id"] > after_id for event in task["events"]):
                self._changed.wait(timeout)
            task = self._tasks.get(task_id)
            return [] if task is None else [copy.deepcopy(event) for event in task["events"] if event["id"] > after_id]


TASKS = TaskManager()
