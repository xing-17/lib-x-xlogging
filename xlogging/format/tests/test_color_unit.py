"""Unit tests for ColorFormat."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from xlogging.format.color import ColorFormat
from xlogging.record.event import LogEvent


class TestColorFormat:
    """Test ColorFormat with both LogRecord and LogEvent."""

    def test_format_basic_log_record(self):
        """Test formatting a basic logging.LogRecord."""
        formatter = ColorFormat()
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

        # Result should contain the message
        assert "Test message" in result
        # Result should contain color escape codes
        assert "\033[" in result or result.startswith("\033")

    def test_format_with_log_event(self):
        """Test formatting an xlogging LogEvent."""
        formatter = ColorFormat()
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
        assert "INFO" in result

    def test_format_different_levels(self):
        """Test formatting records with different log levels."""
        formatter = ColorFormat()

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

            assert f"{level_name} message" in result
            assert level_name in result

    def test_format_with_custom_colors(self):
        """Test formatting with custom color configuration."""
        custom_colors = {
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }
        formatter = ColorFormat(colors=custom_colors)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="/test/path.py",
            lineno=25,
            msg="Warning with custom color",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "Warning with custom color" in result
        assert "WARNING" in result

    def test_format_with_custom_format_string(self):
        """Test formatting with custom format string."""
        custom_format = "[%(levelname)s] %(name)s: %(message)s"
        formatter = ColorFormat(format=custom_format)

        record = logging.LogRecord(
            name="custom.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=15,
            msg="Custom format message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "Custom format message" in result
        assert "custom.logger" in result
        assert "[INFO]" in result

    def test_format_with_custom_date_format(self):
        """Test formatting with custom date format."""
        date_format = "%Y-%m-%d"
        formatter = ColorFormat(date_format=date_format)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=20,
            msg="Date format test",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "Date format test" in result

    def test_format_contains_reset_code(self):
        """Test that formatted output contains color reset code."""
        formatter = ColorFormat()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=30,
            msg="Reset code test",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should end with reset code
        assert result.endswith("\033[0m")
