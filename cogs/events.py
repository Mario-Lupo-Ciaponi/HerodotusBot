import discord
from discord.ext import commands
from discord.message import Message

from better_profanity import profanity

import difflib


profanity.load_censor_words()


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            await member.send(
                "Welcome, eager student! Together we shall journey through the annals of time, "
                "and from the deeds of mortals past, wisdom shall be gained."
            )
        except discord.Forbidden:
            print(f"Could not DM {member.name}, they might have DMs disabled.")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.bot.user:
            return

        if profanity.contains_profanity(message.content):
            await message.delete()
            await message.channel.send(
                f"Such words are unworthy of our discourse, my pupil! "
                f"In this hall of learning, we speak with dignity."
            )

    @commands.Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if profanity.contains_profanity(after.content):
            await after.delete()
            await after.channel.send(
                f"Lo! {after.author} sought to alter their words, yet their speech "
                f"was found impure! Before their edit, they declared: {before.content}"
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            all_commands = [cmd.name for cmd in self.bot.commands]
            closest = difflib.get_close_matches(ctx.message.content[1:], all_commands, n=1)
            suggestion = f" Did you mean `{closest[0]}`?" if closest else ""

            await ctx.send(
                f"Alas, {ctx.author.mention}, the command you seek is "
                f"not recorded among my chronicles! {suggestion}"
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Events(bot))
