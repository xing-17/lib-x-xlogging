from __future__ import annotations

import logging
from typing import Optional


class ConsoleGroup(logging.StreamHandler):
    def __init__(
        self,
        stream=None,
        formatter: Optional[logging.Formatter] = None,
    ) -> None:
        super().__init__(stream)
        self.setFormatter(formatter)
