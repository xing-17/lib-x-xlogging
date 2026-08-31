from __future__ import annotations

import logging
from typing import Any

from ._common import (
    IColorConfig,
    IFormatConfig,
    ILogRecord,
    ITreeConfig,
)
from .tree import TreeFormat


class ColorTreeFormat(TreeFormat):
    def __init__(
        self,
        colors: dict[str, str] | None = None,
        date_format: str | None = None,
        tb_as_str: bool = False,
        ignore_unset: bool = True,
        reduced_attrs: bool = False,
    ) -> None:
        super().__init__(
            ignore_unset=ignore_unset,
        )
        self._colors = IColorConfig.resolve_colors_config(colors)
        self._date_format = IFormatConfig.resolve_date_format(date_format)
        self._tb_as_str = tb_as_str
        self._ignore_unset = ignore_unset
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
        _message: str = _serial.pop("message", "")
        _created_at: str = _serial.pop("created_at", "")
        _color = self._colors.get(record.levelname, "")
        _reset = IColorConfig.color_reset
        _header = f"{_color}[{_created_at}][{record.levelname}]: {_message} {_reset}"
        lines = [_header]
        for i, (key, value) in enumerate(_serial.items()):
            is_last = i == len(_serial) - 1
            if is_last:
                connector = ITreeConfig.tree_last
                child_prefix = ITreeConfig.tree_space
            else:
                connector = ITreeConfig.tree_branch
                child_prefix = ITreeConfig.tree_pipe
            if isinstance(value, dict):
                lines.append(f"{connector}{key}:")
                self._render_dict(value, child_prefix, lines)
            elif isinstance(value, list):
                lines.append(f"{connector}{key}:")
                self._render_list(value, child_prefix, lines)
            else:
                val_lines = str(value).splitlines() or [""]
                lines.append(f"{connector}{key}: {val_lines[0]}")
                for vl in val_lines[1:]:
                    lines.append(f"{child_prefix}{vl}")
        return "\n".join(lines)
