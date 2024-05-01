import aiohttp
import asyncio
from src import csrf, cprint

async def start(self):
    try:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
            friends = await get_friends(session, self.id)
            self.display_theme(1)
            if friends is not None and len(friends) >= 1:
                cprint.info(f"Gathered {len(friends)} friends")
                choice = cprint.user_input(f"Do you want to Fast Unfriend? (y/N) > ")
                
                whitelisted_ids = []
                if choice in ["yes", "y"]:
                    choice_wl = cprint.user_input(f"Do you want to add a whitelist? (y/N) > ")

                    if choice_wl in ["yes", "y"]:
                        whitelist_input = cprint.user_input(f"Enter user ids you don't want to unfriend separated by a comma (id, id..) > ")
                        whitelisted_ids = [id.strip() for id in whitelist_input.split(',')]

                    xcsrf = csrf.get(self.cookie)
                    session.headers.update({"X-Csrf-Token": xcsrf})

                    tasks = [asyncio.create_task(fast_unfriend(session, friend, whitelisted_ids)) for friend in friends]
                    await asyncio.gather(*tasks)

                if choice in ["no", "n"]:
                    for friend in friends:
                        friend_name = friend['name']
                        friend_id = friend['id']

                        choice = cprint.user_input(f"Do you want to unfriend: {friend_name} (ID: {friend_id})? (y/N): ")
                        if choice in ["yes", "y"]:
                            await unfriend(session, friend, self.cookie)
                            continue

            if friends == []:
                cprint.info(f"No friends found")

    except Exception as e:
        cprint.error(e)


async def get_friends(session, id):
    async with session.get(f"https://friends.roblox.com/v1/users/{id}/friends", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            friends = data.get("data")
            return friends
        else:
            cprint.error("Failed to fetch friends")
            return None

async def fast_unfriend(session, friend, whitelisted):
    friend_name = friend['name']
    friend_id = friend['id']

    if str(friend_id) in whitelisted:
        cprint.info("Skipping whitelisted friend")
        return
    
    async with session.post(f"https://friends.roblox.com/v1/users/{friend_id}/unfriend", ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"{friend_name} (ID: {friend_id})", "UNFRIEND", (0, 255, 0))
        else:
            cprint.error(f"Failed to unfriend: {friend_name} (ID: {friend_id}) {response.status}")

async def unfriend(session, friend, cookie):
    xcsrf = csrf.get(cookie)
    friend_name = friend['name']
    friend_id = friend['id']

    async with session.post(f"https://friends.roblox.com/v1/users/{friend_id}/unfriend", headers={"x-csrf-token": xcsrf}, ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"{friend_name} (ID: {friend_id})", "UNFRIEND", (0, 255, 0))
        else:
            cprint.error(f"Failed to unfriend: {friend_name} (ID: {friend_id}) {response.status}")