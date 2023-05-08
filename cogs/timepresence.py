import os
from datetime import datetime
import pytz
import discord
from discord.ext import commands, tasks

# Presence rate limit once per 15 seconds
class TimePresence(commands.Cog):
    """
    A Cog that contains a background task that updates the Bot's presence with a time from a designated timezone.

    ...

    Attributes
    ----------
    bot : commands.Bot
        The discord bot

    Methods
    -------
    time_channel_name()
        Formats the timezone to display
    update_time_task()
        Updates the bot's presence with the formatted timezone
    """

    MODULE_NAME = {
        "module": f"{os.path.splitext(os.path.basename(__file__))[0].capitalize()}"
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: {self.MODULE_NAME['module']} loaded.")
        self.update_time_task.start()

    def time_channel_name(self):
        jst_tz = datetime.now(pytz.timezone("Asia/Tokyo"))
        # %m/%d %H:%M %Z (MM/DD HH:MM TZ)
        return jst_tz.strftime("%m/%d, %H:%M %Z")

    @tasks.loop(seconds=20)
    async def update_time_task(self):
        # print(f"Time task running...")

        presence_time = self.time_channel_name()
        game = discord.Game(presence_time)
        await self.bot.change_presence(activity=game)


async def setup(bot):
    await bot.add_cog(TimePresence(bot))
