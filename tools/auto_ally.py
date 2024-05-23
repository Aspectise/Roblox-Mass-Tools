import aiohttp
import asyncio

from src import cprint, csrf

async def start(self):
    async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
        group_id = int(cprint.user_input("Enter your group id > "))
        group_keyword = cprint.user_input("Enter a keyword that will be used to search for groups > ")
        groups = await get_groups(session, group_keyword)
        if groups:
            for group in groups:
                xcsrf = csrf.get(self.cookie)
                session.headers.update({"X-Csrf-Token": xcsrf})
                await send_ally(session, group_id, group['id'], group['name'])

async def get_groups(session, keyword):
    all_groups = []
    cursor = ''
    for _ in range(3):
        async with session.get(f"https://groups.roblox.com/v1/groups/search?keyword={keyword}&limit=100&cursor={cursor}", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                group_data = data.get("data")
                for group in group_data:
                    entry = {"name": group.get("name"),"id": group.get("id")}
                    all_groups.append(entry)
                
                if data.get("nextPageCursor"):
                    cursor = data.get("nextPageCursor")
                else:
                    return all_groups
            else:
                text = await response.text()
                cprint.error(f"Failed to gather groups: {text}")
                return None
    return all_groups

async def send_ally(session, main_id, group_id, group_name):
    async with session.post(f"https://groups.roblox.com/v1/groups/{main_id}/relationships/allies/{group_id}", ssl=False) as response:
        if response.status == 200:
            cprint.success(f"Sent ally request to {group_name} ({group_id})")
        elif response.status == 429:
            cprint.error("Rate limit, waiting 1 minute...")
            await asyncio.sleep(60)
        else:
            text = await response.text()
            cprint.error(f"Failed to send ally request: {text}")


