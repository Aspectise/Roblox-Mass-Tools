import aiohttp
from aiohttp import FormData
import asyncio
import os
import json
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import traceback
import re
import uuid

from src import cprint, csrf

async def start(self):
    try:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
            choice = cprint.user_input("This will cost you 10 robux for each upload, are you sure you want to continue? (y/N) > ").lower()
            if choice in ['yes', 'y']:
                while True:
                    group_id = cprint.user_input("Enter the group id you want to upload the clothes to > ")
                    max_robux = cprint.user_input("How much robux to spend before stopping? > ")
                    try:
                        group_id = int(group_id)
                        max_robux = int(max_robux)
                        break
                    except ValueError:
                        continue

                png_files = [file for file in os.listdir('clothes') if file.lower().endswith('.png')]
                if not png_files:
                    cprint.error("No clothes found in the 'clothes' folder, steal some clothes before uploading.")
                    return
                
                for file_name in png_files:
                    if await robux(session, self.main_cookie[self.cookie]['id']) <= max_robux:
                        cprint.info(f"Hit the max robux limit of {max_robux} R$, stopping.")
                        break

                    xcsrf = csrf.get(self.cookie)
                    session.headers.update({"X-Csrf-Token": xcsrf})
                    file_path = os.path.join('clothes', file_name)
                    cprint.info(f"Uploading \"{file_path}\"...")
                    data = decode(file_path)
                    if 'name' not in data:
                        cprint.error(f"Invalid image or old image ({file_path})")
                        continue
                    await publish(session, file_path, data, group_id, self.main_cookie[self.cookie]['id'])
    except Exception:
        traceback.print_exc()
                
async def publish(session, image_path, data, group_id, user_id):
    form_data = FormData()
    description = data["description"]
    new_description = re.sub(r'(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#/%?=~_|!:,.;]*[-A-Z0-9+&@#/%=~_|])|\b(www\.[^\s]+)', '', description, flags=re.IGNORECASE)
    payload = {
        "displayName": data["name"],
        "description": new_description,
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
                item_info = [
                    "item_id": status_data['response']["assetId"],
                    "user_id": user_id,
                    "group_id": group_id,
                    "name": data["name"],
                    "description": new_description
                ]
                await release(session, item_info)
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

async def release(session, item_info):
    data = {    
        "saleLocationConfiguration": {"saleLocationType": 1, "places": []},
        "targetId": item_info.get("item_id"),
        "priceInRobux": 5,
        "publishingType": 2,
        "idempotencyToken": str(uuid.uuid4()),
        "publisherUserId": item_info.get("user_id"),
        "creatorGroupId": item_info.get("group_id"),
        "name": item_info.get("name"),
        "description": item_info.get("description"),
        "isFree": False,
        "agreedPublishingFee": 0,
        "priceOffset": 0,
        "quantity": 0,
        "quantityLimitPerUser": 0,
        "resaleRestriction": 2,
        "targetType": 0
    }
    async with session.post(f"https://itemconfiguration.roblox.com/v1/collectibles", json=data, ssl=False) as response:
        if response.status == 200:
            cprint.success("Clothing went on sale for 5 robux!")

def decode(file_path):
    with Image.open(file_path) as img: metadata = img.info
    return metadata

async def robux(session, user_id):
    async with session.get(f"https://economy.roblox.com/v1/users/{user_id}/currency", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return int(data.get("robux"))
        else:
            return 999999
