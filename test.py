"""Test the Py module."""


import logging
import asyncio
from pyfamilysafety import FamilySafety, Authenticator

_LOGGER = logging.getLogger(__name__)

async def main():
    """Running function"""
    login = True
    while login:
        try:
            auth = await Authenticator.create(token=input("Response URL: "))
            _LOGGER.info("Logged in, ready.")
            _LOGGER.debug("Access token is: %s", auth.refresh_token)
            login = False
            family_safety = FamilySafety(auth)
            await family_safety.update()
        except Exception as err:
            _LOGGER.critical(err)

    while True:
        for account in family_safety.accounts:
            _LOGGER.debug("Discovered account %s, label %s", account.user_id, account.first_name)
            _LOGGER.debug(account)
            _LOGGER.debug("Usage today %s", account.today_screentime_usage)

        _LOGGER.debug("ping")
        await asyncio.sleep(15)
        _LOGGER.debug("pong")
        await family_safety.update()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
