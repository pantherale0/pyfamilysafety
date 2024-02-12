"""Test the Py module."""


import logging
import asyncio
from pyfamilysafety import FamilySafety

_LOGGER = logging.getLogger(__name__)

async def main():
    """Running function"""
    login = True
    while login:
        try:
            auth = await FamilySafety.create(token=input("Response URL: "), use_refresh_token=True)
            _LOGGER.info("Logged in, ready.")
            _LOGGER.debug("Access token is: %s", auth.api.authenticator.refresh_token)
            login = False
        except Exception as err:
            _LOGGER.critical(err)

    while True:
        for account in auth.accounts:
            _LOGGER.debug("Discovered account %s, label %s", account.user_id, account.first_name)
            _LOGGER.debug(account)
            _LOGGER.debug("Usage today %s", account.today_screentime_usage)

        _LOGGER.debug("ping")
        await asyncio.sleep(15)
        _LOGGER.debug("pong")
        await auth.update()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
