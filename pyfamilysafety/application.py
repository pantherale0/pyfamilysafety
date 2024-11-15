"""An application instance."""

from .api import FamilySafetyAPI

def get_platform(app_id: str):
    """Return platform identifier."""
    if app_id.startswith("x:"):
        return "XBOX"
    if app_id.startswith("appx:"):
        return "WINDOWS"
    ### This needs validating
    if app_id.startswith("a:"):
        return "MOBILE"

class Application:
    """Application."""

    def __init__(self, api: FamilySafetyAPI, user_id):
        self.app_id = None
        self.name = None
        self.icon = None
        self._usage = None
        self.policy = None
        self.blocked: bool = None
        self._api: FamilySafetyAPI = api
        self._user_id = user_id

    def update(self, app: 'Application'):
        """Updates the data."""
        self.app_id = app.app_id
        self.name = app.name
        self.icon = app.icon
        self._usage = (app.usage*60)*1000
        self.policy = app.policy
        self.blocked = app.blocked

    async def block_app(self):
        """Blocks this application from running."""
        await self._api.send_request(
            endpoint="set_app_policy",
            body={
                "appId": self.app_id,
                "appTimeEnforcementPolicy": "WeekendAndWeekday",
                "blockState": "BlockedAlways",
                "blocked": False,
                "displayName": self.app_id,
                "enabled": True
            },
            USER_ID=self._user_id,
            APP_ID=self.app_id,
            platform=get_platform(self.app_id)
        )
        self.blocked = True

    async def unblock_app(self):
        """Allows this application to run."""
        await self._api.send_request(
            endpoint="set_app_policy",
            body={
                "appId": self.app_id,
                "appTimeEnforcementPolicy": "WeekendAndWeekday",
                "blockState": "NotBlocked",
                "blocked": False,
                "displayName": self.app_id,
                "enabled": True
            },
            USER_ID=self._user_id,
            APP_ID=self.app_id,
            platform=get_platform(self.app_id)
        )
        self.blocked = False

    @classmethod
    def from_app_activity_report(cls, raw_response: dict, api, user_id) -> list['Application']:
        """Converts the activity report into a list of applications."""
        parsed_apps = []
        if "appActivity" in raw_response.keys():
            apps = raw_response.get("appActivity")
            for app in apps:
                parsed = cls(api, user_id)
                parsed.app_id = app["appId"]
                parsed.name = app["displayName"]
                parsed.icon = app["iconUrl"]
                parsed._usage = app["usage"]
                parsed.policy = app["policy"]
                parsed.blocked = (app["blockState"] == "Blocked") or (
                    app["isLegacyBlocked"]) or (
                        app["blockState"] == "BlockedAlways"
                    )
                parsed_apps.append(parsed)
        else:
            raise ValueError("Missing appActivity in JSON response.")
        return parsed_apps

    @property
    def usage(self) -> float:
        """Returns the usage, adjused in minutes."""
        return (self._usage/1000)/60
