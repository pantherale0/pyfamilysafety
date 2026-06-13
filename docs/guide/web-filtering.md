# Web filtering

Manage website restrictions and exceptions for a family member through the web
restrictions API.

## Read current restrictions

```python
restrictions = await account.get_web_restrictions()
```

Returns the raw JSON from `GET /v1/WebRestrictions/{USER_ID}`.

## Add an exception

Allow or block a specific site:

```python
await account.add_web_exception(
    website="example.com",
    allowed=True,
    source="",
)
```

`allowed=True` adds an allow exception; `allowed=False` blocks the site regardless
of the default filter level.

## Custom patch operations

For bulk changes, pass JSON Patch operations directly:

```python
await account.update_web_restrictions([
    {
        "op": "Add",
        "path": "/exceptions",
        "source": "",
        "value": {
            "website": "education.example.org",
            "allowed": True,
        },
    },
])
```

Operations are sent as `{"operations": [...]}` in the PATCH body.

## API reference

See [Account](../reference/account.md) — `get_web_restrictions`,
`update_web_restrictions`, and `add_web_exception`.
