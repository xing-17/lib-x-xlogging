from __future__ import annotations

import logging
from typing import Any


class ConsoleGroup(logging.StreamHandler):
    """
    Console Group Handler for logging.

    Args:
        stream (Any):
            The stream to which the log messages will be written. If None, defaults to sys.stderr.
        format (logging.Formatter | None):
            The formatter to use for formatting log messages. If None, a default formatter will be used

    Example:
        >>> handler = ConsoleGroup(
        ...     stream=sys.stdout,
        ...     format=ColorFormat(
        ...         format="%(log_color)s[%(asctime)s][%(levelname)-8s]%(reset)s %(message)s",
        ...         date_format="%Y-%m-%d %H:%M:%S",
        ...         colors={
        ...             "DEBUG": "cyan",
        ...             "INFO": "green",
        ...             ...
        ...     ),
        ... )
        >>> logger = logging.getLogger(__name__)
        >>> logger.addHandler(handler)

    """

    def __init__(
        self,
        stream: Any = None,
        format: logging.Formatter | None = None,
    ) -> None:
        super().__init__(stream)
        self.setFormatter(format)
