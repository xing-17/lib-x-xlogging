from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from xlogging.format._common import (
    IFormatConfig,
)


class FileGroup(RotatingFileHandler):
    def __init__(
        self,
        path: str | Path,
        encoding: str = "utf-8",
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 1,
        date_format: str | None = None,
    ) -> None:
        resolved = Path(path).expanduser().resolve()
        resolved.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(
            str(resolved),
            encoding=encoding,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        self._date_format = IFormatConfig.resolve_date_format(date_format)
        self.records: list[logging.LogRecord] = []

    def emit(
        self,
        record: logging.LogRecord,
    ) -> None:
        self.records.append(record)
        super().emit(record)

    def get_records(
        self,
        level: int | None = None,
    ) -> list[logging.LogRecord]:
        if level is None:
            return list(self.records)
        return [r for r in self.records if r.levelno >= level]
