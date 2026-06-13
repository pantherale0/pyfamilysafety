# Logging

**pyfamilysafety** uses Python's standard `logging` module. Enable debug output to
trace HTTP requests and authentication.

## Logger names

| Logger | Module |
| --- | --- |
| `pyfamilysafety` | `FamilySafety` |
| `pyfamilysafety.api` | HTTP requests and responses |
| `pyfamilysafety.authenticator` | Token exchange and refresh |
| `pyfamilysafety.account` | Account updates |

## Basic configuration

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)
```

## What debug logs include

- Endpoint names and built URLs (without printing full tokens)
- HTTP status codes
- Token refresh events
- Aggregator warnings during `FamilySafety.update()`

## Security

Do not log `auth.refresh_token` or raw `Authorization` headers in production.
The sample script in the repository logs the refresh token at DEBUG level for
development only — remove or redact this in deployed applications.

## Aggregator warnings

At WARNING level, `FamilySafety.update()` logs when an `AggregatorException` is
swallowed:

```
Aggregator exception occured, ignoring this update request.
```

This indicates a transient Microsoft-side failure; the next `update()` may succeed.
