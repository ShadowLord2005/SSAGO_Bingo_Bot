import asyncio
from enum import Enum
from os import getenv
from pathlib import Path

import discord
from core_classes import handler, logger
from discord import app_commands, ui
from discord.ext import commands

dev_guild_id = getenv("DEV_GUILD_ID")
guild = discord.Object(int(dev_guild_id)) if dev_guild_id != None else None

with Path("bot_token.txt").open() as token_file:
    discord_token = token_file.read()

if discord_token == None:
    raise Exception

cog_dirs = ["bot_games"]


class SSAGOGameBot(commands.Bot):
    #Suppress error on the User attribute being None
    user: discord.ClientUser # type: ignore

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned_or("$$"),intents=intents)

    async def setup_hook(self) -> None:
        for directory_name in cog_dirs:
            for file in Path.iterdir(Path(f'./{directory_name}')):
                if file.suffix == ".py":
                    await bot.load_extension(f'{directory_name}.{file.name[:-3]}')
                    logger.info(f"Loaded extension {file.name[:-3]}")


    async def on_ready(self):
        logger.info("Logged in as %s", self.user)
        try:
            synced = await bot.tree.sync(guild=guild)
            id = guild.id if guild != None else "all"
            logger.info("Synced %s commands with server %s", len(synced), id)
        except Exception as e:
            logger.error(e)


bot = SSAGOGameBot()


if __name__ == "__main__":

    bot.run(discord_token, log_handler=handler)

