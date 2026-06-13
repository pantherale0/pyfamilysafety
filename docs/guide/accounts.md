# Accounts

Each `Account` represents one family member with Digital Safety enabled. Accounts
are created automatically when you first call `FamilySafety.update()`.

## Profile attributes

After `update()`, common attributes include:

| Attribute | Description |
| --- | --- |
| `user_id` | Microsoft member ID |
| `role` | Family role from the roster |
| `first_name`, `surname` | Display name |
| `profile_picture` | Profile image URL |
| `devices` | List of `Device` objects |
| `applications` | List of `Application` objects |
| `today_screentime_usage` | Total device screen time today (ms) |
| `average_screentime_usage` | Daily average from the API |
| `blocked_platforms` | Platforms currently blocked via override |
| `account_balance`, `account_currency` | Microsoft Store allowance |

## Refreshing an account

`FamilySafety.update()` calls `account.update()` for every member. You can also
refresh a single account:

```python
await account.update()
```

This fetches devices, device and app screen time (today), override/block state,
and spending balance in parallel.

## Screen time queries

For custom date ranges, use `get_screentime_usage`:

```python
from datetime import datetime, time, date
from pyfamilysafety.helpers import API_TIMEZONE

start = datetime.combine(date.today(), time(0, 0), tzinfo=API_TIMEZONE)
end = datetime.combine(date.today(), time(23, 59, 59), tzinfo=API_TIMEZONE)

usage = await account.get_screentime_usage(start_time=start, end_time=end)
```

When called with default times (today), results are stored on the account and
applications are parsed automatically.

## Lookups

```python
device = account.get_device(device_id="...")
app = account.get_application(application_id="...")
```

## Callbacks

Register handlers that run after each `account.update()`:

```python
def on_account_updated():
    print(account.today_screentime_usage)

account.add_account_callback(on_account_updated)
account.remove_account_callback(on_account_updated)
```

Async callbacks are supported.

## Related guides

- [Devices](devices.md)
- [Screen time](screen-time.md)
- [Device limits](device-limits.md)
- [Device overrides](device-overrides.md)
- [Web filtering](web-filtering.md)
- [Spending](spending.md)

## API reference

See [Account](../reference/account.md).
