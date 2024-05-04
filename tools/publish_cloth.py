import aiohttp
from aiohttp import FormData
import asyncio
import os
import json
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import traceback

from src import cprint, csrf

async def start(self):
    try:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
            choice = cprint.user_input("This will cost you 10 robux for each upload, are you sure you want to continue? (y/N) > ")
            if choice in ['yes', 'y']:
                while True:
                    group_id = cprint.user_input("Enter the group id you want to upload the clothes to > ")
                    try:
                        group_id = int(group_id)
                        break
                    except ValueError:continue

                if await check_owner(session, group_id, self.id):
                    png_files = [file for file in os.listdir('clothes') if file.lower().endswith('.png')]
                    if not png_files:
                        cprint.error("No clothes found in the 'clothes' folder, steal some clothes before uploading.")
                        return


                    for file_name in png_files:
                        xcsrf = csrf.get(self.cookie)
                        session.headers.update({"X-Csrf-Token": xcsrf})

                        file_path = os.path.join('clothes', file_name)
                        cprint.info(f"Uploading \"{file_path}\"...")
                        data = decode(file_path)
                        await publish(session, file_path, data, group_id)
                else:
                    cprint.error("You can't upload clothes to this group.")
    except Exception:
        traceback.print_exc()
                
async def publish(session, image_path, data, group_id):
    form_data = FormData()
    payload = {
        "displayName": data["name"],
        "description": data["description"],
        "assetType": "Shirt" if int(data["assetType"]) == 11 else "Pants",
        "creationContext": {
            "creator": {
                "groupId": int(group_id)
            },
            "expectedPrice": 10
        },
    }
    form_data.add_field('request', json.dumps(payload))
    form_data.add_field('fileContent', open(image_path, 'rb'), filename='cloth.png', content_type='image/png')

    async with session.post("https://apis.roblox.com/assets/user-auth/v1/assets", data=form_data, ssl=False) as response:
        if response.status == 200:
            cdata = await response.json()
            cprint.success(f"Successfully uploaded clothing ({data['name']})")
            status_data = await check_cloth(session, cdata)
            if status_data:
                await release(session, status_data["assetId"])
        else:
            text = await response.text()
            cprint.error(f"Failed to upload cloth: {text}")

async def check_cloth(session, cloth_data):
    for i in range(10):
        async with session.get(f"https://apis.roblox.com/assets/user-auth/v1/operations/{cloth_data.get('operationId')}", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("done"):
                    cprint.success("Clothing approved!")
                    return data
                else:
                    await asyncio.sleep(5)
                    continue
            else:
                cprint.error(response.status)
                await asyncio.sleep(5)
    return False

async def release(session, id):
    async with session.post(f"https://itemconfiguration.roblox.com/v1/assets/{id}/release", json={"priceConfiguration": {"priceInRobux": 5}, "saleStatus": "OnSale", "releaseConfiguration": {"saleAvailabilityLocations": [0,1]}}, ssl=False) as response:
        if response.status == 200:
            cprint.success("Clothing went on sale for 5 robux!")

def decode(file_path):
    with Image.open(file_path) as img: metadata = img.info
    return metadata

async def check_owner(session, group_id, id):
    async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            owner_id = data.get("owner").get("userId")
            if owner_id == id:
                return True
            else:
                return False
        else:
            cprint.error(f"Failed to check group ownership: {response.status}")
            return None