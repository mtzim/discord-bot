import discord
from db_helper import SqlHelper as SQL
from discord.ext import commands, tasks

# Channel edit rate limit twice per 10 minutes
class GuildMemberCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # called when the client is done preparing the data received from Discord
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: Guild Member Count loaded.")

        await self.update_member_count_task.start()

    # if the guild has a member count channel, update it
    async def update_channel_member_count(self, guild):
        db = SQL("discord_bot_data")
        channel_id = db.get_guild_channel_id(guild.id)
        db.close()

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
    @commands.has_guild_permissions(manage_channels=True)
    async def set_member_count_channel_id(self, ctx, message: int):
        # look at invoking command and get chid from it
        channel_id = message
        channel = discord.utils.get(ctx.guild.channels, id=channel_id)

        # check if channel exists
        if channel != None:
            db = SQL("discord_bot_data")
            db.update_guild_channel_id(ctx.guild.id, channel.id)
            db.close()
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

    @commands.command(name="get_channel", help="Usage: `?get_channel`")
    @commands.has_guild_permissions(manage_channels=True)
    async def get_member_count_channel(self, ctx: commands.Context):
        db = SQL("discord_bot_data")
        channel_id = db.get_guild_channel_id(ctx.guild.id)
        db.close()

        # check if a channel has been set
        if channel_id != None:
            channel = discord.utils.get(ctx.guild.channels, id=channel_id)

            # check if channel still exists in the guild
            if channel != None:
                await ctx.reply(
                    f"Member count channel currently set to `{channel} (ID:{channel_id})`"
                )
            else:
                await ctx.reply(f"Channel no longer exists, please set a new one.")
        else:
            await ctx.reply(f"No channel currently set.")

    @get_member_count_channel.error
    @set_member_count_channel_id.error
    async def member_count_cmd_error(self, ctx, err):
        if type(err) == discord.ext.commands.errors.MissingRequiredArgument:
            await ctx.reply(
                f"Invalid format - Try: `?set_channel <CHANNEL ID>`\nChannel ID should be a valid ID for an already existing channel within the server."
            )
        elif type(err) == discord.ext.commands.errors.BadArgument:
            await ctx.reply(f"Invalid Channel id, please make sure it's an integer.")
        elif type(err) == discord.ext.commands.errors.MissingPermissions:
            await ctx.reply(f"You lack the necessary permissions for this command.")
        else:
            await ctx.send(f"Error: {type(err)}, {err}")

    # Set accordingly to avoid rate limit (2 per 10 minutes)
    @tasks.loop(minutes=6)
    async def update_member_count_task(self):
        print(f"Updating member counts...")

        # update member count for all guilds bot is connected to
        if len(self.bot.guilds) > 0:
            for guild in self.bot.guilds:
                await self.update_channel_member_count(guild)


async def setup(bot):
    await bot.add_cog(GuildMemberCount(bot))
