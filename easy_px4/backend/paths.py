from pathlib import Path

def get_own_root_package():
    import __main__
    package = __package__ or getattr(__main__, '__package__', None)
    return package.split('.')[0] if package else None

WORK_DIR = Path().home() / f".{get_own_root_package()}"

PX4_DIR = WORK_DIR / "PX4-Autopilot"
