import os
import shutil
import json
import getpass
import time
import asyncio
import aiohttp
import requests
from rgbprint import gradient_print, Color, rgbprint
from src import cprint
import tools

os.system('cls' if os.name == 'nt' else 'clear')
settings = json.load(open("settings.json", "r"))
class Main:
    def __init__(self) -> None:
        self.cookie = settings.get("Cookie_section").get("Cookie")
        self.version = "1.0.0"

        self.check_version()

        cprint.info(f"Checking the cookie...")
        if settings.get("Cookie_section").get("Bypass"):
            cprint.info(f"Bypassing the cookie...")
            self.cookie = tools.bypass.start(self, 1)

        self.username, self.id = asyncio.run(self.check_cookie())
        cprint.custom(f"Logged in as {self.username}!", "SUCCESS", (0,255,0))
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

    def get_username(self):
        if os.name == 'nt':
            return os.environ.get('USERNAME')
        else: 
            return getpass.getuser()

    async def check_cookie(self):
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
            try:
                async with session.get("https://users.roblox.com/v1/users/authenticated") as response:
                    if response.status == 200:
                        data = await response.json()
                        name = data.get("name")
                        id = data.get("id")
                        return name, id
                    else:
                        cprint.error(f"Please provide a valid cookie.")
                        os.system("pause")
                        os._exit(0)
            except Exception as e:
                cprint.error(f"Please provide a valid cookie.")
                os.system("pause")
                os._exit(0)


    def display_theme(self, page=None):
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
    "10": "Steal Group Clothes"}
        
        NEXT_PAGE: str = f"[00] -> Next Page (SOON)"
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
        if page is None:
            _print_centered(NEXT_PAGE, color=ACCENT_COLOR)
            previous_batch = None
            for batch in batched(map(lambda x: f"[{x[0]}] -> {x[1]}", OPTIONS.items()), 5):
                if previous_batch is None:
                    previous_batch = batch
                    continue

                max_previous_page = max(len(x) for x in previous_batch)
                max_page = max(len(x) for x in batch)

                for i, previous_element in enumerate(previous_batch):
                    _print_centered(f"{previous_element:{max_previous_page}}{OPTIONS_SPACING}{batch[i]:{max_page}}", color=ACCENT_COLOR)
        print()

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
            if str(choice).zfill(2) not in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']:
                cprint.error(f"Please provide a valid option.")
                time.sleep(1)
                continue
            
            try:
                if str(choice).zfill(2) == '00': continue

                if str(choice).zfill(2) == '01': await tools.info.start(self)

                if str(choice).zfill(2) == '02': await tools.leaver.start(self)

                if str(choice).zfill(2) == '03': await tools.unfavorite.start(self)

                if str(choice).zfill(2) == '04': await tools.unfollow.start(self)

                if str(choice).zfill(2) == '05': await tools.unfriend.start(self)

                if str(choice).zfill(2) == '06': await tools.del_tshirts.start(self)

                if str(choice).zfill(2) == '07': tools.bypass.start(self)

                if str(choice).zfill(2) == '08': await tools.nuke.start(self)

                if str(choice).zfill(2) == '09': await tools.pin_crack.start(self)

                if str(choice).zfill(2) == '10': await tools.steal_cloth.start(self)
            except Exception as e:
                cprint.error(e)

            choice = input(f"""\n{Color(0xA080FF)}┌───({Color(255, 255, 255)}{username_pc}@root{Color(0xA080FF)})─[{Color(255, 255, 255)}~{Color(0xA080FF)}]
└──{Color(255, 255, 255)}$ Press enter to go back . . .""")


if __name__ == "__main__":
    Main()

