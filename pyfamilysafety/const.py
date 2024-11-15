# pylint: disable=line-too-long
"""pyfamilysafety"""

BASE_URL = "https://mobileaggregator.family.microsoft.com/api"
APP_VERSION = "v 1.26.0.1001"
USER_AGENT = f"Family Safety-prod/({APP_VERSION}) Android/33 google/Pixel 4 XL"

AGGREGATOR_ERROR = "Something went wrong in the Aggregator service"

ENDPOINTS = {
    "get_accounts": {
        "url": "{BASE_URL}/v2/roster",
        "method": "GET"
    },
    "get_pending_requests": {
        "url": "{BASE_URL}/v1/PendingRequests",
        "method": "GET"
    },
    "deny_pending_request": {
        "url": "{BASE_URL}/v1/pendingRequests/deny/{USER_ID}",
        "method": "POST"
    },
    "approve_pending_request": {
        "url": "{BASE_URL}/v1/pendingRequests/approve/{USER_ID}",
        "method": "POST"
    },
    "get_premium_entitlement": {
        "url": "{BASE_URL}/v1/entitlement",
        "method": "GET"
    },
    "get_user_device_screentime_usage": {
        "url": "{BASE_URL}/v4/activityreport/deviceScreenTimeUsage/{USER_ID}?beginTime={BEGIN_TIME}&endTime={END_TIME}&topDeviceCount={DEVICE_COUNT}",
        "method": "GET"
    },
    "update_schedule": {
        "url": "{BASE_URL}/v4/devicelimits/schedules/{USER_ID}",
        "method": "PATCH"
    },
    "get_user_devices": {
        "url": "{BASE_URL}/v1/devices/{USER_ID}",
        "method": "GET"
    },
    "get_user_spending": {
        "url": "{BASE_URL}/v1/Spending/{USER_ID}",
        "method": "GET"
    },
    "get_user_payment_methods": {
        "url": "{BASE_URL}/v1/spending/paymentmethods/{USER_ID}?cid={CID}",
        "method": "GET"
    },
    "get_user_content_restrictions": {
        "url": "{BASE_URL}/v1/ContentRestrictions/{USER_ID}",
        "method": "GET"
    },
    "get_user_web_restrictions": {
        "url": "{BASE_URL}/v1/WebRestrictions/{USER_ID}",
        "method": "GET"
    },
    "get_user_app_screentime_usage": {
        "url": "{BASE_URL}/v4/activityReport/appUsage/{USER_ID}?beginTime={BEGIN_TIME}&endTime={END_TIME}",
        "method": "GET"
    },
    "get_user_web_activity": {
        "url": "{BASE_URL}/v1/activityreport/webactivity/{USER_ID}?beginTime={BEGIN_TIME}&endTime={END_TIME}&allowStatus={ALLOW_STATUS}",
        "method": "GET"
    },
    "get_user_search_activity": {
        "url": "{BASE_URL}/v1/activityreport/searchactivity/{USER_ID}?beginTime={BEGIN_TIME}&endTime={END_TIME}",
        "method": "GET"
    },
    "get_override_device_restrictions": {
        "url": "{BASE_URL}/v1/devicelimits/{USER_ID}/overrides",
        "method": "GET"
    },
    "override_device_restriction": {
        "url": "{BASE_URL}/v1/devicelimits/{USER_ID}/overrides",
        "method": "POST"
    },
    "set_app_policy": {
        "url": "{BASE_URL}/v3/appLimits/policies/{USER_ID}/{APP_ID}",
        "method": "PATCH"
    },
    "update_web_restrictions": {
        "url": "{BASE_URL}/v1/WebRestrictions/{USER_ID}",
        "method": "PATCH"
    },
    "update_content_restrictions": {
        "url": "{BASE_URL}/v1/ContentRestrictions/{USER_ID}",
        "method": "PATCH"
    },
    "get_additional_permission_token": {
        "url": "{BASE_URL}/v1/FamilyPermission/permissiontoken/{USER_ID}?scopes={SCOPES}",
        "method": "GET"
    }
}
