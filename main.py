import asyncio

import discord
from discord.ext import commands

from dotenv import load_dotenv

import os

import logging

load_dotenv()
bot_token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w",
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

bot.remove_command("help")


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    print(f"Ready to merge in history...")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(bot_token)

if __name__ == "__main__":
    asyncio.run(main())

