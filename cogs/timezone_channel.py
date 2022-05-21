import os
from datetime import datetime
import pytz
import discord
from discord.ext import commands


class ChannelTime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Channel Timezone Cog loaded.")

        if len(self.bot.guilds) > 0:
            for guild in self.bot.guilds:
                await self.update_time_channel(guild)

    async def update_time_channel(self, guild):
        channel_id = self.get_voice_channel_id(guild)
        if channel_id != None:
            channel = discord.utils.get(guild.channels, id=channel_id)
            channel_name = self.time_channel_name()

            try:
                await channel.edit(name=channel_name)
            except discord.errors.Forbidden:
                print(
                    f"Bot doesn't have permission to edit the Time channel. (Guild: {guild.name}#{guild.id}, Channel: {channel.name}#{channel_id})"
                )
        else:
            print(f"channel id not found, can't update Time for {guild}")

    def time_channel_name(self):
        jst_tz = datetime.now(pytz.timezone("Asia/Tokyo"))
        # %m/%d %H:%M %Z (MM/DD HH:MM TZ)
        return jst_tz.strftime("%m/%d %H:%M %Z")

    def get_voice_channel_id(self, guild):
        channel_id = os.getenv("TIME_CHANNEL")
        guild_id = os.getenv("GUILD_ID")

        if int(guild_id) == guild.id:
            return int(channel_id)

        return None


async def setup(bot):
    await bot.add_cog(ChannelTime(bot))
