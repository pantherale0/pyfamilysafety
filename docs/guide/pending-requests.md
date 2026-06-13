# Pending requests

Family members can request extra screen time. **pyfamilysafety** can list, approve,
and deny these requests when experimental mode is enabled.

!!! warning "Experimental"
    Pending request support is experimental. Set `FamilySafety.experimental = True`
    before calling `update()`.

## Enable pending request polling

```python
family_safety.experimental = True
await family_safety.update()

for request in family_safety.pending_requests:
    print(request["id"], request["type"], request.get("platform"))
```

Only requests with `type == "DeviceScreenTime"` are included. Other request types
are filtered out.

## Approve with extension

```python
success = await family_safety.approve_pending_request(
    request_id="...",
    extension_time=30,  # seconds
)
```

`extension_time` is converted to milliseconds internally (`× 100`).

## Deny

```python
success = await family_safety.deny_pending_request(request_id="...")
```

Both methods return `True` when the API responds with HTTP 204 and refresh the
pending request list.

## Look up requests

```python
request = family_safety.get_request(request_id="...")
member_requests = family_safety.get_account_requests(user_id=account.user_id)
```

## Callbacks

Run code whenever pending requests are refreshed:

```python
async def on_pending():
    for req in family_safety.pending_requests:
        print(req)

family_safety.add_pending_request_callback(on_pending)
```

Sync and async callables are supported.

## API reference

See [FamilySafety](../reference/family-safety.md).
