"""Unit tests for LogEvent."""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone

from xlogging.record.event import LogEvent


class TestLogEventCreation:
    """Test LogEvent instantiation and initialization."""

    def test_create_basic_log_event(self):
        """Test creating a basic LogEvent with required parameters."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        assert event.name == "test.logger"
        assert event.levelno == logging.INFO
        assert event.levelname == "INFO"
        assert event.pathname == "/test/path.py"
        assert event.lineno == 42
        assert event.msg == "Test message"
        assert event.getMessage() == "Test message"

    def test_create_with_created_at(self):
        """Test creating LogEvent with custom created_at datetime."""
        created_at = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Event with timestamp",
            args=(),
            exc_info=None,
            created_at=created_at,
        )

        assert event.created_at == created_at
        assert event.getMessage() == "Event with timestamp"

    def test_create_with_metadata(self):
        """Test creating LogEvent with metadata."""
        metadata = {"user_id": "12345", "action": "login", "ip": "192.168.1.1"}

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="User action",
            args=(),
            exc_info=None,
            metadata=metadata,
        )

        assert event.metadata == metadata
        assert event.metadata["user_id"] == "12345"
        assert event.metadata["action"] == "login"

    def test_create_with_tags(self):
        """Test creating LogEvent with tags."""
        tags = {"env": "production", "service": "api", "version": "1.2.3"}

        event = LogEvent(
            name="test.logger",
            level=logging.WARNING,
            pathname="/test/path.py",
            lineno=42,
            msg="Warning message",
            args=(),
            exc_info=None,
            tags=tags,
        )

        assert event.tags == tags
        assert event.tags["env"] == "production"
        assert event.tags["service"] == "api"

    def test_create_with_all_custom_fields(self):
        """Test creating LogEvent with all custom fields."""
        created_at = datetime(2024, 6, 20, 14, 30, 0, tzinfo=timezone.utc)
        metadata = {"request_id": "abc-123", "duration_ms": 250}
        tags = {"env": "staging", "region": "us-west"}

        event = LogEvent(
            name="app.service",
            level=logging.ERROR,
            pathname="/app/service.py",
            lineno=100,
            msg="Service error",
            args=(),
            exc_info=None,
            func="handle_request",
            sinfo=None,
            created_at=created_at,
            metadata=metadata,
            tags=tags,
        )

        assert event.name == "app.service"
        assert event.levelname == "ERROR"
        assert event.created_at == created_at
        assert event.metadata == metadata
        assert event.tags == tags
        assert event.funcName == "handle_request"


class TestLogEventDefaults:
    """Test LogEvent default values and None handling."""

    def test_created_at_defaults_to_none(self):
        """Test that created_at defaults to None when not provided."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
        )

        assert event.created_at is None

    def test_metadata_defaults_to_empty_dict(self):
        """Test that metadata defaults to empty dict when not provided."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
        )

        assert event.metadata == {}
        assert isinstance(event.metadata, dict)

    def test_tags_defaults_to_empty_dict(self):
        """Test that tags defaults to empty dict when not provided."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
        )

        assert event.tags == {}
        assert isinstance(event.tags, dict)

    def test_metadata_none_creates_empty_dict(self):
        """Test that passing None for metadata creates empty dict."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
            metadata=None,
        )

        assert event.metadata == {}

    def test_tags_none_creates_empty_dict(self):
        """Test that passing None for tags creates empty dict."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
            tags=None,
        )

        assert event.tags == {}


