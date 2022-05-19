import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands

def setup_logging():
    # Create logging directory
    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    #Setup logging
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='./logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def main():
    setup_logging()
    load_dotenv()


    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='?', description='Nothing yet', intents=intents)

    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user} (ID: {bot.user.id})')

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
    
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == "__main__":
    main()
