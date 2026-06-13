# Devices

`Device` objects represent hardware registered to a family member. They are
populated when `Account.update()` runs.

## Attributes

| Attribute | Description |
| --- | --- |
| `device_id` | Unique device identifier (without `g:` prefix) |
| `device_name` | Friendly name |
| `device_class`, `device_make`, `device_model` | Hardware metadata |
| `form_factor` | Device form factor from the API |
| `os_name` | Operating system |
| `today_time_used` | Screen time today for this device (ms) |
| `last_seen` | Last activity timestamp |
| `blocked` | Whether the device is blocked via a platform override |
| `issues`, `states` | Raw status fields from the API |

## Accessing devices

```python
await family_safety.update()
account = family_safety.accounts[0]

for device in account.devices:
    print(device.device_name, device.today_time_used)

single = account.get_device(device_id="...")
```

## Blocked state

`Device.blocked` reflects platform-level overrides, not per-device limit schedules.
When you block Desktop, Xbox, or Mobile via `Account.override_device`, affected
devices on that platform are marked blocked.

Check `account.blocked_platforms` for which platforms are currently locked.

## Screen time per device

`today_time_used` is filled from the device screen-time aggregate report during
`Account.update()`. For historical or custom ranges, use
[Screen time](screen-time.md).

## API reference

See [Device](../reference/device.md).
