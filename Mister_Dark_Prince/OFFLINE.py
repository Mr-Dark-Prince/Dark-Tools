from main import app
import pyrogram


@app.on_user_status()
async def make_offline(_, user):
    if user.id == 5029694040 and user.status == "online":
        await app.send(pyrogram.raw.functions.account.UpdateStatus(offline=True))
        print(m.from_user.status)
