# pyfamilysafety

An async Python client for the Microsoft Family Safety mobile aggregator API.

Use **pyfamilysafety** to manage family members, read screen time, set device limits,
block platforms or applications, manage web filtering, and handle pending screen-time
extension requests — all from Python.

## Features

- **Family roster** — list members with Digital Safety enabled
- **Screen time** — device and application usage for today or custom ranges
- **Device limits** — per-platform schedules (Desktop, Xbox, Mobile)
- **Device overrides** — block or unblock a platform until a given time
- **Application blocking** — block or unblock individual apps
- **Web filtering** — read restrictions and add allow/block exceptions
- **Spending balance** — read Microsoft Store allowance balance
- **Pending requests** — approve or deny screen-time extension requests (experimental)

## Requirements

- Python 3.8 or later
- [aiohttp](https://docs.aiohttp.org/) and [python-dateutil](https://dateutil.readthedocs.io/)

## Home Assistant integration

Looking for the Home Assistant integration? See
[ha-familysafety](https://github.com/pantherale0/ha-familysafety).

## Next steps

1. [Install](getting-started/installation.md) the package
2. [Authenticate](getting-started/authentication.md) with Microsoft
3. Follow the [quick start](getting-started/quick-start.md) example
