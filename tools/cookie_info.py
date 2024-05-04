import aiohttp
import asyncio
from src import cprint
from rgbprint import Color, rgbprint
import shutil
import traceback

async def start(self):
    try:
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
                        asyncio.create_task(get_lastlocation(session, user_id)),
                        asyncio.create_task(get_followers(session, user_id)),
                        asyncio.create_task(get_friends(session, user_id)),
                        asyncio.create_task(get_pending(session, user_id)),
                        asyncio.create_task(get_games(session, user_id))
                    ]
                    results = await asyncio.gather(*tasks)
                    birthday, gender, info, robux, emailver, agever, country, pinstatus, lastlocation, followers, friends, pending, games = results

                    created = info.get("created")
                    user_name = data.get("name")
                    display_name = data.get("displayName")

                    self.display_theme(1)


                    INFO: dict[str, str] = {
                "USER ID": user_id,
                "USERNAME": user_name,
                "DISPLAY NAME": display_name,
                "ROBUX": robux,
                "EMAIL VERIFIED": emailver,
                "AGE VERIFIED": agever,
                "COUNTRY": country,
                "BIRTHDAY": birthday,
                "PIN STATUS": 'Enabled' if pinstatus else 'Disabled',
                "GENDER": gender,
                "LAST LOCATION": lastlocation,
                "CREATED": created,
                "FOLLOWERS": followers,
                "FRIENDS": friends,
                "GAMES": games,
                "PENDING ROBUX": pending,
                "SOON": "SOON",
                "SOON1": "SOON",
                "SOON2": "SOON",
                "SOON3": "SOON"
                }

                    OPTIONS_SPACING: str = f"{str().ljust(30)}"

                    def _get_shell_size() -> int:
                        return shutil.get_terminal_size().columns

                    def _print_centered(text: str, *, color: Color = None, end: str = "\n") -> None:
                        for line in text.splitlines():
                            rgbprint(line.center(_get_shell_size()), color=color, end=end)

                    def batched(iterable, n):
                        import itertools
                        it = iter(iterable)
                        while batch := tuple(itertools.islice(it, n)):
                            yield batch

                    previous_batch = None
                    for batch in batched(map(lambda x: f"[{x[0]}] -> {x[1]}", INFO.items()), 10):
                        if previous_batch is None:
                            previous_batch = batch
                            continue
                        
                        max_previous_page = max(len(x) for x in previous_batch)
                        max_page = max(len(x) for x in batch)
                        for i, previous_element in enumerate(previous_batch):
                            _print_centered(f"{previous_element:{max_previous_page}}{OPTIONS_SPACING}{batch[i]:{max_page}}", color=Color(255, 255, 255))
                else:
                    cprint.error(f"Cookie is invalid.")
    except Exception:
        traceback.print_exc()

async def get_birthday(session):
    async with session.get("https://users.roblox.com/v1/birthdate", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return f'{data.get("birthMonth")}/{data.get("birthDay")}/{data.get("birthYear")}'
        else:
            cprint.error(f"Cookie is invalid.")

async def get_gender(session):
    async with session.get("https://users.roblox.com/v1/gender", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            gender = data.get("gender")
            if gender == 1: return "Gay"
            elif gender == 2: return "Male"
            elif gender == 3: return "Female"
            else: return None
        else:
            cprint.error(f"Cookie is invalid.")

async def get_info(session, id):
    async with session.get(f"https://users.roblox.com/v1/users/{id}", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            cprint.error(f"Cookie is invalid.")

async def get_robux(session, id):
    async with session.get(f"https://economy.roblox.com/v1/users/{id}/currency", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("robux")
        else:
            cprint.error(f"Cookie is invalid.")
            
async def get_emailver(session):
    async with session.get(f"https://accountsettings.roblox.com/v1/email", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("verified")
        else:
            cprint.error(f"Cookie is invalid.")

async def get_agever(session):
    async with session.get(f"https://apis.roblox.com/age-verification-service/v1/age-verification/verified-age", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("isVerified")
        else:
            cprint.error(f"Cookie is invalid.")

async def get_country(session):
    async with session.get(f"https://accountsettings.roblox.com/v1/account/settings/account-country", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("value").get("countryName")
        else:
            cprint.error(f"Cookie is invalid.")

async def get_pinstatus(session):
    async with session.get(f"https://auth.roblox.com/v1/account/pin", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("isEnabled")
        else:
            cprint.error(f"Cookie is invalid.")

async def get_lastlocation(session, id):
    async with session.post(f"https://presence.roblox.com/v1/presence/users", json={"userIds":[id]}, ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("userPresences")[0].get("lastLocation")
        else:
            cprint.error(f"Cookie is invalid.")

async def get_followers(session, id):
    async with session.get(f"https://friends.roblox.com/v1/users/{id}/followers/count", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            count = data.get("count")
            return count
        else:
            cprint.error(f"Cookie is invalid.")

async def get_friends(session, id):
    async with session.get(f"https://friends.roblox.com/v1/users/{id}/friends/count", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            count = data.get("count")
            return count
        else:
            cprint.error(f"Cookie is invalid.")

async def get_pending(session, id):
    async with session.get(f"https://economy.roblox.com/v2/users/{id}/transaction-totals?timeFrame=Year&transactionType=summary", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            pending = data.get("pendingRobuxTotal")
            return pending
        else:
            cprint.error(f"Cookie is invalid.")

async def get_games(session, id):
    cursor = ''
    total_games = []
    while True:
        async with session.get(f"https://games.roblox.com/v2/users/{id}/games?limit=50&sortOrder=Asc&cursor={cursor}", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                games = data.get("data")
                for game in games:
                    total_games.append(game)
                
                if data.get("nextPageCursor"):
                    cursor = data.get("nextPageCursor")
                else:
                    return len(total_games)
            else:
                cprint.error("Failed to fetch games")
                return None