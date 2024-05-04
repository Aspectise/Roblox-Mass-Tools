import aiohttp
import asyncio
import os
import traceback
from PIL import Image
from PIL.PngImagePlugin import PngInfo

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

            amount = cprint.user_input("Amount of clothing to scrape > ")
            
            cprint.info("Gathering the group's clothes...")
            asset_ids = await get_clothes(session, group_id, amount)
            if asset_ids:
                cprint.info(f"Gathered {len(asset_ids)} clothings. Getting there id... (This process might take a while)")

                tasks = [asyncio.create_task(get_asset_id(session, asset["id"], asset)) for asset in asset_ids]
                all_ids = await asyncio.gather(*tasks)
                all_ids = [id for id in all_ids if id is not None]

                cprint.info(f"Gathered {len(all_ids)} ids. Saving them... (This process might take a while)")

                tasks = [asyncio.create_task(save_asset(session, asset["assetid"], asset["clothingid"], asset["data"])) for asset in all_ids]
                await asyncio.gather(*tasks)
            else:
                cprint.info("Couldn't get clothes.")
    except Exception:
        traceback.print_exc()


async def get_clothes(session, id, amount):
    cursor = ''
    assets = []
    while True:
        async with session.get(f"https://catalog.roblox.com/v1/search/items/details?Category=3&CreatorType=2&IncludeNotForSale=false&Limit=30&CreatorTargetId={id}&cursor={cursor}", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                clothings = data.get("data")
                for asset in clothings:
                    entry = {
                        "name": asset.get("name"),
                        "description": asset.get("description"),
                        "assetType": asset.get("assetType"),
                        "id": asset.get("id")
                    }
                    assets.append(entry)
                
                if data.get("nextPageCursor") and len(assets) < int(amount):
                    cursor = data.get("nextPageCursor")
                else:
                    return assets
            else:
                await asyncio.sleep(3)

async def get_asset_id(session, clothing_id, clothing_data):
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
                    return {"assetid": asset_id, "clothingid": clothing_id, "data": clothing_data}
            else:
                return None
    except aiohttp.ClientError as e:
        return None

async def save_asset(session, asset_id, clothing_id, clothing_data):
    try:
        if not os.path.exists("clothes"):
            os.makedirs("clothes")

        if os.path.exists(f"clothes/{clothing_id}.png"):
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
                file_path = f'clothes/{clothing_id}.png'
                with open(file_path, 'wb') as f:
                    f.write(image)
                process_image(file_path)
                encode(file_path, clothing_data)
                cprint.success(f"Saved cloth in \"{os.path.abspath(file_path)}\"")
    except aiohttp.ClientError as e:
        cprint.error(f"{e}")
        return None

def encode(orfile, metadata_dict):
    metadata = PngInfo()
    for key, value in metadata_dict.items():
        metadata.add_text(str(key), str(value))
    with Image.open(orfile) as img:
        img.save(orfile, pnginfo=metadata)

def process_image(filepath):
    img1 = Image.open(filepath)
    img2 = Image.open("src/template.png")
    img1.paste(img2, (0,0), mask = img2)
    img1.save(filepath)
