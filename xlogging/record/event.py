from __future__ import annotations

from logging import LogRecord
from zoneinfo import ZoneInfo


class EventRecord(LogRecord):
    @classmethod
    def from_record(
        cls,
        record: LogRecord,
        timezone: str | ZoneInfo | None = None,
        metadata: dict | None = None,
        tags: dict | None = None,
    ) -> EventRecord:
        return cls(
            name=record.name,
            level=record.levelno,
            pathname=record.pathname,
            lineno=record.lineno,
            msg=record.msg,
            args=record.args,
            exc_info=record.exc_info,
            func=record.funcName,
            sinfo=record.stack_info,
            timezone=timezone,
            metadata=metadata,
            tags=tags,
        )

    def __init__(
        self,
        name: str,
        level: int,
        pathname: str,
        lineno: int,
        msg: str,
        args: tuple,
        exc_info: tuple | None,
        func: str | None = None,
        sinfo: str | None = None,
        timezone: str | ZoneInfo | None = None,
        metadata: dict | None = None,
        tags: dict | None = None,
    ) -> None:
        super().__init__(
            name=name,
            level=level,
            pathname=pathname,
            lineno=lineno,
            msg=msg,
            args=args,
            exc_info=exc_info,
            func=func,
            sinfo=sinfo,
        )
        self.timezone: ZoneInfo | None = self._resolve_timezone(timezone)
        self.metadata: dict = metadata or {}
        self.tags: dict = tags or {}

    def _resolve_timezone(
        self,
        timezone: str | ZoneInfo | None = None,
    ) -> ZoneInfo | None:
        if isinstance(timezone, str):
            return ZoneInfo(timezone)
        if isinstance(timezone, ZoneInfo):
            return timezone
        return timezone
