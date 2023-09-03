# pylint: disable=line-too-long
"""Authenticator constants"""

CLIENT_ID = "dce5010f-c52d-4353-ae86-d666373528d8"
SCOPE = "service::familymobile.microsoft.com::MBI_SSL"

BASE_URL = "https://login.live.com/"
TOKEN_ENDPOINT = BASE_URL + "oauth20_token.srf"
REDIRECT_URL = "https://login.live.com/oauth20_desktop.srf"
# we use a fake user_agent here from a real device as a preventative measure in case of captchas or bot protection.
USER_AGENT = "Mozilla/5.0 (Linux; Android 13; Pixel 4 XL Build/TQ3A.230705.001.B4; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.166 Mobile Safari/537.36"

REDIR_REGEXP = r"https://login.live.com/oauth20_desktop.srf\?code=(.*?)&lc=([0-9]{3,5})"
