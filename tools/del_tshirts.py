import aiohttp
import asyncio
from src import csrf, cprint

async def start(self, cookies):
    for user in cookies:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": user['cookie']}) as session:
            tshirts = await get_tshirts(session, user['id'])
            self.display_theme(1)
            cprint.info(f"Gathered {len(tshirts)} t-shirts!")
            if tshirts is not None and len(tshirts) >= 1:
                xcsrf = csrf.get(user['cookie'])
                session.headers.update({"X-Csrf-Token": xcsrf})

                tasks = [asyncio.create_task(delete(session, item)) for item in tshirts]
                await asyncio.gather(*tasks)

            if tshirts == []:
                cprint.info("No t-shirts found.")

async def get_tshirts(session, id):
    async with session.get(f"https://www.roblox.com/users/inventory/list-json?assetTypeId=2&cursor=&itemsPerPage=10000000&userId={id}", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("Data").get("Items")
        else:
            cprint.error(f"Failed to gather t-shirts: {response.status}")
            return None
        
async def delete(session, item): 
    item_id = item.get("Item").get("AssetId")
    item_name = item.get("Item").get("Name")
    async with session.post("https://www.roblox.com/asset/delete-from-inventory", data={"assetId": item_id}, ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"{item_name} (ID: {item_id})", "DELETED", (0, 255, 0))
        else:
            cprint.error(f"Failed to delete {item_name}: {response.text}")