"""Unit tests for FileGroup."""

from __future__ import annotations

import logging

from xlogging.format.json import JsonFormat
from xlogging.format.tree import TreeFormat
from xlogging.handler.file import FileGroup
from xlogging.record.event import LogEvent


class TestFileGroupCreation:
    """Test FileGroup instantiation."""

    def test_create_basic_file_handler(self, tmp_path):
        """Test creating a basic FileGroup."""
        log_file = tmp_path / "test.log"
        handler = FileGroup(path=log_file)

        assert isinstance(handler, logging.Handler)
        assert log_file.parent.exists()

    def test_create_with_custom_encoding(self, tmp_path):
        """Test creating FileGroup with custom encoding."""
        log_file = tmp_path / "test.log"
        handler = FileGroup(path=log_file, encoding="utf-8")

        assert handler.encoding == "utf-8"

    def test_create_with_max_bytes(self, tmp_path):
        """Test creating FileGroup with max bytes."""
        log_file = tmp_path / "test.log"
        handler = FileGroup(path=log_file, max_bytes=1024)

        assert handler.maxBytes == 1024

    def test_create_with_backup_count(self, tmp_path):
        """Test creating FileGroup with backup count."""
        log_file = tmp_path / "test.log"
        handler = FileGroup(path=log_file, backup_count=3)

        assert handler.backupCount == 3

    def test_create_directory_if_not_exists(self, tmp_path):
        """Test that directory is created if it doesn't exist."""
        log_file = tmp_path / "subdir" / "nested" / "test.log"
        _ = FileGroup(path=log_file)

        assert log_file.parent.exists()


class TestFileGroupWithLogRecord:
    """Test FileGroup with standard logging.LogRecord."""

    def test_emit_standard_log_record(self, tmp_path):
        """Test emitting a standard LogRecord."""
        log_file = tmp_path / "test.log"
        handler = FileGroup(path=log_file)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)
        assert log_file.exists()

        content = log_file.read_text()
        assert "INFO - Test message" in content

    def test_emit_with_json_formatter(self, tmp_path):
        """Test emitting LogRecord with JsonFormat."""
        log_file = tmp_path / "test.log"
        handler = FileGroup(path=log_file)
        formatter = JsonFormat(indent=2)
        handler.setFormatter(formatter)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=20,
            msg="JSON message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        content = log_file.read_text()
        assert "JSON message" in content


class TestFileGroupWithLogEvent:
    """Test FileGroup with xlogging.LogEvent."""

    def test_emit_log_event(self, tmp_path):
        """Test emitting a LogEvent."""
        log_file = tmp_path / "test.log"
        handler = FileGroup(path=log_file)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Event message",
            args=(),
            exc_info=None,
            metadata={"key": "value"},
            tags={"env": "test"},
        )

        handler.emit(event)
        content = log_file.read_text()
        assert "INFO - Event message" in content

    def test_emit_log_event_with_json_formatter(self, tmp_path):
        """Test emitting LogEvent with JsonFormat."""
        log_file = tmp_path / "test.log"
        handler = FileGroup(path=log_file)
        formatter = JsonFormat(indent=2)
        handler.setFormatter(formatter)

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Event with metadata",
            args=(),
            exc_info=None,
            metadata={"user": "alice", "action": "login"},
            tags={"region": "us-east", "env": "prod"},
        )

        handler.emit(event)

        content = log_file.read_text()
        assert "Event with metadata" in content
        assert "metadata" in content
        assert "alice" in content

    def test_emit_log_event_with_tree_formatter(self, tmp_path):
        """Test emitting LogEvent with TreeFormat."""
        log_file = tmp_path / "test.log"
        handler = FileGroup(path=log_file)
        formatter = TreeFormat()
        handler.setFormatter(formatter)

        event = LogEvent(
            name="test.logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=15,
            msg="Event with nested data",
            args=(),
            exc_info=None,
            metadata={"nested": {"key": "value"}},
            tags={"type": "warning"},
        )

        handler.emit(event)

        content = log_file.read_text()
        assert "Event with nested data" in content
