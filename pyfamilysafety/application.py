"""An application instance."""

class Application:
    """Application."""

    def __init__(self):
        self.app_id = None
        self.name = None
        self.icon = None
        self._usage = None
        self.policy = None
        self.blocked = None

    @classmethod
    def from_app_activity_report(cls, raw_response: dict) -> list['Application']:
        """Converts the activity report into a list of applications."""
        parsed_apps = []
        if "appActivity" in raw_response.keys():
            apps = raw_response.get("appActivity")
            for app in apps:
                parsed = cls()
                parsed.app_id = app["appId"]
                parsed.name = app["displayName"]
                parsed.icon = app["iconUrl"]
                parsed._usage = app["usage"]
                parsed.policy = app["policy"]
                parsed.blocked = app["blockState"] == "Blocked" or app["isLegacyBlocked"]
                parsed_apps.append(parsed)
        else:
            raise ValueError("Missing appActivity in JSON response.")
        return parsed_apps

    @property
    def usage(self) -> float:
        """Returns the usage, adjused in minutes."""
        return (self._usage/1000)/60
