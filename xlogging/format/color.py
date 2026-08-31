from __future__ import annotations

import logging

from ._common import (
    IColorConfig,
    IFormatConfig,
)


class ColorFormat(logging.Formatter):
    """
    Color formatter for logging.

    Args:
        format (str | None):
            The log message format. If None, a default format will be used.
        date_format (str | None):
            The date format for log messages. If None, a default date format will be used.
        colors (dict[str, str] | None):
            A dictionary mapping log levels to color codes. If None, default colors will be used.

    Example:
        >>> formatter = ColorFormat(
        ...    format="%(log_color)s[%(asctime)s][%(levelname)-8s]%(reset)s %(message)s",
        ...    date_format="%Y-%m-%d %H:%M:%S",
        ...    colors={
        ...        "DEBUG": "cyan",
        ...        "INFO": "green",
        ...        "WARNING": "yellow",
        ...        "ERROR": "red",
        ...        "CRITICAL": "bold_red",
        ...    }
        ... )
        >>> formatter.format(record)
        ... [2024-06-01 12:00:00][INFO]: This is a log message

    """

    def __init__(
        self,
        format: str | None = None,
        date_format: str | None = None,
        colors: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        _format = IFormatConfig.resolve_format(format)
        _date_format = IFormatConfig.resolve_date_format(date_format)
        self._inner = logging.Formatter(fmt=_format, datefmt=_date_format)
        self._colors = IColorConfig.resolve_colors_config(colors)
        self._colors_reset = IColorConfig.color_reset

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        _color = self._colors.get(record.levelname, "")
        _reset = self._colors_reset
        return f"{_color}{self._inner.format(record)}{_reset}"
