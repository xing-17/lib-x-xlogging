"""Unit tests for EventStream."""

from __future__ import annotations

import logging
from datetime import datetime
from io import StringIO
from zoneinfo import ZoneInfo

import pytest

from xlogging.format.json import JsonFormat
from xlogging.format.tree import TreeFormat
from xlogging.record.event import LogEvent
from xlogging.stream.event import EventStream


class TestEventStreamCreation:
    """Test EventStream instantiation."""

    def test_create_basic_event_stream(self):
        """Test creating a basic EventStream."""
        stream = EventStream("test.logger")

        assert stream.name == "test.logger"
        assert stream.level == logging.NOTSET
        assert isinstance(stream, logging.Logger)

    def test_create_with_level(self):
        """Test creating EventStream with specific level."""
        stream = EventStream("test.logger", level=logging.INFO)

        assert stream.name == "test.logger"
        assert stream.level == logging.INFO

    def test_create_with_timezone_string(self):
        """Test creating EventStream with timezone string."""
        stream = EventStream("test.logger", timezone="America/New_York")

        assert stream._timezone == ZoneInfo("America/New_York")

    def test_create_with_timezone_object(self):
        """Test creating EventStream with ZoneInfo object."""
        tz = ZoneInfo("Asia/Tokyo")
        stream = EventStream("test.logger", timezone=tz)

        assert stream._timezone == tz

    def test_create_with_default_timezone(self):
        """Test that default timezone is UTC."""
        stream = EventStream("test.logger")

        assert stream._timezone == ZoneInfo("UTC")

    def test_create_with_metadata(self):
        """Test creating EventStream with default metadata."""
        metadata = {"app": "myapp", "version": "1.0"}
        stream = EventStream("test.logger", metadata=metadata)

        assert stream._metadata == metadata

    def test_create_with_tags(self):
        """Test creating EventStream with default tags."""
        tags = {"env": "production", "region": "us-west"}
        stream = EventStream("test.logger", tags=tags)

        assert stream._tags == tags

    def test_create_with_all_parameters(self):
        """Test creating EventStream with all parameters."""
        metadata = {"service": "api"}
        tags = {"env": "dev"}
        stream = EventStream(
            "test.logger",
            level=logging.DEBUG,
            timezone="Europe/London",
            metadata=metadata,
            tags=tags,
        )

        assert stream.name == "test.logger"
        assert stream.level == logging.DEBUG
        assert stream._timezone == ZoneInfo("Europe/London")
        assert stream._metadata == metadata
        assert stream._tags == tags


