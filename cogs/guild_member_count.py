import os
import discord
from discord.ext import commands, tasks

# Channel edit rate limit twice per 10 minutes
class GuildMemberCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # called when the client is done preparing the data received from Discord
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged into Discord as {self.bot.user} (ID: {self.bot.user.id})")

        await self.update_member_count_task.start()

    # if the guild has a member count channel, update it
    async def update_channel_member_count(self, guild):
        channel_id = self.get_channel_id_member_count(guild)
        if channel_id != None:
            channel = discord.utils.get(guild.channels, id=channel_id)
            channel_name = f"Members - {len(guild.members)}"

            try:
                await channel.edit(name=channel_name)
            except discord.errors.Forbidden:
                print(
                    f"Bot doesn't have permission to edit the member count channel. (Guild: {guild.name}#{guild.id}, Channel: {channel.name}#{channel_id})"
                )
        else:
            print(f"channel id not found, can't update member count for {guild}")

    """ return guild's channel id to edit if guild has a designated channel to edit,
    in the future try and use a database to keep track of designated channels within
    different guilds """

    def get_channel_id_member_count(self, guild):
        channel_id = os.getenv("GUILD_CHANNEL")
        guild_id = os.getenv("GUILD_ID")

        if int(guild_id) == guild.id:
            return int(channel_id)

        return None

    # 6 minutes to avoid rate limit (2 per 10 minutes)
    @tasks.loop(minutes=6)
    async def update_member_count_task(self):
        print(f"Updating member counts...")

        # list all guilds bot is connected to
        if len(self.bot.guilds) > 0:
            print("Connected to the following guilds:")

            for count, guild in enumerate(self.bot.guilds):
                print(
                    f"{count+1}) {guild.name}#{guild.id} - Members: {len(guild.members)}"
                )
                await self.update_channel_member_count(guild)


async def setup(bot):
    await bot.add_cog(GuildMemberCount(bot))
