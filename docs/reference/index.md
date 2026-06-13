# API reference overview

The API reference is generated from Python docstrings using
[mkdocstrings](https://mkdocstrings.github.io/). Use the navigation tabs to browse
by class.

## Public entry points

Import these from the top-level package:

```python
from pyfamilysafety import Authenticator, FamilySafety, Account, FamilySafetyAPI
from pyfamilysafety.enum import DayOfWeek, OverrideTarget, OverrideType, DeviceLimitsMode
from pyfamilysafety.schedule import AllottedInterval, DailyRestriction, DeviceLimitsSchedule
```

## Recommended usage layers

| Layer | When to use |
| --- | --- |
| `FamilySafety` + `Account` | Normal application code |
| `Authenticator` | Session creation and token refresh |
| `FamilySafetyAPI` | Advanced: endpoints without high-level wrappers |

## Async API

All network I/O is **async**. Use `asyncio.run()` or integrate with an async
framework (Home Assistant, FastAPI, etc.).

## Related documentation

- [User guide](../guide/family-safety-client.md) — workflows and examples
- [Endpoint map](../advanced/endpoints.md) — raw API coverage
- [Error handling](../advanced/error-handling.md) — exception types
