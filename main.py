import os
import logging
import discord
from db import SqlDatabase as SQL
from dotenv import load_dotenv
from discord.ext import commands
from helper import MyHelpCommand
from customhelper import CustomHelpCommand


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):

        self.db = SQL("example.db")

        if "intents" not in kwargs:
            intents = discord.Intents.default()
            intents.members = True
            intents.message_content = True
            kwargs["intents"] = intents

        if "command_prefix" not in kwargs:
            kwargs["command_prefix"] = "?"

        # super().__init__(*args, help_command=MyHelpCommand(), **kwargs)
        super().__init__(*args, **kwargs)

        self.initial_extensions = [
            "cogs.shutdown",
            "cogs.timezone_presence",
            "cogs.guild_member_count",
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

        self.db.execute(
            """CREATE TABLE IF NOT EXISTS guilds
            (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            guild_name TEXT NOT NULL,
            guild_id INTEGER NOT NULL UNIQUE, 
             member_count_channel_id INTEGER)"""
        )

    async def close(self):
        self.db.close()
        await super().close()

    async def on_ready(self):
        print(f"MyBot is ready!")

        if len(self.guilds) > 0:
            print("Connected to the following guilds:")

            for count, guild in enumerate(self.guilds):
                print(
                    f"{count+1}) {guild.name}#{guild.id} - Members: {len(guild.members)}"
                )
                self.db.add_guild(guild.name, guild.id)

    async def on_guild_join(self, guild: discord.Guild):
        self.db.add_guild(guild.name, guild.id)

    async def on_guild_remove(self, guild: discord.Guild):
        self.db.delete_guild(guild.id)

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        if before.name != after.name:
            self.db.update_guild_name(after.name, after.id)

    async def on_message(self, message):
        if message.content == "$test":
            await message.reply("I hear you!")
        await super().process_commands(message)


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

# Changes to async in discord.py 2.0

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    bot = MyBot()
    bot.run(token)
