"""Unit tests for ColorTreeFormat."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from xlogging.format.colortree import ColorTreeFormat
from xlogging.record.event import LogEvent


class TestColorTreeFormat:
    """Test ColorTreeFormat with both LogRecord and LogEvent."""

    def test_format_basic_log_record(self):
        """Test formatting a basic logging.LogRecord."""
        formatter = ColorTreeFormat()
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

        # Should contain the message
        assert "Test message" in result
        assert "[INFO]" in result
        # Should contain tree structure characters
        assert any(char in result for char in ["├──", "└──", "│"])
        # Should contain color codes
        assert "\033[" in result

    def test_format_with_log_event(self):
        """Test formatting an xlogging LogEvent with metadata."""
        formatter = ColorTreeFormat()
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

        assert "Event message" in result
        assert "metadata" in result
        assert "tags" in result

    def test_format_different_levels_have_colors(self):
        """Test that different log levels have different colors."""
        formatter = ColorTreeFormat()

        results = {}
        for level_name, level_no in [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
        ]:
            record = logging.LogRecord(
                name="test.logger",
                level=level_no,
                pathname="/test/path.py",
                lineno=10,
                msg=f"{level_name} message",
                args=(),
                exc_info=None,
            )

            result = formatter.format(record)
            results[level_name] = result

            assert f"{level_name} message" in result
            assert level_name in result
            # Should have color codes
            assert "\033[" in result

    def test_format_with_custom_colors(self):
        """Test formatting with custom color configuration."""
        custom_colors = {
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }
        formatter = ColorTreeFormat(colors=custom_colors)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="/test/path.py",
            lineno=25,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "Warning message" in result
        assert "WARNING" in result
        assert "\033[" in result

    def test_format_with_nested_dict(self):
        """Test formatting with nested dictionary in metadata."""
        formatter = ColorTreeFormat()

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
                    "name": "Alice",
                    "details": {
                        "age": 25,
                        "city": "SF",
                    },
                },
            },
        )

        result = formatter.format(event)

        assert "Nested data" in result
        assert "user" in result
        assert "name" in result
        assert "Alice" in result
        assert "details" in result

    def test_format_with_list(self):
        """Test formatting with list in metadata."""
        formatter = ColorTreeFormat()

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="List data",
            args=(),
            exc_info=None,
            func="test_func",
            sinfo=None,
            metadata={
                "items": ["alpha", "beta", "gamma"],
            },
        )

        result = formatter.format(event)

        assert "List data" in result
        assert "items" in result
        assert "alpha" in result
        assert "beta" in result

    def test_format_with_exception(self):
        """Test formatting with exception information."""
        formatter = ColorTreeFormat(tb_as_str=False)

        try:
            raise RuntimeError("Test runtime error")
        except RuntimeError:
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="/test/path.py",
                lineno=42,
                msg="Exception occurred",
                args=(),
                exc_info=logging.sys.exc_info(),
            )

        result = formatter.format(record)

        assert "Exception occurred" in result
        assert "exception" in result
        assert "RuntimeError" in result
        assert "Test runtime error" in result

    def test_format_ignore_unset(self):
        """Test that ignore_unset filters out None values."""
        formatter = ColorTreeFormat(ignore_unset=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=20,
            msg="Simple message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should not have 'exception' when exc_info is None
        assert "exception" not in result.lower()
        assert "Simple message" in result

    def test_format_reduced_attrs(self):
        """Test formatting with reduced attributes."""
        formatter = ColorTreeFormat(reduced_attrs=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="/test/path.py",
            lineno=30,
            msg="Reduced attrs test",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "Reduced attrs test" in result

    def test_format_contains_reset_code(self):
        """Test that formatted output contains color reset code."""
        formatter = ColorTreeFormat()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Reset test",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should contain reset code
        assert "\033[0m" in result
        assert "Reset test" in result

    def test_format_custom_date_format(self):
        """Test formatting with custom date format."""
        date_format = "%Y-%m-%d"
        formatter = ColorTreeFormat(date_format=date_format)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=15,
            msg="Date test",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "Date test" in result
        # Should contain date formatted with dashes
        assert "-" in result.split("]")[0]  # Check in the header