class TestEventStreamMakeRecord:
    """Test EventStream record creation."""

    def test_make_record_returns_log_event(self):
        """Test that makeRecord returns LogEvent instances."""
        stream = EventStream("test.logger")

        record = stream.makeRecord(
            name="test.logger",
            level=logging.INFO,
            fn="/test/path.py",
            lno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        assert isinstance(record, LogEvent)
        assert record.name == "test.logger"
        assert record.levelno == logging.INFO
        assert record.msg == "Test message"

    def test_make_record_with_created_at(self):
        """Test that makeRecord includes created_at timestamp."""
        stream = EventStream("test.logger")

        before = datetime.now(tz=ZoneInfo("UTC"))
        record = stream.makeRecord(
            name="test.logger",
            level=logging.INFO,
            fn="/test/path.py",
            lno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        after = datetime.now(tz=ZoneInfo("UTC"))

        assert record.created_at is not None
        assert before <= record.created_at <= after

    def test_make_record_with_default_metadata(self):
        """Test that makeRecord includes default metadata."""
        stream = EventStream("test.logger", metadata={"app": "test"})

        record = stream.makeRecord(
            name="test.logger",
            level=logging.INFO,
            fn="/test/path.py",
            lno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        assert record.metadata == {"app": "test"}

    def test_make_record_with_default_tags(self):
        """Test that makeRecord includes default tags."""
        stream = EventStream("test.logger", tags={"env": "test"})

        record = stream.makeRecord(
            name="test.logger",
            level=logging.INFO,
            fn="/test/path.py",
            lno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        assert record.tags == {"env": "test"}

    def test_make_record_merges_metadata(self):
        """Test that makeRecord merges default and extra metadata."""
        stream = EventStream("test.logger", metadata={"app": "test"})

        record = stream.makeRecord(
            name="test.logger",
            level=logging.INFO,
            fn="/test/path.py",
            lno=42,
            msg="Test message",
            args=(),
            exc_info=None,
            extra={"metadata": {"user": "alice"}},
        )

        assert record.metadata == {"app": "test", "user": "alice"}

    def test_make_record_merges_tags(self):
        """Test that makeRecord merges default and extra tags."""
        stream = EventStream("test.logger", tags={"env": "test"})

        record = stream.makeRecord(
            name="test.logger",
            level=logging.INFO,
            fn="/test/path.py",
            lno=42,
            msg="Test message",
            args=(),
            exc_info=None,
            extra={"tags": {"version": "1.0"}},
        )

        assert record.tags == {"env": "test", "version": "1.0"}


class TestEventStreamLoggingMethods:
    """Test EventStream logging methods (info, debug, warning, error, critical)."""

    def test_info_method(self):
        """Test info logging method."""
        stream = EventStream("test.logger", level=logging.INFO)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.info("Info message")

        assert len(handler.buffer) == 1
        record = handler.buffer[0]
        assert isinstance(record, LogEvent)
        assert record.levelname == "INFO"
        assert record.getMessage() == "Info message"

    def test_debug_method(self):
        """Test debug logging method."""
        stream = EventStream("test.logger", level=logging.DEBUG)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.debug("Debug message")

        assert len(handler.buffer) == 1
        record = handler.buffer[0]
        assert isinstance(record, LogEvent)
        assert record.levelname == "DEBUG"

    def test_warning_method(self):
        """Test warning logging method."""
        stream = EventStream("test.logger", level=logging.WARNING)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.warning("Warning message")

        assert len(handler.buffer) == 1
        record = handler.buffer[0]
        assert isinstance(record, LogEvent)
        assert record.levelname == "WARNING"

    def test_error_method(self):
        """Test error logging method."""
        stream = EventStream("test.logger", level=logging.ERROR)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.error("Error message")

        assert len(handler.buffer) == 1
        record = handler.buffer[0]
        assert isinstance(record, LogEvent)
        assert record.levelname == "ERROR"

    def test_critical_method(self):
        """Test critical logging method."""
        stream = EventStream("test.logger", level=logging.CRITICAL)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.critical("Critical message")

        assert len(handler.buffer) == 1
        record = handler.buffer[0]
        assert isinstance(record, LogEvent)
        assert record.levelname == "CRITICAL"

    def test_exception_method(self):
        """Test exception logging method."""
        stream = EventStream("test.logger", level=logging.ERROR)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        try:
            raise ValueError("Test error")
        except ValueError:
            stream.exception("Exception occurred")

        assert len(handler.buffer) == 1
        record = handler.buffer[0]
        assert isinstance(record, LogEvent)
        assert record.exc_info is not None

    def test_log_method(self):
        """Test generic log method."""
        stream = EventStream("test.logger", level=logging.DEBUG)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.log(logging.WARNING, "Log message")

        assert len(handler.buffer) == 1
        record = handler.buffer[0]
        assert isinstance(record, LogEvent)
        assert record.levelname == "WARNING"


class TestEventStreamMetadataAndTags:
    """Test EventStream metadata and tags handling."""

    def test_info_with_metadata(self):
        """Test info method with metadata parameter."""
        stream = EventStream("test.logger", level=logging.INFO)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.info("Test", metadata={"user": "alice"})

        record = handler.buffer[0]
        assert record.metadata == {"user": "alice"}

    def test_info_with_tags(self):
        """Test info method with tags parameter."""
        stream = EventStream("test.logger", level=logging.INFO)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.info("Test", tags={"env": "prod"})

        record = handler.buffer[0]
        assert record.tags == {"env": "prod"}

    def test_info_with_metadata_and_tags(self):
        """Test info method with both metadata and tags."""
        stream = EventStream("test.logger", level=logging.INFO)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.info("Test", metadata={"user": "bob"}, tags={"env": "dev"})

        record = handler.buffer[0]
        assert record.metadata == {"user": "bob"}
        assert record.tags == {"env": "dev"}

    def test_metadata_merging_with_defaults(self):
        """Test that metadata merges with default metadata."""
        stream = EventStream(
            "test.logger",
            level=logging.INFO,
            metadata={"app": "myapp"},
        )
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.info("Test", metadata={"user": "charlie"})

        record = handler.buffer[0]
        assert record.metadata == {"app": "myapp", "user": "charlie"}

    def test_tags_merging_with_defaults(self):
        """Test that tags merge with default tags."""
        stream = EventStream(
            "test.logger",
            level=logging.INFO,
            tags={"env": "staging"},
        )
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.info("Test", tags={"version": "2.0"})

        record = handler.buffer[0]
        assert record.tags == {"env": "staging", "version": "2.0"}

    def test_all_methods_support_metadata_and_tags(self):
        """Test that all logging methods support metadata and tags."""
        stream = EventStream("test.logger", level=logging.DEBUG)
        handler = logging.handlers.MemoryHandler(capacity=100)
        stream.addHandler(handler)

        methods = [
            ("debug", logging.DEBUG),
            ("info", logging.INFO),
            ("warning", logging.WARNING),
            ("error", logging.ERROR),
            ("critical", logging.CRITICAL),
        ]

        for method_name, level in methods:
            method = getattr(stream, method_name)
            method(
                f"{method_name} message",
                metadata={"key": method_name},
                tags={"level": method_name},
            )

        assert len(handler.buffer) == 5
        for i, (method_name, _) in enumerate(methods):
            record = handler.buffer[i]
            assert record.metadata == {"key": method_name}
            assert record.tags == {"level": method_name}


class TestEventStreamWithFormatters:
    """Test EventStream integration with formatters."""

    def test_with_json_formatter(self):
        """Test EventStream with JsonFormat formatter."""
        stream = EventStream("test.logger", level=logging.INFO)

        output = StringIO()
        handler = logging.StreamHandler(output)
        handler.setFormatter(JsonFormat(indent=None))
        stream.addHandler(handler)

        stream.info("Test message", metadata={"key": "value"})

        result = output.getvalue()
        assert "Test message" in result
        assert "key" in result
        assert "value" in result
        assert "INFO" in result

    def test_with_tree_formatter(self):
        """Test EventStream with TreeFormat formatter."""
        stream = EventStream("test.logger", level=logging.INFO)

        output = StringIO()
        handler = logging.StreamHandler(output)
        handler.setFormatter(TreeFormat())
        stream.addHandler(handler)

        stream.info("Test message", metadata={"key": "value"}, tags={"env": "test"})

        result = output.getvalue()
        assert "Test message" in result
        assert "[INFO]" in result
        assert "metadata" in result
        assert "tags" in result

    def test_with_standard_formatter(self):
        """Test EventStream with standard logging.Formatter."""
        stream = EventStream("test.logger", level=logging.INFO)

        output = StringIO()
        handler = logging.StreamHandler(output)
        handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        stream.addHandler(handler)

        stream.info("Test message")

        result = output.getvalue()
        assert "INFO - Test message" in result


class TestEventStreamHelperMethods:
    """Test EventStream helper methods."""

    def test_resolve_timezone_with_none(self):
        """Test timezone resolution with None defaults to UTC."""
        stream = EventStream("test.logger")
        tz = stream._resolve_timezone(None)

        assert tz == ZoneInfo("UTC")

    def test_resolve_timezone_with_string(self):
        """Test timezone resolution with string."""
        stream = EventStream("test.logger")
        tz = stream._resolve_timezone("Asia/Shanghai")

        assert tz == ZoneInfo("Asia/Shanghai")

    def test_resolve_timezone_with_zoneinfo(self):
        """Test timezone resolution with ZoneInfo object."""
        stream = EventStream("test.logger")
        expected = ZoneInfo("Europe/Paris")
        tz = stream._resolve_timezone(expected)

        assert tz == expected

    def test_resolve_timezone_with_invalid_type_raises_error(self):
        """Test timezone resolution with invalid type raises TypeError."""
        stream = EventStream("test.logger")

        with pytest.raises(TypeError, match="Invalid timezone type"):
            stream._resolve_timezone(123)  # type: ignore

    def test_merge_dict_with_none(self):
        """Test dict merging with None update."""
        stream = EventStream("test.logger")
        base = {"a": 1, "b": 2}

        result = stream._merge_dict(base, None)

        assert result == {"a": 1, "b": 2}

    def test_merge_dict_with_update(self):
        """Test dict merging with update dict."""
        stream = EventStream("test.logger")
        base = {"a": 1, "b": 2}
        update = {"b": 3, "c": 4}

        result = stream._merge_dict(base, update)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_dict_does_not_modify_base(self):
        """Test that merge_dict doesn't modify the base dict."""
        stream = EventStream("test.logger")
        base = {"a": 1}
        update = {"b": 2}

        result = stream._merge_dict(base, update)

        assert base == {"a": 1}  # unchanged
        assert result == {"a": 1, "b": 2}

    def test_get_current_datetime_uses_timezone(self):
        """Test that _get_current_datetime uses the configured timezone."""
        stream = EventStream("test.logger", timezone="Asia/Tokyo")

        dt = stream._get_current_datetime()

        assert dt.tzinfo == ZoneInfo("Asia/Tokyo")


class TestEventStreamEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_metadata_and_tags(self):
        """Test with empty metadata and tags."""
        stream = EventStream("test.logger", level=logging.INFO, metadata={}, tags={})
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.info("Test")

        record = handler.buffer[0]
        assert record.metadata == {}
        assert record.tags == {}

    def test_logging_with_args(self):
        """Test logging with format arguments."""
        stream = EventStream("test.logger", level=logging.INFO)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.info("User %s logged in", "alice")

        record = handler.buffer[0]
        assert record.getMessage() == "User alice logged in"

    def test_multiple_handlers(self):
        """Test EventStream with multiple handlers."""
        stream = EventStream("test.logger", level=logging.INFO)

        handler1 = logging.handlers.MemoryHandler(capacity=10)
        handler2 = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler1)
        stream.addHandler(handler2)

        stream.info("Test message")

        assert len(handler1.buffer) == 1
        assert len(handler2.buffer) == 1
        assert isinstance(handler1.buffer[0], LogEvent)
        assert isinstance(handler2.buffer[0], LogEvent)

    def test_level_filtering(self):
        """Test that log level filtering works correctly."""
        stream = EventStream("test.logger", level=logging.WARNING)
        handler = logging.handlers.MemoryHandler(capacity=10)
        stream.addHandler(handler)

        stream.debug("Debug message")
        stream.info("Info message")
        stream.warning("Warning message")
        stream.error("Error message")

        assert len(handler.buffer) == 2  # Only warning and error
        assert handler.buffer[0].levelname == "WARNING"
        assert handler.buffer[1].levelname == "ERROR"
