import aiohttp
import asyncio
from src import csrf, cprint

async def start(self, cookies):
    try:
        for cookie in cookies:
            async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie['cookie']}) as session:
                games = await get_favorites(session, cookie['id'])
                self.display_theme(1)
                if games is not None and len(games) >= 1:
                    cprint.info(f"Gathered {len(games)} favorited games for {cookie['name']}")
                    while True:
                        choice = cprint.user_input(f"Do you want to Fast Unfavorite Games? (y/N) > ")
                        if choice not in ["yes", "no", "n", "y"]:
                            continue
                        break

                    if choice in ["no", "n"]:
                        for game in games:
                            game_name = game['name']
                            game_id = game['id']

                            choice = cprint.user_input(f"Do you want to unfavorite: {game_name} (ID: {game_id})? (y/N): ")
                            if choice in ["yes", "y"]:
                                await unfavorite(session, game, cookie['cookie'])
                                continue
                    else:
                        xcsrf = csrf.get(cookie['cookie'])
                        session.headers.update({"X-Csrf-Token": xcsrf})

                        tasks = [asyncio.create_task(fast_unfavorite(session, game)) for game in games]
                        await asyncio.gather(*tasks)

                if games == []:
                    cprint.info(f"No favorited games found")

    except Exception as e:
        cprint.error(e)


async def get_favorites(session, id):
    cursor = ""
    all_games = []
    while True:
        async with session.get(f"https://www.roblox.com/users/favorites/list-json?assetTypeId=9&itemsPerPage=10000000&userId={id}&cursor={cursor}", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                games = data.get("Data").get("Items")

                for game in games:
                    entry = {
                        "name": game.get("Item").get("Name"),
                        "id": game.get("Item").get("AssetId"),
                        "uid": game.get("Item").get("UniverseId")
                    }
                    all_games.append(entry)

                nextcursor = data.get("NextCursor")
                if nextcursor:
                    cursor = nextcursor
                else:
                    return all_games
            else:
                cprint.error(f"Failed to fetch favorited games")
                return None

async def fast_unfavorite(session, game):
    game_name = game['name']
    game_id = game['id']
    game_uid = game['uid']

    async with session.post(f"https://games.roblox.com/v1/games/{game_uid}/favorites", json={"isFavorited": False}, ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"{game_name} (ID: {game_id})", "UNFAVORITED", (0, 255, 0))
        else:
            cprint.error(f"Failed to unfavorite game: {game_name} (ID: {game_id}) {response.status}")

async def unfavorite(session, game, cookie):
    xcsrf = csrf.get(cookie)
    game_name = game['name']
    game_id = game['id']
    game_uid = game['uid']
    
    async with session.post(f"https://games.roblox.com/v1/games/{game_uid}/favorites", json={"isFavorited": False}, headers={"x-csrf-token": xcsrf}, ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"{game_name} (ID: {game_id})", "UNFAVORITED", (0, 255, 0))
        else:
            cprint.error(f"Failed to unfavorite game: {game_name} (ID: {game_id}) {response.status}")
