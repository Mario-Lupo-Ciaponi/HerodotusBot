import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from better_profanity import profanity
from discord.message import Message
import requests


WIKI_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"


profanity.load_censor_words()

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w",
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix="!", intents=intents)


# <-------------- Start of events -------------->

@bot.event
async def on_ready():

    print(f"Ready to merge in history...")

@bot.event
async def member_join(member):
    try:
        await member.send("Welcome, my student! Together we shall learn!")
    except discord.Forbidden:
        print(f"Could not DM {member.name}, they might have DMs disabled.")


@bot.event
async def on_message(message: Message):
    if message.author == bot.user.name:
        return

    if profanity.contains_profanity(message.content):
        await message.delete()
        await message.channel.send(f"These words are not allowed in my class!")

    await bot.process_commands(message)


@bot.event
async def on_message_edit(before: Message, after: Message):
    if profanity.contains_profanity(after.content):
        await after.delete()
        await after.channel.send(f"{after.author} tried to edit his message, but it contains profanity!"
                                 f"Before the edit -> {before.content}")

# <-------------- End of events -------------->

# <-------------- Start of commands -------------->

@bot.command()
async def wave(ctx):
    await ctx.send("Well, hello there, dear student! Welcome to the class of history and knowledge!")


@bot.command()
async def info(ctx):
    description = "Greetings, traveler of time and curiosity! I am Herodotus Bot, chronicler of deeds long past and seeker of tales untold. From the rise and fall of empires to the whispers of forgotten civilizations, I gather stories, legends, and truths, preserving them for all who wish to learn. Ask, and I shall recount the annals of history; probe, and I shall reveal the marvels of our shared past. Through me, the ages speak once more."

    embed = discord.Embed(
        title="Herodotus bot info",
        description=description,
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)


@bot.command()
async def figure(ctx, *args):
    historical_figure = "_".join(args)

    response = requests.get(WIKI_URL + historical_figure)

    if response.status_code == 200:
        data = response.json()

        title = data["title"]
        description = data["extract"]

        embed = discord.Embed(
            title=title,
            description=description
        )

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"I apologies, {ctx.author.mention}, but I cannot seem to find the historical "
                       f"figure you were looking for.")



bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)
