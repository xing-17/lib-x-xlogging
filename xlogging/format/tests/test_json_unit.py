"""Unit tests for JsonFormat."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from xlogging.format.json import JsonFormat
from xlogging.record.event import LogEvent


class TestJsonFormat:
    """Test JsonFormat with both LogRecord and LogEvent."""

    def test_format_basic_log_record(self):
        """Test formatting a basic logging.LogRecord."""
        formatter = JsonFormat()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["message"] == "Test message"
        assert data["name"] == "test.logger"
        assert data["level_name"] == "INFO"
        assert "created_at" in data

    def test_format_with_log_event(self):
        """Test formatting an xlogging LogEvent."""
        formatter = JsonFormat()
        created_at = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Event message",
            args=(),
            exc_info=None,
            func="test_func",
            sinfo=None,
            created_at=created_at,
            metadata={"key": "value"},
            tags={"env": "test"},
        )

        result = formatter.format(event)
        data = json.loads(result)

        assert data["message"] == "Event message"
        assert data["metadata"] == {"key": "value"}
        assert data["tags"] == {"env": "test"}

    def test_format_with_exception(self):
        """Test formatting a log record with exception."""
        formatter = JsonFormat(tb_as_str=False)

        try:
            raise ValueError("Test error")
        except ValueError:
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="/test/path.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=logging.sys.exc_info(),
            )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["message"] == "Error occurred"
        assert "exception" in data
        assert data["exception"]["type"] == "ValueError"
        assert data["exception"]["message"] == "Test error"

    def test_format_with_custom_options(self):
        """Test formatting with custom indent and sort options."""
        formatter = JsonFormat(indent=2, sort_keys=False, ensure_ascii=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.DEBUG,
            pathname="/test/path.py",
            lineno=10,
            msg="Debug message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["message"] == "Debug message"
        assert data["level_name"] == "DEBUG"

    def test_format_ignore_unset(self):
        """Test that ignore_unset filters out None values."""
        formatter = JsonFormat(ignore_unset=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="/test/path.py",
            lineno=20,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        # Should not have 'exception' key when exc_info is None and ignore_unset=True
        assert "exception" not in data
        assert data["message"] == "Warning message"

    def test_format_reduced_attrs(self):
        """Test formatting with reduced attributes."""
        formatter = JsonFormat(reduced_attrs=True, ignore_unset=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=30,
            msg="Info message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        # With reduced_attrs, should have limited fields
        assert "name" in data
        assert "message" in data
        assert "created_at" in data
        assert "level_name" in data
        # Should not have detailed fields like pathname, filename
        assert "pathname" not in data
        assert "filename" not in data
