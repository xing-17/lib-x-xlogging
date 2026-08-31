from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from xlogging.format.json import JsonFormat


class FileGroup(RotatingFileHandler):
    """
    File Group handler for local storage

    Args:
        path (str | Path):
            The path to the log file or directory. If a directory is provided, a default log file name will be used.
        name (str | None):
            The name of the log file. If None, a default name will be used.
        encoding (str | None):
            The encoding to use for the log file. If None, a default encoding will be used.
        max_bytes (int | None):
            The maximum size in bytes of the log file before it is rotated. If None, a default size will be used.
        backup_count (int | None):
            The number of backup files to keep. If None, a default count will be used.

    Example:
        >>> handler = FileGroup(
        ...     path="/var/log/myapp",
        ...     name="myapp",
        ...     encoding="utf-8",
        ...     max_bytes=10 * 1024 * 1024,
        ...     backup_count=5,
        ... )
        >>> logger = logging.getLogger(__name__)
        >>> logger.addHandler(handler)

    """

    default_name: str = "default"
    default_encoding: str = "utf-8"
    default_max_bytes: int = 10 * 1024 * 1024
    default_backup_count: int = 1

    def __init__(
        self,
        path: str | Path,
        name: str | None = None,
        encoding: str | None = None,
        max_bytes: int | None = None,
        backup_count: int | None = None,
        format: logging.Formatter | None = None,
    ) -> None:
        _name: str = name or self.default_name
        _path: Path = self._resolve_path(path, _name)
        _encoding: str = encoding or self.default_encoding
        _max_bytes: int = max_bytes or self.default_max_bytes
        _backup_count: int = backup_count or self.default_backup_count
        super().__init__(
            str(_path),
            encoding=_encoding,
            maxBytes=_max_bytes,
            backupCount=_backup_count,
        )
        self._name: str = _name
        self._path: Path = _path
        self._encoding: str = _encoding
        self._max_bytes: int = _max_bytes
        self._backup_count: int = _backup_count
        self._date_format: str = "%Y-%m-%dT%H:%M:%S%z"
        self._format = format or JsonFormat(
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            ignore_unset=False,
            date_format=self._date_format,
        )
        self.setFormatter(self._format)

    def _resolve_path(
        self,
        path: str | Path,
        name: str | None = None,
    ) -> Path:
        _path = Path(path)
        if not _path.parent.exists():
            _path.parent.mkdir(parents=True, exist_ok=True)
        if _path.is_dir():
            _path: Path = _path / f"{name}.log"
        return _path.expanduser().resolve()
