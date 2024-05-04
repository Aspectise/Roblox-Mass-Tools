import aiohttp
import asyncio
import traceback

from src import cprint, csrf

async def start(self):
    try:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": self.cookie}) as session:
            self.display_theme(1)
            user_id = cprint.user_input("Enter the user id you want to spam > ")
            subject = cprint.user_input("Enter the subject of the message > ")
            message = cprint.user_input("Enter the message you want to send > ")
            amount = cprint.user_input("Enter the amount of time to spam the user > ")

            xcsrf = csrf.get(self.cookie)
            session.headers.update({"X-Csrf-Token": xcsrf})
            tasks = [asyncio.create_task(send(session, user_id, subject, message)) for i in range(int(amount))]
            await asyncio.gather(*tasks)
    except Exception:
        traceback.print_exc()

async def send(session, user_id, subject, message):
    async with session.post("https://privatemessages.roblox.com/v1/messages/send", json={"subject": f"{subject}", "body": f"{message}", "recipientId": int(user_id)}, ssl=False) as response:
        if response.status == 200:
            data = await response.json()
            success = data.get("success")
            if success:
                cprint.success(f"Sent private message to {user_id}!")
            else:
                cprint.error(f"Failed to send private message to {user_id}: {data.get('shortMessage')}")
        else:
            cprint.error(f"Failed to send private message to {user_id}: {response.status}")