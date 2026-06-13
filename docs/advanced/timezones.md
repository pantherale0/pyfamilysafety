# Timezones

The Family Safety API expects timestamps with timezone offsets. **pyfamilysafety**
uses helpers in `pyfamilysafety.helpers` to convert datetimes before requests.

## Constants

| Name | Value | Usage |
| --- | --- | --- |
| `API_TIMEZONE` | UTC (`dateutil.tz.tzutc()`) | Standardised API timestamps |
| `LOCAL_TIMEZONE` | Local system timezone | Applied when localising user datetimes |

## Functions

### `localise_datetime(dt)`

Adds the local timezone to a naive datetime (or replaces tzinfo). Used when
building query parameters for screen-time requests and device limit timestamps.

### `standardise_datetime(dt)`

Sets tzinfo to UTC. Used when sending `validUntil` for device overrides.

## Screen time queries

Default today's range in `Account.update()` and `get_screentime_usage()`:

```python
from datetime import datetime, date, time
from pyfamilysafety.helpers import localise_datetime, API_TIMEZONE

start = localise_datetime(datetime.combine(date.today(), time(0, 0), tzinfo=API_TIMEZONE))
```

Times are formatted as `YYYY-MM-DDTHH:MM:SS+ZZZZ` and URL-encoded for GET requests.

## Device limits

`Account.set_device_limits` adds a `time` field using:

```python
localise_datetime(datetime.now()).strftime("%Y-%m-%dT%H:%M:%S%z")
```

## Device overrides

`valid_until` is converted with `standardise_datetime` before posting to the API.

## Tip

When constructing custom ranges, prefer aware datetimes with an explicit timezone
to avoid ambiguity on systems where local timezone differs from the family's locale.
