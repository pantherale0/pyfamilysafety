# Microsoft Family Safety Python Module
A Microsoft Family Safety implementation written in Python

## Getting started

**Looking for the Home Assistant integration?** [Navigate here](https://github.com/pantherale0/ha-familysafety)

Full API docs to follow at a later date as part of #1

### Log in

This module won't handle authentication via OAuth and instead you'll need to navigate to the following URL:

https://login.live.com/oauth20_authorize.srf?cobrandid=b5d15d4b-695a-4cd5-93c6-13f551b310df&client_id=000000000004893A&response_type=code&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf&response_mode=query&scope=service%3A%3Afamilymobile.microsoft.com%3A%3AMBI_SSL&lw=1&fl=easi2&login_hint=

After login this should redirect you to a blank page, you'll need to copy the whole URL of this page which will be used to initiate a session.

### Device limits

Device limits are applied per platform (Desktop, Xbox, or Mobile) on a family member account, not to individual devices. Build a `DeviceLimitsSchedule` and pass it to `Account.set_device_limits`.

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

`DailyRestriction.from_minutes()` converts an allowance from minutes to milliseconds:

```python
DayOfWeek.SUNDAY: DailyRestriction.from_minutes(
    285,
    allotted_intervals=[
        AllottedInterval("07:00:00", "11:00:00"),
        AllottedInterval("12:00:00", "18:30:00"),
    ],
)
```

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

Only the days included in `daily_restrictions` are sent to the API. The request timestamp is added automatically at send time.

## Privacy questions

1) Can this access other services within my Microsoft account? No, using the above link has its scope restricted to purely the Family Safety app which will only allow applications using generated tokens to use Family Safety API and no other APIs (such as OneDrive / Outlook).

## Sources / tools used

- https://www.reddit.com/r/learnpython/comments/4d4wpf/microsoft_web_login_with_requests/
- Microsoft Family Safety Android
- mitmproxy
