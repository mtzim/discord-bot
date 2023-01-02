import os
import logging
from discord import Message, Intents, Guild
from db_helper import SqlHelper as SQL
from dotenv import load_dotenv
from discord.ext import commands
from customhelper import CustomHelpCommand
from typing import Union, List


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):

        if "intents" not in kwargs:
            intents = Intents.all()
            # intents.members = True
            # intents.message_content = True
            kwargs["intents"] = intents

        if "command_prefix" not in kwargs:
            kwargs["command_prefix"] = self.get_prefix

        super().__init__(*args, help_command=CustomHelpCommand(), **kwargs)
        # super().__init__(*args, **kwargs)

        self.initial_extensions = [
            "cogs.timezone_presence",
            "cogs.guild_member_count",
            "cogs.utility",
            "cogs.moderation",
        ]

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

    @bot.command()
    async def ping(ctx: commands.Context):
        await ctx.reply(f"Pong! `{round(ctx.bot.latency*1000)}ms`")

    @bot.command(help=f"Usage: `?prefix <NEW PREFIX>`")
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(ctx: commands.Context, new_prefix: str):
        db = SQL()
        if not db.set_prefix(ctx.guild.id, new_prefix):
            await ctx.reply(f"Unable to change prefix.")
        else:
            await ctx.reply(f"Prefix successfully changed to `{new_prefix}`")
        db.close()

    @prefix.error
    async def prefix_err(ctx, err):
        if type(err) == commands.errors.MissingRequiredArgument:
            await ctx.reply(f"Missing required argument `<NEW PREFIX>`")

    """ @bot.command()
    async def invite(ctx: commands.Context):
        pass """


# Changes to async in discord.py 2.0

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    bot = MyBot()
    load_commands(bot)

    bot.run(token)
