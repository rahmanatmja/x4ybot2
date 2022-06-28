from __future__ import annotations

import asyncio
import os
import sys
import traceback

import aiohttp
import discord
import random
import datetime
from itertools import cycle
from discord.ext import commands
from discord.ext.commands import ExtensionFailed, ExtensionNotFound, NoEntryPointError
from dotenv import load_dotenv

from utils import locale_v2
from utils.valorant.cache import get_cache

load_dotenv()

initial_extensions = [
    'cogs.admin',
    'cogs.errors',
    'cogs.notify',
    'cogs.valorant'
]

# intents required
intents = discord.Intents.default()
intents.message_content = True

BOT_PREFIX = '-'


class ValorantBot(commands.Bot):
    debug: bool
    bot_app_info: discord.AppInfo
    
    def __init__(self) -> None:
        super().__init__(command_prefix=BOT_PREFIX, case_insensitive=True, intents=intents)
        self.bot_version = '3.2.1'
        self.tree.interaction_check = self.interaction_check
    
    @staticmethod
    async def interaction_check(interaction: discord.Interaction) -> bool:
        locale_v2.set_interaction_locale(interaction.locale)  # bot responses localized # wait for update
        locale_v2.set_valorant_locale(interaction.locale)  # valorant localized
        return True
    
    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner
    
status = cycle ([
    "4ly don't be afraid ❤️",
    "listening to 4ly's heart ❤️",
    "watching my beautiful 4ly ❤️",
    "I Love My Girlfriend",
    "ILY 4ly ❤️",
    "4ly, i never wanna lose you"
    "4ly you're cute!"
])

listening = discord.ActivityType.listening

@tasks.loop(seconds=30)
async def status_swap():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(next(status)))

@client.event
async def on_ready():
    status_swap.start()
    print('Connected to bot: {}'.format(client.user.name))
    print('Bot ID: {}'.format(client.user.id))
    print('x4ybot is online')
    
    #async def on_ready(self) -> None:
       # await self.tree.sync()
       # print(f"\nLogged in as: {self.user}\n\n BOT IS READY !")
       # print(f"Version: {self.bot_version}")
        
        # bot presence
        #activity_type = discord.ActivityType.listening
        #status_idle = discord.Status.idle
        #await self.change_presence(status=discord.Status(type=status_idle), activity=discord.Activity(type=activity_type, name="4ly's heart ❤️")) #original (╯•﹏•╰)
        #await asyncio.sleep(5)

        #status_dnd = discord.Status.do_not_disturb
        #await self.change_presence(status=discord.Status(type=status_dnd), activity=discord.Activity(type=activity_type, name="my beautiful 4ly ❤️")) #original (╯•﹏•╰)
        #await asyncio.sleep(5)

        #status_invis = discord.Status.invisible
        #await self.change_presence(status=discord.Status(type=status_invis), activity=discord.Game("I Love You 4ly ❤️")) #original (╯•﹏•╰)
        #await asyncio.sleep(5)

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        
        try:
            self.owner_id = int(os.getenv('OWNER_ID'))
        except ValueError:
            self.bot_app_info = await self.application_info()
            self.owner_id = self.bot_app_info.owner.id
        
        self.setup_cache()
        await self.load_cogs()
    
    async def load_cogs(self) -> None:
        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
            except (
                ExtensionNotFound,
                NoEntryPointError,
                ExtensionFailed,
            ):
                print(f'Failed to load extension {ext}.', file=sys.stderr)
                traceback.print_exc()
    
    @staticmethod
    def setup_cache() -> None:
        try:
            open('data/cache.json')
        except FileNotFoundError:
            get_cache()
    
    async def close(self) -> None:
        await self.session.close()
        await super().close()
    
    async def start(self, debug: bool = False) -> None:
        self.debug = debug
        return await super().start(os.getenv('TOKEN'), reconnect=True)


def run_bot() -> None:
    bot = ValorantBot()
    asyncio.run(bot.start(debug=False))


if __name__ == '__main__':
    run_bot()
