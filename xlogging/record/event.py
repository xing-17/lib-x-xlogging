from __future__ import annotations

from datetime import datetime
from logging import LogRecord


class LogEvent(LogRecord):
    """
    Extended logging record with structured metadata and tags.

    Args:
        name: (str) from LogRecord, name of the logger.
        level: (int) from LogRecord, numeric level of message (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        lineno: (int) from LogRecord, the line number in source file.
        pathname: (str) from LogRecord, the full pathname of the source file.
        msg: (str) from LogRecord, the message.
        args: (tuple) from LogRecord, the arguments to be merged into msg (if any).
        exc_info: (tuple | None) from LogRecord, exception information.
        func: (str | None) from LogRecord, the name of the function or method from which the logging call was made.
        sinfo: (str | None) from LogRecord, stack information.

        created_at: (datetime) the datetime when the log event was created.
        metadata: (dict | None) additional metadata associated with the log event.
        tags: (dict | None) additional tags associated with the log event.

    """

    def __init__(
        self,
        *args,
        created_at: datetime | None = None,
        metadata: dict | None = None,
        tags: dict | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.created_at: datetime | None = created_at
        self.metadata: dict = dict(metadata or {})
        self.tags: dict = dict(tags or {})
