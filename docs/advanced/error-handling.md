# Error handling

**pyfamilysafety** raises typed exceptions for HTTP failures. Handle them at the
boundary of your async code.

## Exception hierarchy

```
HttpException
├── Unauthorized          (401)
├── RequestDenied         (403)
└── AggregatorException   (500, known aggregator message)
```

## When each exception is raised

| Exception | Typical cause |
| --- | --- |
| `Unauthorized` | Invalid or expired auth code/refresh token during login or refresh |
| `RequestDenied` | Authenticated but forbidden (wrong account, missing permission) |
| `AggregatorException` | Microsoft aggregator returned HTTP 500 with the known error string |
| `HttpException` | Other non-success HTTP status codes |

## AggregatorException in update()

`FamilySafety.update()` catches `AggregatorException` internally, logs a warning,
and skips that refresh cycle. Cached account data from the previous successful
update remains available.

For other operations (setting limits, overrides, etc.), `AggregatorException`
propagates to the caller.

## Example

```python
from pyfamilysafety.exceptions import Unauthorized, RequestDenied, AggregatorException

try:
    await family_safety.update()
except Unauthorized:
    # Re-authenticate or refresh stored token
    ...
except RequestDenied as exc:
    print("Access denied:", exc)
except AggregatorException:
    print("Microsoft aggregator error — retry later")
```

## ValueError

Several methods raise `ValueError` for invalid input (missing OAuth code, unknown
endpoint key, missing `valid_until` for block-until overrides, etc.). These are
client-side validation errors, not HTTP failures.

## API reference

See [Exceptions](../reference/exceptions.md).
