from __future__ import annotations

import logging
from typing import Any

from ._common import (
    IFormatConfig,
    ILogRecord,
    ITreeConfig,
)


class TreeFormat(logging.Formatter):
    def __init__(
        self,
        date_format: str | None = None,
        tb_as_str: bool = False,
        ignore_unset: bool = True,
        reduced_attrs: bool = False,
    ) -> None:
        super().__init__()
        self._date_format = IFormatConfig.resolve_date_format(date_format)
        self._tb_as_str = tb_as_str
        self._ignore_unset = ignore_unset
        self._reduced_attrs = reduced_attrs

    def _render_list(
        self,
        items: list[Any],
        prefix: str,
        lines: list[str],
    ) -> None:
        for j, item in enumerate(items):
            is_last = j == len(items) - 1
            connector = ITreeConfig.tree_last if is_last else ITreeConfig.tree_branch
            if is_last:
                child_prefix = prefix + ITreeConfig.tree_space
            else:
                child_prefix = prefix + ITreeConfig.tree_pipe
            if isinstance(item, dict):
                lines.append(f"{prefix}{connector}[{j}]:")
                self._render_dict(item, child_prefix, lines)
            elif isinstance(item, list):
                lines.append(f"{prefix}{connector}[{j}]:")
                self._render_list(item, child_prefix, lines)
            else:
                val_lines = str(item).splitlines() or [""]
                lines.append(f"{prefix}{connector}{val_lines[0]}")
                for vl in val_lines[1:]:
                    lines.append(f"{child_prefix}{vl}")

    def _render_dict(
        self,
        data: dict,
        prefix: str,
        lines: list[str],
    ) -> list[str]:
        items = list(data.items())
        for i, (k, v) in enumerate(items):
            is_last = i == len(items) - 1
            if is_last:
                connector = ITreeConfig.tree_last
                child_prefix = prefix + ITreeConfig.tree_space
            else:
                connector = ITreeConfig.tree_branch
                child_prefix = prefix + ITreeConfig.tree_pipe
            if isinstance(v, dict):
                lines.append(f"{prefix}{connector}{k}:")
                self._render_dict(v, child_prefix, lines)
            elif isinstance(v, list):
                lines.append(f"{prefix}{connector}{k}:")
                self._render_list(v, child_prefix, lines)
            else:
                val_lines = str(v).splitlines() or [""]
                lines.append(f"{prefix}{connector}{k}: {val_lines[0]}")
                for vl in val_lines[1:]:
                    lines.append(f"{child_prefix}{vl}")
        return lines

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
        _header = f"[{_created_at}][{record.levelname}]: {_message}"
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
