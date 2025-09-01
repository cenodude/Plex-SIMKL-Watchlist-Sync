# modules/_logging.py
from __future__ import annotations
import sys, datetime
from typing import Any, Optional, TextIO

RESET = "\033[0m"
DIM = "\033[90m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[33m"
BLUE = "\033[94m"

LEVELS = {"silent": 60, "error": 40, "warn": 30, "info": 20, "debug": 10}

class Logger:
    def __init__(
        self,
        stream: TextIO = sys.stdout,
        level: str = "info",
        use_color: bool = True,
        show_time: bool = True,
        time_fmt: str = "%Y-%m-%d %H:%M:%S",
        tag_color_map: Optional[dict[str, str]] = None,
    ):
        self.stream = stream
        self.level_no = LEVELS.get(level, 20)
        self.use_color = use_color
        self.show_time = show_time
        self.time_fmt = time_fmt
        self.tag_color_map = tag_color_map or {
            "[i]": BLUE,
            "[debug]": YELLOW,
            "[✓]": GREEN,
            "[!]": RED,
        }

    def set_level(self, level: str) -> None:
        self.level_no = LEVELS.get(level, self.level_no)

    def enable_color(self, on: bool = True) -> None:
        self.use_color = on

    def enable_time(self, on: bool = True) -> None:
        self.show_time = on

    def _fmt(self, *parts: Any) -> str:
        msg = " ".join(str(p) for p in parts)
        if self.use_color:
            for tag, col in self.tag_color_map.items():
                msg = msg.replace(tag, f"{col}{tag}{RESET}")
        if self.show_time:
            ts = datetime.datetime.now().strftime(self.time_fmt)
            prefix = f"{DIM}[{ts}]{RESET}" if self.use_color else f"[{ts}]"
            return f"{prefix} {msg}"
        return msg

    def _write(self, s: str) -> None:
        self.stream.write(s + "\n")
        self.stream.flush()

    def debug(self, *parts: Any) -> None:
        if self.level_no <= LEVELS["debug"]:
            self._write(self._fmt(*parts))

    def info(self, *parts: Any) -> None:
        if self.level_no <= LEVELS["info"]:
            self._write(self._fmt(*parts))

    def warn(self, *parts: Any) -> None:
        if self.level_no <= LEVELS["warn"]:
            self._write(self._fmt(*parts))

    def error(self, *parts: Any) -> None:
        if self.level_no <= LEVELS["error"]:
            self._write(self._fmt(*parts))

    def success(self, *parts: Any) -> None:
        if self.level_no <= LEVELS["info"]:
            tag = "[✓]"
            self._write(self._fmt(tag, *parts))

# Default logger instance
log = Logger()

__all__ = ["Logger", "log", "LEVELS", "RESET", "DIM", "RED", "GREEN", "YELLOW", "BLUE"]
