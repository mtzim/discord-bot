from typing import Union
import discord
from db_helper import SqlHelper as SQL
from discord.ext import commands, tasks
from discord import app_commands

# Channel edit rate limit twice per 10 minutes
class GuildMemberCount(commands.Cog):
    """
    A Cog containing commands and a task to set a guild channel to update periodically to display a guild's total member count.

    ...

    Attributes
    ----------
    bot : commands.Bot
        The discord bot

    Methods
    -------
    update_channel_member_count(guild)
        Formats the timezone to display
    set_member_count_channel_id(interaction,channel)
        Set a guild channel to display the guild's member count
    get_member_count_channel(interaction)
        Show the channel that is currently set to display the guild's member count
    update_member_count_task()
        Background task that updates a guild channel to reflect the total guild member count
    """

    def __init__(self, bot):
        self.bot = bot

    # called when the client is done preparing the data received from Discord
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: Guild Member Count loaded.")

        await self.update_member_count_task.start()

    # if the guild has a member count channel, update it
    async def update_channel_member_count(self, guild):
        """
        Updates a guild channel to reflect the total guild member count

        ...

        Parameters
        ----------
        guild : discord.Guild
            The guild that contains the channel to update
        """
        db = SQL()
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

    @app_commands.command(
        name="set_channel",
        description=f"Set a guild channel to display the guild's member count",
        extras={"module": "Config"},
    )
    @app_commands.describe(channel="[CHANNEL] guild channel to set")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def set_member_count_channel_id(
        self,
        interaction: discord.Interaction,
        channel: Union[discord.TextChannel, discord.VoiceChannel],
    ):
        """
        Set a guild channel to display the guild's member count

        ...

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction caused by a user performing a slash command
        channel : discord.TextChannel, discord.VoiceChannel
            The channel that will get edited to reflect the total member count
        """
        db = SQL()
        db.update_guild_channel_id(interaction.guild.id, channel.id)
        db.close()
        await interaction.response.send_message(
            f"Updated the channel id successfully, Member Count Channel Id: {channel.id}."
        )
        try:
            await channel.edit(name=f"Members - {len(interaction.guild.members)}")
        except discord.errors.Forbidden:
            await interaction.response.send_message(
                f"Bot doesn't have permission to edit the member count channel. (Channel: {channel.name}#{channel.id})"
            )

    @app_commands.command(
        name="get_channel",
        description=f"Show the channel that is currently set to display the guild's member count",
        extras={"module": "Config"},
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def get_member_count_channel(self, interaction: discord.Interaction):
        """
        Show the channel that is currently set to display the guild's member count

        ...

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction caused by a user performing a slash command
        """
        db = SQL()
        channel_id = db.get_guild_channel_id(interaction.guild.id)
        db.close()

        # check if a channel has been set
        if channel_id != None:
            channel = discord.utils.get(interaction.guild.channels, id=channel_id)

            # check if channel still exists in the guild
            if channel != None:
                await interaction.response.send_message(
                    f"Member count channel currently set to `{channel} (ID:{channel_id})`"
                )
            else:
                await interaction.response.send_message(
                    f"Channel no longer exists, please set a new one."
                )
        else:
            await interaction.response.send_message(f"No channel currently set.")

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
        """
        Background task that updates a guild channel to reflect the total guild member count
        """

        print(f"Running member count task...")
        # update member count for all guilds bot is connected to
        if len(self.bot.guilds) > 0:
            print(f"Updating member counts...")
            for guild in self.bot.guilds:
                await self.update_channel_member_count(guild)
            print(f"Finished updating.")


async def setup(bot):
    await bot.add_cog(GuildMemberCount(bot))
