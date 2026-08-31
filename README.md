# xlogging

A lightweight extension on top of Python's built-in `logging` module. Structured, readable output for local dev and production services.

## What it solves

stdlib `logging` emits flat, hard-to-read text. When a log record carries nested context — request metadata, exception details, tags — there's no clean way to display or store it. `xlogging` adds structured formatters and a first-class `LogEvent` record so that context travels with the message.

## Key features

- **TreeFormat / ColorTreeFormat** — renders nested dicts and lists as a Unicode tree, readable in terminal
- **JsonFormat** — emits newline-delimited JSON for file storage and log aggregators
- **EventStream** — a `Logger` subclass that accepts `metadata` and `tags` per call, and supports per-logger timezone
- **LogEvent** — a `LogRecord` subclass with `created_at`, `metadata`, and `tags` fields
- **FileGroup** — rotating file handler that defaults to JSON format
- **ConsoleGroup** — stream handler with pluggable formatter

## Usage

```python
from xlogging import EventStream, ColorTreeFormat, ConsoleGroup

stream = EventStream.from_options(
    name="app",
    handlers=[ConsoleGroup(format=ColorTreeFormat())],
)

stream.info(
    "order filled",
    metadata={"symbol": "AAPL", "qty": 100, "price": 189.5},
    tags={"strategy": "momentum"},
)

stream.error(
    "execution failed",
    metadata={"order_id": "x-001", "reason": "insufficient margin"},
)
```

Terminal output:

```
[2026-08-31 09:00:00][INFO]: order filled
    ├── metadata:
    │   ├── symbol: AAPL
    │   ├── qty: 100
    │   └── price: 189.5
    └── tags:
        └── strategy: momentum
```

### File handler

```python
from xlogging import EventStream, FileGroup

stream = EventStream.from_options(
    name="app",
    handlers=[FileGroup(path="logs/", name="app")],
)
```

Writes rotating JSON logs to `logs/app.log` (10 MB per file, 1 backup by default).

## Install

```bash
pip install lib-x-xlogging
```

Requires Python 3.11+. Runtime dependency: `colorlog`.
