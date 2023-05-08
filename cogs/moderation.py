import os
from typing import Dict, Optional
import discord
from discord import app_commands
from discord.ext import commands
import re


class Moderation(commands.Cog):
    """
    A Cog that contains moderation commands.

    ...

    Attributes
    ----------
    bot : commands.Bot
        The discord bot

    Methods
    -------
    prune(interaction,amount,attachments,bots,embeds,filter,invites,pinned,reactions,silent,system,until,user)
        Message Pruning
    prune_helper(interaction,amount,attachments,bots,embeds,filter,invites,pinned,reactions,silent,system,until,user)
        A helper that handles message pruning logic based on the parameters that were supplied
    """

    MODULE_NAME = {
        "module": f"{os.path.splitext(os.path.basename(__file__))[0].capitalize()}"
    }

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: {self.MODULE_NAME['module']} loaded.")

    @app_commands.command(
        description=f"Message Pruning",
        extras=MODULE_NAME,
    )
    @app_commands.describe(
        amount="[INTEGER] Prunes messages by the specified amount",
        attachments="[BOOLEAN] Only prunes messages containing attachments",
        bots="[BOOLEAN] Prunes all messages created by any bot",
        embeds="[BOOLEAN] Only prunes messages containing embeds",
        filter="[STRING] Only prunes messages that contain the specified string",
        invites="[BOOLEAN] Only prunes messages containing Discord invites",
        pinned="[BOOLEAN] Also prunes pinned messages (they are not pruned by default)",
        reactions="[BOOLEAN] Only removes the reactions from the targeted messages instead of deleting them",
        silent="[BOOLEAN] Silent. Disables printing the prune results at the end",
        system="[BOOLEAN] Only removes system messages",
        until="[STRING] Prunes messages until the given message is reached",
        user="[USER] Prunes all messages by the specified user",
    )
    @app_commands.checks.has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    async def prune(
        self,
        interaction: discord.Interaction,
        amount: Optional[int] = None,
        attachments: Optional[bool] = False,
        bots: Optional[bool] = False,
        embeds: Optional[bool] = False,
        filter: Optional[str] = None,
        invites: Optional[bool] = False,
        pinned: Optional[bool] = False,
        reactions: Optional[bool] = False,
        silent: Optional[bool] = False,
        system: Optional[bool] = False,
        until: Optional[str] = None,
        user: Optional[discord.User] = None,
    ):
        """
        Message Pruning

        ...

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction caused by a user performing a slash command
        amount: int, optional, default=None
            Prunes messages by the specified amount
        attachments: bool, optional, default=False
            Only prunes messages containing attachments
        bots: bool, optional, default=False
            Prunes all messages created by any bot
        embeds: bool, optional, default=False
            Only prunes messages containing embeds
        filter: str, optional, default=None
            Only prunes messages that contain the specified string
        invites: bool, optional, default=False
            Only prunes messages containing Discord invites
        pinned: bool, optional, default=False
            Also prunes pinned messages (they are not pruned by default)
        reactions: bool, optional, default=False
            Only removes the reactions from the targeted messages instead of deleting them
        silent: bool, optional, default=False
            Silent. Disables printing the prune results at the end
        system: bool, optional, default=False
            Only removes system messages
        until: str, optional, default=None
            Prunes messages until the given message is reached
        user: discord.User, optional, default=None
            Prunes all messages by the specified user
        """
        # Mandatory option is missing
        if not until and not amount:
            await interaction.response.send_message(
                f"One of the option out of `amount or until` is mandatory to process this command. To see the usage and definitions of these options, you can run the command `help prune`."
            )
            return
        await self.prune_helper(
            interaction,
            amount,
            attachments,
            bots,
            embeds,
            filter,
            invites,
            pinned,
            reactions,
            silent,
            system,
            until,
            user,
        )

    # Use the parsed arguments to process a set of messages
    async def prune_helper(
        self,
        interaction: discord.Interaction,
        amount: int,
        attachments: bool,
        bots: bool,
        embeds: bool,
        filter: str,
        invites: bool,
        pinned: bool,
        reactions: bool,
        silent: bool,
        system: bool,
        until: str,
        user: discord.User,
    ):
        """
        A helper that handles message pruning logic based on the parameters that were supplied

        ...

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction caused by a user performing a slash command
        amount: int, optional, default=None
            Prunes messages by the specified amount
        attachments: bool, optional, default=False
            Only prunes messages containing attachments
        bots: bool, optional, default=False
            Prunes all messages created by any bot
        embeds: bool, optional, default=False
            Only prunes messages containing embeds
        filter: str, optional, default=None
            Only prunes messages that contain the specified string
        invites: bool, optional, default=False
            Only prunes messages containing Discord invites
        pinned: bool, optional, default=False
            Also prunes pinned messages (they are not pruned by default)
        reactions: bool, optional, default=False
            Only removes the reactions from the targeted messages instead of deleting them
        silent: bool, optional, default=False
            Silent. Disables printing the prune results at the end
        system: bool, optional, default=False
            Only removes system messages
        until: str, optional, default=None
            Prunes messages until the given message is reached
        user: discord.User, optional, default=None
            Prunes all messages by the specified user
        """
        # find the substr in the str
        def contains_str(filter: str, content: str) -> bool:
            # if filter found in content, return True
            # matching whole worlds, content.find(filter) != -1 for any occurance
            if filter in content.split():
                return True
            return False

        # find the substr pattern in the str
        def contains_invites(content: str) -> bool:
            # if invite link found, return True
            invite_filter = re.compile(
                r"(https:\/\/)?(www\.)?(discord\.gg|discord\.me|discordapp\.com\/invite|discord\.com\/invite)\/([a-z0-9-.]+)?",
                re.I,
            )
            if invite_filter.search(content):
                return True
            return False

        # count how many messages deleted per user
        def count_msgs(name, cnt) -> Dict:
            if name not in cnt:
                cnt[name] = 1
                return cnt
            cnt[name] += 1
            return cnt

        # format message count into printable string
        def del_by_user(total_by_user: Dict) -> str:
            fmt = []
            for item in total_by_user.items():
                fmt.append(f"{item[0]} : {item[1]}")
            to_print = "\n".join(fmt)
            return to_print

        # Core logic for prune command
        async def purge_check(msg: discord.Message):
            # Delete only system messages, ignore AEPIR(treat AEPIR as False)
            if system == True and msg.is_system() == True and msg.pinned == False:
                # only delete system messages, ignore pinned, can be combined with user/bot/filter
                return True
            # Delete if flag and conditions met
            elif (
                bots or user or filter or attachments or embeds or invites or reactions
            ):
                if bots and msg.author.bot and not reactions:
                    if msg.pinned == True and pinned == False:
                        return False
                    return True
                if user and user == msg.author.mention and not reactions:
                    if msg.pinned == True and pinned == False:
                        return False
                    return True
                if filter and contains_str(filter, msg.content) and not reactions:
                    if msg.pinned == True and pinned == False:
                        return False
                    return True
                if attachments and (len(msg.attachments) > 0) and not reactions:
                    if msg.pinned == True and pinned == False:
                        return False
                    return True
                if embeds and (len(msg.embeds) > 0) and not reactions:
                    if msg.pinned == True and pinned == False:
                        return False
                    return True
                if invites and contains_invites(msg.content) and not reactions:
                    if msg.pinned == True and pinned == False:
                        return False
                    return True
                if reactions:
                    await msg.clear_reactions()
                return False
            # Regular message or no flags set
            elif msg.pinned == True and pinned == False:
                return False
            else:
                return True

        # Get the set of messages to delete from --until or amount, excluding pinned by default: until ID error(Message doesn't exist in this channel)
        if amount:
            if not silent:
                await interaction.response.send_message(
                    f"Fetching {amount} messages, it may take awhile"
                )
                skip_first_msg = True
                msgs_to_del = []
                msgs_per_author = {}
                async for message in interaction.channel.history(limit=amount + 1):
                    if skip_first_msg:
                        # exclude prune results from deletion and include command msg for deletion
                        skip_first_msg = False
                        continue
                    if await purge_check(message):
                        msgs_to_del.append(message)
                        msgs_per_author = count_msgs(message.author, msgs_per_author)
            else:
                # Adjust limit for unprinted prune results
                msgs_to_del = []
                async for message in interaction.channel.history(limit=amount):
                    if await purge_check(message):
                        msgs_to_del.append(message)

            if not silent:
                await interaction.edit_original_response(
                    content=f"Deleting {len(msgs_to_del)} messages, it may take awhile"
                )
            await interaction.channel.delete_messages(msgs_to_del)

            # Disable printing of prune results
            # Print out prune results after finished, disabled by -s
            if not silent:
                embed_stats = discord.Embed()
                embed_stats.set_author(name=f"Prune results")
                embed_stats.add_field(
                    name=f"Total messages deleted",
                    value=f"```apache\n{len(msgs_to_del)}```",
                    inline=False,
                )
                embed_stats.add_field(
                    name=f"Deleted messages by user",
                    value=f"```apache\n{del_by_user(msgs_per_author)}```",
                    inline=False,
                )
                embed_stats.set_footer(
                    text=f"Autodelete is enabled. This message will be deleted after 10 seconds."
                )
                msg_to_del = await interaction.edit_original_response(
                    content=f"Done! Showing prune results below.", embed=embed_stats
                )
                await msg_to_del.delete(delay=10)
        else:
            try:
                msg = await interaction.channel.fetch_message(until)
            except discord.NotFound:
                await interaction.response.send_message(
                    f"The message id that was used in the until option could not be found in this channel."
                )
                return

            msgs_per_author = {}
            if not silent:
                await interaction.response.send_message(
                    f"Fetching messages, it may take awhile"
                )
                skip_first_msg = True
                msgs_to_del = []

                async for message in interaction.channel.history(
                    limit=None, after=msg, oldest_first=False
                ):
                    if skip_first_msg:
                        # exclude prune results from deletion and include command msg for deletion
                        # don't use check logic for the msgs added for deletion
                        skip_first_msg = False
                        continue

                    if await purge_check(message):
                        msgs_to_del.append(message)
                        msgs_per_author = count_msgs(message.author, msgs_per_author)
            else:
                # Not printing prune results
                msgs_to_del = []
                async for message in interaction.channel.history(
                    limit=None, after=msg, oldest_first=False
                ):
                    if await purge_check(message):
                        msgs_to_del.append(message)

            # Include fetched msg for deletion if criteria met
            if await purge_check(msg):
                msgs_to_del.append(msg)
                msgs_per_author = count_msgs(msg.author, msgs_per_author)

            if not silent:
                await interaction.edit_original_response(
                    content=f"Deleting {len(msgs_to_del)} messages, it may take awhile"
                )
            await interaction.channel.delete_messages(msgs_to_del)

            # Disable printing of prune results
            # Print out prune results after finished, disabled by -s
            if not silent:
                embed_stats = discord.Embed()
                embed_stats.set_author(name=f"Prune results")
                embed_stats.add_field(
                    name=f"Total messages deleted",
                    value=f"```apache\n{len(msgs_to_del)}```",
                    inline=False,
                )
                embed_stats.add_field(
                    name=f"Deleted messages by user",
                    value=f"```apache\n{del_by_user(msgs_per_author)}```",
                    inline=False,
                )
                embed_stats.set_footer(
                    text=f"Autodelete is enabled. This message will be deleted after 10 seconds."
                )
                msg_to_del = await interaction.edit_original_response(
                    content=f"Done! Showing prune results below.", embed=embed_stats
                )
                await msg_to_del.delete(delay=10)

    @prune.error
    async def prune_err(self, interaction: discord.Interaction, error):
        if type(error) == app_commands.MissingPermissions:
            await interaction.response.send_message(
                f"You lack the necessary permissions for this command. You need to be able to `manage messages` and `read message history`."
            )
        elif type(error) == app_commands.BotMissingPermissions:
            await interaction.response.send_message(
                f"I lack the necessary permissions for this command. I need to be able to `manage messages` and `read message history`."
            )
        else:
            await interaction.response.send_message(f"Error: {type(error)}, {error}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
