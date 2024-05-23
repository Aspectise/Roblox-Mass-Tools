import aiohttp
import asyncio

from src import cprint, csrf

async def start(self, cookies):
    for user in cookies:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": user['cookie']}) as session:
            self.display_theme(1)
            cprint.info(f"Account: {user['name']}")
            while True:
                game_id = cprint.user_input("Enter the game id > ")
                try:
                    game_id = int(game_id)
                    break
                except ValueError:
                    cprint.error("Invalid game id.")
                    continue

            unv_id = await get_game(session, game_id)
            gamepasses = await get_gamepasses(session, unv_id)
            if gamepasses:
                cprint.info(f"You have {len(gamepasses)} gamepasses on this game.")
            else:
                cprint.error("No gamepasses found for this game.")
                break
            
            while True:
                amount = cprint.user_input("How many gamepases do you want to delete? > ")
                try:
                    amount = int(amount)
                    if amount > len(gamepasses):
                        continue
                    break
                except ValueError:
                    cprint.error("Invalid amount.")
                    continue

            for _ in range(amount):
                for gamepass in gamepasses:
                    tasks = [asyncio.create_task(off_sale(session, gamepass))]
            await asyncio.gather(*tasks)


        
async def get_game(session, game):
    async with session.get(f"https://apis.roblox.com/universes/v1/places/{game}/universe", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            unv_id = data.get("universeId")
            return unv_id
        else:
            cprint.error(f"Failed to get game universe id: {response.status}")
            return

async def get_gamepasses(session, game):
    async with session.get(f"https://games.roblox.com/v1/games/{game}/game-passes?limit=100&cursor=&sortOrder=Desc", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("data")
        else:
            cprint.error(f"Failed to get gamepasess: {response.status}")
            return

async def off_sale(session, gamepass):
    async with session.post(f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass['id']}/details", data={"IsForSale": False}, ssl=False) as response:
        if response.status == 200:
            cprint.success(f"Changed gamepass ({gamepass['id']}) to off sale!")
            return
        else:
            cprint.error(f"Failed to put gamepass ({gamepass['id']}) off sale.")