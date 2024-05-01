import aiohttp
import asyncio
from rgbprint import gradient_print, Color, rgbprint
import re

async def start(self):
    async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
        async with session.get("https://users.roblox.com/v1/users/authenticated", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                user_id = data.get("id")
                tasks = [
                    asyncio.create_task(get_birthday(session)),
                    asyncio.create_task(get_gender(session)),
                    asyncio.create_task(get_info(session, user_id)),
                    asyncio.create_task(get_robux(session, user_id)),
                    asyncio.create_task(get_emailver(session)),
                    asyncio.create_task(get_agever(session)),
                    asyncio.create_task(get_country(session)),
                    asyncio.create_task(get_pinstatus(session)),
                    asyncio.create_task(get_lastlocation(session, user_id))
                ]
                results = await asyncio.gather(*tasks)
                birthday, gender, info, robux, emailver, agever, country, pinstatus, lastlocation = results

                created = info.get("created")
                user_name = data.get("name")
                display_name = data.get("displayName")

                self.display_theme(1)

                user_info = f"""
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}USER ID{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {str(user_id)}
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}USERNAME{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {str(user_name)} 
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}DISPLAY NAME{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {str(display_name)}
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}ROBUX{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {robux}
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}EMAIL VERIFIED{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {emailver}
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}AGE VERIFIED{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {agever}
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}COUNTRY{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {country}
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}BIRTHDAY{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {str(birthday)}
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}PIN STATUS{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {'Enabled' if pinstatus else 'Disabled'}
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}GENDER{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {str(gender)} 
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}LAST LOCATION{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {lastlocation}
                {Color(255, 255, 255)}[{Color(0xC8BFFF)}CREATED{Color(255, 255, 255)}] {Color(0xC8BFFF)}->{Color(255, 255, 255)} {str(created)}
                """

                for line in user_info.splitlines():
                    print(line)
            else:
                print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")

async def get_birthday(session):
    async with session.get("https://users.roblox.com/v1/birthdate", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return f'{data.get("birthMonth")}/{data.get("birthDay")}/{data.get("birthYear")}'
        else:
            print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")

async def get_gender(session):
    async with session.get("https://users.roblox.com/v1/gender", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            gender = data.get("gender")
            if gender == 1: return "N/A"
            elif gender == 2: return "Male"
            elif gender == 3: return "Female"
            else: return None
        else:
            print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")

async def get_info(session, id):
    async with session.get(f"https://users.roblox.com/v1/users/{id}", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")

async def get_robux(session, id):
    async with session.get(f"https://economy.roblox.com/v1/users/{id}/currency", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("robux")
        else:
            print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")
            
async def get_emailver(session):
    async with session.get(f"https://accountsettings.roblox.com/v1/email", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("verified")
        else:
            print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")

async def get_agever(session):
    async with session.get(f"https://apis.roblox.com/age-verification-service/v1/age-verification/verified-age", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("isVerified")
        else:
            print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")

async def get_country(session):
    async with session.get(f"https://accountsettings.roblox.com/v1/account/settings/account-country", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("value").get("countryName")
        else:
            print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")

async def get_pinstatus(session):
    async with session.get(f"https://auth.roblox.com/v1/account/pin", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("isEnabled")
        else:
            print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")

async def get_lastlocation(session, id):
    async with session.post(f"https://presence.roblox.com/v1/presence/users", json={"userIds":[id]}, ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("userPresences")[0].get("lastLocation")
        else:
            print(f"{Color(255, 0, 0)}ERROR{Color(255, 255, 255)} | Cookie is invalid.")
