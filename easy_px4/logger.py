import logging
import sys

# ANSI escape codes for colors
LOG_COLORS = {
    'DEBUG': '\033[94m',     # Blue
    'INFO': '\033[92m',      # Green
    'WARNING': '\033[93m',   # Yellow
    'ERROR': '\033[91m',     # Red
    'CRITICAL': '\033[95m',  # Magenta
    'RESET': '\033[0m',
}

class ColoredCommandFormatter(logging.Formatter):
    def format(self, record):
        color = LOG_COLORS.get(record.levelname, '')
        reset = LOG_COLORS['RESET']
        level = f"{color}[{record.levelname}]{reset}"

        command = record.__dict__.get("command", __package__)
        record.msg = f"{level} [{command}] {record.msg}"
        return super().format(record)

_base_logger = logging.getLogger(__package__)
_base_logger.setLevel(logging.DEBUG)

if not _base_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = ColoredCommandFormatter("%(message)s")
    handler.setFormatter(formatter)

    _base_logger.addHandler(handler)

_base_logger.propagate = False

# Function to get a logger with command context
def get_logger(command: str = "main") -> logging.LoggerAdapter:
    return logging.LoggerAdapter(_base_logger, {"command": command})

