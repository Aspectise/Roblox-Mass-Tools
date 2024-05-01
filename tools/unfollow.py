import aiohttp
import asyncio
import traceback
from src import csrf, cprint

async def start(self):
    try:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
            following_count = await get_following_count(session, self.id)
            self.display_theme(1)
            cprint.info(f"You are currently following {following_count} users")
            followings = await get_followings(session, self.id)

            xcsrf = csrf.get(self.cookie)
            session.headers.update({"X-Csrf-Token": xcsrf})

            tasks = [asyncio.create_task(unfollow(session, following["id"], following["name"])) for following in followings]
            await asyncio.gather(*tasks)
    except Exception as e:
        traceback.print_exc()

async def get_following_count(session, user_id):
    async with session.get(f"https://friends.roblox.com/v1/users/{user_id}/followings/count", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            count = data.get("count")
            return count

async def get_followings(session, user_id):
    async with session.get(f"https://friends.roblox.com/v1/users/{user_id}/followings?sortOrder=Desc&limit=100", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            followings = data.get("data")
            return followings

async def unfollow(session, user_id, username):
    async with session.post(f"https://friends.roblox.com/v1/users/{user_id}/unfollow", json={"targetUserId": user_id}, ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"{username} (ID: {user_id})", "UNFOLLOWED", (0, 255, 0))