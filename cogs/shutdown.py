import discord
from discord.ext import commands


class Shutdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Shutdown cog loaded.")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.bot.close()


async def setup(bot):
    await bot.add_cog(Shutdown(bot))
