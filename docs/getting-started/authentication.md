# Authentication

**pyfamilysafety** does not embed a browser login flow. You sign in through Microsoft
in a browser, then pass the resulting redirect URL (or a saved refresh token) to
`Authenticator.create`.

## OAuth login (first time)

1. Open this URL in a browser (while signed in to the Microsoft account that manages
   your family):

   [Microsoft Family Safety OAuth login](https://login.live.com/oauth20_authorize.srf?cobrandid=b5d15d4b-695a-4cd5-93c6-13f551b310df&client_id=000000000004893A&response_type=code&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf&response_mode=query&scope=service%3A%3Afamilymobile.microsoft.com%3A%3AMBI_SSL&lw=1&fl=easi2&login_hint=)

2. Complete Microsoft sign-in. You are redirected to a blank page on
   `login.live.com/oauth20_desktop.srf`.

3. Copy the **entire URL** from the browser address bar. It contains a `code=`
   query parameter.

4. Pass that URL to the authenticator:

```python
import asyncio
from pyfamilysafety import Authenticator

async def main():
    redirect_url = "https://login.live.com/oauth20_desktop.srf?code=..."
    auth = await Authenticator.create(token=redirect_url)
    print("Logged in as", auth.user_id)
    # Save auth.refresh_token for later sessions

asyncio.run(main())
```

## Refresh token sessions

For long-running apps, store `auth.refresh_token` securely and reuse it:

```python
auth = await Authenticator.create(
    token=stored_refresh_token,
    use_refresh_token=True,
)
```

## Automatic token refresh

Access tokens expire after a short period. `FamilySafetyAPI` refreshes the token
automatically before each request when `auth.access_token_expired` is true. You do
not need to call `perform_refresh()` yourself during normal use.

## Session sharing

Pass an existing `aiohttp.ClientSession` if you manage HTTP connections yourself:

```python
import aiohttp
from pyfamilysafety import Authenticator

async with aiohttp.ClientSession() as session:
    auth = await Authenticator.create(token=redirect_url, client_session=session)
```

## Privacy and scope

The OAuth scope is restricted to the Family Safety service
(`service::familymobile.microsoft.com::MBI_SSL`). Tokens grant access to Family
Safety APIs only — not OneDrive, Outlook, or other Microsoft services. See the
[FAQ](../faq.md) for more detail.

Next: [Quick start](quick-start.md)
