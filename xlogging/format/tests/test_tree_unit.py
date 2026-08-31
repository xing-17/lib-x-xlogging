"""Unit tests for TreeFormat."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from xlogging.format.tree import TreeFormat
from xlogging.record.event import LogEvent


class TestTreeFormat:
    """Test TreeFormat with both LogRecord and LogEvent."""

    def test_format_basic_log_record(self):
        """Test formatting a basic logging.LogRecord."""
        formatter = TreeFormat()
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

        # Should contain the message in header
        assert "Test message" in result
        assert "[INFO]" in result
        # Should contain tree structure characters
        assert any(char in result for char in ["├──", "└──", "│"])

    def test_format_with_log_event(self):
        """Test formatting an xlogging LogEvent with metadata and tags."""
        formatter = TreeFormat()
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
            metadata={"key1": "value1", "key2": "value2"},
            tags={"env": "test", "version": "1.0"},
        )

        result = formatter.format(event)

        assert "Event message" in result
        assert "metadata" in result
        assert "tags" in result
        assert "key1" in result
        assert "value1" in result

    def test_format_with_nested_dict(self):
        """Test formatting a log event with nested dictionary metadata."""
        formatter = TreeFormat()

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Nested data",
            args=(),
            exc_info=None,
            func="test_func",
            sinfo=None,
            metadata={
                "user": {
                    "name": "John",
                    "age": 30,
                    "address": {
                        "city": "NYC",
                        "zip": "10001",
                    },
                },
            },
        )

        result = formatter.format(event)

        assert "Nested data" in result
        assert "user" in result
        assert "name" in result
        assert "John" in result
        assert "address" in result
        assert "city" in result

    def test_format_with_list(self):
        """Test formatting a log event with list in metadata."""
        formatter = TreeFormat()

        event = LogEvent(
            name="test.logger",
            level=logging.WARNING,
            pathname="/test/path.py",
            lineno=42,
            msg="List data",
            args=(),
            exc_info=None,
            func="test_func",
            sinfo=None,
            metadata={
                "items": ["item1", "item2", "item3"],
                "numbers": [1, 2, 3],
            },
        )

        result = formatter.format(event)

        assert "List data" in result
        assert "items" in result
        assert "item1" in result
        assert "numbers" in result

    def test_format_with_exception(self):
        """Test formatting a log record with exception."""
        formatter = TreeFormat(tb_as_str=False)

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

        assert "Error occurred" in result
        assert "exception" in result
        assert "ValueError" in result
        assert "Test error" in result

    def test_format_ignore_unset(self):
        """Test that ignore_unset filters out None values."""
        formatter = TreeFormat(ignore_unset=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=20,
            msg="Clean message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should not have 'exception' in output when exc_info is None
        assert "exception" not in result.lower()
        assert "Clean message" in result

    def test_format_reduced_attrs(self):
        """Test formatting with reduced attributes."""
        formatter = TreeFormat(reduced_attrs=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.DEBUG,
            pathname="/test/path.py",
            lineno=30,
            msg="Debug message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "Debug message" in result
        assert "name" in result
        # Should not have verbose fields like pathname
        assert "pathname" not in result.lower() or "/test/path.py" not in result

    def test_format_multiline_value(self):
        """Test formatting with multiline string values."""
        formatter = TreeFormat()

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Multiline test",
            args=(),
            exc_info=None,
            func="test_func",
            sinfo=None,
            metadata={
                "description": "Line 1\nLine 2\nLine 3",
            },
        )

        result = formatter.format(event)

        assert "Multiline test" in result
        assert "description" in result
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_format_custom_date_format(self):
        """Test formatting with custom date format."""
        date_format = "%Y/%m/%d %H:%M"
        formatter = TreeFormat(date_format=date_format)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Date format test",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "Date format test" in result
        # Should contain date in the custom format (YYYY/MM/DD)
        assert "/" in result.split("]")[0]  # Check in the header part
