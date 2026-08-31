from __future__ import annotations

import json
import logging
from typing import Any

from ._common import (
    IFormatConfig,
    ILogRecord,
)


class JsonFormat(logging.Formatter):
    """
    Json Formatter for logging.

    Args:
        indent (int | None):
            The number of spaces to use for indentation in the JSON output. If None, no indentation will be applied.
        sort_keys (bool):
            Whether to sort the keys in the JSON output. Default is True.
        ensure_ascii (bool):
            Whether to escape non-ASCII characters in the JSON output. Default is False.
        ignore_unset (bool):
            Whether to ignore unset attributes in the log record. Default is True.
        date_format (str | None):
            The date format for log messages. If None, a default date format will be used.
        tb_as_str (bool):
            Whether to convert traceback objects to strings. Default is False.
        reduced_attrs (bool):
            Whether to reduce the attributes in the log record. Default is False.
    Example:
        >>> formatter = JsonFormat(
        ...     indent=4,
        ...     sort_keys=True,
        ...     ensure_ascii=False,
        ...     ignore_unset=True,
        ...     date_format="%Y-%m-%d %H:%M:%S",
        ...     tb_as_str=True,
        ...     reduced_attrs=False,
        ... )
        >>> formatter.format(record)
        ... {
        ...     "asctime": "2024-06-01 12:00:00",
        ...     "levelname": "INFO",
        ...     "message": "This is a log message",
        ...     "name": "my_logger",
        ...     ...
        ... }
    """

    def __init__(
        self,
        indent: int | None = 4,
        sort_keys: bool = True,
        ensure_ascii: bool = False,
        ignore_unset: bool = True,
        date_format: str | None = None,
        tb_as_str: bool = False,
        reduced_attrs: bool = False,
    ) -> None:
        super().__init__()
        self._indent = indent
        self._sort_keys = sort_keys
        self._ensure_ascii = ensure_ascii
        self._ignore_unset = ignore_unset
        self._date_format = IFormatConfig.resolve_date_format(date_format)
        self._tb_as_str = tb_as_str
        self._reduced_attrs = reduced_attrs

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        _serial: dict[str, Any] = ILogRecord.serialise_all(
            record=record,
            date_format=self._date_format,
            tb_as_str=self._tb_as_str,
            ignore_unset=self._ignore_unset,
            reduced_attrs=self._reduced_attrs,
        )
        return json.dumps(
            _serial,
            indent=self._indent,
            sort_keys=self._sort_keys,
            ensure_ascii=self._ensure_ascii,
        )
