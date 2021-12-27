import re
from time import time
from typing import Dict, Union

from pyrogram import Client, ContinuePropagation, filters
from pyrogram.errors import (
    UserAdminInvalid,
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameInvalid,
)
from pyrogram.raw import functions, types
from pyrogram.types import Message, ChatPermissions
from pyrogram.utils import (
    get_channel_id,
    MAX_USER_ID,
    MIN_CHAT_ID,
    MAX_CHANNEL_ID,
    MIN_CHANNEL_ID,
)


from .utils.scripts import text, chat_permissions
from config import HNDLR


async def check_username_or_id(data: Union[str, int]) -> str:
    data = str(data)
    if (
        not data.isdigit()
        and data[0] == "-"
        and not data[1:].isdigit()
        or not data.isdigit()
        and data[0] != "-"
    ):
        return "channel"
    else:
        peer_id = int(data)
    if peer_id < 0:
        if MIN_CHAT_ID <= peer_id:
            return "chat"

        if MIN_CHANNEL_ID <= peer_id < MAX_CHANNEL_ID:
            return "channel"
    elif 0 < peer_id <= MAX_USER_ID:
        return "user"

    raise ValueError(f"Peer id invalid: {peer_id}")


async def get_user_and_name(message):
    if message.reply_to_message.from_user:
        return (
            message.reply_to_message.from_user.id,
            message.reply_to_message.from_user.first_name,
        )
    elif message.reply_to_message.sender_chat:
        return (
            message.reply_to_message.sender_chat.id,
            message.reply_to_message.sender_chat.title,
        )


@Client.on_message(filters.command(["ban"], prefixes=f"{HNDLR}") & filters.me)
async def ban_command(client: Client, message: Message):
    cause = await text(client, message)
    if message.reply_to_message and message.chat.type not in ["private", "channel"]:
        user_for_ban, name = await get_user_and_name(message)
        try:
            await client.kick_chat_member(message.chat.id, user_for_ban)
            channel = await client.resolve_peer(message.chat.id)
            user_id = await client.resolve_peer(user_for_ban)
            if "report_spam" in cause.lower().split():
                await client.send(
                    functions.channels.ReportSpam(
                        channel=(channel),
                        user_id=(user_id),
                        id=[message.reply_to_message.message_id],
                    )
                )
            if "delete_history" in cause.lower().split():
                await client.send(
                    functions.channels.DeleteUserHistory(
                        channel=(channel), user_id=(user_id)
                    )
                )
            text_c = "".join(
                f" {_}"
                for _ in cause.split()
                if _.lower() not in ["delete_history", "report_spam"]
            )

            await message.edit(
                f"<b>{name}</b> <code>banned!</code>"
                + f"\n{'<b>Cause:</b> <i>' + text_c.split(maxsplit=1)[1] + '</i>' if len(text_c.split()) > 1 else ''}"
            )
        except UserAdminInvalid:
            await message.edit("<b>No rights</b>")
        except ChatAdminRequired:
            await message.edit("<b>No rights</b>")
        except Exception as e:
            print(e)
            await message.edit("<b>No rights</b>")
    elif not message.reply_to_message and message.chat.type not in [
        "private",
        "channel",
    ]:
        if len(cause.split()) > 1:
            try:
                if await check_username_or_id(cause.split(" ")[1]) == "channel":
                    user_to_ban = await client.get_chat(cause.split(" ")[1])
                    name = user_to_ban.title
                elif await check_username_or_id(cause.split(" ")[1]) == "user":
                    user_to_ban = await client.get_users(cause.split(" ")[1])
                    name = user_to_ban.first_name
                try:
                    await client.kick_chat_member(message.chat.id, user_to_ban.id)
                    await message.edit(
                        f"<b>{name}</b> <code>banned!</code>"
                        + f"\n{'<b>Cause:</b> <i>' + cause.split(' ', maxsplit=2)[2] + '</i>' if len(cause.split()) > 2 else ''}"
                    )
                except UserAdminInvalid:
                    await message.edit("<b>No rights</b>")
                except ChatAdminRequired:
                    await message.edit("<b>No rights</b>")
                except Exception as e:
                    print(e)
                    await message.edit("<b>No rights</b>")
            except PeerIdInvalid:
                await message.edit("<b>User is not found</b>")
            except UsernameInvalid:
                await message.edit("<b>User is not found</b>")
            except IndexError:
                await message.edit("<b>User is not found</b>")
        else:
            await message.edit("<b>user_id or username</b>")
    else:
        await message.edit("<b>Unsupported</b>")