class TestLogEventCompatibility:
    """Test LogEvent compatibility with LogRecord functionality."""

    def test_inherits_from_log_record(self):
        """Test that LogEvent is a subclass of LogRecord."""
        assert issubclass(LogEvent, logging.LogRecord)

    def test_get_message_with_args(self):
        """Test getMessage with string formatting arguments."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="User %s logged in from %s",
            args=("alice", "192.168.1.1"),
            exc_info=None,
        )

        assert event.getMessage() == "User alice logged in from 192.168.1.1"

    def test_with_exception_info(self):
        """Test LogEvent with exception information."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()
            event = LogEvent(
                name="test.logger",
                level=logging.ERROR,
                pathname="/test/path.py",
                lineno=20,
                msg="Error occurred",
                args=(),
                exc_info=exc_info,
            )

        assert event.exc_info is not None
        assert event.exc_info[0] is ValueError
        assert str(event.exc_info[1]) == "Test exception"

    def test_level_names_mapping(self):
        """Test that level numbers map to correct level names."""
        levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ]

        for level_no, level_name in levels:
            event = LogEvent(
                name="test.logger",
                level=level_no,
                pathname="/test/path.py",
                lineno=10,
                msg="Test",
                args=(),
                exc_info=None,
            )

            assert event.levelno == level_no
            assert event.levelname == level_name

    def test_func_name_parameter(self):
        """Test that func parameter is properly stored."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
            func="my_function",
        )

        assert event.funcName == "my_function"

    def test_stack_info_parameter(self):
        """Test that sinfo parameter is properly stored."""
        stack_info = "Stack trace info here"
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
            sinfo=stack_info,
        )

        assert event.stack_info == stack_info


class TestLogEventMutability:
    """Test that LogEvent metadata and tags are mutable."""

    def test_metadata_is_mutable(self):
        """Test that metadata can be modified after creation."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
            metadata={"initial": "value"},
        )

        event.metadata["new_key"] = "new_value"
        event.metadata["initial"] = "updated"

        assert event.metadata["new_key"] == "new_value"
        assert event.metadata["initial"] == "updated"

    def test_tags_is_mutable(self):
        """Test that tags can be modified after creation."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
            tags={"env": "dev"},
        )

        event.tags["service"] = "api"
        event.tags["env"] = "production"

        assert event.tags["service"] == "api"
        assert event.tags["env"] == "production"

    def test_metadata_dict_is_copy(self):
        """Test that metadata dict is a copy, not the original."""
        original_metadata = {"key": "value"}

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
            metadata=original_metadata,
        )

        # Modify the event's metadata
        event.metadata["new_key"] = "new_value"

        # Original should not be affected
        assert "new_key" not in original_metadata
        assert original_metadata == {"key": "value"}

    def test_tags_dict_is_copy(self):
        """Test that tags dict is a copy, not the original."""
        original_tags = {"env": "dev"}

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
            tags=original_tags,
        )

        # Modify the event's tags
        event.tags["service"] = "api"

        # Original should not be affected
        assert "service" not in original_tags
        assert original_tags == {"env": "dev"}


class TestLogEventEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_message(self):
        """Test LogEvent with empty message."""
        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="",
            args=(),
            exc_info=None,
        )

        assert event.msg == ""
        assert event.getMessage() == ""

    def test_complex_metadata_types(self):
        """Test LogEvent with complex metadata types."""
        metadata = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "list": [1, 2, 3],
            "nested": {"inner": "value"},
            "none": None,
        }

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Complex metadata",
            args=(),
            exc_info=None,
            metadata=metadata,
        )

        assert event.metadata["string"] == "value"
        assert event.metadata["number"] == 42
        assert event.metadata["float"] == 3.14
        assert event.metadata["bool"] is True
        assert event.metadata["list"] == [1, 2, 3]
        assert event.metadata["nested"]["inner"] == "value"
        assert event.metadata["none"] is None

    def test_unicode_in_metadata(self):
        """Test LogEvent with unicode characters in metadata."""
        metadata = {
            "chinese": "你好世界",
            "emoji": "🎉🚀",
            "special": "Ñoño",
        }

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Unicode test",
            args=(),
            exc_info=None,
            metadata=metadata,
        )

        assert event.metadata["chinese"] == "你好世界"
        assert event.metadata["emoji"] == "🎉🚀"
        assert event.metadata["special"] == "Ñoño"

    def test_very_long_metadata(self):
        """Test LogEvent with large metadata."""
        metadata = {f"key_{i}": f"value_{i}" for i in range(100)}

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=10,
            msg="Large metadata",
            args=(),
            exc_info=None,
            metadata=metadata,
        )

        assert len(event.metadata) == 100
        assert event.metadata["key_0"] == "value_0"
        assert event.metadata["key_99"] == "value_99"
