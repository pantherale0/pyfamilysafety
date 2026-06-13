# FAQ

## Can this access other services in my Microsoft account?

No. The OAuth scope is limited to the Family Safety mobile service
(`service::familymobile.microsoft.com::MBI_SSL`). Tokens generated through the
documented login URL can only call Family Safety APIs — not OneDrive, Outlook,
Xbox Live outside Family Safety, or other Microsoft APIs.

## Do I need to store my Microsoft password?

No. Authentication uses the standard OAuth authorization-code flow. You sign in
in a browser once (or provide a refresh token). The library never sees your
password.

## Why does login redirect to a blank page?

That is expected. After sign-in, Microsoft redirects to
`login.live.com/oauth20_desktop.srf` with a `code` in the query string. Copy the
full URL from the address bar.

## Why is my access token expiring?

Access tokens are short-lived. The library refreshes them automatically using
the refresh token. Ensure you persist `auth.refresh_token` for unattended use.

## What is the experimental flag on FamilySafety?

Setting `family_safety.experimental = True` before `update()` enables polling of
pending screen-time extension requests. See [Pending requests](guide/pending-requests.md).

## Why does update() sometimes log a warning about AggregatorException?

Microsoft's aggregator occasionally returns HTTP 500 with a known error message.
`FamilySafety.update()` catches `AggregatorException` and skips that refresh
cycle rather than failing entirely.

## Where does this library come from?

The API surface was reverse-engineered from the official Family Safety Android
app. See the project README for attribution and tools used during discovery.

## Is there a Home Assistant integration?

Yes — [ha-familysafety](https://github.com/pantherale0/ha-familysafety) builds
on this library.
