import os
import json
import time
import tools
import shutil
import getpass
import asyncio
import aiohttp
import requests
from src import cprint
from rgbprint import Color, rgbprint

os.system('cls' if os.name == 'nt' else 'clear')
settings = json.load(open("settings.json", "r"))
class Main:
    def __init__(self) -> None:
        self.cookie = settings.get("Main_Cookie").get("Cookie")
        self.version = "1.3.0"
        self.multicookies = []
        self.main_cookie = {self.cookie: {"cookie":self.cookie, "name": None, "id": None}}
        self.check_version()

        cprint.info(f"Checking the cookie...")
        if settings.get("Main_Cookie").get("Bypass"):
            cprint.info(f"Bypassing the cookie...")
            self.cookie = tools.region_bypass.start(self, 1)
            if not self.cookie:
                cprint.info("Falling back to normal checking... ")
                self.cookie = settings.get("Main_Cookie").get("Cookie")

        asyncio.run(self.check_cookie(self.cookie))
        cprint.success(f"Logged in as {self.main_cookie[self.cookie]['name']}!")
        if os.path.exists('cookies.txt'):
            with open('cookies.txt', 'r') as f:
                for line in f:
                    if line.startswith('_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|'):
                        self.multicookies.append(line.strip())

            if len(self.multicookies) >= 1:
                while True:
                    cookie_amount = cprint.user_input(f"You have {len(self.multicookies)} cookies, how many do you want to use? > ")
                    try:
                        cookie_amount = int(cookie_amount)
                        if cookie_amount < 0 or cookie_amount > len(self.multicookies):
                            cprint.error(f"Number should be equal or lower to {len(self.multicookies)}")
                            continue

                        if cookie_amount == 0:
                            self.multicookies = []
                        else:
                            self.multicookies = self.multicookies[:cookie_amount]

                        break
                    except ValueError:
                        continue

                if self.multicookies:
                    asyncio.run(self.multi_cookie())
        time.sleep(2)

        os.system('cls' if os.name == 'nt' else 'clear')
        asyncio.run(self.main())

    def check_version(self):
        cprint.info(f"Checking for updates...")
        try:
            response = requests.get("https://raw.githubusercontent.com/Aspectise/death-sniper/main/mass-tools")
            latest_version = response.text.strip()
            if latest_version != self.version:
                cprint.custom(f"New version available. Please update to version {latest_version} from the Github! (continuing in 5s)\n", "NEW", (255,165,0))
                time.sleep(5)
            else:
                cprint.info(f"Up-To-Date!")

        except requests.exceptions.RequestException:
            pass
        except:
            pass

    async def multi_cookie(self):
        self.multicookies_data = {cookie: {"cookie": cookie, "name": None, "id": None} for cookie in self.multicookies} 
        tasks = [asyncio.create_task(self.check_cookie(cookie, 1)) for cookie in self.multicookies]
        await asyncio.gather(*tasks)

    def get_username(self):
        if os.name == 'nt':
            return os.environ.get('USERNAME')
        else: 
            return getpass.getuser()

    async def check_cookie(self, cookie, mass=None):
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as session:
            try:
                async with session.get("https://users.roblox.com/v1/users/authenticated") as response:
                    if response.status == 200:
                        data = await response.json()
                        name = data.get("name")
                        id = data.get("id")
                        if not mass:
                            self.main_cookie[cookie]["name"] = name
                            self.main_cookie[cookie]["id"] = id
                        else:
                            self.multicookies_data[cookie]["name"] = name
                            self.multicookies_data[cookie]["id"] = id
                            cprint.success(f"Logged in {name}!")
                    else:
                        if not mass:
                            cprint.error(f"Please provide a valid cookie.")
                            os.system("pause")
                            os._exit(0)
                        else:
                            cprint.error(f"Invalid cookie.")
                            return None
            except Exception as e:
                cprint.error(f"Please provide a valid cookie.")
                os.system("pause")
                os._exit(0)


    def display_theme(self, banner=None):
        os.system('cls' if os.name == 'nt' else 'clear')
        MAIN_COLOR: Color = Color(0xA080FF)
        ACCENT_COLOR: Color = Color(255, 255, 255)

        TITLE: str = f"""
        ░▒▓███████▓▒░░▒▓████████▓▒░░▒▓██████▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░ 
        ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░ 
        ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░ 
        ░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░ ░▒▓████████▓▒░ ░▒▓█▓▒░   ░▒▓████████▓▒░ 
        ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░ 
        ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░ 
        ░▒▓███████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░ 
        """

        TEXT_IN_BOX: str = "Roblox-Mass-Tools"

        SIGNATURE: str = f"""
        ╔═{"═" * (len(TEXT_IN_BOX) + len(self.version) + 1)}═╗
        ║ {TEXT_IN_BOX} {self.version} ║
        ╚═{"═" * (len(TEXT_IN_BOX) + len(self.version) + 1)}═╝
        """

        OPTIONS: dict[str, str] = {
    "01": "Display Cookie Info",
    "02": "Mass Group Leaver",
    "03": "Mass Unfavorite Games",
    "04": "Mass Unfollow",
    "05": "Mass Unfriend",
    "06": "Mass delete t-shirts",
    "07": "Unregion Lock Cookie",
    "08": "Nuke Account/Cookie",
    "09": "Pin Cracker",
    "10": "Steal Group Clothes",

    "11": "Mass Create Gamepasses",
    "12": "Spam User Inbox",
    "13": "Check Group ID",
    "14": "Randomize Avatar",
    "15": "Upload Clothes",
    "16": "Mass Create Outfits",
    "17": "Mass Delete Outfits",
    "18": "Auto Ally",
    "19": "Mass Off Sale Gamepasses",
    "20": "SOON"
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

        _print_centered(TITLE, color=MAIN_COLOR)
        _print_centered(SIGNATURE, color=ACCENT_COLOR)
        print()

        if banner is None:
            previous_batch = None
            for batch in batched(map(lambda x: f"[{x[0]}] -> {x[1]}", OPTIONS.items()), 10):
                if previous_batch is None:
                    previous_batch = batch
                    continue

                max_previous_page = max(len(x) for x in previous_batch)
                max_page = max(len(x) for x in batch)

                for i, previous_element in enumerate(previous_batch):
                    _print_centered(f"{previous_element:{max_previous_page}}{OPTIONS_SPACING}{batch[i]:{max_page}}", color=ACCENT_COLOR)
        print()

    async def handle(self, tool):
        if self.multicookies:
            choice = cprint.user_input("Use main cookie? (y/N) > ").lower()
            if choice in ["y", "yes"]:
                await tool.start(self, list(self.main_cookie.values()))
            else:
                if len(self.multicookies) > 1:
                    amount = cprint.user_input("How many cookies to use? > ")
                    await tool.start(self, list(self.multicookies_data.values())[:int(amount)])
                else:
                    await tool.start(self, list(self.multicookies_data.values()))
        else:
            await tool.start(self, list(self.main_cookie.values()))

    async def main(self):
        while True:
            self.display_theme()
            try:
                username_pc = self.get_username()
            except Exception:
                username_pc = self.username
            choice = input(f"""{Color(0xA080FF)}┌───({Color(255, 255, 255)}{username_pc}@root{Color(0xA080FF)})─[{Color(255, 255, 255)}~{Color(0xA080FF)}]
└──{Color(255, 255, 255)}$ """)
            
            if choice == "exit":
                break

            if not choice.isdigit():
                cprint.error(f"Please provide a valid option.")
                time.sleep(1)
                continue

            choice = int(choice)
            if f"{choice:02d}" not in [f"{i:02d}" for i in range(21)]:
                cprint.error(f"Please provide a valid option.")
                time.sleep(1)
                continue
            
            try:
                if str(choice).zfill(2) == '00': continue
                if str(choice).zfill(2) == '01': await tools.cookie_info.start(self)
                if str(choice).zfill(2) == '02': await self.handle(tools.group_leaver)
                if str(choice).zfill(2) == '03': await self.handle(tools.unfavorite)
                if str(choice).zfill(2) == '04': await self.handle(tools.unfollow)
                if str(choice).zfill(2) == '05': await self.handle(tools.unfriend)
                if str(choice).zfill(2) == '06': await self.handle(tools.del_tshirts)
                if str(choice).zfill(2) == '07': tools.region_bypass.start(self)
                if str(choice).zfill(2) == '08': await tools.nuker.start(self)
                if str(choice).zfill(2) == '09': await tools.pin_crack.start(self)
                if str(choice).zfill(2) == '10': await tools.steal_cloth.start(self)
                if str(choice).zfill(2) == '11': await self.handle(tools.create_gamepass)
                if str(choice).zfill(2) == '12': await self.handle(tools.inbox_message)
                if str(choice).zfill(2) == '13': await tools.group_check.start(self)
                if str(choice).zfill(2) == '14': await self.handle(tools.randomize_avatar)
                if str(choice).zfill(2) == '15': await tools.publish_cloth.start(self)
                if str(choice).zfill(2) == '16': await self.handle(tools.create_outfits)
                if str(choice).zfill(2) == '17': await self.handle(tools.delete_fits)
                if str(choice).zfill(2) == '18': await tools.auto_ally.start(self)
                if str(choice).zfill(2) == '19': await self.handle(tools.offsale_gamepass)
            except Exception as e:
                import traceback
                traceback.print_exc()
                cprint.error(e)

            choice = input(f"""\n{Color(0xA080FF)}┌───({Color(255, 255, 255)}{username_pc}@root{Color(0xA080FF)})─[{Color(255, 255, 255)}~{Color(0xA080FF)}]
└──{Color(255, 255, 255)}$ Press enter to go back . . .""")


if __name__ == "__main__":
    Main()

