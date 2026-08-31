from __future__ import annotations

import json
import logging
from typing import Any

from ._common import (
    IFormatConfig,
    ILogRecord,
)


class JsonFormat(logging.Formatter):
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
