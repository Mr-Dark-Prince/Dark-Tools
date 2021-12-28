from pyrogram import Client
import pyrogram


@Client.on_user_status()
async def make_offline(_, user client: Client):
    if user.id == 5029694040 and user.status == "online":
        await client.send(pyrogram.raw.functions.account.UpdateStatus(offline=True))
        print(m.from_user.status)
