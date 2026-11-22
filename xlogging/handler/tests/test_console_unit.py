"""Unit tests for ConsoleGroup."""

from __future__ import annotations

import logging
import sys
from io import StringIO

from xlogging.format.color import ColorFormat
from xlogging.format.json import JsonFormat
from xlogging.format.tree import TreeFormat
from xlogging.handler.console import ColorConsoleGroup, ConsoleGroup
from xlogging.record.event import LogEvent


class TestConsoleGroupCreation:
    """Test ConsoleGroup instantiation."""

    def test_create_basic_console_handler(self):
        """Test creating a basic ConsoleGroup."""
        handler = ConsoleGroup()

        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream == sys.stderr

    def test_create_with_custom_stream(self):
        """Test creating ConsoleGroup with custom stream."""
        stream = StringIO()
        handler = ConsoleGroup(stream=stream)

        assert handler.stream == stream

    def test_create_with_formatter(self):
        """Test creating ConsoleGroup with formatter."""
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler = ConsoleGroup(format=formatter)

        assert handler.formatter == formatter


class TestConsoleGroupWithLogRecord:
    """Test ConsoleGroup with standard logging.LogRecord."""

    def test_emit_standard_log_record(self):
        """Test emitting a standard LogRecord."""
        stream = StringIO()
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler = ConsoleGroup(stream=stream, format=formatter)

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
        output = stream.getvalue()

        assert "INFO - Test message" in output

    def test_emit_with_json_formatter(self):
        """Test emitting LogRecord with JsonFormat."""
        stream = StringIO()
        formatter = JsonFormat(indent=None)
        handler = ConsoleGroup(stream=stream, format=formatter)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=20,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)
        output = stream.getvalue()

        assert "Warning message" in output

    def test_emit_with_tree_formatter(self):
        """Test emitting LogRecord with TreeFormat."""
        stream = StringIO()
        formatter = TreeFormat()
        handler = ConsoleGroup(stream=stream, format=formatter)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=30,
            msg="Error message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)
        output = stream.getvalue()

        assert "Error message" in output


class TestConsoleGroupWithLogEvent:
    """Test ConsoleGroup with xlogging.LogEvent."""

    def test_emit_log_event(self):
        """Test emitting a LogEvent."""
        stream = StringIO()
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler = ConsoleGroup(stream=stream, format=formatter)

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
        output = stream.getvalue()

        assert "INFO - Event message" in output

    def test_emit_log_event_with_json_formatter(self):
        """Test emitting LogEvent with JsonFormat."""
        stream = StringIO()
        formatter = JsonFormat(indent=None)
        handler = ConsoleGroup(stream=stream, format=formatter)

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
        output = stream.getvalue()

        assert "Event with metadata" in output
        assert "metadata" in output
        assert "tags" in output

    def test_emit_log_event_with_tree_formatter(self):
        """Test emitting LogEvent with TreeFormat."""
        stream = StringIO()
        formatter = TreeFormat()
        handler = ConsoleGroup(stream=stream, format=formatter)

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
        output = stream.getvalue()

        assert "Event with nested data" in output


class TestColorConsoleGroup:
    """Test ColorConsoleGroup."""

    def test_create_uses_color_format_by_default(self):
        """Test the handler is created with a ColorFormat formatter."""
        handler = ColorConsoleGroup()

        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream == sys.stderr
        assert isinstance(handler.formatter, ColorFormat)

    def test_create_with_custom_stream(self):
        """Test creating ColorConsoleGroup with custom stream."""
        stream = StringIO()
        handler = ColorConsoleGroup(stream=stream)

        assert handler.stream == stream

    def test_emit_log_record(self):
        """Test emitting a record writes the message to the stream."""
        stream = StringIO()
        handler = ColorConsoleGroup(stream=stream)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Color message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)
        output = stream.getvalue()

        assert "Color message" in output
        assert "\x1b[" in output

    def test_emit_via_logger(self):
        """Test emitting through a real logger."""
        stream = StringIO()
        handler = ColorConsoleGroup(stream=stream)
        logger = logging.getLogger("test.color_console_group")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.addHandler(handler)
        try:
            logger.error("Color error")
        finally:
            logger.removeHandler(handler)

        assert "Color error" in stream.getvalue()
