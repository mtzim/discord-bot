from typing import Dict
import discord
from discord.ext import commands
import re

prune_help = """```asciidoc
        [Prune Help]

        =prune <Amount> - Prunes messages by the specified amount
        =prune --until <Message ID> - Prunes messages until the given message is reached

        Options:
            [--bots] - Prunes all messages created by any bot
            [--user <User>] - Prunes all messages by the specified user

            [--filter <Filter>] - Only prunes messages that contain the specified string

            [--attachments | -a] - Only prunes messages containing attachments (can be combined with --embeds)
            [--embeds | -e] - Only prunes messages containing embeds (can be combined with --attachments)
            [--pinned | -p] - Also prunes pinned messages (they are not pruned by default)
            [--invites | -i] - Only prunes messages containing Discord invites
            [--reactions | -r] - Only removes the reactions from the targeted messages instead of deleting them
            [--system] - Only removes system messages (Ignores -a, -e, -p, -i and -r)

            [--silent | -s] - Silent. Disables printing the prune results at the end

        Examples:
            =prune 10
            =prune -aes
            =prune --filter hello

        <> = required information, [] = optional information, | = or. Do not include <> [] or | in your command input.```"""


class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.has_guild_permissions(manage_messages=True, read_message_history=True)
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.command(help=f"{prune_help}")
    async def prune(self, ctx: commands.Context, *, msg: str):
        args = msg.split(" ")
        processed_args = {
            "amount": 0,
            "--until": "",
            "--bots": False,
            "--user": "",
            "--filter": "",
            "--attachments": False,
            "--embeds": False,
            "--pinned": False,
            "--invites": False,
            "--reactions": False,
            "--system": False,
            "--silent": False,
        }
        short_name_to_long = {
            "-a": "--attachments",
            "-e": "--embeds",
            "-p": "--pinned",
            "-i": "--invites",
            "-r": "--reactions",
            "-s": "--silent",
        }

        # Check args, flags, and make sure 1 mandatory option is set
        prev = None
        for arg in args:
            if (
                (arg.isdecimal())
                and (prev not in ("--until", "--user", "--filter"))
                and (processed_args["--until"] == "")
            ):
                processed_args["amount"] = int(arg)
            elif prev in ("--user", "--filter"):
                processed_args[prev] = arg
            elif (
                prev == "--until" and processed_args["amount"] == 0 and arg.isdecimal()
            ):
                processed_args[prev] = int(arg)
            elif arg in (
                "--attachments",
                "--embeds",
                "--pinned",
                "--invites",
                "--reactions",
                "--system",
                "--silent",
                "--bots",
            ):
                processed_args[arg] = True
            elif arg in (
                "-a",
                "-e",
                "-p",
                "-i",
                "-r",
                "-s",
            ):
                processed_args[short_name_to_long[arg]] = True
            elif arg in ("--until", "--user", "--filter"):
                pass  # would be prev = arg, but done at end anyway
            else:
                # combination flag (i.e. -aes -sea -seirp) or error
                # catch everything that doesn't start with `-` or isn't at least 2 char long (i.e. -a)
                if arg[0] != "-" or len(arg) < 2:
                    await ctx.reply(
                        f"Invalid syntax, missing -, refer to `?help prune` to see usage and definitions for this command."
                    )
                    return
                # remove '-' and split merged flags
                split_flags = list(arg[1:])
                for flag in split_flags:
                    # catch any flag passed that isn't a char in aepirs
                    if flag in ("a", "e", "p", "i", "r", "s"):
                        processed_args[short_name_to_long[f"-{flag}"]] = True
                    else:
                        await ctx.reply(
                            f"Invalid syntax, flag doesn't exist, refer to `?help prune` to see usage and definitions for this command."
                        )
                        return
            prev = arg

        # Mandatory option is missing
        if processed_args["--until"] == "" and processed_args["amount"] == 0:
            await ctx.reply(f"Mandatory options missing")
            return
        await self.prune_helper(processed_args, ctx)

    # Use the parsed arguments to process a set of messages
    async def prune_helper(self, processed_args: Dict, ctx: commands.Context):
        amount = processed_args["amount"]
        until = processed_args["--until"]
        bots = processed_args["--bots"]
        user = processed_args["--user"]
        filter = processed_args["--filter"]
        attachments = processed_args["--attachments"]
        embeds = processed_args["--embeds"]
        pinned = processed_args["--pinned"]
        invites = processed_args["--invites"]
        reactions = processed_args["--reactions"]
        system = processed_args["--system"]
        silent = processed_args["--silent"]

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
        if amount > 0:
            if not silent:
                msg_to_edit = await ctx.send(
                    f"Fetching {amount} messages, it may take awhile"
                )
                skip_first_msg = True
                add_no_chk = True
                msgs_to_del = []
                msgs_per_author = {}
                async for message in ctx.channel.history(limit=amount + 2):
                    if skip_first_msg or add_no_chk:
                        # exclude prune results from deletion and include command msg for deletion
                        if skip_first_msg:
                            skip_first_msg = False
                        else:
                            msgs_to_del.append(message)
                            add_no_chk = False
                        continue
                    if await purge_check(message):
                        msgs_to_del.append(message)
                        msgs_per_author = count_msgs(message.author, msgs_per_author)
            else:
                # Adjust limit for unprinted prune results
                add_no_chk = True
                msgs_to_del = []
                async for message in ctx.channel.history(limit=amount + 1):
                    if add_no_chk:
                        # include command msg for deletion
                        msgs_to_del.append(message)
                        add_no_chk = False
                        continue
                    if await purge_check(message):
                        msgs_to_del.append(message)

            if not silent:
                await msg_to_edit.edit(
                    content=f"Deleting {len(msgs_to_del)-1} messages, it may take awhile"
                )
            await ctx.channel.delete_messages(msgs_to_del)

            # Disable printing of prune results
            # Print out prune results after finished, disabled by -s
            if not silent:
                embed_stats = discord.Embed()
                embed_stats.set_author(name=f"Prune results")
                embed_stats.add_field(
                    name=f"Total messages deleted",
                    value=f"```apache\n{len(msgs_to_del)-1}```",
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
                await msg_to_edit.edit(
                    content=f"Done! Showing prune results below.",
                    embed=embed_stats,
                    delete_after=10,
                )
        else:
            try:
                msg = await ctx.channel.fetch_message(until)
            except discord.NotFound:
                await ctx.reply(
                    f"Message not found, check if the Message ID is correct and that the ID is from a message in this channel."
                )
                return

            msgs_per_author = {}
            if not silent:
                msg_to_edit = await ctx.send(f"Fetching messages, it may take awhile")
                skip_first_msg = True
                add_no_chk = True
                msgs_to_del = []

                async for message in ctx.channel.history(
                    limit=None, after=msg, oldest_first=False
                ):
                    if skip_first_msg or add_no_chk:
                        # exclude prune results from deletion and include command msg for deletion
                        # don't use check logic for the msgs added for deletion
                        if skip_first_msg:
                            skip_first_msg = False
                        else:
                            msgs_to_del.append(message)
                            add_no_chk = False
                        continue
                    if await purge_check(message):
                        msgs_to_del.append(message)
                        msgs_per_author = count_msgs(message.author, msgs_per_author)
            else:
                # Not printing prune results
                add_no_chk = True
                msgs_to_del = []
                async for message in ctx.channel.history(
                    limit=None, after=msg, oldest_first=False
                ):
                    if add_no_chk:
                        # include command msg for deletion
                        msgs_to_del.append(message)
                        add_no_chk = False
                        continue
                    if await purge_check(message):
                        msgs_to_del.append(message)

            # Include fetched msg for deletion if criteria met
            if await purge_check(msg):
                msgs_to_del.append(msg)
                msgs_per_author = count_msgs(msg.author, msgs_per_author)

            if not silent:
                await msg_to_edit.edit(
                    content=f"Deleting {len(msgs_to_del)-1} messages, it may take awhile"
                )
            await ctx.channel.delete_messages(msgs_to_del)

            # Disable printing of prune results
            # Print out prune results after finished, disabled by -s
            if not silent:
                embed_stats = discord.Embed()
                embed_stats.set_author(name=f"Prune results")
                embed_stats.add_field(
                    name=f"Total messages deleted",
                    value=f"```apache\n{len(msgs_to_del)-1}```",
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
                await msg_to_edit.edit(
                    content=f"Done! Showing prune results below.",
                    embed=embed_stats,
                    delete_after=10,
                )

    @prune.error
    async def prune_err(self, ctx, err):
        if type(err) == discord.ext.commands.errors.MissingRequiredArgument:
            await ctx.reply(
                f"One of the options out of `amount or until` is mandatory to process this command.\nTo see the usage and definitions of these options, you can run the command `?help prune`."
            )
        elif type(err) == discord.ext.commands.errors.BadArgument:
            await ctx.reply(
                f"Invalid syntax, refer to `?help prune` to see usage and definitions for this command."
            )
        elif type(err) == discord.ext.commands.errors.MissingPermissions:
            await ctx.reply(f"You lack the necessary permissions for this command.")
        elif type(err) == discord.ext.commands.errors.BotMissingPermissions:
            await ctx.reply(f"{err}")
        else:
            await ctx.send(f"Error: {type(err)}, {err}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
