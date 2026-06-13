# Endpoint map

Raw endpoints are defined in `pyfamilysafety.const.ENDPOINTS`. `FamilySafetyAPI.send_request`
accepts an endpoint **key** and URL format kwargs.

Base URL: `https://mobileaggregator.family.microsoft.com/api`

| Endpoint key | Method | High-level wrapper |
| --- | --- | --- |
| `get_accounts` | GET | `FamilySafety.update()` |
| `get_pending_requests` | GET | `FamilySafety._get_pending_requests()` (experimental) |
| `approve_pending_request` | POST | `FamilySafety.approve_pending_request()` |
| `deny_pending_request` | POST | `FamilySafety.deny_pending_request()` |
| `get_premium_entitlement` | GET | `FamilySafetyAPI.async_get_premium_entitlement()` |
| `get_user_device_screentime_usage` | GET | `Account.get_screentime_usage()` / `update()` |
| `get_user_app_screentime_usage` | GET | `Account.get_screentime_usage()` / `update()` |
| `update_schedule` | PATCH | `Account.set_device_limits()` |
| `get_user_devices` | GET | `Account.update()` |
| `get_user_spending` | GET | `Account.update()` |
| `get_user_payment_methods` | GET | `FamilySafetyAPI.async_get_user_payment_methods()` |
| `get_user_content_restrictions` | GET | `FamilySafetyAPI.async_get_user_content_restrictions()` |
| `get_user_web_restrictions` | GET | `Account.get_web_restrictions()` |
| `update_web_restrictions` | PATCH | `Account.update_web_restrictions()` |
| `get_user_web_activity` | GET | **No wrapper** |
| `get_user_search_activity` | GET | **No wrapper** |
| `get_override_device_restrictions` | GET | `Account.update()` |
| `override_device_restriction` | POST | `Account.override_device()` |
| `set_app_policy` | PATCH | `Application.block_app()` / `unblock_app()` |
| `update_content_restrictions` | PATCH | **No wrapper** |
| `get_additional_permission_token` | GET | **No wrapper** |

## Using an unwrapped endpoint

```python
response = await account._api.send_request(
    "get_user_web_activity",
    USER_ID=account.user_id,
    BEGIN_TIME=begin_time,
    END_TIME=end_time,
    ALLOW_STATUS="All",
)
```

Refer to Microsoft's mobile API shapes when constructing bodies for endpoints
without high-level wrappers. Contributions adding `Account` methods for missing
endpoints are welcome.

## API reference

See [FamilySafetyAPI](../reference/api-internals.md).
