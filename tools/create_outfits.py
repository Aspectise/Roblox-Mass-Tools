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
                while True:
                    outfits_type = cprint.user_input("Random outfits or Current avatar outfits? (random/current) > ").lower()
                    if outfits_type in ['random','current']:
                        break
                if outfits_type == 'random':
                    cprint.info("Getting accessories...")
                    assetids = [8,42,43,46,47,19,53,55,50,52,51,54,48,2,11,12,17,18,41]

                    tasks = [asyncio.create_task(get_accessories(session, user['id'], asset)) for asset in assetids]
                    result = await asyncio.gather(*tasks)
                    items = list(itertools.chain.from_iterable(task for task in result if task))
                else:
                    payload = await get_avatar(session)

                while True:
                    amount = cprint.user_input("How many outfits to create? > ")
                    try:
                        amount = int(amount)
                        break
                    except ValueError:
                        continue

                xcsrf = csrf.get(user['cookie'])
                session.headers.update({"X-Csrf-Token": xcsrf})
                for _ in range(int(amount)):
                    if outfits_type == "random":
                        random_items = random.sample(items, min(10, len(items)))
                        tasks = [asyncio.create_task(create_outfit(session, user['name'], ids=random_items))]
                        await asyncio.gather(*tasks)
                    else:
                        tasks = [asyncio.create_task(create_outfit(session, user['name'], payload_avatar=payload))]
                        await asyncio.gather(*tasks)


    except Exception:
        traceback.print_exc()

async def get_accessories(session, id, assetid):
    async with session.get(f"https://www.roblox.com/users/inventory/list-json?assetTypeId={assetid}&cursor=&itemsPerPage=10000000&userId={id}", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            items = data["Data"]["Items"]
            if items:
                item_ids = [item["Item"]["AssetId"] for item in items]
                return item_ids
        else:
            return None
        
async def get_avatar(session):
    async with session.get(f"https://avatar.roblox.com/v1/avatar", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            assets = data['assets']
            asset_ids = []
            for item in assets:
                asset_ids.append(int(item.get("id")))
            body_colors = data['bodyColors']
            scale = data['scales']
            payload = {
                'name': "CREATED WITH DEATH",
                'assetIds': asset_ids,
                'bodyColors': body_colors,
                'scale': scale
            }
            print(payload)
            return payload
        else:
            cprint.error(f"Failed to get avatar: {response.status}")
            return None


async def create_outfit(session, username, ids=None, payload_avatar=None):
    if not payload_avatar:
        payload = {"name": "CREATED WITH DEATH", "bodyColors": {"headColorId": 18, "torsoColorId": 18, "rightArmColorId": 18, "leftArmColorId": 18, "rightLegColorId": 18, "leftLegColorId": 18}, "assetIds": ids, "scale": {"height": 1, "width": 1, "head": 1, "depth": 1, "proportion": 1, "bodyType": 1}}
    else:
        payload = payload_avatar

    async with session.post("https://avatar.roblox.com/v1/outfits/create", json=payload, ssl=False) as response:
        if response.status == 200:
            cprint.success(f"Created outfit for {username}")
        else:
            cprint.error(f"Failed to create outfit for {username}: {response.status}")