import os
from pathlib import Path

env_work_dir = os.environ.get("EASY_PX4_WORK_DIR", str(Path.home()))
WORK_DIR = Path(env_work_dir) / ".easy_px4"

PX4_DIR = WORK_DIR / "PX4-Autopilot"
