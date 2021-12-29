import asyncio
import sys

from pytgcalls import idle
from pyrogram import Client, idle
from pyrogram.raw.functions.account import GetAuthorizations
from config import call_py

from Mister_Dark_Prince.utils.db import db

async def main():
    await call_py.start()
    print(
        """
    ------------------
   | Dark Prince Started! |
    ------------------
"""
    )
    await idle()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
