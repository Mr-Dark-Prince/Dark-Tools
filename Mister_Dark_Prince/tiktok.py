import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from .darkprince.helpo import modules_help


@Client.on_message(filters.command("tt", prefixes="{HNDLR}") & filters.me)
async def tiktok(client: Client, message: Message):
    if message.reply_to_message:
        link = message.reply_to_message.text
    elif len(message.command) == 2:
        link = message.command[1]
    else:
        return await message.edit(
            "<i>You have not provided a link, check out the documentation for this module</i>"
        )
    await message.edit("<i> Loading...</i>")
    await client.send_message("@ttlessbot", "/start")
    await asyncio.sleep(0.5)
    await client.send_message("@ttlessbot", link)
    await asyncio.sleep(7)
    messages = await client.get_history("@ttlessbot")
    video = messages[1].video.file_id
    await message.delete()
    await client.send_video(message.chat.id, video)


modules_help.append(
    {
        "tiktok": [
            {"tt [link]/[reply]*": " Download video from TikTok and send it to chat "}
        ]
    }
)
