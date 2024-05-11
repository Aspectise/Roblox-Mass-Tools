import aiohttp
import asyncio
import random
import traceback
import itertools

from src import cprint, csrf

async def start(self, cookies):
    try:
        for user in cookies:
            async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": user['cookie']}) as session:
                self.display_theme(1)
                cprint.info("Avatar randomization in progress...")
                assetids = [8,42,43,46,47,19,53,55,50,52,51,54,48,2,11,12,17,18,41]
                tasks = [asyncio.create_task(get_accessories(session, user['id'], asset)) for asset in assetids]
                result = await asyncio.gather(*tasks)
                items = list(itertools.chain.from_iterable(task for task in result if task))
                cprint.info(f"Gathered {len(items)} accessories for {user['name']}, wearing them...")
                xcsrf = csrf.get(user['cookie'])
                session.headers.update({"X-Csrf-Token": xcsrf})
                await wear(session, items, user['name'])

    except Exception:
        traceback.print_exc()

async def get_accessories(session, id, assetid):
    async with session.get(f"https://www.roblox.com/users/inventory/list-json?assetTypeId={assetid}&cursor=&itemsPerPage=10000000&userId={id}", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            items = data["Data"]["Items"]
            if items:
                item_ids = [item["Item"]["AssetId"] for item in items]

                random_items = random.sample(item_ids, 1)
                return random_items
        else:
            cprint.error(f"Failed to get accessories ({assetid}): {response.status}")
            return None


async def wear(session, ids, username):
    async with session.post("https://avatar.roblox.com/v1/avatar/set-wearing-assets", json={"assetIds": ids}, ssl=False) as response:
        if response.status == 200:
            cprint.success(f"Successfully randomized avatar for {username}!")
        else:
            text = await response.text()
            cprint.error(f"Failed to randomize avatar: {text}")