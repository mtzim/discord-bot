import os
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

    MODULE_NAME = {
        "module": f"{os.path.splitext(os.path.basename(__file__))[0].capitalize()}"
    }

    def __init__(self, bot):
        self.bot = bot

    # called when the client is done preparing the data received from Discord
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: {self.MODULE_NAME['module']} loaded.")

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

    membercount_group = app_commands.Group(
        name="membercount",
        description="Manage server member count channel",
        extras=MODULE_NAME,
    )

    @membercount_group.command(
        name="set",
        description="Set a guild channel to display the guild's member count",
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

    @membercount_group.command(
        name="view",
        description="Show the channel that is currently set to display the guild's member count",
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

    prefix_group = app_commands.Group(
        name="prefix", description="Manage command prefix", extras=MODULE_NAME
    )

    @prefix_group.command(name="set", description="Set Prefix")
    @app_commands.describe(prefix="[STRING] New Prefix")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_prefix(self, interaction: discord.Interaction, prefix: str):
        """
        Set Prefix

        ...

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction caused by a user performing a slash command
        prefix : str
            A guild's new prefix
        """
        db = SQL()
        if not db.set_prefix(interaction.guild_id, prefix):
            await interaction.response.send_message(f"Unable to change prefix.")
        else:
            await interaction.response.send_message(
                f"Prefix successfully changed to `{prefix}`"
            )
        db.close()

    @prefix_group.command(name="view", description="View Prefix")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def view_prefix(self, interaction: discord.Interaction):
        """
        View Prefix

        ...

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction caused by a user performing a slash command
        """
        db = SQL()
        prefix = db.get_prefix(interaction.guild_id)
        if not prefix:
            await interaction.response.send_message(f"Unable to retrieve prefix.")
        else:
            await interaction.response.send_message(
                f"Prefix currently set to `{prefix}`"
            )
        db.close()

    @view_prefix.error
    @set_prefix.error
    async def prefix_error(self, interaction: discord.Interaction, error):
        if type(error) == app_commands.MissingPermissions:
            await interaction.response.send_message(
                f"You lack the necessary permissions for this command. You need to be able to `manage guild`."
            )
        else:
            await interaction.response.send_message(f"Error: {type(error)}, {error}")

    @get_member_count_channel.error
    @set_member_count_channel_id.error
    async def member_count_cmd_error(self, interaction: discord.Interaction, error):
        if type(error) == app_commands.MissingPermissions:
            await interaction.response.send_message(
                f"You lack the necessary permissions for this command. You need to be able to `manage channels`."
            )
        else:
            await interaction.response.send_message(f"Error: {type(error)}, {error}")

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
