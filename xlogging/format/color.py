from __future__ import annotations

import logging
from typing import Optional

from ._common import (
    IColorConfig,
    IFormatConfig,
)


class ColorFormat(logging.Formatter):
    def __init__(
        self,
        format: Optional[str] = None,
        date_format: Optional[str] = None,
        colors: Optional[dict[str, str]] = None,
    ) -> None:
        super().__init__()
        self._inner = logging.Formatter(
            fmt=IFormatConfig.resolve_format(format),
            datefmt=IFormatConfig.resolve_date_format(date_format),
        )
        self._colors = IColorConfig.resolve_colors_config(colors)
        self._colors_reset = IColorConfig.color_reset

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        _color = self._colors.get(record.levelname, "")
        _reset = self._colors_reset
        return f"{_color}{self._inner.format(record)}{_reset}"
