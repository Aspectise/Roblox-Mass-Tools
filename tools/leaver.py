import aiohttp
import asyncio
from src import csrf, cprint

async def start(self):
    try:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
            groups = await get_groups(session, self.id)
            self.display_theme(1)
            if groups is not None and len(groups) >= 1:
                cprint.info(f"Gathered {len(groups)} groups")
                choice = cprint.user_input(f"Do you want to Fast Leave Groups? (y/N) > ")
                whitelisted_ids = []
                if choice in ["yes", "y"]:
                    choice_wl = cprint.user_input(f"Do you want to add a whitelist? (y/N) > ")

                    if choice_wl in ["yes", "y"]:
                        whitelist_input = cprint.user_input(f"Enter group ids you don't want to leave separated by a comma (id, id..) > ")
                        whitelisted_ids = [id.strip() for id in whitelist_input.split(',')]

                    xcsrf = csrf.get(self.cookie)
                    session.headers.update({"X-Csrf-Token": xcsrf})

                    tasks = [asyncio.create_task(leave_groups(session, group, self.id, whitelisted_ids)) for group in groups]
                    await asyncio.gather(*tasks)

                if choice in ["no", "n"]:
                    for group in groups:
                        group_name = group['group']['name']
                        group_id = group['group']['id']
                        group_rank = group["role"]['rank']

                        if group_rank == 255:
                            cprint.info(f"Skipping group (owned): {group_name} (ID: {group_id})")
                            continue

                        choice = cprint.user_input(f"Do you want to leave: {group_name} (ID: {group_id})? (y/N): ")
                        if choice in ["yes", "y"]:
                            await leave_group(session, group, self.id, self.cookie)
                            continue

            if groups == []:
                cprint.info(f"No groups found")

    except Exception as e:
        cprint.error(e)


async def get_groups(session, id):
    async with session.get(f"https://groups.roblox.com/v2/users/{id}/groups/roles", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            groups = data.get("data")
            return groups
        else:
            cprint.error("Failed to fetch groups")
            return None

async def leave_groups(session, group, id, whitelisted):
    group_name = group['group']['name']
    group_id = group['group']['id']
    group_rank = group["role"]['rank']

    if str(group_id) in whitelisted:
        cprint.info(f"Skipping whitelisted group")
        return

    if group_rank == 255:
        cprint.info(f"Skipping group (owned): {group_name} (ID: {group_id})")
        return

    async with session.delete(f"https://groups.roblox.com/v1/groups/{group_id}/users/{id}", ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"{group_name} (ID: {group_id})", "LEFT", (0, 255, 0))
        else:
            cprint.error(f"Failed to leave group: {group_name} (ID: {group_id}) {response.status}")

async def leave_group(session, group, id, cookie):
    xcsrf = csrf.get(cookie)
    group_name = group['group']['name']
    group_id = group['group']['id']

    async with session.delete(f"https://groups.roblox.com/v1/groups/{group_id}/users/{id}", headers={"x-csrf-token": xcsrf}, ssl=False) as response:
        if response.status == 200:
            cprint.custom(f"{group_name} (ID: {group_id})", "LEFT", (0, 255, 0))
        else:
            cprint.error(f"Failed to leave group: {group_name} (ID: {group_id}) {response.status}")