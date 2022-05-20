import os
import asyncio
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands


# Create logging directory
if not os.path.exists("./logs"):
    os.makedirs("./logs")

# Setup logging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="./logs/discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

# Load data from .env file
load_dotenv()

# Enable necessary Gateway features
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="?", description="Nothing yet", intents=intents)


""" @bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    # allow commands to still be processed
    await bot.process_commands(message) """

# Changes to async in discord.py 2.0


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # remove .py from end of file
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    token = os.getenv("DISCORD_TOKEN")
    async with bot:
        await load_extensions()
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
