# Screen time

Screen time data comes from two API reports: **device** usage (per hardware) and
**application** usage (per app).

## Today's usage (default)

`Account.update()` loads today's device and app reports automatically:

```python
await family_safety.update()
account = family_safety.accounts[0]

print(account.today_screentime_usage)       # total ms, all devices
print(account.average_screentime_usage)     # daily average
print(account.screentime_usage)             # raw device report dict
print(account.application_usage)            # raw app report dict
```

Device-level totals are on each `Device.today_time_used`. Application usage is
available through `account.applications` and each `Application.usage` (minutes).

## Custom time ranges

```python
from datetime import datetime, date, time
from pyfamilysafety.helpers import localise_datetime, API_TIMEZONE

start = localise_datetime(datetime.combine(date.today(), time(0, 0), tzinfo=API_TIMEZONE))
end = localise_datetime(datetime.combine(date.today(), time(23, 59, 59), tzinfo=API_TIMEZONE))

result = await account.get_screentime_usage(
    start_time=start,
    end_time=end,
    device_count=4,
    platform="ALL",
)
```

When `start_time` and `end_time` are omitted, the method defaults to today and
updates cached account fields.

When you pass explicit times, the return value is:

```python
{
    "devices": {...},      # device screen time JSON
    "applications": {...}  # app activity JSON
}
```

## Platform filter

Pass `platform` to filter by platform identifier (e.g. `"ALL"`, `"WINDOWS"`,
`"XBOX"`, `"MOBILE"`) as accepted by the Family Safety API.

## Timezones

Datetime values are localised before being sent to the API. See
[Timezones](../advanced/timezones.md) for details on `localise_datetime` and
`API_TIMEZONE`.

## API reference

See [Account.get_screentime_usage](../reference/account.md).
