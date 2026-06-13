# Device overrides

Use `Account.override_device` to temporarily block or unblock a **platform**
(Desktop, Xbox, or Mobile) for a family member — distinct from scheduled device
limits.

## Block until a time

```python
from datetime import datetime, timedelta
from pyfamilysafety.enum import OverrideTarget, OverrideType

until = datetime.now() + timedelta(hours=2)

await account.override_device(
    target=OverrideTarget.DESKTOP,
    override=OverrideType.UNTIL,
    valid_until=until,
    culture="en-GB",
)
```

`OverrideType.UNTIL` requires `valid_until`.

## Cancel (unblock)

```python
await account.override_device(
    target=OverrideTarget.DESKTOP,
    override=OverrideType.CANCEL,
)
```

`OverrideType.CANCEL` lifts the override immediately (`valid_until` is set to now).

## Enum reference

| Enum | API value | Meaning |
| --- | --- | --- |
| `OverrideType.UNTIL` | BlockUntil | Block platform until `valid_until` |
| `OverrideType.CANCEL` | Cancel | Remove active block |
| `OverrideTarget.DESKTOP` | Desktop | Windows devices |
| `OverrideTarget.XBOX` | Xbox | Xbox consoles |
| `OverrideTarget.MOBILE` | Mobile | Mobile devices |

## Blocked state after override

After a successful override, the account refreshes block state from the API:

- `account.blocked_platforms` lists platforms with active overrides.
- Each affected `Device.blocked` is updated for devices on that platform.

## Culture parameter

`culture` defaults to `"en-GB"` and is sent to the API for localized responses.

## API reference

See [Account.override_device](../reference/account.md) and
[Enums](../reference/enums.md).
