# Quick start

This example authenticates, loads the family roster, and prints each member's
screen time for today.

```python
import asyncio
import logging

from pyfamilysafety import Authenticator, FamilySafety

logging.basicConfig(level=logging.INFO)


async def main():
    redirect_url = input("Paste OAuth redirect URL: ")
    auth = await Authenticator.create(token=redirect_url)
    family_safety = FamilySafety(auth)

    await family_safety.update()

    for account in family_safety.accounts:
        name = account.first_name or account.user_id
        usage_ms = account.today_screentime_usage or 0
        usage_min = usage_ms / 1000 / 60
        print(f"{name}: {usage_min:.0f} minutes today")


asyncio.run(main())
```

## What happens

1. `Authenticator.create` exchanges the OAuth code for access and refresh tokens.
2. `FamilySafety(auth)` creates the API client.
3. `await family_safety.update()` fetches the roster (first call) and refreshes
   each account's devices, screen time, overrides, and spending balance.

## Polling for updates

Call `update()` periodically to refresh data:

```python
while True:
    await family_safety.update()
    await asyncio.sleep(60)
```

## Look up a member by ID

```python
account = family_safety.get_account(user_id="...")
```

## Next steps

- [FamilySafety client](../guide/family-safety-client.md) — client lifecycle and options
- [Device limits](../guide/device-limits.md) — set platform screen-time schedules
- [API reference](../reference/index.md) — full class documentation
