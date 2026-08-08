#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import threading


class Logger:

    LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

    def __init__(self):
        self.level = "INFO"
        self.log_dir = Path(".aios/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def configure(self, level="INFO"):
        level = level.upper()
        if level in self.LEVELS:
            self.level = level

    def _enabled(self, level):
        return self.LEVELS.index(level) >= self.LEVELS.index(self.level)

    def log(self, level, message, plugin="core"):

        level = level.upper()

        if not self._enabled(level):
            return

        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

        line = f"[{timestamp}] [{level}] [{plugin}] {message}"

        with self.lock:
            print(line)

            logfile = self.log_dir / f"{datetime.now(timezone.utc):%Y-%m-%d}.log"

            with logfile.open("a") as f:
                f.write(line + "\n")

    def debug(self, message, plugin="core"):
        self.log("DEBUG", message, plugin)

    def info(self, message, plugin="core"):
        self.log("INFO", message, plugin)

    def warning(self, message, plugin="core"):
        self.log("WARNING", message, plugin)

    def error(self, message, plugin="core"):
        self.log("ERROR", message, plugin)

    def critical(self, message, plugin="core"):
        self.log("CRITICAL", message, plugin)


logger = Logger()


if __name__ == "__main__":
    logger.configure("DEBUG")
    logger.info("AIOS started")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
