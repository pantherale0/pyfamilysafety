# FamilySafety client

`FamilySafety` is the main entry point after authentication. It holds the API
client, the list of family `Account` objects, and optional pending-request handling.

## Construction

```python
from pyfamilysafety import Authenticator, FamilySafety

auth = await Authenticator.create(token=redirect_url)
family_safety = FamilySafety(auth)
```

## Updating data

Call `await family_safety.update()` to refresh state:

- On the **first** call, fetches the family roster and creates `Account` instances
  for members with Digital Safety enabled.
- On every call, runs `account.update()` for each member in parallel.
- If `experimental` is enabled, also fetches pending screen-time requests.

```python
await family_safety.update()
print(len(family_safety.accounts), "members")
```

### Aggregator errors

If Microsoft's aggregator returns a transient 500 error, `update()` logs a warning
and returns without raising. The previous cached data remains available.

## Account lookup

```python
account = family_safety.get_account(user_id="member-id")
```

Raises `IndexError` if no member matches the ID.

## Experimental mode

```python
family_safety.experimental = True
await family_safety.update()
```

When enabled, `update()` loads pending requests and invokes registered callbacks.
See [Pending requests](pending-requests.md).

## Pending requests

When experimental mode is on:

```python
requests = family_safety.pending_requests
await family_safety.approve_pending_request(request_id="...", extension_time=30)
await family_safety.deny_pending_request(request_id="...")
```

- `extension_time` is in **seconds** (converted to milliseconds internally).
- Only `DeviceScreenTime` request types are exposed.

## Callbacks

Register sync or async callables to run after pending requests are refreshed:

```python
async def on_requests():
    print("Pending requests updated")

family_safety.add_pending_request_callback(on_requests)
family_safety.remove_pending_request_callback(on_requests)
```

## API reference

See [FamilySafety](../reference/family-safety.md).
