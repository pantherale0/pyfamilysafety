# Device limits

Device limits control how much screen time a family member may use on a **platform**
(Desktop, Xbox, or Mobile) — not on an individual device. Build a
`DeviceLimitsSchedule` and pass it to `Account.set_device_limits`.

## Platform vs device

Limits apply per platform type via `OverrideTarget`:

| Enum | API value | Typical devices |
| --- | --- | --- |
| `OverrideTarget.DESKTOP` | Desktop | Windows PCs |
| `OverrideTarget.XBOX` | Xbox | Xbox consoles |
| `OverrideTarget.MOBILE` | Mobile | Phones and tablets |

## Basic example

```python
import asyncio
from datetime import time

from pyfamilysafety import Authenticator, FamilySafety
from pyfamilysafety.enum import DayOfWeek, OverrideTarget
from pyfamilysafety.schedule import (
    AllottedInterval,
    DailyRestriction,
    DeviceLimitsSchedule,
)


async def main():
    auth = await Authenticator.create(token="...")
    family_safety = FamilySafety(auth)
    await family_safety.update()

    account = family_safety.accounts[0]

    schedule = DeviceLimitsSchedule(
        platform=OverrideTarget.XBOX,
        daily_restrictions={
            DayOfWeek.SUNDAY: DailyRestriction(
                allowance=17100000,  # milliseconds (4 h 45 min)
                allotted_intervals=[
                    AllottedInterval.from_time(time(7, 0), time(11, 0)),
                    AllottedInterval.from_time(time(12, 0), time(18, 30)),
                ],
            ),
        },
    )

    await account.set_device_limits(schedule)


asyncio.run(main())
```

## Schedule building blocks

| Class | Purpose |
| --- | --- |
| `AllottedInterval` | Allowed usage window (`begin` / `end` as `HH:MM:SS`) |
| `DailyRestriction` | Allowance and optional intervals for one day |
| `DeviceLimitsSchedule` | Platform, mode, culture, and per-day restrictions |

| Enum | Values |
| --- | --- |
| `DayOfWeek` | `MONDAY` … `SUNDAY` (serialized as lowercase day names) |
| `DeviceLimitsMode` | `PER_DEVICE_TYPE` (default) |
| `OverrideTarget` | `DESKTOP`, `XBOX`, `MOBILE` |

## Allowance units

`DailyRestriction.allowance` is in **milliseconds**. Convert from minutes with
`DailyRestriction.from_minutes()`:

```python
DayOfWeek.SUNDAY: DailyRestriction.from_minutes(
    285,
    allotted_intervals=[
        AllottedInterval("07:00:00", "11:00:00"),
        AllottedInterval("12:00:00", "18:30:00"),
    ],
)
```

Or build intervals from `datetime.time`:

```python
AllottedInterval.from_time(time(7, 0), time(11, 0))
```

## Partial week schedules

Only days included in `daily_restrictions` are sent to the API. Omit days you do
not want to change.

## Request timestamp

`Account.set_device_limits` adds a `time` field automatically using the current
local time before sending the PATCH request. You do not set this on the schedule
object.

## API reference

See [Schedules](../reference/schedule.md) and [Account.set_device_limits](../reference/account.md).
