import discord
from db import SqlDatabase as SQL
from discord.ext import commands, tasks

# Channel edit rate limit twice per 10 minutes
class GuildMemberCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SQL("example.db")

    # called when the client is done preparing the data received from Discord
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: Guild Member Count loaded.")

        await self.update_member_count_task.start()

    # if the guild has a member count channel, update it
    async def update_channel_member_count(self, guild):
        channel_id = self.db.get_guild_channel_id(guild.id)

        if channel_id != None:
            channel = discord.utils.get(guild.channels, id=channel_id)
            channel_name = f"Members - {len(guild.members)}"

            # Don't waste an api call if the name doesn't need changing
            if channel.name != channel_name:
                try:
                    await channel.edit(name=channel_name)
                except discord.errors.Forbidden:
                    print(
                        f"Bot doesn't have permission to edit the member count channel. (Guild: {guild.name}#{guild.id}, Channel: {channel.name}#{channel_id})"
                    )
                except discord.errors.HTTPException:
                    print(f"HTTPException, most likely being rate limited...")
        else:
            print(f"channel id not found, can't update member count for {guild}")

    @commands.command(name="set_channel", help="Usage: `?set_channel <CHANNEL ID>`")
    @commands.is_owner()
    async def set_member_count_channel_id(self, ctx, message: int):
        # look at invoking command and get chid from it
        channel_id = message
        channel = discord.utils.get(ctx.guild.channels, id=channel_id)
        # check if channel exists
        # short circuit
        if (channel != None) and (channel_id == channel.id):
            self.db.update_guild_channel_id(ctx.guild.id, channel.id)
            await ctx.reply(
                f"Updated the channel id successfully, Member Count Channel Id: {channel.id}."
            )
            try:
                await channel.edit(name=f"Members - {len(ctx.guild.members)}")
            except discord.errors.Forbidden:
                await ctx.send(
                    f"Bot doesn't have permission to edit the member count channel. (Channel: {channel.name}#{channel_id})"
                )

        else:
            await ctx.reply(
                "Channel Id not found within this server, please try again."
            )

    @set_member_count_channel_id.error
    async def set_member_count_cmd_error(self, ctx, err):
        if type(err) == discord.ext.commands.errors.MissingRequiredArgument:
            await ctx.reply(
                "Invalid format - Try: [prefix]set_channel [CHANNEL_ID]\nChannel ID should be a valid ID for an already existing channel within the server."
            )
        elif type(err) == discord.ext.commands.errors.BadArgument:
            await ctx.reply("Invalid Channel id, please make sure it's an integer.")
        else:
            await ctx.send(f"Error: {type(err)}, {err}")

    # Set accordingly to avoid rate limit (2 per 10 minutes)
    @tasks.loop(minutes=6)
    async def update_member_count_task(self):
        # print(f"Updating member counts...")

        # update member count for all guilds bot is connected to
        if len(self.bot.guilds) > 0:
            for guild in self.bot.guilds:
                await self.update_channel_member_count(guild)


async def setup(bot):
    await bot.add_cog(GuildMemberCount(bot))
