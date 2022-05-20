import os
import discord
from discord.ext import commands


class GuildMemberCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # called when the client is done preparing the data received from Discord
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged into Discord as {self.bot.user} (ID: {self.bot.user.id})")

        # list all guilds bot is connected to
        if len(self.bot.guilds) > 0:
            print("Connected to the following guilds:")

            for count, guild in enumerate(self.bot.guilds):
                print(
                    f"{count+1}) {guild.name}#{guild.id} - Members: {len(guild.members)}"
                )
                await self.update_channel_member_count(guild)

    # called when a new member joins a guild
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member} joined {member.guild}.")
        await self.update_channel_member_count(member.guild)

    # called when a member leaves or gets removed from a guild
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f"{member} left {member.guild}.")
        await self.update_channel_member_count(member.guild)

    @commands.command(name="update")
    async def update_count_cmd(self, ctx):
        print(f"update channel count command called by {ctx.author}")
        await self.update_channel_member_count(ctx.guild, ctx)

    # if the guild has a member count channel, update it
    async def update_channel_member_count(self, guild, *args):
        channel_id = self.get_channel_id_member_count(guild)
        if channel_id != None:
            channel = discord.utils.get(guild.channels, id=channel_id)
            channel_name = f"Members - {len(guild.members)}"

            try:
                await channel.edit(name=channel_name)
            except discord.errors.Forbidden:
                if len(args) > 0:
                    if isinstance(args[0], discord.ext.commands.context.Context):
                        ctx = args[0]
                        await ctx.send(
                            f"I don't have permission to edit the member count channel for this server."
                        )
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


async def setup(bot):
    await bot.add_cog(GuildMemberCount(bot))
