import requests
from rgbprint import Color

def get(cookie) -> str:
    response = requests.post("https://auth.roblox.com/v2/logout", cookies = {".ROBLOSECURITY": cookie})
    xcsrf_token = response.headers.get("x-csrf-token")
    if not xcsrf_token:
        print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | An error occurred while getting the X-CSRF-TOKEN. Could be due to an invalid Roblox Cookie")
        return None
    return xcsrf_token
