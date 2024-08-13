import aiohttp
import asyncio
import traceback

from src import cprint, csrf

async def start(self, cookies):
    try:
        for user in cookies:
            async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": user['cookie']}) as session:
                self.display_theme(1)
                cprint.info(f"Gathering {user['name']}'s private servers...")
                private_servers = await get_ps(session, user['id'], user['name'])
                if private_servers:
                    cprint.info(f"Found {len(private_servers)} paid private server, deactivating...")
                    private_servers = await check_ps(session, private_servers, user['id'])
                    xcsrf = csrf.get(self.cookie)
                    session.headers.update({"X-Csrf-Token": xcsrf})
                    await deactivate_ps(session, private_servers)
    except Exception:
        traceback.print_exc()

async def get_ps(session, user_id, username):
    paid_ps = []
    cursor = ""
    while True:
        async with session.get(f"https://www.roblox.com/users/inventory/list-json?assetTypeId=9&itemsPerPage=1000&placeTab=MyPrivateServers&userId={user_id}&cursor={cursor}", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                data = data.get("Data", None)
                private_servers = data.get("Items", None)
                if data and private_servers:
                    if len(private_servers) == 1:
                        server = private_servers[0]
                        if not server.get("PrivateServer"):
                            cprint.info(f"No private servers found for {username}")
                            return None
                        
                    for server in private_servers:
                        game_id = server.get("Item").get("AssetId")
                        ps_price = server.get("Product").get("PriceInRobux")
                        if ps_price:
                            entry = {"id":game_id}
                            paid_ps.append(entry)
                    if data.get("nextPageCursor"):
                        cursor = data.get("nextPageCursor")
                        continue
                    return paid_ps
                else:
                    cprint.info(f"No private servers found for {username}")
                    return None
            else:
                cprint.error(f"Failed to gather private servers: {response.status}")
                return None
            
async def check_ps(session, servers, user_id):
    private_servers = []
    for server in servers:
        async with session.get(f"https://games.roblox.com/v1/games/{server['id']}/private-servers", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                data = data.get("data")
                for ps in data:
                    if ps.get("owner").get("id") == user_id:
                        ps_code = ps.get("vipServerId")
                        entry = {"id":server['id'], "code": ps_code}
                        private_servers.append(entry)
                return private_servers
            else:
                cprint.error(f"Failed to gather private servers code: {response.status}")
                return None

async def deactivate_ps(session, servers):
    for server in servers:
        async with session.get(f"https://games.roblox.com/v1/vip-servers/{server['code']}", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("active") and data.get("subscription").get("active"):
                    async with session.patch(f"https://games.roblox.com/v1/vip-servers/{server['code']}/subscription", json={"active": False, "price": data.get("subscription").get("price")}, ssl=False) as response:
                        if response.status == 200:
                            cprint.success(f"Deactivated a {data.get('game').get('name')} private server!")
                        else:
                            cprint.error(f"Failed to deactivate a {data.get('game').get('name')} private server: {response.status}")
                else:
                    cprint.info(f"A {data.get('game').get('name')} private server is either expired or already deactivated.")
