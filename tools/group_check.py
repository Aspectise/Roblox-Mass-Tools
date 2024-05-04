import aiohttp
import shutil
from rgbprint import Color, rgbprint
import traceback

from src import cprint

async def start(self):
    try:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
            self.display_theme(1)
            while True:
                group_id = cprint.user_input("Enter a group id > ")
                try:
                    group_id = int(group_id)
                    break
                except ValueError:
                    cprint.error("Group id must be a number.")

            group_info = await check(session, group_id)
            if group_info:
                group_owner = group_info.get("owner").get("username")
                group_oid = group_info.get("owner").get("userId")
                group_name = group_info.get("name")
                group_count = group_info.get("memberCount")
                group_access = group_info.get("publicEntryAllowed")
                shout = group_info.get("shout")
                group_shout = "N/A"
                if shout:
                    group_shout = shout.get("body")

                group_pending = 'N/A'
                group_premium = 'N/A'
                group_payout = 'N/A'
                group_sales = 'N/A'

                if group_oid == self.id:
                    private_info = await check_private(session, group_id)
                    if private_info:
                        group_pending = private_info.get("pendingRobux")
                        group_premium = private_info.get("premiumPayouts")
                        group_payout = private_info.get("groupPayoutRobux")
                        group_sales = private_info.get("itemSaleRobux")

                self.display_theme(1)

                INFO: dict[str, str] = {
            "GROUP OWNER": group_owner,
            "GROUP OWNER ID": group_oid,
            "GROUP NAME": group_name,
            "MEMBER COUNT": group_count,
            "ACCESS": 'Public' if group_access else 'Private',
            "GROUP SHOUT": group_shout,
            "GROUP PENDING": group_pending,
            "GROUP PREMIUM PAYOUT": group_premium,
            "GROUP PAYOUT": group_payout,
            "GROUP SALES": group_sales
            }
                OPTIONS_SPACING: str = f"{str().ljust(30)}"
                def _get_shell_size() -> int:
                    return shutil.get_terminal_size().columns

                def _print_centered(text: str, *, color: Color = None, end: str = "\n") -> None:
                    for line in text.splitlines():
                        rgbprint(line.center(_get_shell_size()), color=color, end=end)

                def batched(iterable, n):
                    import itertools
                    it = iter(iterable)
                    while batch := tuple(itertools.islice(it, n)):
                        yield batch

                previous_batch = None
                for batch in batched(map(lambda x: f"[{x[0]}] -> {x[1]}", INFO.items()), 5):
                    if previous_batch is None:
                        previous_batch = batch
                        continue
                    
                    max_previous_page = max(len(x) for x in previous_batch)
                    max_page = max(len(x) for x in batch)
                    for i, previous_element in enumerate(previous_batch):
                        _print_centered(f"{previous_element:{max_previous_page}}{OPTIONS_SPACING}{batch[i]:{max_page}}", color=Color(255, 255, 255))
    except Exception:
        traceback.print_exc()


async def check(session, group_id):
    async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            cprint.error(f"Failed to get group information: {response.status}")
            return None

async def check_private(session, group_id):
    async with session.get(f"https://economy.roblox.com/v1/groups/{group_id}/revenue/summary/year", ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            cprint.error(f"Failed to get pending robux: {response.status}")
            return None