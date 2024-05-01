import aiohttp
import asyncio
import os
import traceback
from PIL import Image

from src import cprint

async def start(self):
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                self.display_theme(1)
                group_id = cprint.user_input("Enter the group id > ")
                try:
                    group_id = int(group_id)
                    break
                except ValueError:
                    cprint.error("Enter a valid group id.")
                    continue

            asset_ids = await get_clothes(session, group_id)
            if asset_ids:
                cprint.info(f"Gathered {len(asset_ids)} clothings. Getting there id... (This process might take a while)")

                tasks = [asyncio.create_task(get_asset_id(session, asset)) for asset in asset_ids]
                all_ids = await asyncio.gather(*tasks)
                all_ids = [id for id in all_ids if id is not None]

                cprint.info(f"Gathered {len(all_ids)} ids. Saving them... (This process might take a while)")

                tasks = [asyncio.create_task(save_asset(session, asset)) for asset in all_ids]
                await asyncio.gather(*tasks)
            else:
                cprint.info("Couldn't get clothes.")
    except Exception:
        traceback.print_exc()


async def get_clothes(session, id):
    cursor = ''
    assets = []
    while True:
        async with session.get(f"https://catalog.roblox.com/v1/search/items/details?Category=3&CreatorType=2&IncludeNotForSale=false&Limit=30&CreatorTargetId={id}&cursor={cursor}", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                clothings = data.get("data")
                for asset in clothings:
                    assets.append(asset.get("id"))
                
                if data.get("nextPageCursor"):
                    cursor = data.get("nextPageCursor")
                else:
                    return assets
            else:
                return None

async def get_asset_id(session, clothing_id):
    try:
        async with session.get(f'https://assetdelivery.roblox.com/v1/assetId/{clothing_id}') as response:
            data = await response.json()
            if data.get("IsCopyrightProtected"):
                cprint.info(f"Copyright Protected! ID: {clothing_id}")
                return None
            location = data.get('location')
            if location:
                async with session.get(location) as asset_id_response:
                    asset_id_response.raise_for_status()
                    asset_id_content = await asset_id_response.text()
                    asset_id = asset_id_content.split('<url>http://www.roblox.com/asset/?id=')[1].split('</url>')[0]
                    return asset_id
            else:
                return None
    except aiohttp.ClientError as e:
        cprint.error(f"{e}")
        return None

async def save_asset(session, asset_id):
    try:
        if os.path.exists(f"clothes/{asset_id}.png"):
            cprint.info(f"File {asset_id}.png already exists. Skipping download.")
            return
        
        async with session.get(f'https://assetdelivery.roblox.com/v1/assetId/{asset_id}') as response:
            data = await response.json()
            if data.get("IsCopyrightProtected"):
                cprint.info(f"Copyright Protected! ID: {asset_id}")
                return None
            png_url = data.get('location')
            async with session.get(png_url) as png_response:
                png_response.raise_for_status()
                image = await png_response.read()
                file_path = f'clothes/{asset_id}.png'
                with open(file_path, 'wb') as f:
                    f.write(image)
                process_image(file_path)
                cprint.custom(f"Saved cloth in \"{os.path.abspath(file_path)}\"", "SUCCESS", (0,255,0))
    except aiohttp.ClientError as e:
        cprint.error(f"{e}")
        return None


def process_image(filename):
    img1 = Image.open(filename)
    img2 = Image.open("src/template.png")
    img1.paste(img2, (0,0), mask = img2)
    img1.save(filename)