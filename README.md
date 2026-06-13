# Microsoft Family Safety Python Module

An async Python client for the Microsoft Family Safety mobile aggregator API.

## Installation

```bash
pip install pyfamilysafety
```

## Documentation

**Full documentation:** [https://pantherale0.github.io/pyfamilysafety/](https://pantherale0.github.io/pyfamilysafety/)

Covers authentication, user guides, API reference, and advanced topics.

## Home Assistant

Looking for the Home Assistant integration? See [ha-familysafety](https://github.com/pantherale0/ha-familysafety).

## Quick example

```python
import asyncio
from pyfamilysafety import Authenticator, FamilySafety

async def main():
    auth = await Authenticator.create(token="...")  # OAuth redirect URL
    fs = FamilySafety(auth)
    await fs.update()
    for account in fs.accounts:
        print(account.first_name, account.today_screentime_usage)

asyncio.run(main())
```

See the [Authentication guide](https://pantherale0.github.io/pyfamilysafety/getting-started/authentication/) for obtaining the OAuth redirect URL.

## License

MIT — see [LICENSE](LICENSE).

## Sources / tools used

- https://www.reddit.com/r/learnpython/comments/4d4wpf/microsoft_web_login_with_requests/
- Microsoft Family Safety Android
- mitmproxy
