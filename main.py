import random

import aiohttp
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from better_profanity import profanity
from discord.message import Message
import requests

import difflib


WIKI_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
HISTORICAL_FIGURE_URL = "https://api.api-ninjas.com/v1/historicalfigures?name="
EVENT_URL = "https://api.api-ninjas.com/v1/historicalevents?text="
QUOTE_URL = "https://philosophersapi.com/api/quotes"
PHILOSOPHER_URL = "https://philosophersapi.com/api/philosophers/"


profanity.load_censor_words()

load_dotenv()

bot_token = os.getenv("DISCORD_TOKEN")
history_token = os.getenv("HISTORY_TOKEN")


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


# <-------------- Start of helper functions -------------->

def build_historical_figure_embed(data, wiki_data):
    description = wiki_data["extract"][:4096]

    name = data["name"]
    title = data["title"]

    information = data["info"]

    born = information.get("born", "Unknown")
    died = information.get("died", "Unknown")
    house = information.get("house", "Unknown")
    reign = information.get("reign", "Unknown")
    dynasty = information.get("dynasty", "Unknown")
    religion = information.get("religion", "Unknown")
    successor = information.get("successor", "Unknown")
    coronation = information.get("coronation", "Unknown")

    embed = discord.Embed(
        title=name,
        description=description,
        color=discord.Color.blue()
    )

    embed.add_field(name="Title:", value=title, inline=False)
    embed.add_field(name="Born:", value=born, inline=False)
    embed.add_field(name="Died:", value=died, inline=False)
    embed.add_field(name="House:", value=house, inline=False)
    embed.add_field(name="Reign:", value=reign, inline=False)
    embed.add_field(name="Dynasty:", value=dynasty, inline=False)
    embed.add_field(name="Religion:", value=religion, inline=False)
    embed.add_field(name="Successor:", value=successor, inline=False)
    embed.add_field(name="Coronation:", value=coronation, inline=False)

    return embed

# <-------------- End of helper functions -------------->

# <-------------- Start of events -------------->

@bot.event
async def on_ready():

    print(f"Ready to merge in history...")

@bot.event
async def member_join(member):
    try:
        await member.send("Welcome, eager student! Together we shall journey through the annals of time, "
                          "and from the deeds of mortals past, wisdom shall be gained.")
    except discord.Forbidden:
        print(f"Could not DM {member.name}, they might have DMs disabled.")


@bot.event
async def on_message(message: Message):
    if message.author == bot.user.name:
        return

    if profanity.contains_profanity(message.content):
        await message.delete()
        await message.channel.send(f"Such words are unworthy of our discourse, my pupil! "
                                   f"In this hall of learning, we speak with dignity.")

    await bot.process_commands(message)


@bot.event
async def on_message_edit(before: Message, after: Message):
    if profanity.contains_profanity(after.content):
        await after.delete()
        await after.channel.send(f"Lo! {after.author} sought to alter their words, yet their speech "
                                 f"was found impure! Before their edit, they declared: {before.content}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        all_commands = [cmd.name for cmd in bot.commands]
        closest = difflib.get_close_matches(ctx.message.content[1:], all_commands, n=1)
        suggestion = f" Did you mean `{closest[0]}`?" if closest else ""

        await ctx.send(f"Alas, {ctx.author.mention}, the command you seek is "
                       f"not recorded among my chronicles! {suggestion}")
    else:
        raise error

# <-------------- End of events -------------->

# <-------------- Start of commands -------------->

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📜 HerodotusBot: Scroll of Commands",
        description="Behold, student of history! Here are the chronicles you may summon:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="!wave",
        value="Receive my salute across the ages!",
        inline=False
    )

    embed.add_field(
        name="!info",
        value="Learn the tale of me, your faithful chronicler.",
        inline=False
    )

    embed.add_field(
        name="!figure {name}",
        value="Uncover the deeds and legacy of a historical figure.",
        inline=False
    )

    embed.add_field(
        name="!event {name}",
        value="Explore a notable event from the annals of time.",
        inline=False
    )

    embed.add_field(
        name="!quote",
        value="Hear a fragment of wisdom plucked from history's pages.",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def wave(ctx):
    await ctx.send("Well met, dear student! You now enter the grand hall of history and knowledge, "
                   "where the deeds of ages past shall be your teachers.")


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
    historical_figure = " ".join(el.capitalize() for el in args)

    url = HISTORICAL_FIGURE_URL + historical_figure
    wiki_url = WIKI_URL + historical_figure

    wiki_response = requests.get(WIKI_URL + historical_figure)


    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'X-Api-Key': history_token}) as response:
            async with session.get(wiki_url) as wiki_response:
                datas = await response.json()

                if datas:
                    await ctx.send(f"Historical figures that match '{historical_figure}'")

                    for data in datas:
                        wiki_data = await wiki_response.json()

                        embed = build_historical_figure_embed(data, wiki_data)

                        await ctx.send(embed=embed)
                else:
                    await ctx.send(f"I must apologize, {ctx.author.mention}, for the chronicles hold no "
                                   f"record of the historical figure you seek.")


@bot.command()
async def event(ctx, *args):
    event_name = " ".join(args)
    url = EVENT_URL + event_name

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'X-Api-Key': history_token}) as response:
            if response.status != 200:
                await ctx.send(f"I must apologize, {ctx.author.mention}, for the annals reveal no record of "
                               f"the event known as '{event_name}'.")
                return

            events = await response.json()

    if not events:
        await ctx.send(f"I must apologize, {ctx.author.mention}, for the annals reveal no record of "
                       f"the event known as '{event_name}'.")
        return

    embed = discord.Embed(
        title=f"Events matching: {event_name}",
        color=discord.Color.blue()
    )

    for h_event in events[:5]:
        day = h_event.get("day", "?")
        month = h_event.get("month", "?")
        year = h_event.get("year", "?")

        try:
            year_int = int(year)
            if year_int >= 0:
                year_display = str(year_int)
            else:
                year_display = f"{abs(year_int)} BC"
        except (ValueError, TypeError):
            year_display = str(year)

        date = f"{day}/{month}/{year_display}"
        description = h_event.get("event", "No description available")
        embed.add_field(name=date, value=description, inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def quote(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(QUOTE_URL) as response:
            if response.status != 200:
                await ctx.send("Sorry, but I have a problem right now.. I am to old for this...")
                return

            quotes = await response.json()

        selected_quote = random.choice(quotes)

        async with session.get(PHILOSOPHER_URL + selected_quote["philosopher"]["id"]) as p_response:
            philosopher = await p_response.json()

    philosopher_name = philosopher["name"]
    description = selected_quote["quote"]

    embed = discord.Embed(
        title=f"Quote by {philosopher_name}",
        description=description,
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

bot.run(token=bot_token, log_handler=handler, log_level=logging.DEBUG)
