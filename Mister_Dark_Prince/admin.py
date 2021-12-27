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


@Client.on_message(filters.command(["unban"], prefix) & filters.me)
async def unban_command(client: Client, message: Message):
    cause = await text(client, message)
    if message.reply_to_message and message.chat.type not in ["private", "channel"]:
        user_for_unban, name = await get_user_and_name(message)
        try:
            await client.unban_chat_member(message.chat.id, user_for_unban)
            await message.edit(
                f"<b>{name}</b> <code>unbanned!</code>"
                + f"\n{'<b>Cause:</b> <i>' + cause.split(maxsplit=1)[1] + '</i>' if len(cause.split()) > 1 else ''}"
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
                    user_to_unban = await client.get_chat(cause.split(" ")[1])
                    name = user_to_unban.title
                elif await check_username_or_id(cause.split(" ")[1]) == "user":
                    user_to_unban = await client.get_users(cause.split(" ")[1])
                    name = user_to_unban.first_name
                try:
                    await client.unban_chat_member(message.chat.id, user_to_unban.id)
                    await message.edit(
                        f"<b>{name}</b> <code>unbanned!</code>"
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


@Client.on_message(filters.command(["kick"], prefix) & filters.me)
async def kick_command(client: Client, message: Message):
    cause = await text(client, message)
    if message.reply_to_message and message.chat.type not in ["private", "channel"]:
        if message.reply_to_message.from_user:
            try:
                await client.kick_chat_member(
                    message.chat.id, message.reply_to_message.from_user.id
                )
                await client.unban_chat_member(
                    message.chat.id, message.reply_to_message.from_user.id
                )
                channel = await client.resolve_peer(message.chat.id)
                user_id = await client.resolve_peer(
                    message.reply_to_message.from_user.id
                )
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
                    f"<b>{message.reply_to_message.from_user.first_name}</b> <code>kicked!</code>"
                    + f"\n{'<b>Cause:</b> <i>' + text_c.split(maxsplit=1)[1] + '</i>' if len(text_c.split()) > 1 else ''}"
                )
            except UserAdminInvalid:
                await message.edit("<b>No rights</b>")
            except ChatAdminRequired:
                await message.edit("<b>No rights</b>")
            except Exception as e:
                print(e)
                await message.edit("<b>No rights</b>")
        else:
            await message.edit("<b>Reply on user msg</b>")
    elif not message.reply_to_message and message.chat.type not in [
        "private",
        "channel",
    ]:
        if len(cause.split()) > 1:
            try:
                user_to_ban = await client.get_users(cause.split(" ")[1])
                try:
                    await client.kick_chat_member(message.chat.id, user_to_ban.id)
                    await client.unban_chat_member(message.chat.id, user_to_ban.id)
                    await message.edit(
                        f"<b>{user_to_ban.first_name}</b> <code>kicked!</code>"
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


@Client.on_message(filters.command(["unmute"], prefix) & filters.me)
async def unmute_command(client, message):
    cause = await text(client, message)
    if message.reply_to_message and message.chat.type not in ["private", "channel"]:
        u_p = await chat_permissions(client, message)
        if message.reply_to_message.from_user:
            try:
                await client.restrict_chat_member(
                    message.chat.id,
                    message.reply_to_message.from_user.id,
                    u_p,
                    int(time() + 30),
                )
                await message.edit(
                    f"<b>{message.reply_to_message.from_user.first_name}</b> <code>unmuted</code>"
                    + f"\n{'<b>Cause:</b> <i>' + cause.split(' ', maxsplit=1)[1] + '</i>' if len(cause.split()) > 1 else ''}"
                )
            except UserAdminInvalid:
                await message.edit("<b>No rights</b>")
            except ChatAdminRequired:
                await message.edit("<b>No rights</b>")
            except Exception as e:
                print(e)
                await message.edit("<b>No rights</b>")
        else:
            await message.edit("<b>Reply on user msg</b>")
    elif not message.reply_to_message and message.chat.type not in [
        "private",
        "channel",
    ]:
        u_p = await chat_permissions(client, message)
        if len(cause.split()) > 1:
            try:
                user_to_unmute = await client.get_users(cause.split(" ")[1])
                try:
                    await client.restrict_chat_member(
                        message.chat.id, user_to_unmute.id, u_p, int(time() + 30)
                    )
                    await message.edit(
                        f"<b>{user_to_unmute.first_name}</b> <code>unmuted!</code>"
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


@Client.on_message(filters.command(["mute"], prefix) & filters.me)
async def mute_command(client: Client, message: Message):
    cause = await text(client, message)
    if message.reply_to_message and message.chat.type not in ["private", "channel"]:
        mute_seconds: int = 0
        for character in "mhdw":
            match = re.search(rf"(\d+|(\d+\.\d+)){character}", message.text)
            if match:
                if character == "m":
                    mute_seconds += int(
                        float(match.string[match.start(): match.end() - 1]) * 60 // 1
                    )
                if character == "h":
                    mute_seconds += int(
                        float(match.string[match.start(): match.end() - 1]) * 3600 // 1
                    )
                if character == "d":
                    mute_seconds += int(
                        float(match.string[match.start(): match.end() - 1])
                        * 86400
                        // 1
                    )
                if character == "w":
                    mute_seconds += int(
                        float(match.string[match.start(): match.end() - 1])
                        * 604800
                        // 1
                    )
        try:
            if mute_seconds > 30:
                await client.restrict_chat_member(
                    message.chat.id,
                    message.reply_to_message.from_user.id,
                    ChatPermissions(),
                    int(time()) + mute_seconds,
                )
                from_user = message.reply_to_message.from_user
                mute_time: Dict[str, int] = {
                    "days": mute_seconds // 86400,
                    "hours": mute_seconds % 86400 // 3600,
                    "minutes": mute_seconds % 86400 % 3600 // 60,
                }
                message_text = (
                        f"<b>{from_user.first_name}</b> <code> was muted for"
                        f" {((str(mute_time['days']) + ' day') if mute_time['days'] > 0 else '') + ('s' if mute_time['days'] > 1 else '')}"
                        f" {((str(mute_time['hours']) + ' hour') if mute_time['hours'] > 0 else '') + ('s' if mute_time['hours'] > 1 else '')}"
                        f" {((str(mute_time['minutes']) + ' minute') if mute_time['minutes'] > 0 else '') + ('s' if mute_time['minutes'] > 1 else '')}</code>"
                        + f"\n{'<b>Cause:</b> <i>' + cause.split(' ', maxsplit=2)[2] + '</i>' if len(cause.split()) > 2 else ''}"
                )
                while "  " in message_text:
                    message_text = message_text.replace("  ", " ")
            else:
                await client.restrict_chat_member(
                    message.chat.id,
                    message.reply_to_message.from_user.id,
                    ChatPermissions(),
                )
                message_text = (
                        f"<b>{message.reply_to_message.from_user.first_name}</b> <code> was muted for never</code>"
                        + f"\n{'<b>Cause:</b> <i>' + cause.split(' ', maxsplit=1)[1] + '</i>' if len(cause.split()) > 1 else ''}"
                )
            await message.edit(message_text)
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
                user_to_unmute = await client.get_users(cause.split(" ")[1])
                mute_seconds: int = 0
                for character in "mhdw":
                    match = re.search(rf"(\d+|(\d+\.\d+)){character}", message.text)
                    if match:
                        if character == "m":
                            mute_seconds += int(
                                float(match.string[match.start(): match.end() - 1])
                                * 60
                                // 1
                            )
                        if character == "h":
                            mute_seconds += int(
                                float(match.string[match.start(): match.end() - 1])
                                * 3600
                                // 1
                            )
                        if character == "d":
                            mute_seconds += int(
                                float(match.string[match.start(): match.end() - 1])
                                * 86400
                                // 1
                            )
                        if character == "w":
                            mute_seconds += int(
                                float(match.string[match.start(): match.end() - 1])
                                * 604800
                                // 1
                            )
                try:
                    if mute_seconds > 30:
                        await client.restrict_chat_member(
                            message.chat.id,
                            user_to_unmute.id,
                            ChatPermissions(),
                            int(time()) + mute_seconds,
                        )
                        mute_time: Dict[str, int] = {
                            "days": mute_seconds // 86400,
                            "hours": mute_seconds % 86400 // 3600,
                            "minutes": mute_seconds % 86400 % 3600 // 60,
                        }
                        message_text = (
                                f"<b>{user_to_unmute.first_name}</b> <code> was muted for"
                                f" {((str(mute_time['days']) + ' day') if mute_time['days'] > 0 else '') + ('s' if mute_time['days'] > 1 else '')}"
                                f" {((str(mute_time['hours']) + ' hour') if mute_time['hours'] > 0 else '') + ('s' if mute_time['hours'] > 1 else '')}"
                                f" {((str(mute_time['minutes']) + ' minute') if mute_time['minutes'] > 0 else '') + ('s' if mute_time['minutes'] > 1 else '')}</code>"
                                + f"\n{'<b>Cause:</b> <i>' + cause.split(' ', maxsplit=3)[3] + '</i>' if len(cause.split()) > 3 else ''}"
                        )
                        while "  " in message_text:
                            message_text = message_text.replace("  ", " ")
                    else:
                        await client.restrict_chat_member(
                            message.chat.id, user_to_unmute.id, ChatPermissions()
                        )
                        message_text = (
                                f"<b>{user_to_unmute.first_name}</b> <code> was muted for never</code>"
                                + f"\n{'<b>Cause:</b> <i>' + cause.split(' ', maxsplit=2)[2] + '</i>' if len(cause.split()) > 2 else ''}"
                        )
                    await message.edit(message_text)
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


@Client.on_message(filters.command(["demote"], prefix) & filters.me)
async def demote_command(client: Client, message: Message):
    cause = await text(client, message)
    if message.reply_to_message and message.chat.type not in ["private", "channel"]:
        if message.reply_to_message.from_user:
            try:
                await client.promote_chat_member(
                    message.chat.id,
                    message.reply_to_message.from_user.id,
                    is_anonymous=False,
                    can_manage_chat=False,
                    can_change_info=False,
                    can_post_messages=False,
                    can_edit_messages=False,
                    can_delete_messages=False,
                    can_restrict_members=False,
                    can_invite_users=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_voice_chats=False,
                )
                await message.edit(
                    f"<b>{message.reply_to_message.from_user.first_name}</b> <code>demoted!</code>"
                    + f"\n{'<b>Cause:</b> <i>' + cause.split(' ', maxsplit=1)[1] + '</i>' if len(cause.split()) > 1 else ''}"
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
                promote_user = await client.get_users(cause.split(" ")[1])
                try:
                    await client.promote_chat_member(
                        message.chat.id,
                        promote_user.id,
                        is_anonymous=False,
                        can_manage_chat=False,
                        can_change_info=False,
                        can_post_messages=False,
                        can_edit_messages=False,
                        can_delete_messages=False,
                        can_restrict_members=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                        can_promote_members=False,
                        can_manage_voice_chats=False,
                    )
                    await message.edit(
                        f"<b>{promote_user.first_name}</b> <code>demoted!</code>"
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


@Client.on_message(filters.command(["promote"], prefix) & filters.me)
async def promote_command(client: Client, message: Message):
    cause = await text(client, message)
    if message.reply_to_message and message.chat.type not in ["private", "channel"]:
        if message.reply_to_message.from_user:
            try:
                await client.promote_chat_member(
                    message.chat.id,
                    message.reply_to_message.from_user.id,
                    can_delete_messages=True,
                    can_restrict_members=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                )
                if len(cause.split()) > 1:
                    await client.set_administrator_title(
                        message.chat.id,
                        message.reply_to_message.from_user.id,
                        cause.split(maxsplit=1)[1],
                    )
                await message.edit(
                    f"<b>{message.reply_to_message.from_user.first_name}</b> <code>promoted!</code>"
                    + f"\n{'<b>Prefix:</b> <i>' + cause.split(' ', maxsplit=1)[1] + '</i>' if len(cause.split()) > 1 else ''}"
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
                promote_user = await client.get_users(cause.split(" ")[1])
                try:
                    await client.promote_chat_member(
                        message.chat.id,
                        promote_user.id,
                        can_delete_messages=True,
                        can_restrict_members=True,
                        can_invite_users=True,
                        can_pin_messages=True,
                    )
                    if len(cause.split()) > 1:
                        await client.set_administrator_title(
                            message.chat.id,
                            promote_user.id,
                            f"\n{cause.split(' ', maxsplit=2)[2] if len(cause.split()) > 2 else None}",
                        )
                    await message.edit(
                        f"<b>{promote_user.first_name}</b> <code>promoted!</code>"
                        + f"\n{'<b>Prefix:</b> <i>' + cause.split(' ', maxsplit=2)[2] + '</i>' if len(cause.split()) > 2 else ''}"
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

