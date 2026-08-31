from __future__ import annotations

import logging

from ._common import (
    IColorConfig,
    IFormatConfig,
)
from .tree import TreeFormat


class ColorTreeFormat(TreeFormat):
    """
    Color tree formatter for logging.

    Args:
        colors (dict[str, str] | None):
            A dictionary mapping log levels to color codes. If None, default colors will be used.
        date_format (str | None):
            The date format for log messages. If None, a default date format will be used.
        tb_as_str (bool):
            Whether to convert traceback objects to strings. Default is False.
        ignore_unset (bool):
            Whether to ignore unset attributes in the log record. Default is True.
        reduced_attrs (bool):
            Whether to reduce the attributes in the log record. Default is True.

    Example:
        >>> formatter = ColorTreeFormat(
        ...     colors={
        ...         "DEBUG": "cyan",
        ...         "INFO": "green",
        ...         "WARNING": "yellow",
        ...         "ERROR": "red",
        ...         "CRITICAL": "bold_red",
        ...     },
        ...     date_format="%Y-%m-%d %H:%M:%S",
        ...     tb_as_str=True,
        ...     ignore_unset=True,
        ...     reduced_attrs=True,
        ... )
        >>> formatter.format(record)
        ... [2024-06-01 12:00:00][INFO]: This is a log message
        ... ├─ key1: value1
        ... ├─ key2:
        ...     ├─ subkey1: subvalue1
        ...     └─ subkey2: subvalue2
    """

    def __init__(
        self,
        colors: dict[str, str] | None = None,
        _full_color: bool = True,
        date_format: str | None = None,
        tb_as_str: bool = False,
        ignore_unset: bool = True,
        reduced_attrs: bool = True,
    ) -> None:
        super().__init__(
            date_format=date_format,
            tb_as_str=tb_as_str,
            ignore_unset=ignore_unset,
            reduced_attrs=reduced_attrs,
        )
        self._colors = IColorConfig.resolve_colors_config(colors)
        self._date_format = IFormatConfig.resolve_date_format(date_format)
        self._full_color = _full_color
        self._tb_as_str = tb_as_str
        self._ignore_unset = ignore_unset
        self._reduced_attrs = reduced_attrs

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        result = super().format(record)
        _color = self._colors.get(record.levelname, "")
        _reset = IColorConfig.color_reset
        if not _color:
            return result
        if self._full_color:
            return f"{_color}{result}{_reset}"
        lines = result.split("\n")
        lines[0] = f"{_color}{lines[0]}{_reset}"
        return "\n".join(lines)
