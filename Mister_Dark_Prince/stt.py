import asyncio

from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.types import Message

from config import HNDLR

from .darkprince.helpo import modules_help


@Client.on_message(filters.command(["vo", "voicy"], prefixes=f"{HNDLR}") & filters.me)
async def voice_text(client: Client, message: Message):
    try:
        if not message.reply_to_message:
            await message.edit("<b> No replay! </b>")
        else:
            if message.reply_to_message.voice:
                await message.edit("<b> ⏳️Wait.... </b>")
                await client.send_message("@voicybot", "/start")
                await asyncio.sleep(1)
                await message.reply_to_message.forward("@voicybot")
                await asyncio.sleep(3)
                messages = await client.get_history("@voicybot")
                await message.edit(
                    f'<b>Text:</b>\n{messages[0].text.replace("Supported by Borodach Invest"," ")}'
                )
                await client.send(
                    functions.messages.DeleteHistory(
                        peer=await client.resolve_peer(259276793),
                        max_id=0,
                        just_clear=True,
                    )
                )
            else:
                await message.edit("<b> This is not a voice !</b>")
    except Exception as e:
        await message.edit(f"<b> Oops😬 :</b> <code>{e}</code")


modules_help.append(
    {"Voice_to_text": [{"voicy": "Replay the voice and get the text from the voice)"}]}
)
