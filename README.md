# Microsoft Family Safety Python Module
A Microsoft Family Safety implementation written in Python

## Getting started

**Looking for the Home Assistant integration?** [Navigate here](https://github.com/pantherale0/ha-familysafety)

Full API docs to follow at a later date as part of #1

### Log in

This module won't handle authentication via OAuth and instead you'll need to navigate to the following URL:

https://login.live.com/oauth20_authorize.srf?cobrandid=b5d15d4b-695a-4cd5-93c6-13f551b310df&client_id=dce5010f-c52d-4353-ae86-d666373528d8&response_type=code&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf&response_mode=query&scope=service%3A%3Afamilymobile.microsoft.com%3A%3AMBI_SSL&lw=1&fl=easi2&login_hint=

After login this should redirect you to a blank page, you'll need to copy the whole URL of this page which will be used to initiate a session.

## Privacy questions

1) Can this access other services within my Microsoft account? No, using the above link has its scope restricted to purely the Family Safety app which will only allow applications using generated tokens to use Family Safety API and no other APIs (such as OneDrive / Outlook).

## Sources / tools used

- https://www.reddit.com/r/learnpython/comments/4d4wpf/microsoft_web_login_with_requests/
- Microsoft Family Safety Android
- mitmproxy
