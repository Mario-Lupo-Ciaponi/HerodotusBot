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


WIKI_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
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
            description=description,
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"I apologies, {ctx.author.mention}, but I cannot seem to find the historical "
                       f"figure you were looking for.")


@bot.command()
async def event(ctx, *args):
    event_name = " ".join(args)
    url = EVENT_URL + event_name

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'X-Api-Key': history_token}) as response:
            if response.status != 200:
                await ctx.send(f"I apologies, {ctx.author.mention}, but I cannot seem to find the event '{event_name}'")
                return

            events = await response.json()

    if not events:
        await ctx.send(f"No events found for '{event_name}'")
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
    response = requests.get(QUOTE_URL)

    if response.status_code != 200:
        await ctx.send("Sorry, but I have a problem right now.. I am to old for this...")
        return

    quotes = response.json()

    selected_quote = random.choice(quotes)

    p_response = requests.get(phylosopher_url + selected_quote["philosopher"]["id"])

    philosopher = p_response.json()

    philosopher_name = philosopher["name"]
    description = selected_quote["quote"]

    embed = discord.Embed(
        title=f"Quote by {philosopher_name}",
        description=description,
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

bot.run(token=bot_token, log_handler=handler, log_level=logging.DEBUG)
