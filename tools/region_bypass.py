import requests
from rgbprint import Color
from src import cprint

    
def start(self, verify=None):
    xcsrf_token = get_csrf_token(self.cookie)
    rbx_authentication_ticket = get_rbx_authentication_ticket(self.cookie, xcsrf_token)
    cookie = get_set_cookie(rbx_authentication_ticket)
    if verify is None:
        self.display_theme(1)
        print(f"{Color(255, 255, 255)}[{Color(0xC8BFFF)}BYPASSED COOKIE{Color(255, 255, 255)}]:\n{Color(255, 255, 255)} {cookie}")
    else:
        return cookie
    
def get_set_cookie(rbx_authentication_ticket):
    response = requests.post("https://auth.roblox.com/v1/authentication-ticket/redeem", headers={"rbxauthenticationnegotiation":"1"}, json={"authenticationTicket": rbx_authentication_ticket})
    set_cookie_header = response.headers.get("set-cookie")
    if not set_cookie_header:
        cprint.error(f"An error occurred while getting the set_cookie")
        return None
    return set_cookie_header.split(".ROBLOSECURITY=")[1].split(";")[0]
    
def get_rbx_authentication_ticket(cookie, xcsrf_token):
    response = requests.post("https://auth.roblox.com/v1/authentication-ticket", headers={"rbxauthenticationnegotiation":"1", "referer": "https://www.roblox.com/camel", 'Content-Type': 'application/json', "x-csrf-token": xcsrf_token}, cookies={".ROBLOSECURITY": cookie})
    if not response.headers.get("rbx-authentication-ticket"):
        cprint.error(f"An error occurred while getting the rbx-authentication-ticket")
        return None
    return response.headers.get("rbx-authentication-ticket")
    
    
def get_csrf_token(cookie) -> str:
    response = requests.post("https://auth.roblox.com/v2/logout", cookies={".ROBLOSECURITY": cookie})
    xcsrf_token = response.headers.get("x-csrf-token")
    if not xcsrf_token:
        cprint.error(f"An error occurred while getting the X-CSRF-TOKEN. Could be due to an invalid Roblox Cookie")
        return None
    return xcsrf_token
