import os
import logging
import discord
from discord import Message, Intents, Guild
from db_helper import SqlHelper as SQL
from dotenv import load_dotenv
from typing import Union, Literal, Optional
from discord.ext import commands
from discord.ext.commands import Greedy, Context


class CustomBot(commands.Bot):
    """
    Represents a custom Discord bot.

    ...

    Attributes
    ----------
    initial_extensions : List
        List of Cogs to load
    help_dict : Dict
        Dictionary that contains all categories as a key and commands that belong to that category as a value

    Methods
    -------
    get_prefix(message)
        Retreives the prefix that's stored in the database for non-slash commands
    setup_hook()
        Loads all of the cogs stored in initial_extensions
    close()
        Closes the Bot's connection to Discord
    on_ready()
        Ensures that all guild information contained in the database is in sync with all guilds the Bot is a member of
    on_guild_join(guild)
        Add a guild's name and id to the database when the Bot joins or creates a guild
    on_guild_remove(guild)
        Removes a guild's entry from the database when a guild is removed from the Bot
    on_guild_update(before,after)
        Updates the guild name in the database to match the server's guild name if it changes
    """

    def __init__(self, *args, **kwargs):

        if "intents" not in kwargs:
            intents = Intents.all()
            kwargs["intents"] = intents

        # Default prefix is assigned during database table creation
        if "command_prefix" not in kwargs:
            kwargs["command_prefix"] = self.get_prefix

        super().__init__(*args, help_command=None, **kwargs)

        self.initial_extensions = [
            "cogs.timepresence",
            "cogs.config",
            "cogs.utility",
            "cogs.moderation",
            "cogs.general",
            "cogs.chatbot",
        ]

        self.help_dict = {}

    async def get_prefix(self, message: Message, /) -> Union[str, None]:
        """
        Retreives the prefix that's stored in the database for non-slash commands

        ...

        Parameters
        ----------
        message : discord.Message
            The message context to get the prefix of

        Returns
        -------
        prefix : str, None
            A prefix that the bot is listening for
        """
        db = SQL()
        prefix = db.get_prefix(message.guild.id)
        db.close()
        return prefix

    async def setup_hook(self):
        """
        Loads all of the cogs stored in initial_extensions
        """
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def close(self):
        """
        Closes the Bot's connection to Discord
        """
        await super().close()

    async def on_ready(self):
        """
        Ensures that all guild information contained in the database is in sync with all guilds the Bot is a member of
        """

        print(f"Logged into Discord as {self.user} (ID: {self.user.id})")

        if len(self.guilds) > 0:
            print("Connected to the following guilds:")

            guilds_in = self.guilds
            for count, guild in enumerate(guilds_in):
                print(
                    f"{count+1}) {guild.name}#{guild.id} - Members: {len(guild.members)}"
                )
                db = SQL()
                db.add_guild(guild.name, guild.id)

            db.check_guilds_remove(guilds_in)
            db.close()

    async def on_guild_join(self, guild: Guild):
        """
        Add a guild's name and id to the database when the Bot joins or creates a guild

        ...

        Parameters
        ----------
        guild : discord.Guild
            The guild that was joined
        """
        db = SQL()
        db.add_guild(guild.name, guild.id)
        db.close()

    async def on_guild_remove(self, guild: Guild):
        """
        Removes a guild's entry from the database when a guild is removed from the Bot

        ...

        Parameters
        ----------
        guild : discord.Guild
            The guild that got removed
        """
        db = SQL()
        db.delete_guild(guild.id)
        db.close()

    async def on_guild_update(self, before: Guild, after: Guild):
        """
        Updates the guild name in the database to match the server's guild name if it changes

        ...

        Parameters
        ----------
        before : discord.Guild
            The guild prior to being updated
        after : discord.Guild
            The guild after being updated
        """
        if before.name != after.name:
            db = SQL()
            db.update_guild_name(after.name, after.id)
            db.close()


# Setup logging
if not os.path.exists("./logs"):
    os.makedirs("./logs")
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="./logs/discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

# Load data from .env file
load_dotenv()


def load_commands(bot: commands.Bot):
    """
    Load default commands

    ...

    Parameters
    ----------
    bot : commands.Bot
        A custom Discord Bot
    """

    @bot.command(hidden=True)
    @commands.is_owner()
    async def shutdown(ctx: commands.Context):
        """
        Shutdown the Discord Bot

        ...

        Parameters
        ----------
        ctx : commands.Context
            Context in which the command is being invoked under
        """
        await ctx.bot.close()

    # Sync slash commands globally or to specific guilds
    @bot.command(hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        ctx: Context,
        guilds: Greedy[discord.Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        """
        Syncs the slash commands to Discord and creates a dictionary that contains all categories and the commands belonging to them,
        calling this command by itself will perform a global sync

        ...

        Parameters
        ----------
        ctx : commands.Context
            Context in which the command is being invoked under
        guilds : discord.Object
            Specific Guild ids to sync
        spec : Literal["~", "*", "^"], optional, default = None
            The special character that determines how the commands will get synced
            ~ - sync current guild
            * - copies all global app commands to current guild, creates a help dictionary, and syncs
            ^ - clears all commands from the current guild target and syncs (removes guild commands)
        """

        def make_help_dict(bot: commands.Bot) -> None:
            if not bot.help_dict:
                slash_commands = bot.tree.get_commands()
                for x in slash_commands:
                    if "module" in x.extras.keys():
                        cmd_category = x.extras["module"]
                        if cmd_category not in bot.help_dict:
                            bot.help_dict[cmd_category] = [x.name]
                        else:
                            hlist_vals = bot.help_dict[cmd_category]
                            hlist_vals.append(x.name)
                            bot.help_dict[cmd_category] = hlist_vals

        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
                make_help_dict(ctx.bot)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
                # use to form help command
                # i.e. help = {"General": ["ping","help","prefix"], "Utility": ["avatar","userinfo"]}
                make_help_dict(ctx.bot)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
                make_help_dict(ctx.bot)
            else:
                synced = await ctx.bot.tree.sync()
                make_help_dict(ctx.bot)

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
                make_help_dict(ctx.bot)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


# Changes to async in discord.py 2.0

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    gid = os.getenv("GUILD_ID")
    bot = CustomBot()
    load_commands(bot)

    bot.run(token)
