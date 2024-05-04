import aiohttp
import asyncio

from src import cprint, csrf

async def start(self):
    async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
        self.display_theme(1)
        while True:
            game_id = cprint.user_input("Enter the game id > ")
            amount = cprint.user_input("How many gamepases do you want to create? > ")
            try:
                game_id = int(game_id)
                amount = int(amount)
                break
            except ValueError:
                cprint.error("Invalid game id/amount.")
                continue

        while True:
            global_price = None
            choice = cprint.user_input("Do you want to specify a price for each gamepass (1) or specify a price for all gamepasses (2)? (1/2) > ")

            if choice not in ['1', '2']:
                continue

            if choice == '2':
                global_price = cprint.user_input("Enter the gamepasses's price > ")
                try:
                    global_price = int(global_price)
                    break
                except ValueError:
                    cprint.error("Price must be a number")
            else:
                break

        
        unv_id = await get_game(session, game_id)
        if unv_id:
            verify = await verify_game(session, unv_id, self.id)
            if verify:
                xcsrf = csrf.get(self.cookie)
                session.headers.update({"X-Csrf-Token": xcsrf})
                if global_price is not None:
                    tasks = [asyncio.create_task(create(session, unv_id, global_price)) for i in range(amount)]
                    await asyncio.gather(*tasks)
                else:
                    for i in range(amount):
                        await create(session, unv_id, global_price)


        
async def get_game(session, game):
    async with session.get(f"https://apis.roblox.com/universes/v1/places/{game}/universe", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            unv_id = data.get("universeId")
            return unv_id
        else:
            cprint.error(f"Failed to get game universe id: {response.status}")
            return
        
async def verify_game(session, game, id):
    async with session.get(f"https://games.roblox.com/v1/games?universeIds={game}", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            data =  data.get("data")[0]
            creator = data.get("creator").get("id")
            if creator != id:
                cprint.error("You can not create gamepasses on this game!")
                return None
            return True
        else:
            cprint.error(f"Failed to get game universe id: {response.status}")
            return

async def create(session, game_id, price):
    async with session.post("https://apis.roblox.com/game-passes/v1/game-passes", data={"Name": "Gamepass", "Description": "Created With Death", "UniverseId": game_id}, ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            gamepass_id = data.get("gamePassId")
            cprint.success(f"Created gamepass ({gamepass_id})!")
            if price is not None:
                task = [asyncio.create_task(change_satus(session, gamepass_id, price))]
                await asyncio.gather(*task)
            else:
                await change_satus(session, gamepass_id, price)
        else:
            cprint.error(f"Failed to create gamepass: {response.status}")

async def change_satus(session, gamepass, price):
    if price is None:
        while True:
            price = cprint.user_input(f"Enter gamepass ({gamepass}) price > ")
            try:
                price = int(price)
                break
            except ValueError:
                cprint.error("Price must be a number!")
                continue

    async with session.post(f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass}/details", data={"IsForSale": True, "Price": int(price)}, ssl=False) as response:
        if response.status == 200:
            cprint.success(f"Changed gamepass ({gamepass}) to on sale for {price}!")
            return
        else:
            cprint.error(f"Failed to put gamepass ({gamepass}) on sale.")