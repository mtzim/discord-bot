from datetime import datetime
import pytz
import discord
from discord.ext import commands, tasks

# Presence rate limit once per 15 seconds
class PresenceTime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Channel Timezone Cog loaded.")
        self.update_time_task.start()

    def time_channel_name(self):
        jst_tz = datetime.now(pytz.timezone("Asia/Tokyo"))
        # %m/%d %H:%M %Z (MM/DD HH:MM TZ)
        return jst_tz.strftime("%m/%d, %H:%M %Z")

    @tasks.loop(seconds=20)
    async def update_time_task(self):
        print(f"Time task running...")

        presence_time = self.time_channel_name()
        game = discord.Game(presence_time)
        await self.bot.change_presence(activity=game)


async def setup(bot):
    await bot.add_cog(PresenceTime(bot))
