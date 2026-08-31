from __future__ import annotations

import logging
from typing import Any

from xlogging.format._common import (
    IFormatConfig,
    ILogRecord,
)


class MemoryGroup(logging.Handler):
    def __init__(
        self,
        level: int = logging.NOTSET,
        date_format: str | None = None,
    ) -> None:
        super().__init__(level)
        self._date_format = IFormatConfig.resolve_date_format(date_format)
        self.records: list[logging.LogRecord] = []

    def emit(
        self,
        record: logging.LogRecord,
    ) -> None:
        self.records.append(record)

    def get_records(
        self,
        level: int | None = None,
    ) -> list[logging.LogRecord]:
        if level is None:
            return list(self.records)
        return [r for r in self.records if r.levelno >= level]

    def clear(self) -> None:
        self.records.clear()

    def export(self) -> list[dict]:
        _result: list[dict[str, Any]] = []
        for record in self.records:
            _result.append(
                ILogRecord.serialise_all(
                    record=record,
                    date_format=self._date_format,
                    tb_as_str=False,
                    ignore_unset=False,
                    reduced_attrs=False,
                )
            )
        return _result
