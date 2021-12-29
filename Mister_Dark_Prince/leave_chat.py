import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from config import HNDLR

from .darkprince.helpo import modules_help


@Client.on_message(
    filters.command(["leave_chat", "lc"], prefixes=f"{HNDLR}") & filters.me
)
async def leave_chat(client: Client, message: Message):
    if message.chat.type in ["group", "supergroup"]:
        await message.edit("<code>Goodbye...</code>")
        await asyncio.sleep(3)
        await client.leave_chat(chat_id=message.chat.id)
    else:
        await message.edit("This is not a group/suppergroup")


modules_help.append({"leave_chat": [{"leave_chat" or "lc": "Quit chat"}]})
