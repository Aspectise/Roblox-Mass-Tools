import aiohttp
import asyncio
import traceback

from src import cprint, csrf

async def start(self, cookies):
    try:
        for user in cookies:
            async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": user['cookie']}) as session:
                self.display_theme(1)
                cprint.info(f"Gathering {user['name']}'s outfits...")
                outfits = await get_outfits(session, user['id'], user['name'])
                if outfits:
                    choice = cprint.user_input(f"Are you sure you want to delete {len(outfits)} outfits? (y/N) > ").lower()
                    if choice in ['y','yes']:
                        xcsrf = csrf.get(user['cookie'])
                        session.headers.update({"X-Csrf-Token": xcsrf})
                        tasks = [asyncio.create_task(delete(session, outfit['id'], outfit['name'])) for outfit in outfits]
                        await asyncio.gather(*tasks)
    except Exception:
        traceback.print_exc()

async def get_outfits(session, user_id, username):
    outfits = []
    async with session.get(f"https://avatar.roblox.com/v2/avatar/users/{user_id}/outfits?isEditable=true&itemsPerPage=100000&outfitType=Avatar", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            data = data.get("data")
            if data:
                for outfit in data:
                    outfit_id = outfit.get("id")
                    outfit_name = outfit.get("name")
                    entry = {"name":outfit_name,"id":outfit_id}
                    outfits.append(entry)
                return outfits
            else:
                cprint.info(f"No outfits found for {username}")
                return None
        else:
            cprint.error(f"Failed to gather outfits: {response.status}")
            return None

async def delete(session, id, name):
    async with session.post(f"https://avatar.roblox.com/v1/outfits/{id}/delete", ssl=False) as response:
        if response.status == 200:
            cprint.success(f"Deleted outfit {name} ({id})!")
        else:
            cprint.error(f"Failed to delete oufit: {response.status}")