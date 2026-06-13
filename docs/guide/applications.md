# Applications

`Application` objects represent apps reported in a member's app activity. They are
parsed during `Account.update()` from the app screen-time report.

## Listing applications

```python
await family_safety.update()
account = family_safety.accounts[0]

for app in account.applications:
    print(app.name, app.usage, "min", "blocked:", app.blocked)
```

`Application.usage` returns minutes used in the current reporting period.

## Block and unblock

```python
app = account.get_application(application_id="...")

await app.block_app()
await app.unblock_app()
```

Blocking updates app policy via the `set_app_policy` endpoint. The platform header
is inferred from the app ID prefix:

| Prefix | Platform |
| --- | --- |
| `x:` | Xbox |
| `appx:` | Windows |
| `a:` | Mobile |

## Block state

An app is considered blocked when the API reports `blockState` of `Blocked` or
`BlockedAlways`, or when `isLegacyBlocked` is true.

## Requirements

Applications are populated only after screen-time data is loaded. Call
`Account.update()` or `get_screentime_usage()` first. Calling
`_apply_applications` without usage data raises `ValueError`.

## API reference

See [Application](../reference/application.md).
