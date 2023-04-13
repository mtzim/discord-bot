import os
import logging
import discord
from discord import Message, Intents, Guild
from db_helper import SqlHelper as SQL
from dotenv import load_dotenv
from customhelper import CustomHelpCommand
from typing import Union, List, Literal, Optional
from discord.ext import commands
from discord.ext.commands import Greedy, Context


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):

        if "intents" not in kwargs:
            intents = Intents.all()
            # intents.members = True
            # intents.message_content = True
            kwargs["intents"] = intents

        # Default prefix is assigned during database table creation
        if "command_prefix" not in kwargs:
            kwargs["command_prefix"] = self.get_prefix

        super().__init__(*args, help_command=CustomHelpCommand(), **kwargs)

        self.initial_extensions = [
            "cogs.timezone_presence",
            "cogs.guild_member_count",
            "cogs.utility",
            "cogs.moderation",
            "cogs.general",
        ]

        self.help_dict = {}

    async def get_prefix(self, message: Message, /) -> Union[List[str], str]:
        db = SQL()
        prefix = db.get_prefix(message.guild.id)
        db.close()
        return prefix

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def close(self):
        await super().close()

    async def on_ready(self):
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
        """Adds the guild entry to the database when the bot joins the guild."""
        db = SQL()
        db.add_guild(guild.name, guild.id)
        db.close()

    async def on_guild_remove(self, guild: Guild):
        """Removes the guild entry from the database if the bot leaves or gets removed from the guild."""
        db = SQL()
        db.delete_guild(guild.id)
        db.close()

    async def on_guild_update(self, before: Guild, after: Guild):
        """Updates the guild name in the database to match the server's guild name if it changes."""
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


def load_commands(bot):
    """Load default commands"""

    @bot.command(hidden=True)
    @commands.is_owner()
    async def shutdown(ctx: commands.Context):
        await ctx.bot.close()

    @bot.tree.command(
        description=f"Check if the bot is online",
        extras={"module": "General"},
    )
    async def ping(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Pong! `{round(interaction.client.latency*1000)}ms`"
        )

    # Sync slash commands globally or to specific guilds
    @bot.command(hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        ctx: Context,
        guilds: Greedy[discord.Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
                # use to form help command
                # help = {"Default": ["sync","help","test"], "Cog": ["ping","update"]}
                # for each command define extras section for which module they belong
                # make a dictionary with key = module names and value = list of command names
                # extras={"module": "Default"}
                slash_commands = bot.tree.get_commands()
                # help_dict = {}
                for x in slash_commands:
                    if "module" in x.extras.keys():
                        cmd_category = x.extras["module"]
                        if cmd_category not in bot.help_dict:
                            bot.help_dict[cmd_category] = [x.name]
                        else:
                            hlist_vals = bot.help_dict[cmd_category]
                            hlist_vals.append(x.name)
                            bot.help_dict[cmd_category] = hlist_vals
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


# Changes to async in discord.py 2.0

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    gid = os.getenv("GUILD_ID")
    bot = MyBot()
    load_commands(bot)

    bot.run(token)
