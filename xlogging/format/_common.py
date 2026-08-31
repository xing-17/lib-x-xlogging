from __future__ import annotations

import logging
import traceback
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from colorlog.escape_codes import escape_codes as _esc


class IColorConfig:
    color_config: dict[str, str] = {
        "DEBUG": "cyan",
        "INFO": "38;5;244",
        "WARNING": "38;5;208",
        "ERROR": "bold_red",
        "CRITICAL": "purple",
    }
    color_reset: str = _esc.get("reset", "\033[0m")

    @staticmethod
    def resolve_colors_config(
        colors: dict[str, str] | None = None,
    ) -> dict[str, str]:
        if colors is not None:
            source = colors
        else:
            source = IColorConfig.color_config

        resolved = {}
        for lvl, color in source.items():
            if color in _esc:
                resolved[lvl] = _esc[color]
            else:
                resolved[lvl] = f"\033[{color}m"
        return resolved

    @staticmethod
    def get_color_reset() -> str:
        return IColorConfig.color_reset

    @staticmethod
    def get_default_colors() -> dict[str, str]:
        return IColorConfig.color_config


class IFormatConfig:
    format: str = "[%(asctime)s][%(levelname)s] %(message)s"
    colored_format: str = "%(log_color)s[%(asctime)s][%(levelname)s] %(message)s%(reset)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def resolve_date_format(
        datefmt: str | None = None,
    ) -> str:
        return datefmt or IFormatConfig.date_format

    @staticmethod
    def resolve_format(
        format: str | None = None,
    ) -> str:
        return format or IFormatConfig.format

    @staticmethod
    def resolve_colored_format(
        format: str | None = None,
    ) -> str:
        return format or IFormatConfig.colored_format


class ITreeConfig:
    tree_branch: str = "├── "
    tree_last: str = "└── "
    tree_pipe: str = "│   "
    tree_space: str = "    "


class ILogRecord:
    @staticmethod
    def serialise_exc(
        record: logging.LogRecord,
        tb_as_str: bool = False,
    ) -> dict[str, Any] | None:
        _exc_info = getattr(record, "exc_info", None)
        if not _exc_info or _exc_info[0] is None:
            return None
        _type, _value, _tb = _exc_info
        _result = {}
        _result["type"] = _type.__qualname__
        _result["message"] = str(_value)
        _tb_lines: list[str] = []
        for chunk in traceback.format_tb(_tb):
            for line in chunk.splitlines():
                if isinstance(line, str):
                    _tb_lines.append(line.strip())
        if tb_as_str:
            _result["traceback"] = "\n".join(_tb_lines)
        else:
            _result["traceback"] = _tb_lines
        return _result

    @staticmethod
    def serialise_cdt(
        record: logging.LogRecord,
        date_format: str | None = None,
    ) -> str:
        _date_format = IFormatConfig.resolve_date_format(date_format)
        _o_ts: float = record.created
        _o_cdt: datetime = datetime.fromtimestamp(_o_ts, tz=ZoneInfo("UTC"))
        _e_cdt: datetime | None = getattr(record, "created_at", None)
        _cdt: str = (_e_cdt or _o_cdt).strftime(_date_format)
        return _cdt

    @staticmethod
    def serialise_all(
        record: logging.LogRecord,
        date_format: str | None = None,
        tb_as_str: bool = False,
        ignore_unset: bool = False,
        reduced_attrs: bool = False,
    ) -> dict[str, Any]:
        _cdt: str = ILogRecord.serialise_cdt(
            record=record,
            date_format=date_format,
        )
        _exc: dict[str, Any] | None = ILogRecord.serialise_exc(
            record=record,
            tb_as_str=tb_as_str,
        )
        _msg: str = record.getMessage()
        if reduced_attrs:
            _result = {
                "message": _msg,
                "created_at": _cdt,
                "level": record.levelname,
                "exception": _exc,
                "metadata": getattr(record, "metadata", None),
                "tags": getattr(record, "tags", None),
            }
        else:
            _result = {
                "message": _msg,
                "created_at": _cdt,
                "level": record.levelname,
                "line_no": record.lineno,
                "func_name": record.funcName,
                "pathname": getattr(record, "pathname", None),
                "filename": getattr(record, "filename", None),
                "module": getattr(record, "module", None),
                "stack_info": getattr(record, "stack_info", None),
                "exception": _exc,
                "metadata": getattr(record, "metadata", None),
                "tags": getattr(record, "tags", None),
                "thread": record.thread,
                "thread_name": record.threadName,
                "process": record.process,
            }
        if ignore_unset:
            _result = {k: v for k, v in _result.items() if v is not None}
        return _result
