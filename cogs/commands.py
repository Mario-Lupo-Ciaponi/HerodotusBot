import time

import discord
from discord.ext import commands
import random
from utils.cache import JSONCache
from utils.helper_functions import build_historical_figure_embed, build_event_embed
import aiohttp
import os

from datetime import date


WIKI_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
HISTORICAL_FIGURE_URL = "https://api.api-ninjas.com/v1/historicalfigures?name="
EVENT_URL = "https://api.api-ninjas.com/v1/historicalevents?"
QUOTE_URL = "https://philosophersapi.com/api/quotes"
PHILOSOPHER_URL = "https://philosophersapi.com/api/philosophers/"


history_token = os.getenv("HISTORY_TOKEN")


quote_cache = JSONCache("quotes.json", ttl=60*5)


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="📜 HerodotusBot: Scroll of Commands",
            description="Behold, student of history! Here are the chronicles you may summon:",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="!wave", value="Receive my salute across the ages!", inline=False
        )

        embed.add_field(
            name="!info",
            value="Learn the tale of me, your faithful chronicler.",
            inline=False,
        )

        embed.add_field(
            name="!figure {name}",
            value="Uncover the deeds and legacy of a historical figure.",
            inline=False,
        )

        embed.add_field(
            name="!event {name}",
            value="Explore a notable event from the annals of time.",
            inline=False,
        )

        embed.add_field(
            name="!quote",
            value="Hear a fragment of wisdom plucked from history's pages.",
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def wave(self, ctx):
        await ctx.send(
            "Well met, dear student! You now enter the grand hall of history and knowledge, "
            "where the deeds of ages past shall be your teachers."
        )

    @commands.command()
    async def info(self, ctx):
        description = "Greetings, traveler of time and curiosity! I am Herodotus Bot, chronicler of deeds long past and seeker of tales untold. From the rise and fall of empires to the whispers of forgotten civilizations, I gather stories, legends, and truths, preserving them for all who wish to learn. Ask, and I shall recount the annals of history; probe, and I shall reveal the marvels of our shared past. Through me, the ages speak once more."

        embed = discord.Embed(
            title="Herodotus bot info", description=description, color=discord.Color.red()
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def figure(self, ctx, *args):
        historical_figure = " ".join(el.capitalize() for el in args)

        url = HISTORICAL_FIGURE_URL + historical_figure

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"X-Api-Key": history_token}) as response:
                datas = await response.json()

                if datas:
                    await ctx.send(
                        f"Historical figures that match '{historical_figure}'"
                    )

                    for data in datas:
                        async with session.get(WIKI_URL + data["name"]) as wiki_response:
                            wiki_data = await wiki_response.json()

                            embed = build_historical_figure_embed(data, wiki_data)

                            await ctx.send(embed=embed)
                else:
                    await ctx.send(
                        f"I must apologize, {ctx.author.mention}, for the chronicles hold no "
                        f"record of the historical figure you seek."
                    )

    @commands.command()
    async def event(self, ctx, *args):
        event_name = " ".join(args)
        url = f"{EVENT_URL}text={event_name}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"X-Api-Key": history_token}) as response:
                if response.status != 200:
                    await ctx.send(
                        f"I must apologize, {ctx.author.mention}, for the annals reveal no record of "
                        f"the event known as '{event_name}'."
                    )
                    return

                events = await response.json()

        if not events:
            await ctx.send(
                f"I must apologize, {ctx.author.mention}, for the annals reveal no record of "
                f"the event known as '{event_name}'."
            )
            return

        embed = discord.Embed(
            title=f"Events matching: {event_name}", color=discord.Color.blue()
        )

        embed = build_event_embed(events, embed)

        await ctx.send(embed=embed)

    @commands.command()
    async def today_in_history(self, ctx):
        today_date = date.today()

        year, month, day = today_date.year, today_date.month, today_date.day

        url = f"{EVENT_URL}year={year}&month={month}&day={day}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"X-Api-Key": history_token}) as response:
                events = await response.json()

                if not events:
                    await ctx.send(
                        f"I must apologize, {ctx.author.mention}, today no event happened."
                    )
                    return

                embed = discord.Embed(
                    title="Events today:"
                )

                embed = build_event_embed(events, embed)

                await ctx.send(embed=embed)

    @commands.command()
    async def quote(self, ctx):
        quotes = quote_cache.load()

        if not quotes:
            async with aiohttp.ClientSession() as session:
                async with session.get(QUOTE_URL) as response:
                    if response.status != 200:
                        await ctx.send(
                            "Sorry, but I have a problem right now.. I am to old for this..."
                        )
                        return

                    quotes = await response.json()
                    quote_cache.save(quotes)

        selected_quote = random.choice(quotes)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    PHILOSOPHER_URL + selected_quote["philosopher"]["id"]
            ) as p_response:
                philosopher = await p_response.json()

        philosopher_name = philosopher["name"]
        description = selected_quote["quote"]

        embed = discord.Embed(
            title=f"Quote by {philosopher_name}",
            description=description,
            color=discord.Color.blue(),
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Commands(bot))
