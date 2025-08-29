import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Ensure project root is on sys.path when running as a script
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    # Import the Celery app instance
    from app.celery_app import celery_app
except Exception as import_error:
    print(f"Failed to import Celery app: {import_error}")
    sys.exit(1)


def count_active_tasks() -> int:
    """Return total number of active (running) tasks across all workers."""
    inspector = celery_app.control.inspect()
    active_by_worker: Optional[Dict[str, List[dict]]] = inspector.active()
    if not active_by_worker:
        return 0
    return sum(len(tasks or []) for tasks in active_by_worker.values())


def collect_active_tasks() -> Dict[str, List[dict]]:
    """Return mapping of worker -> list of active tasks (empty mapping if none)."""
    inspector = celery_app.control.inspect()
    active_by_worker: Optional[Dict[str, List[dict]]] = inspector.active() or {}
    return active_by_worker


def main() -> None:
    total_active = count_active_tasks()
    active_detail = collect_active_tasks()

    result = {
        "total_active": total_active,
        "by_worker": {worker: len(tasks or []) for worker, tasks in active_detail.items()},
    }

    # Print a concise human-readable line and a JSON blob for tooling
    print(f"Active (running) Celery tasks: {result['total_active']}")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()


