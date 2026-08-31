"""Unit tests for MemoryGroup."""

from __future__ import annotations

import logging

from xlogging.handler.memory import MemoryGroup
from xlogging.record.event import LogEvent


class TestMemoryGroupCreation:
    """Test MemoryGroup instantiation."""

    def test_create_basic_memory_handler(self):
        """Test creating a basic MemoryGroup."""
        handler = MemoryGroup()

        assert isinstance(handler, logging.Handler)
        assert handler.level == logging.NOTSET
        assert handler.records == []

    def test_create_with_level(self):
        """Test creating MemoryGroup with specific level."""
        handler = MemoryGroup(level=logging.INFO)

        assert handler.level == logging.INFO

    def test_create_with_date_format(self):
        """Test creating MemoryGroup with custom date format."""
        handler = MemoryGroup(date_format="%Y-%m-%d")

        assert handler._date_format == "%Y-%m-%d"


class TestMemoryGroupWithLogRecord:
    """Test MemoryGroup with standard logging.LogRecord."""

    def test_emit_standard_log_record(self):
        """Test emitting a standard LogRecord."""
        handler = MemoryGroup()

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

        assert len(handler.records) == 1
        assert handler.records[0] == record

    def test_emit_multiple_records(self):
        """Test emitting multiple LogRecords."""
        handler = MemoryGroup()

        for i in range(5):
            record = logging.LogRecord(
                name="test.logger",
                level=logging.INFO,
                pathname="test.py",
                lineno=10 + i,
                msg=f"Message {i}",
                args=(),
                exc_info=None,
            )
            handler.emit(record)

        assert len(handler.records) == 5

    def test_get_records(self):
        """Test retrieving records."""
        handler = MemoryGroup()

        # Emit records at different levels
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
        for level in levels:
            record = logging.LogRecord(
                name="test.logger",
                level=level,
                pathname="test.py",
                lineno=10,
                msg="Test message",
                args=(),
                exc_info=None,
            )
            handler.emit(record)

        # Get all records
        all_records = handler.get_records()
        assert len(all_records) == 4

        # Get records by level
        info_records = handler.get_records(level=logging.INFO)
        assert len(info_records) == 3  # INFO, WARNING, ERROR

        error_records = handler.get_records(level=logging.ERROR)
        assert len(error_records) == 1

    def test_clear_records(self):
        """Test clearing records."""
        handler = MemoryGroup()

        for i in range(3):
            record = logging.LogRecord(
                name="test.logger",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg=f"Message {i}",
                args=(),
                exc_info=None,
            )
            handler.emit(record)

        assert len(handler.records) == 3

        handler.clear()

        assert len(handler.records) == 0

    def test_export_records(self):
        """Test exporting records to dict."""
        handler = MemoryGroup()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Export test",
            args=(),
            exc_info=None,
        )

        handler.emit(record)
        exported = handler.export()

        assert len(exported) == 1
        assert isinstance(exported[0], dict)
        assert "message" in exported[0] or "msg" in exported[0]


class TestMemoryGroupWithLogEvent:
    """Test MemoryGroup with xlogging.LogEvent."""

    def test_emit_log_event(self):
        """Test emitting a LogEvent."""
        handler = MemoryGroup()

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

        assert len(handler.records) == 1
        assert handler.records[0] == event
        assert handler.records[0].metadata == {"key": "value"}
        assert handler.records[0].tags == {"env": "test"}

    def test_emit_multiple_log_events(self):
        """Test emitting multiple LogEvents."""
        handler = MemoryGroup()

        for i in range(3):
            event = LogEvent(
                name="test.logger",
                level=logging.INFO,
                pathname="test.py",
                lineno=10 + i,
                msg=f"Event {i}",
                args=(),
                exc_info=None,
                metadata={"index": i},
                tags={"batch": "test"},
            )
            handler.emit(event)

        assert len(handler.records) == 3
        assert all(hasattr(r, "metadata") for r in handler.records)
        assert all(hasattr(r, "tags") for r in handler.records)

    def test_get_records_with_events(self):
        """Test retrieving LogEvents by level."""
        handler = MemoryGroup()

        # Emit events at different levels
        for i, level in enumerate([logging.DEBUG, logging.INFO, logging.WARNING]):
            event = LogEvent(
                name="test.logger",
                level=level,
                pathname="test.py",
                lineno=10,
                msg=f"Event {i}",
                args=(),
                exc_info=None,
                metadata={"index": i, "level": logging.getLevelName(level)},
            )
            handler.emit(event)

        all_records = handler.get_records()
        assert len(all_records) == 3

        warning_records = handler.get_records(level=logging.WARNING)
        assert len(warning_records) == 1

    def test_export_log_events(self):
        """Test exporting LogEvents to dict."""
        handler = MemoryGroup()

        event = LogEvent(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Export event test",
            args=(),
            exc_info=None,
            metadata={"user": "bob", "action": "create"},
            tags={"env": "dev", "version": "1.0"},
        )

        handler.emit(event)
        exported = handler.export()

        assert len(exported) == 1
        assert isinstance(exported[0], dict)
        # Check that metadata and tags are included in export
        exported_data = exported[0]
        assert "metadata" in exported_data or any(
            key in exported_data for key in ["user", "action"]
        )

    def test_clear_log_events(self):
        """Test clearing LogEvents."""
        handler = MemoryGroup()

        for i in range(5):
            event = LogEvent(
                name="test.logger",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg=f"Event {i}",
                args=(),
                exc_info=None,
                metadata={"index": i},
            )
            handler.emit(event)

        assert len(handler.records) == 5

        handler.clear()

        assert len(handler.records) == 0


class TestMemoryGroupIntegration:
    """Integration tests for MemoryGroup."""

    def test_filter_and_export(self):
        """Test filtering records and exporting."""
        handler = MemoryGroup()

        # Add mixed records and events
        for i in range(3):
            record = logging.LogRecord(
                name="test.logger",
                level=logging.DEBUG,
                pathname="test.py",
                lineno=10,
                msg=f"Debug {i}",
                args=(),
                exc_info=None,
            )
            handler.emit(record)

        for i in range(2):
            event = LogEvent(
                name="test.logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=20,
                msg=f"Error {i}",
                args=(),
                exc_info=None,
                metadata={"error_id": i},
            )
            handler.emit(event)

        # Get only error level records
        error_records = handler.get_records(level=logging.ERROR)
        assert len(error_records) == 2

        # Export all
        exported = handler.export()
        assert len(exported) == 5

    def test_memory_handler_with_logger(self):
        """Test MemoryGroup integrated with a logger."""
        handler = MemoryGroup(level=logging.INFO)
        logger = logging.getLogger("test.integration")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Log some messages
        logger.debug("Debug message")  # Should not be captured
        logger.info("Info message")
        logger.warning("Warning message")

        # Check captured records
        assert len(handler.records) == 2
        assert handler.records[0].levelname == "INFO"
        assert handler.records[1].levelname == "WARNING"

        # Clean up
        logger.removeHandler(handler)
