"""Regenerate the single official S0/S1/S2 evaluation result file."""

from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DEMO_DIR = PROJECT_ROOT / "demo"
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

# Keep interpreter caches and temporary files inside the project workspace.
LOCAL_TMP = PROJECT_ROOT / ".codex_tmp"
LOCAL_TMP.mkdir(exist_ok=True)
os.environ.setdefault("TEMP", str(LOCAL_TMP))
os.environ.setdefault("TMP", str(LOCAL_TMP))
os.environ.setdefault("PYTHONPYCACHEPREFIX", str(LOCAL_TMP / "pycache"))

from core.evaluation_engine import EvaluationEngine  # noqa: E402


if __name__ == "__main__":
    target = EvaluationEngine(str(PROJECT_ROOT)).write_results()
    print(target)
