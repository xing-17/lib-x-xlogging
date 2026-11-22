from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from xlogging.record.event import LogEvent


class EventStream(logging.Logger):
    """
    Events logger for logging module

    Args:
        name (str):
            The name of the logger.
        level (int):
            The logging level for the logger. Default is logging.NOTSET.
        timezone (ZoneInfo | str | None):
            The timezone for the logger. If None, defaults to UTC.
        metadata (dict[str, Any] | None):
            Additional metadata to include in log records. If None, no additional metadata will be included.
        tags (dict[str, str] | None):
            Additional tags to include in log records. If None, no additional tags will be included.

    Methods:
        info(msg, *args, metadata=None, tags=None, **kwargs):
            Log a message with level INFO, including optional metadata and tags.
        debug(msg, *args, metadata=None, tags=None, **kwargs):
            Log a message with level DEBUG, including optional metadata and tags.
        warning(msg, *args, metadata=None, tags=None, **kwargs):
            Log a message with level WARNING, including optional metadata and tags.
        error(msg, *args, metadata=None, tags=None, **kwargs):
            Log a message with level ERROR, including optional metadata and tags.
        critical(msg, *args, metadata=None, tags=None, **kwargs):
            Log a message with level CRITICAL, including optional metadata and tags.
        exception(msg, *args, metadata=None, tags=None, **kwargs):
            Log a message with level ERROR, including exception information, optional metadata and tags.

    Example:
        >>> logger = EventStream(
        ...     name="my_logger",
        ...     level=logging.INFO,
        ...     timezone="UTC",
        ...     metadata={"user_id": 123, "session_id": "abc123"},
        ...     tags={"module": "my_module", "function": "my_function"},
        ... )
        >>> logger.info(
        ...     "This is a log message",
        ...     metadata={"request_id": "xyz789"},
        ...     tags={"endpoint": "/api/v1/resource"},
        ... )
    """

    @classmethod
    def from_options(
        cls,
        name: str | None = None,
        level: int | None = None,
        timezone: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        handlers: list[logging.Handler] | None = None,
    ) -> EventStream:
        """Create an EventStream from options."""
        stream = EventStream(
            name=name,
            level=level,
            timezone=timezone,
            metadata=metadata,
            tags=tags,
        )
        for handler in handlers or []:
            stream.addHandler(handler)
        return stream

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        timezone: ZoneInfo | str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
    ) -> None:
        super().__init__(name, level)
        self._timezone: ZoneInfo = self._resolve_timezone(timezone)
        self._metadata: dict[str, Any] = dict(metadata or {})
        self._tags: dict[str, str] = dict(tags or {})

    def _resolve_timezone(
        self,
        timezone: ZoneInfo | str | None = None,
    ) -> ZoneInfo:
        if not timezone:
            return ZoneInfo("UTC")
        if isinstance(timezone, ZoneInfo):
            return timezone
        if isinstance(timezone, str):
            return ZoneInfo(timezone)
        raise TypeError(f"Invalid timezone type: {type(timezone)}")

    def _merge_dict(
        self,
        base: dict[str, Any],
        update: dict[str, Any] | None,
    ) -> dict[str, Any]:
        merged = dict(base)
        if update:
            merged.update(update)
        return merged

    def _get_current_datetime(self) -> datetime:
        current = datetime.now(tz=self._timezone)
        return current

    def _with_event_context(
        self,
        kwargs: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        _extra = dict(kwargs.pop("extra", {}) or {})
        if metadata is not None:
            _extra["metadata"] = self._merge_dict(
                base=self._metadata,
                update=metadata,
            )
        if tags is not None:
            _extra["tags"] = self._merge_dict(
                base=self._tags,
                update=tags,
            )
        kwargs["extra"] = _extra
        return kwargs

    def info(
        self,
        msg: object,
        *args: Any,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs = self._with_event_context(kwargs, metadata, tags)
        super().info(msg, *args, **kwargs)

    def debug(
        self,
        msg: object,
        *args: Any,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs = self._with_event_context(kwargs, metadata, tags)
        super().debug(msg, *args, **kwargs)

    def warning(
        self,
        msg: object,
        *args: Any,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs = self._with_event_context(kwargs, metadata, tags)
        super().warning(msg, *args, **kwargs)

    def error(
        self,
        msg: object,
        *args: Any,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs = self._with_event_context(kwargs, metadata, tags)
        super().error(msg, *args, **kwargs)

    def critical(
        self,
        msg: object,
        *args: Any,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs = self._with_event_context(kwargs, metadata, tags)
        super().critical(msg, *args, **kwargs)

    def exception(
        self,
        msg: object,
        *args: Any,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs = self._with_event_context(kwargs, metadata, tags)
        super().exception(msg, *args, **kwargs)

    def log(
        self,
        level: int,
        msg: object,
        *args: Any,
        metadata: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs = self._with_event_context(kwargs, metadata, tags)
        super().log(level, msg, *args, **kwargs)

    def makeRecord(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: object,
        args: tuple[Any, ...] | dict[str, Any],
        exc_info: tuple[type[BaseException], BaseException, object] | None,
        func: str | None = None,
        extra: dict[str, Any] | None = None,
        sinfo: str | None = None,
    ) -> LogEvent:
        _extra = dict(extra or {})
        _created_at: datetime = self._get_current_datetime()
        _metadata: dict[str, Any] = self._merge_dict(
            base=self._metadata,
            update=_extra.pop("metadata", {}),
        )
        _tags: dict[str, str] = self._merge_dict(
            base=self._tags,
            update=_extra.pop("tags", {}),
        )
        record = LogEvent(
            name=name,
            level=level,
            pathname=fn,
            lineno=lno,
            msg=msg,
            args=args,
            exc_info=exc_info,
            func=func,
            sinfo=sinfo,
            created_at=_created_at,
            metadata=_metadata,
            tags=_tags,
        )
        if _extra:
            for key, value in _extra.items():
                if key in {"message", "asctime"} or key in record.__dict__:
                    raise KeyError(f"Attempt to overwrite {key!r} in LogEvent")
                record.__dict__[key] = value
        return record

    def add(
        self,
        group: logging.Handler,
    ) -> None:
        self.addHandler(group)
