import os
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):

        if "intents" not in kwargs:
            print(f"intents weren't found, loading from within class")
            intents = discord.Intents.default()
            intents.members = True
            intents.message_content = True
            kwargs["intents"] = intents

        if "command_prefix" not in kwargs:
            kwargs["command_prefix"] = "?"

        super().__init__(*args, **kwargs)

        self.initial_extensions = [
            "cogs.shutdown",
            "cogs.timezone_presence",
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        print(f"setup_hook running...")

    async def close(self):
        await super().close()

    async def on_ready(self):
        print(f"MyBot is ready!")

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
